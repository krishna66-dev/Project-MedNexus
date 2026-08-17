
"""
Ladybird Triage (Prototype) — Flask + Rules + Retrieval + NHS Links (Cached)

✅ What this app does
1) Verifies a patient using PostgreSQL (name + DOB)
2) Lets user choose Clinical or Non-Clinical
3) Clinical flow:
   - Select symptoms + optional notes
   - Shows NHS link + summary for selected symptoms (cached)
   - Applies safety overrides (red flags)
   - Applies age-based overrides (e.g., fever in infant < 3 months)
   - If pain detected → asks pain severity (mild/moderate/severe)
   - If certain symptoms detected → asks follow-up safety questions
   - Otherwise runs TF-IDF retrieval vs Dataset.xlsx to decide 999 / 111 / GP
4) Non-clinical flow:
   - Simple selection → routes to gp_non_clinical response
5) Logs actions to audit_log.csv

Required local files:
- Dataset.xlsx
- ladybird-logo.png

Patient records are loaded from PostgreSQL; patient.xlsx is no longer required.

Install dependencies:
    pip install flask pandas numpy requests beautifulsoup4 scikit-learn openpyxl

Run:
    python app11.py
"""

import os
import re
import csv
import json
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
from urllib.parse import quote_plus, urljoin

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

import requests
from bs4 import BeautifulSoup

from flask import (
    Flask,
    request,
    session,
    redirect,
    url_for,
    render_template_string,
    jsonify,
    send_file,
)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# ============================================================
# PostgreSQL Configuration
# ============================================================

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB", "medtriage")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

if not DB_PASSWORD:
    raise RuntimeError(
        "POSTGRES_PASSWORD is missing from the .env file."
    )

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

db_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

print("PostgreSQL configured:", DB_NAME)

# =========================
# FILES (same folder)
# =========================
# Patient records are loaded from PostgreSQL.
# Kept as a compatibility argument for existing function calls.
PATIENT_XLSX = "postgresql"

# symptom dataset used for TF-IDF retrieval triage
DATASET_XLSX = "Dataset.xlsx"

# audit log file (CSV) where every verification/triage decision is appended
AUDIT_LOG_FILE = "audit_log.csv"

# local cache for NHS lookups (so app still works with limited internet later)
NHS_CACHE_FILE = "nhs_cache.json"

# Logo in same folder
LOGO_FILE = "ladybird-logo.png"
LOGO_URL = "/logo"


# =========================
# BASE TRIAGE THRESHOLDS
# =========================
# Weighted intensity >= BASE_T999 => emergency
BASE_T999 = 85

# Weighted intensity >= BASE_T111 => urgent advice
BASE_T111 = 50

# "no guessing" gates for retrieval:
# if retrieval similarity is too low, return UNKNOWN rather than guessing
MIN_BEST_SIM = 0.25
MIN_AVG_SIM = 0.18

# Final message mapping (what we show on result page)
RESPONSES = {
    "999": "This may be an emergency. Please call 999 now.",
    "111": "Please call NHS 111 for urgent medical advice.",
    "gp_non_clinical": "This is non-clinical. Please leave two messages with your name and request.",
    "UNKNOWN": "I’m not sure based on the dataset. Please add more details (severity, duration, red flags).",
}


# =========================
# NHS LOOKUP (link + short description)
# =========================
# NHS base URL + search endpoint
NHS_BASE = "https://www.nhs.uk"
NHS_SEARCH = "https://www.nhs.uk/search/results?q="

# Overrides for common symptoms (fast + reliable vs search scraping)
NHS_OVERRIDES = {
    "fever": "https://www.nhs.uk/symptoms/fever-in-adults/",
    "high temperature": "https://www.nhs.uk/symptoms/fever-in-adults/",
    "temperature": "https://www.nhs.uk/symptoms/fever-in-adults/",
    "cold": "https://www.nhs.uk/conditions/common-cold/",
    "flu": "https://www.nhs.uk/conditions/flu/",
    "cough": "https://www.nhs.uk/conditions/cough/",
    "sore throat": "https://www.nhs.uk/conditions/sore-throat/",
    "headache": "https://www.nhs.uk/conditions/headaches/",
    "migraine": "https://www.nhs.uk/conditions/migraine/",
    "diarrhoea": "https://www.nhs.uk/conditions/diarrhoea-and-vomiting/",
    "vomiting": "https://www.nhs.uk/conditions/diarrhoea-and-vomiting/",
    "chest pain": "https://www.nhs.uk/conditions/chest-pain/",
    "shortness of breath": "https://www.nhs.uk/conditions/shortness-of-breath/",
}


def load_nhs_cache() -> Dict[str, Dict]:
    """
    Load NHS cache from local JSON file (nhs_cache.json).

    Returns:
        dict mapping symptom_text_lower -> {query,url,title,desc,status}
    """
    if os.path.isfile(NHS_CACHE_FILE):
        try:
            with open(NHS_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_nhs_cache(cache: Dict[str, Dict]):
    """
    Save NHS cache to disk so repeated symptom lookups are faster.

    This is best-effort: failure should not crash the app.
    """
    try:
        with open(NHS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# global cache stored in memory + persisted to disk
NHS_CACHE = load_nhs_cache()


def _http_get(url: str, timeout: int = 10) -> Optional[str]:
    """
    Make a simple GET request and return HTML (string) if successful.

    Returns:
        HTML text if status 200 else None
    """
    try:
        r = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (local-triage-prototype)"},
        )
        if r.status_code != 200:
            return None
        return r.text
    except Exception:
        return None


def nhs_find_best_url(query: str) -> Optional[str]:
    """
    Find a relevant NHS URL for a given query.

    Logic:
    1) Try overrides (exact or substring)
    2) If no override, scrape NHS search results and pick the first relevant link

    Returns:
        A full NHS URL or None if not found / offline
    """
    q = (query or "").strip().lower()
    if not q:
        return None

    # override match (either exact or query contains keyword)
    for k, v in NHS_OVERRIDES.items():
        if q == k or k in q:
            return v

    # fallback to NHS search scraping
    html = _http_get(NHS_SEARCH + quote_plus(q))
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # pick the first useful link under NHS domain
    for a in soup.select("a"):
        href = a.get("href") or ""
        if href.startswith("/"):
            full = urljoin(NHS_BASE, href)
        elif href.startswith("http"):
            full = href
        else:
            continue

        if full.startswith(NHS_BASE) and (
            "/conditions/" in full
            or "/symptoms/" in full
            or "/medicines/" in full
            or "/services/" in full
        ):
            return full

    return None


def nhs_extract_description(page_html: str) -> str:
    """
    Extract a short description from an NHS page HTML.

    Strategy:
    - Find the first sufficiently-long paragraph inside <main>
    - If nothing usable, fall back to <title>

    Returns:
        Short plain-text summary (max ~380 chars)
    """
    soup = BeautifulSoup(page_html, "html.parser")
    main = soup.find("main") or soup
    ps = main.find_all("p")

    for p in ps:
        text = " ".join(p.get_text(" ", strip=True).split())
        if len(text) >= 60:
            return text[:380] + ("…" if len(text) > 380 else "")

    title = soup.find("title")
    if title:
        t = title.get_text(strip=True)
        return t[:180]
    return ""


def nhs_lookup(symptom_text: str) -> Dict[str, str]:
    """
    Lookup NHS info (url + title + short description) for a symptom text.

    Uses:
    - local cache (nhs_cache.json)
    - overrides
    - NHS search scrape

    Returns:
        dict:
          query: original
          url: NHS link or NHS search link
          title: NHS page h1 if available
          desc: extracted summary
          status: cached | ok | offline | not_found
    """
    q = (symptom_text or "").strip()
    key = q.lower()
    if not key:
        return {"query": q, "url": "", "title": "", "desc": "", "status": "not_found"}

    # Return cached if exists
    if key in NHS_CACHE:
        cached = NHS_CACHE[key].copy()
        cached["status"] = "cached"
        return cached

    url = nhs_find_best_url(q)
    if not url:
        return {"query": q, "url": NHS_SEARCH + quote_plus(q), "title": "", "desc": "", "status": "not_found"}

    page = _http_get(url)
    if not page:
        data = {"query": q, "url": url, "title": "", "desc": "", "status": "offline"}
        NHS_CACHE[key] = data
        save_nhs_cache(NHS_CACHE)
        return data

    soup = BeautifulSoup(page, "html.parser")
    title = soup.find("h1")
    title_text = title.get_text(strip=True) if title else ""
    desc = nhs_extract_description(page)

    data = {"query": q, "url": url, "title": title_text, "desc": desc, "status": "ok"}
    NHS_CACHE[key] = data
    save_nhs_cache(NHS_CACHE)
    return data


def render_nhs_cards(selected_items: List[str]) -> str:
    """
    Render up to 3 NHS cards as HTML for the selected symptoms.

    Used inside the result page to show:
    - title
    - short description
    - NHS URL
    - cache status
    """
    if not selected_items:
        return "<div class='muted'>No NHS info (no symptom selected).</div>"

    cards = []
    for item in selected_items[:3]:
        info = nhs_lookup(item)
        url = info.get("url", "")
        title = info.get("title", "") or item
        desc = info.get("desc", "")
        status = info.get("status", "")
        badge = status.upper()

        cards.append(
            f"""
        <div class="nhsCard">
          <div class="nhsTitle">{title}</div>
          <div class="nhsDesc">{desc if desc else "<span class='muted'>No description available (offline/not found).</span>"}</div>
          <div class="nhsLink"><a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></div>
          <div class="nhsBadge">{badge}</div>
        </div>
        """
        )

    return "\n".join(cards)


# =========================
# FOLLOW-UP QUESTIONS
# =========================
# These are additional safety questions for certain topics (e.g., chest pain).
FOLLOW_UP_QUESTIONS = {
    "chest pain": [
        ("Is the pain severe or crushing?", "severe"),
        ("Are you struggling to breathe?", "breathing"),
        ("Is the pain spreading to your arm, jaw, or back?", "radiating"),
        ("Did it start suddenly?", "sudden"),
    ],
    "shortness of breath": [
        ("Are you unable to speak full sentences?", "cant_speak_full"),
        ("Is it getting worse rapidly?", "worsening"),
        ("Are your lips/face turning blue or grey?", "blue_lips"),
    ],
    "stroke": [
        ("Is one side of your face drooping?", "face_droop"),
        ("Is your speech slurred or difficult?", "speech"),
        ("Is one arm weak or numb?", "arm_weak"),
        ("Did it start suddenly?", "sudden"),
    ],
    "severe bleeding": [
        ("Is the bleeding heavy and not stopping?", "heavy"),
        ("Are you feeling faint or dizzy?", "faint"),
        ("Did it follow a major injury?", "injury"),
    ],
    "seizure": [
        ("Has the seizure lasted more than 5 minutes?", "long"),
        ("Is this the first seizure?", "first"),
        ("Are they not fully waking up after?", "not_waking"),
    ],
}

# answers that should count as "yes"
YES_SET = {"yes", "y", "true", "1"}


def detect_followup_trigger(text: str) -> Optional[str]:
    """
    Decide if the user's text should trigger a follow-up safety questionnaire.

    Example:
    - If input contains "chest pain" → return "chest pain"
    - If input contains certain synonyms → map into a trigger category

    Returns:
        trigger key (string) or None
    """
    t = (text or "").lower()
    for key in FOLLOW_UP_QUESTIONS.keys():
        if key in t:
            return key
    if "tight chest" in t or "pressure in chest" in t:
        return "chest pain"
    if "breathing problem" in t or "breathing difficulty" in t:
        return "shortness of breath"
    return None


def evaluate_followups(answers: Dict[str, str], threshold_yes: int = 2) -> Tuple[bool, int]:
    """
    Convert follow-up answers into a safety decision.

    If yes_count >= threshold_yes:
        treat as dangerous → caller should be routed to 999
    else:
        route to 111

    Returns:
        (danger_boolean, yes_count)
    """
    yes_count = 0
    for v in answers.values():
        if (v or "").strip().lower() in YES_SET:
            yes_count += 1
    return (yes_count >= threshold_yes, yes_count)


# =========================
# PAIN SEVERITY FEATURE
# =========================
# Keywords that indicate pain, causing a pain severity screen to appear
PAIN_KEYWORDS = [r"\bpain\b", r"\bhurts\b", r"\bache\b", r"\baching\b", r"\bsore\b"]


def contains_pain(text: str) -> bool:
    """
    Detect whether the user input contains pain keywords.

    Returns:
        True if pain-like words found, else False
    """
    t = (text or "").lower()
    return any(re.search(p, t) for p in PAIN_KEYWORDS)


def apply_pain_severity_decision(user_text: str, severity: str) -> Tuple[str, Dict]:
    """
    Convert pain severity into a triage decision.

    Logic:
    - mild/normal → gp_clinical
    - moderate → gp_clinical
    - severe → normally 111
    - severe + chest pain → trigger FOLLOWUP safety questions

    Returns:
        (label, debug_dict)
    """
    t = (user_text or "").lower()
    severity = (severity or "").lower().strip()

    if severity in {"normal", "mild"}:
        return "gp_clinical", {"source": "pain_severity", "severity": severity, "rule": "mild_pain_gp_clinical"}
    if severity in {"moderate"}:
        return "gp_clinical", {"source": "pain_severity", "severity": severity, "rule": "moderate_pain_gp_clinical"}
    if severity in {"severe"}:
        if "chest pain" in t or "tight chest" in t or "pressure in chest" in t:
            return "FOLLOWUP", {"source": "pain_severity", "severity": severity, "rule": "chest_pain_followup"}
        return "111", {"source": "pain_severity", "severity": severity, "rule": "severe_pain_111"}
    return "", {}


# =========================
# AGE-AWARE FEATURE
# =========================
FEVER_PATTERNS = [r"\bfever\b|\btemperature\b|\bhigh temp\b|\bhigh temperature\b|\bfeeling hot\b|\bchills\b"]


def parse_dob_to_date(dob_str: str) -> Optional[date]:
    """
    Parse DOB string into a python date object using pandas tolerant parser.

    Returns:
        date or None if parsing failed
    """
    if not dob_str:
        return None
    s = str(dob_str).strip()
    try:
        dt = pd.to_datetime(s, errors="coerce")
        if pd.isna(dt):
            return None
        return dt.date()
    except Exception:
        return None


def calc_age(dob: Optional[date]) -> Tuple[Optional[int], Optional[int]]:
    """
    Calculate age in years and days.

    Returns:
        (age_years, age_days)
        Both None if dob missing or invalid.
    """
    if dob is None:
        return None, None
    today = date.today()
    age_days = (today - dob).days
    if age_days < 0:
        return None, None
    age_years = age_days // 365
    return age_years, age_days


def adjusted_thresholds(age_years: Optional[int], age_days: Optional[int]) -> Tuple[int, int, Dict]:
    """
    Adjust retrieval thresholds based on age.

    Example currently implemented:
    - age >= 65 => stricter thresholds (lower)
    """
    debug = {"source": "age_thresholds", "age_years": age_years, "age_days": age_days}
    t111, t999 = BASE_T111, BASE_T999
    if age_years is not None and age_years >= 65:
        t111 = 40
        t999 = 75
        debug["adjustment"] = "elderly_stricter"
    return t111, t999, debug


def has_any(patterns: List[str], text: str) -> bool:
    """
    Utility: check if ANY regex pattern matches text (case-insensitive).
    """
    return any(re.search(p, text, flags=re.I) for p in patterns)


def age_rule_override(text: str, age_days: Optional[int]) -> Tuple[str, Dict]:
    """
    Age-specific rule overrides (applied before normal rules/retrieval).

    Implemented:
    - infant < 3 months (90 days) + fever => route to 111

    Returns:
        (label, debug_dict) or ("", {}) if no override
    """
    t = (text or "").lower().strip()
    if not t or age_days is None:
        return "", {}
    if age_days < 90 and has_any(FEVER_PATTERNS, t):
        return "111", {"source": "age_rules", "rule": "fever_in_infant_under_3_months", "age_days": age_days}
    return "", {}


# =========================
# RULE OVERRIDES
# =========================
# Hard safety patterns that should immediately go to 999
RED_FLAG_PATTERNS = [
    r"\b(can'?t breathe|cannot breathe|struggling to breathe|severe shortness of breath)\b",
    r"\bstroke\b|\bface droop\b|\bslurred speech\b|\bone side (is )?weak\b|\barm weakness\b",
    r"\bfainted\b|\bpassed out\b|\bloss of consciousness\b",
    r"\bsevere bleeding\b|\bbleeding a lot\b",
    r"\bseizure\b|\bfit\b",
    r"\banaphylaxis\b|\bthroat closing\b|\bswollen lips\b|\bhives\b.*\bbreath\b",
]

# Mild common illness patterns → GP clinical (if not severe)
COMMON_ILLNESS_PATTERNS = [
    r"\bfever\b|\btemperature\b|\bfeeling hot\b|\bchills\b",
    r"\bcold\b|\brunny nose\b|\bsneezing\b|\bnasal congestion\b|\bstuffy nose\b",
    r"\bcough\b|\bsore throat\b|\bthroat pain\b",
    r"\bflu\b|\bflu like\b|\bbody ache\b|\baches\b",
    r"\bheadache\b|\bmigraine\b",
    r"\bnausea\b|\bvomit\b|\bvomiting\b|\bdiarrh(o)?ea\b|\bstomach upset\b",
]

# Limb pain patterns → GP clinical (if not severe)
LIMB_PAIN_PATTERNS = [
    r"\b(arm|leg|knee|ankle|wrist|elbow|shoulder|hip|foot|hand)\s+pain\b",
    r"\bpain in (my )?(arm|leg|knee|ankle|wrist|elbow|shoulder|hip|foot|hand)\b",
    r"\b(arm|leg)\s+hurts\b",
]

# Indicators that something is severe (used to block "mild illness" shortcut)
SEVERE_PATTERNS = [
    r"\bsevere\b|\bunbearable\b|\bworst\b|\bextreme\b|\bintense\b",
    r"\bnot improving\b|\bgetting worse\b|\bworsening\b|\brapidly\b",
    r"\bhigh fever\b|\bvery high fever\b",
    r"\bshort of breath\b|\bbreathing difficulty\b",
    r"\bconfusion\b|\bdisoriented\b",
    r"\bnumb\b|\bnumbness\b|\btingling\b",
    r"\bcan'?t move\b|\bcannot move\b|\bweakness\b",
    r"\bswelling\b|\bswollen\b",
    r"\bdeformed\b|\bfracture\b|\bbroken\b|\bbone\b",
    r"\bblood\b|\bbleeding\b",
]


def rule_override(text: str) -> Tuple[str, Dict]:
    """
    Rule-based triage override applied BEFORE retrieval.

    Priority:
    1) If any red flag pattern matches → 999
    2) If mild common illness (and not severe) → gp_clinical
    3) If normal limb pain (and not severe) → gp_clinical
    4) Otherwise no override

    Returns:
        (label, debug_dict) or ("", {})
    """
    t = (text or "").lower().strip()
    if not t:
        return "", {}

    # emergency red flags
    for pat in RED_FLAG_PATTERNS:
        if re.search(pat, t, flags=re.I):
            return "999", {"source": "rules", "rule": "red_flag", "pattern": pat}

    severe = has_any(SEVERE_PATTERNS, t)

    # mild/common illness → GP (unless severe)
    if has_any(COMMON_ILLNESS_PATTERNS, t) and not severe:
        return "gp_clinical", {"source": "rules", "rule": "common_mild_illness"}

    # mild limb pain → GP (unless severe)
    if has_any(LIMB_PAIN_PATTERNS, t) and not severe:
        return "gp_clinical", {"source": "rules", "rule": "normal_limb_pain"}

    return "", {}


# =========================
# RETRIEVAL TRIAGE
# =========================
def normalize_clinical_flag(x: str) -> str:
    """
    Normalize dataset clinical flag to one of:
      - "clinical"
      - "non_clinical"
    """
    s = str(x).strip().lower()
    if "non" in s and "clinical" in s:
        return "non_clinical"
    if "clinical" in s:
        return "clinical"
    return "non_clinical"


@dataclass
class Match:
    """
    Data object representing one dataset match (for debugging and scoring).
    """
    text: str
    intensity: float
    clinical_flag: str
    category: str
    similarity: float


class RetrievalTriage:
    """
    TF-IDF retrieval engine.

    Builds a vector index from dataset symptom strings.
    For a user query:
      - fetch top_k most similar dataset rows
      - compute weighted intensity score
      - compute weighted "clinical vs non-clinical" vote
      - output label: 999 / 111 / gp_clinical / gp_non_clinical / UNKNOWN
    """

    def __init__(self, df: pd.DataFrame):
        """
        Prepare dataset and build TF-IDF matrix.

        Args:
            df: pandas DataFrame loaded from Dataset.xlsx
        """
        self.df = df.copy()

        # normalize important columns for retrieval
        self.df["text"] = self.df["SYMPTOMS/DISEASES"].astype(str).str.lower().str.strip()
        self.df["clinical_flag"] = self.df["CLINICAL/NON CLINICAL"].astype(str)
        self.df["category"] = self.df["CATEGORY"].astype(str) if "CATEGORY" in self.df.columns else ""
        self.df["intensity"] = pd.to_numeric(self.df["EMERGENCY INTENSITY"], errors="coerce").fillna(0.0)

        # TF-IDF vectorizer: unigrams + bigrams improves matching phrases
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)

        # matrix of dataset texts
        self.X = self.vectorizer.fit_transform(self.df["text"].tolist())

    def search(self, query: str, top_k: int = 6) -> List[Match]:
        """
        Find the top_k most similar dataset rows for a query.

        Returns:
            list of Match sorted by similarity desc
        """
        q = (query or "").lower().strip()
        if not q:
            return []

        qv = self.vectorizer.transform([q])
        sims = cosine_similarity(qv, self.X).reshape(-1)
        idx = np.argsort(-sims)[:top_k]

        out: List[Match] = []
        for i in idx:
            out.append(
                Match(
                    text=self.df.iloc[i]["text"],
                    intensity=float(self.df.iloc[i]["intensity"]),
                    clinical_flag=str(self.df.iloc[i]["clinical_flag"]),
                    category=str(self.df.iloc[i]["category"]),
                    similarity=float(sims[i]),
                )
            )
        return out

    def decide(self, matches: List[Match], t111: int, t999: int) -> Tuple[str, Dict]:
        """
        Convert retrieval matches into a triage decision.

        Steps:
        1) Gate using similarity thresholds (no guessing)
        2) Compute weights proportional to similarity
        3) Weighted intensity score → compare to thresholds for 999/111
        4) If not 999/111, decide GP type based on clinical vote

        Returns:
            (label, debug_dict)
        """
        if not matches:
            return "UNKNOWN", {"source": "retrieval", "reason": "no matches"}

        best_sim = matches[0].similarity
        avg_sim = float(np.mean([m.similarity for m in matches]))

        # No guessing gate: avoid random decisions for weak matches
        if best_sim < MIN_BEST_SIM or avg_sim < MIN_AVG_SIM:
            return "UNKNOWN", {
                "source": "retrieval",
                "reason": "similarity too low (no guessing)",
                "best_sim": best_sim,
                "avg_sim": avg_sim,
            }

        sims = np.array([m.similarity for m in matches], dtype=np.float32)
        weights = sims / (sims.sum() + 1e-9)

        intensities = np.array([m.intensity for m in matches], dtype=np.float32)
        weighted_intensity = float((weights * intensities).sum())

        clinical_votes = np.array(
            [1.0 if normalize_clinical_flag(m.clinical_flag) == "clinical" else 0.0 for m in matches],
            dtype=np.float32,
        )
        clinical_score = float((weights * clinical_votes).sum())
        is_clinical = clinical_score >= 0.5

        # Final thresholds mapping
        if weighted_intensity >= t999:
            label = "999"
        elif weighted_intensity >= t111:
            label = "111"
        else:
            label = "gp_clinical" if is_clinical else "gp_non_clinical"

        debug = {
            "source": "retrieval",
            "best_sim": best_sim,
            "avg_sim": avg_sim,
            "weighted_intensity": weighted_intensity,
            "clinical_score": clinical_score,
            "used_top_k": len(matches),
            "t111": t111,
            "t999": t999,
        }
        return label, debug


# =========================
# AUDIT LOG
# =========================
def audit_log(event_type: str, payload: Dict):
    """
    Append a row into audit_log.csv with:
    - user identity from session (name, dob, gp)
    - last input text
    - decision + source + details

    Args:
        event_type: e.g. "verify", "triage"
        payload: dict containing decision/source/details
    """
    exists = os.path.isfile(AUDIT_LOG_FILE)
    now = datetime.utcnow().isoformat()

    row = {
        "timestamp_utc": now,
        "event_type": event_type,
        "patient_name": session.get("name", ""),
        "patient_dob": session.get("dob", ""),
        "age_years": session.get("age_years", ""),
        "registered_gp": session.get("gp_office", ""),
        "service_type": session.get("service_type", ""),
        "input_text": session.get("last_input", ""),
        "decision": payload.get("decision", ""),
        "source": payload.get("source", ""),
        "details": payload.get("details", ""),
    }

    fieldnames = list(row.keys())
    with open(AUDIT_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


# =========================
# LOAD XLSX
# =========================
def load_patients_xlsx(path: str) -> pd.DataFrame:
    """
    Load patient records from the PostgreSQL ``patients`` table.

    The ``path`` argument is retained for compatibility with the previous
    Excel-based implementation; it is intentionally ignored.

    Required PostgreSQL columns:
      - name
      - dob

    Any additional columns are preserved and displayed as read-only patient
    details in the application.
    """
    query = "SELECT * FROM patients;"

    try:
        df = pd.read_sql_query(query, db_engine)
    except Exception as e:
        raise RuntimeError(
            f"Failed to load patients from PostgreSQL: {e}"
        ) from e

    required = ["name", "dob"]
    for req in required:
        if req not in df.columns:
            raise RuntimeError(
                f"PostgreSQL patients table is missing column '{req}'. "
                f"Found: {list(df.columns)}"
            )

    # Normalized helper columns used only for exact name + DOB verification.
    df["_name_norm"] = (
        df["name"].astype(str).str.strip().str.lower()
    )
    df["_dob_norm"] = (
        df["dob"].astype(str).str.strip()
    )

    return df


def verify_patient(df: pd.DataFrame, name: str, dob: str) -> Optional[Dict]:
    """
    Verify patient identity by matching name + DOB against PostgreSQL.

    Returns:
        patient row as dict if found, otherwise None.
    """
    n = (name or "").strip().lower()
    d = (dob or "").strip()

    if not n or not d:
        return None

    m = df[(df["_name_norm"] == n) & (df["_dob_norm"] == d)]
    if m.empty:
        return None

    return m.iloc[0].to_dict()

def load_dataset_xlsx(path: str) -> pd.DataFrame:
    """
    Load Dataset.xlsx and enforce required columns needed by retrieval.

    Required:
      - SYMPTOMS/DISEASES
      - EMERGENCY INTENSITY
      - CLINICAL/NON CLINICAL
    """
    if not os.path.isfile(path):
        raise RuntimeError(f"Dataset.xlsx not found: {path}")
    df = pd.read_excel(path)
    required = ["SYMPTOMS/DISEASES", "EMERGENCY INTENSITY", "CLINICAL/NON CLINICAL"]
    for c in required:
        if c not in df.columns:
            raise RuntimeError(f"Dataset.xlsx missing column '{c}'. Found: {list(df.columns)}")
    return df.dropna(subset=["SYMPTOMS/DISEASES"]).copy()


def build_dropdowns(dataset_df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Build dropdown lists for clinical and non-clinical items
    based on dataset column CLINICAL/NON CLINICAL.

    Returns:
        (clinical_items, nonclinical_items)
    """
    clinical_items, nonclinical_items = [], []
    for _, r in dataset_df.iterrows():
        item = str(r["SYMPTOMS/DISEASES"]).strip()
        flag = normalize_clinical_flag(r["CLINICAL/NON CLINICAL"])
        if not item:
            continue
        if flag == "clinical":
            clinical_items.append(item)
        else:
            nonclinical_items.append(item)
    return sorted(set(clinical_items)), sorted(set(nonclinical_items))


# =========================
# FLASK APP
# =========================
app = Flask(__name__)

# Secret key is required for Flask sessions.
# In production: store in env var, not hardcoded.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

# Allow the separate Svelte/Vite MedNexus frontend to use this Flask backend.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@app.after_request
def add_frontend_cors(response):
    origin = request.headers.get("Origin")
    if origin == FRONTEND_URL:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# Load everything once at startup
patients_df = load_patients_xlsx(PATIENT_XLSX)
dataset_df = load_dataset_xlsx(DATASET_XLSX)
engine = RetrievalTriage(dataset_df)
CLINICAL_LIST, NONCLINICAL_LIST = build_dropdowns(dataset_df)


# =========================
# UI (Gray=#BDBDBD, red=#FF0000, SF Pro + Patrick Hand SC)
# =========================
CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand+SC&display=swap');

  :root{
    --purple:#2b135a;
    --red:#FF0000;
    --gray:#BDBDBD;
    --ink:#0b0b0b;
    --muted:#6b7280;
    --line: var(--gray);
    --border: var(--gray);
  }
  *{box-sizing:border-box}
  body{
    margin:0;
    font-family: "SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,ui-sans-serif,system-ui;
    color:var(--ink);
    background:#fff;
  }

  .topstrip{
    height:54px;
    background:linear-gradient(90deg, #3a1d79, var(--purple));
  }
  .wrap{
    max-width: 1300px;
    margin: 0 auto;
    padding: 0 18px;
  }

  .hero{
    min-height: calc(100vh - 54px);
    display:flex;
    flex-direction:column;
    justify-content:flex-start;
    align-items:center;
    padding-top: 70px;
  }

  .brandRow{
    width: 980px;
    max-width: 96vw;
    display:flex;
    justify-content:center;
    align-items:center;
    margin-bottom: 18px;
  }
  .brandLogo{
    height: 70px;
    width: auto;
    display:block;
  }

  .title{
    font-size: 72px;
    line-height: 1;
    margin: 0;
    letter-spacing: -1px;
    font-weight: 700;
    text-align:center;
  }
  .subtitle{
    margin-top: 18px;
    font-family: "Patrick Hand SC", cursive;
    font-size: 34px;
    letter-spacing: 1px;
    text-align:center;
    font-weight: 400;
  }

  .centerForm{
    margin-top: 56px;
    width: 620px;
    max-width: 92vw;
  }
  .label{
    font-size: 14px;
    color: var(--muted);
    margin-bottom: 8px;
  }

  .inputLine{
    width:100%;
    border:none;
    border-bottom: 2px solid var(--line);
    padding: 12px 6px;
    font-size: 16px;
    outline:none;
  }
  .inputLine:focus{
    border-bottom-color: #111827;
  }

  .btnRed{
    margin-top: 14px;
    width:100%;
    border:none;
    background: var(--red);
    color:#fff;
    padding: 14px 18px;
    font-size: 18px;
    cursor:pointer;
  }
  .btnRed:hover{ filter: brightness(0.95); }

  .tiny{
    margin-top: 14px;
    font-size: 13px;
    color: #4b5563;
    text-align:center;
  }
  .tiny a{ color:#111; font-weight:600; text-decoration:none; }
  .tiny a:hover{ text-decoration:underline; }

  /* ✅ bigger patient details area */
  .panel{
    margin-top: 28px;
    width: 1240px;
    max-width: 98vw;
    display:grid;
    grid-template-columns: 1fr 1.45fr; /* RIGHT side much bigger */
    gap: 28px;
  }
  @media (max-width: 1100px){
    .panel{ grid-template-columns:1fr; }
  }

  .card{
    border:1px solid #e5e7eb;
    border-color: var(--border);
    border-radius: 12px;
    padding: 18px;
    background: #fff;
  }
  .card h2{ margin:0 0 8px 0; font-size:20px; font-weight:600; }
  .card h3{ margin:0 0 10px 0; font-size:16px; font-weight:600; }
  .muted{ color: var(--muted); font-size: 13px; line-height: 1.5; }

  .pills{ display:flex; flex-wrap:wrap; gap:10px; margin-top: 10px; }
  .pill{
    border:1px solid var(--border);
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 13px;
    background:#fff;
  }

  .row{ display:flex; gap: 14px; flex-wrap:wrap; margin-top: 10px; }
  .btn{
    border:1px solid #111;
    background:#fff;
    color:#111;
    padding: 12px 14px;
    border-radius: 8px;
    cursor:pointer;
    font-size: 14px;
  }
  .btn:hover{ background:#f3f4f6; }
  .btnGhost{
    border:1px solid var(--border);
    color:#111;
  }
  .btnPrimary{
    border:none;
    background: var(--red);
    color:#fff;
  }

  .selectLine{
    width:100%;
    border:1px solid var(--border);
    border-radius: 10px;
    padding: 12px 10px;
    font-size: 14px;
    outline:none;
  }

  .resultsBox{
    margin-top: 10px;
    border:1px solid var(--border);
    border-radius: 12px;
    padding: 10px;
    max-height: 260px;
    overflow:auto;
    background:#fff;
  }

  .resItem{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:20px;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid var(--border);
    margin: 12px 0;
    background:#ffffff;
    font-size:15px;
  }
  .resItem:hover{ background:#f9fafb; }

  .addBtn{
    border:1px solid #111;
    background:#fff;
    padding: 8px 10px;
    border-radius: 8px;
    cursor:pointer;
  }

  .chips{ display:flex; flex-wrap:wrap; gap:10px; margin-top: 12px; }
  .chip{
    border:1px solid var(--border);
    border-radius: 999px;
    padding: 8px 12px;
    display:flex;
    align-items:center;
    gap:10px;
    background:#fff;
  }
  .chipX{
    width:22px;height:22px;border-radius:999px;
    border:1px solid var(--border);background:#f3f4f6;
    display:flex;align-items:center;justify-content:center;
    cursor:pointer;
    font-weight:700;
  }

  textarea{
    width:100%;
    border:1px solid var(--border);
    border-radius: 10px;
    padding: 12px 10px;
    min-height: 100px;
    outline:none;
    margin-top: 10px;
  }

  pre{
    white-space: pre-wrap;
    word-break: break-word;
    background:#0b0b0b;
    color:#fff;
    padding: 12px;
    border-radius: 12px;
    overflow:auto;
    font-size: 12px;
  }

  .nhsCard{
    border:1px solid var(--border);
    border-radius: 12px;
    padding: 12px;
    margin-top: 12px;
    background:#fff;
  }
  .nhsTitle{ font-weight:700; margin-bottom:6px; }
  .nhsDesc{ color:#374151; font-size: 13px; line-height: 1.45; }
  .nhsLink{ margin-top:8px; font-size: 12px; word-break: break-all; }
  .nhsBadge{
    margin-top: 10px;
    display:inline-block;
    font-size: 11px;
    padding: 4px 8px;
    border-radius: 999px;
    border:1px solid var(--border);
    background:#f9fafb;
    color:#111;
  }

  /* ✅ Patient details window bigger */
  .patientDetailsBox{
    max-height: 760px !important;
    padding: 16px;
  }

  .dangerNote{
    width: 980px;
    max-width: 96vw;
    margin-top: 18px;
    font-size: 13px;
    color: #6b7280;
    text-align:center;
  }
</style>
"""

BASE_TOP = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Ladybird Triage</title>
  """ + CSS + """
</head>
<body>
  <div class="topstrip"></div>
  <div class="wrap">
"""

BASE_BOTTOM = """
  </div>
</body>
</html>
"""

# =========================
# PAGES (templates)
# =========================
LOGIN_HTML = BASE_TOP + f"""
  <div class="hero">
    <div class="brandRow">
      <img class="brandLogo" src="{LOGO_URL}" alt="Ladybird logo"/>
    </div>

    <h1 class="title">Curious?</h1>
    <div class="subtitle">JOIN US FOR ALL THINGS AI</div>

    <div class="centerForm">
      <form method="post">
        <div class="label">Enter your name here</div>
        <input class="inputLine" name="name" required placeholder="e.g., John Smith" />

        <div style="height:14px"></div>

        <div class="label">Enter your DOB here (YYYY-MM-DD)</div>
        <input class="inputLine" name="dob" required placeholder="e.g., 1990-01-20" />

        <button class="btnRed" type="submit">Continue</button>

        <div class="tiny">
          By continuing, you agree to Ladybird's <a href="#">Terms of Use</a> and <a href="#">Privacy Policy</a>
        </div>

        {{% if error %}}
          <div class="tiny" style="color:#dc2626;margin-top:10px;font-weight:700">{{{{error}}}}</div>
        {{% endif %}}
      </form>
    </div>

    <div class="dangerNote">
      Important: This is a prototype triage assistant. If you believe it is an emergency, call <b>999</b>.
    </div>
  </div>
""" + BASE_BOTTOM


SERVICE_HTML = BASE_TOP + """
  <div class="hero" style="padding-top:60px">
    <!-- Verified heading: no tick, not bold -->
    <h1 class="title" style="font-size:52px;font-weight:500">Verified</h1>
    <div class="subtitle" style="font-size:26px">Choose a service to continue</div>

    <div class="panel">
      <div class="card">
        <h2>Patient</h2>
        <div class="pills">
          <div class="pill"><b>Name:</b> {{name}}</div>
          <div class="pill"><b>DOB:</b> {{dob}}</div>
          <div class="pill"><b>Age:</b> {{age_display}}</div>
          <div class="pill"><b>GP:</b> {{gp_office}}</div>
        </div>

        <div class="row" style="margin-top:18px">
          <form method="post" action="/service">
            <input type="hidden" name="service_type" value="clinical"/>
            <button class="btn btnPrimary" type="submit">Clinical</button>
          </form>

          <form method="post" action="/service">
            <input type="hidden" name="service_type" value="non_clinical"/>
            <button class="btn btnPrimary" type="submit">Non Clinical</button>
          </form>

          <form method="post" action="/logout">
            <button class="btn btnGhost" type="submit">Logout</button>
          </form>
        </div>

        <div class="dangerNote" style="text-align:left;margin-top:14px">
          For emergencies, call <b>999</b>. For urgent advice, call <b>111</b>.
        </div>
      </div>

      <div class="card">
        <h2>Patient Details</h2>
        <div class="muted">Read-only fields from <b>PostgreSQL</b></div>
        <div class="resultsBox patientDetailsBox">
          {% for k,v in details.items() %}
            <div class="resItem">
              <div class="muted" style="max-width:55%"><b>{{k}}</b></div>
              <div style="text-align:right;max-width:45%">{{v}}</div>
            </div>
          {% endfor %}
        </div>
      </div>
    </div>
  </div>
""" + BASE_BOTTOM


NONCLINICAL_FORM_HTML = BASE_TOP + """
  <div class="hero" style="padding-top:70px">
    <h1 class="title" style="font-size:52px">Non Clinical</h1>
    <div class="subtitle" style="font-size:26px">Select your request</div>

    <div class="centerForm" style="margin-top:40px">
      <form method="post" action="/triage">
        <input type="hidden" name="service_type" value="non_clinical"/>

        <div class="label">Choose request</div>
        <select class="selectLine" name="selected_item" required>
          <option value="">-- Select --</option>
          {% for item in items %}<option value="{{item}}">{{item}}</option>{% endfor %}
        </select>

        <button class="btnRed" type="submit" style="margin-top:18px">Submit</button>

        <div class="row" style="margin-top:12px">
          <a href="/service_page"><button class="btn btnGhost" type="button">Back</button></a>
        </div>
      </form>
    </div>
  </div>
""" + BASE_BOTTOM


CLINICAL_FORM_HTML = BASE_TOP + """
  <div class="hero" style="padding-top:70px">
    <h1 class="title" style="font-size:52px">Clinical</h1>
    <div class="subtitle" style="font-size:26px">Search and select symptoms</div>

    <div class="panel" style="margin-top:34px">
      <div class="card">
        <form method="post" action="/triage" onsubmit="return buildHiddenSelections()">
          <input type="hidden" name="service_type" value="clinical"/>

          <div class="label">Search symptoms (type 2+ letters)</div>
          <input id="symSearch" class="inputLine" placeholder="e.g., fever, cough, arm pain"/>

          <div id="resultsBox" class="resultsBox" style="display:none;margin-top:16px"></div>
          <div id="hintBox" class="muted" style="margin-top:12px">Start typing to see matches (max 20).</div>

          <div class="label" style="margin-top:22px">Selected symptoms</div>
          <div id="selectedChips" class="chips"></div>

          <div id="hiddenSelections"></div>

          <div class="label" style="margin-top:22px">Additional notes (optional)</div>
          <textarea name="custom_text" placeholder="e.g., started 2 days ago, mild fever"></textarea>

          <button class="btnRed" type="submit" style="margin-top:18px">Submit</button>

          <div class="row" style="margin-top:12px">
            <a href="/service_page"><button class="btn btnGhost" type="button">Back</button></a>
          </div>
        </form>
      </div>

      <div class="card">
        <h2>NHS Link</h2>
        <div class="muted">When you select a symptom/condition, its NHS page is shown here.</div>

        <div id="nhsPreview" class="nhsCard" style="margin-top:12px">
          <div class="nhsTitle">No selection yet</div>
          <div class="nhsDesc muted">Add a symptom to see the NHS link and summary.</div>
          <div class="nhsLink muted">—</div>
          <div class="nhsBadge">READY</div>
        </div>
      </div>
    </div>
  </div>

<script>
  // ALL_ITEMS comes from server as JSON list of clinical symptoms
  const ALL_ITEMS = {{ items_json | safe }};
  const searchEl = document.getElementById('symSearch');
  const resultsBox = document.getElementById('resultsBox');
  const hintBox = document.getElementById('hintBox');
  const chipsBox = document.getElementById('selectedChips');
  const hiddenBox = document.getElementById('hiddenSelections');
  const nhsPreview = document.getElementById('nhsPreview');

  // Store selected items in a Map (key: lowercase string, value: original text)
  const selected = new Map();

  function escapeHtml(s){
    return (s||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
  }

  // Fetch NHS info from /api/nhs and display inside preview card
  async function updateNhsPreview(symptom){
    if (!symptom){
      nhsPreview.innerHTML = `
        <div class="nhsTitle">No selection yet</div>
        <div class="nhsDesc muted">Add a symptom to see the NHS link and summary.</div>
        <div class="nhsLink muted">—</div>
        <div class="nhsBadge">READY</div>
      `;
      return;
    }

    nhsPreview.innerHTML = `
      <div class="nhsTitle">${escapeHtml(symptom)}</div>
      <div class="nhsDesc muted">Loading NHS info…</div>
      <div class="nhsLink muted">—</div>
      <div class="nhsBadge">LOADING</div>
    `;

    try{
      const r = await fetch('/api/nhs?q=' + encodeURIComponent(symptom));
      const data = await r.json();

      const title = data.title || data.query || symptom;
      const desc = data.desc || 'No description available (offline/not found).';
      const url  = data.url || '';
      const status = (data.status || 'ok').toUpperCase();

      nhsPreview.innerHTML = `
        <div class="nhsTitle">${escapeHtml(title)}</div>
        <div class="nhsDesc">${escapeHtml(desc)}</div>
        <div class="nhsLink">${url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(url)}</a>` : `<span class="muted">No link available.</span>`}</div>
        <div class="nhsBadge">${escapeHtml(status)}</div>
      `;
    }catch(e){
      nhsPreview.innerHTML = `
        <div class="nhsTitle">${escapeHtml(symptom)}</div>
        <div class="nhsDesc muted">Could not load NHS info (network error).</div>
        <div class="nhsLink muted">—</div>
        <div class="nhsBadge">ERROR</div>
      `;
    }
  }

  // Render selected items as removable chips
  function renderChips(){
    chipsBox.innerHTML = '';
    for (const [k, v] of selected.entries()){
      const chip = document.createElement('div');
      chip.className = 'chip';
      chip.innerHTML = '<span>'+escapeHtml(v)+'</span><div class="chipX">×</div>';
      chip.querySelector('.chipX').addEventListener('click', () => {
        selected.delete(k);
        renderChips();
        const last = Array.from(selected.values()).slice(-1)[0];
        updateNhsPreview(last || '');
      });
      chipsBox.appendChild(chip);
    }
  }

  // Show filtered results as user types, allow adding to selection
  function renderResults(q){
    const query = (q||'').toLowerCase().trim();
    if (query.length < 2){
      resultsBox.style.display = 'none';
      hintBox.style.display = 'block';
      hintBox.textContent = 'Start typing to see matches (max 20).';
      resultsBox.innerHTML = '';
      return;
    }

    const out = [];
    for (let i=0; i<ALL_ITEMS.length; i++){
      const it = ALL_ITEMS[i];
      const low = it.toLowerCase();
      if (low.includes(query)) out.push(it);
      if (out.length >= 20) break;
    }

    resultsBox.style.display = 'block';
    hintBox.style.display = 'none';
    resultsBox.innerHTML = '';

    if (out.length === 0){
      resultsBox.innerHTML = '<div class="muted" style="padding:8px">No matches. Try another keyword.</div>';
      return;
    }

    out.forEach(it => {
      const low = it.toLowerCase();
      const row = document.createElement('div');
      row.className = 'resItem';
      row.innerHTML = '<div>'+escapeHtml(it)+'</div><button type="button" class="addBtn">'+(selected.has(low) ? 'Added' : 'Add')+'</button>';
      row.querySelector('.addBtn').addEventListener('click', () => {
        if (!selected.has(low)){
          selected.set(low, it);
          renderChips();
          row.querySelector('.addBtn').textContent = 'Added';
          updateNhsPreview(it);
        }
      });
      resultsBox.appendChild(row);
    });
  }

  // Convert selected items into hidden inputs so Flask receives them
  function buildHiddenSelections(){
    hiddenBox.innerHTML = '';
    for (const [k, v] of selected.entries()){
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'selected_items';
      input.value = v;
      hiddenBox.appendChild(input);
    }
    return true;
  }

  searchEl.addEventListener('input', () => renderResults(searchEl.value));
</script>
""" + BASE_BOTTOM


PAIN_SEVERITY_HTML = BASE_TOP + """
  <div class="hero" style="padding-top:70px">
    <h1 class="title" style="font-size:52px">Pain Severity</h1>
    <div class="subtitle" style="font-size:26px">Select severity to continue</div>

    <div class="centerForm" style="margin-top:40px">
      <div class="muted"><b>Your input:</b> {{user_input}}</div>

      <form method="post" action="/pain_severity_submit" style="margin-top:14px">
        <div class="label">Severity</div>
        <select class="selectLine" name="pain_severity" required>
          <option value="">-- Select --</option>
          <option value="normal">Normal / Mild</option>
          <option value="moderate">Moderate</option>
          <option value="severe">Severe</option>
        </select>

        <button class="btnRed" type="submit" style="margin-top:18px">Continue</button>

        <div class="row" style="margin-top:12px">
          <a href="/service_page"><button class="btn btnGhost" type="button">Cancel</button></a>
        </div>
      </form>
    </div>
  </div>
""" + BASE_BOTTOM


FOLLOWUP_HTML = BASE_TOP + """
  <div class="hero" style="padding-top:70px">
    <h1 class="title" style="font-size:52px">Safety Questions</h1>
    <div class="subtitle" style="font-size:26px">Confirm severity</div>

    <div class="centerForm" style="margin-top:40px">
      <div class="muted"><b>Trigger:</b> {{trigger}}</div>
      <div class="muted" style="margin-top:8px"><b>Your input:</b> {{user_input}}</div>

      <form method="post" action="/followup_submit" style="margin-top:14px">
        <input type="hidden" name="trigger" value="{{trigger}}"/>
        {% for q, key in questions %}
          <div class="label" style="margin-top:14px">{{q}}</div>
          <select class="selectLine" name="{{key}}" required>
            <option value="">-- Select --</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        {% endfor %}

        <button class="btnRed" type="submit" style="margin-top:18px">Submit</button>

        <div class="row" style="margin-top:12px">
          <a href="/service_page"><button class="btn btnGhost" type="button">Cancel</button></a>
        </div>
      </form>
    </div>
  </div>
""" + BASE_BOTTOM


RESULT_HTML = BASE_TOP + """
  <div class="hero" style="padding-top:70px">
    <h1 class="title" style="font-size:52px">Decision</h1>
    <div class="subtitle" style="font-size:26px">Your guided triage result</div>

    <div class="panel" style="margin-top:40px">
      <div class="card">
        <h2>Outcome</h2>
        <div class="pills">
          <div class="pill"><b>Decision:</b> {{decision}}</div>
          <div class="pill"><b>Service:</b> {{service_type}}</div>
          <div class="pill"><b>GP:</b> {{gp_office}}</div>
          <div class="pill"><b>Age:</b> {{age_display}}</div>
        </div>

        <div class="card" style="margin-top:14px;background:#fafafa">
          <div class="muted"><b>Input:</b><br>{{user_input}}</div>
        </div>

        <div class="card" style="margin-top:14px;background:#fafafa">
          <div class="muted"><b>Response:</b><br>{{response}}</div>
        </div>

        <details style="margin-top:12px">
          <summary class="muted">Debug</summary>
          <pre>{{debug}}</pre>
        </details>

        <div class="row" style="margin-top:14px">
          <a href="/service_page"><button class="btn btnPrimary" type="button">New Request</button></a>
        </div>
      </div>

      <div class="card">
        <h2>Matches</h2>
        <div class="muted">NHS information for selected symptom(s). Cached results work later.</div>
        <div>
          {{ nhs_html | safe }}
        </div>

        <details style="margin-top:16px">
          <summary class="muted">Dataset retrieval matches (debug)</summary>
          {% if matches %}
            <pre style="margin-top:10px">{{matches}}</pre>
          {% else %}
            <div class="muted" style="margin-top:10px">No dataset match list available for this step.</div>
          {% endif %}
        </details>
      </div>
    </div>

    <div class="dangerNote">
      Important: If you believe it is an emergency, call <b>999</b>.
    </div>
  </div>
""" + BASE_BOTTOM


# =========================
# ROUTES
# =========================
@app.route("/logo")
def logo():
    """
    Serve the Ladybird logo image to the frontend at /logo.
    """
    if not os.path.isfile(LOGO_FILE):
        return ("Logo file not found: " + LOGO_FILE, 404)
    return send_file(LOGO_FILE)


@app.route("/api/nhs", methods=["GET"])
def api_nhs():
    """
    NHS API endpoint for frontend preview panel.
    Frontend calls: /api/nhs?q=<symptom text>
    Returns JSON containing URL + title + description.
    """
    q = (request.args.get("q") or "").strip()
    return jsonify(nhs_lookup(q))


@app.route("/", methods=["GET", "POST"])
def login():
    """
    Login/Verification page:
    - On POST, verify user name and DOB against PostgreSQL
    - If verified: store details in session and redirect to /service_page
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        dob = request.form.get("dob", "").strip()

        patient = verify_patient(patients_df, name, dob)
        if not patient:
            return render_template_string(LOGIN_HTML, error="Not verified. Name/DOB not found in PostgreSQL")

        # Reset session and store verified identity
        session.clear()
        session["verified"] = True
        session["name"] = name
        session["dob"] = dob
        session["service_type"] = ""
        session["last_input"] = ""

        # Pain follow flow variables
        session["pain_severity_done"] = False
        session["pain_original_input"] = ""
        session["pain_severity"] = ""

        # store patient row as read-only details in session
        details = {}
        for k, v in patient.items():
            if str(k).startswith("_"):
                continue
            details[str(k)] = "" if v is None else str(v)
        session["details"] = details

        # attempt to get GP field from PostgreSQL (column naming may differ)
        gp_office = details.get("registered GP") or details.get("gp_office") or "Unknown GP"
        session["gp_office"] = gp_office

        # Age computation stored for rules / thresholds
        dob_date = parse_dob_to_date(dob)
        age_years, age_days = calc_age(dob_date)
        session["age_years"] = "" if age_years is None else int(age_years)
        session["age_days"] = "" if age_days is None else int(age_days)

        # audit verification event
        audit_log("verify", {"decision": "VERIFIED", "source": "verification", "details": f"name={name}, dob={dob}"})
        return redirect(url_for("service_page"))

    return render_template_string(LOGIN_HTML, error=None)


@app.route("/service_page", methods=["GET"])
def service_page():
    """
    After login verification, show service selection page:
    - Clinical
    - Non-clinical
    Also shows patient details (read-only).
    """
    if not session.get("verified"):
        return redirect(url_for("login"))

    # reset pain path on returning to service page
    session["pain_severity_done"] = False
    session["pain_original_input"] = ""
    session["pain_severity"] = ""

    # format age display for UI
    ay = session.get("age_years", "")
    ad = session.get("age_days", "")
    age_display = "Unknown"
    if isinstance(ay, int):
        age_display = f"{ay} years"
    elif isinstance(ad, int):
        age_display = f"{ad} days"

    return render_template_string(
        SERVICE_HTML,
        details=session.get("details", {}),
        gp_office=session.get("gp_office", "Unknown GP"),
        name=session.get("name", ""),
        dob=session.get("dob", ""),
        age_display=age_display,
    )


@app.route("/service", methods=["POST"])
def service():
    """
    Handle selection of service type:
    - stores service_type in session
    - renders:
        - Non-clinical dropdown form, OR
        - Clinical symptom search form
    """
    if not session.get("verified"):
        return redirect(url_for("login"))

    stype = (request.form.get("service_type") or "").strip()
    if stype not in {"clinical", "non_clinical"}:
        return redirect(url_for("service_page"))

    session["service_type"] = stype

    # reset pain path for a new request
    session["pain_severity_done"] = False
    session["pain_original_input"] = ""
    session["pain_severity"] = ""

    if stype == "non_clinical":
        return render_template_string(NONCLINICAL_FORM_HTML, items=NONCLINICAL_LIST)

    # send clinical items to JS as JSON list
    items_json = pd.Series(CLINICAL_LIST).to_json(orient="values")
    return render_template_string(CLINICAL_FORM_HTML, items_json=items_json)


@app.route("/pain_severity_submit", methods=["POST"])
def pain_severity_submit():
    """
    Handle user response from pain severity page.

    Decision logic uses apply_pain_severity_decision():
    - if FOLLOWUP => show follow-up questions
    - else => show final result
    """
    if not session.get("verified"):
        return redirect(url_for("login"))

    severity = (request.form.get("pain_severity") or "").strip().lower()
    original = session.get("pain_original_input", "") or session.get("last_input", "")

    session["pain_severity_done"] = True
    session["pain_severity"] = severity

    label, dbg = apply_pain_severity_decision(original, severity)

    # if severe chest pain style → follow-up
    if label == "FOLLOWUP":
        trigger = detect_followup_trigger(original) or "chest pain"
        session["followup_trigger"] = trigger
        session["followup_input"] = original
        return render_template_string(
            FOLLOWUP_HTML,
            trigger=trigger,
            questions=FOLLOW_UP_QUESTIONS[trigger],
            user_input=original,
        )

    gp_office = session.get("gp_office", "Unknown GP")

    # GP clinical uses special response message
    response = (
        f"Your appointment is booked with your Registered GP: {gp_office}."
        if label == "gp_clinical"
        else RESPONSES.get(label, RESPONSES["UNKNOWN"])
    )

    nhs_html = render_nhs_cards(session.get("selected_items", []))
    audit_log("triage", {"decision": label, "source": "pain_severity", "details": str(dbg)})

    age_display = "Unknown"
    ay = session.get("age_years", "")
    if isinstance(ay, int):
        age_display = f"{ay} years"

    return render_template_string(
        RESULT_HTML,
        decision=label,
        service_type="clinical",
        gp_office=gp_office,
        age_display=age_display,
        user_input=original,
        response=response,
        debug=str(dbg),
        matches="",
        nhs_html=nhs_html,
    )


@app.route("/followup_submit", methods=["POST"])
def followup_submit():
    """
    Handle follow-up safety questionnaire submission.

    Uses evaluate_followups():
    - if "danger" (>= 2 YES answers) => 999
    - else => 111
    """
    if not session.get("verified"):
        return redirect(url_for("login"))

    trigger = (request.form.get("trigger") or "").strip()
    user_input = session.get("followup_input", "") or session.get("last_input", "")

    answers = {}
    for _, key in FOLLOW_UP_QUESTIONS.get(trigger, []):
        answers[key] = request.form.get(key, "")

    danger, yes_count = evaluate_followups(answers, threshold_yes=2)
    decision = "999" if danger else "111"
    dbg = {"source": "followups", "trigger": trigger, "answers": answers, "yes_count": yes_count}

    response = RESPONSES.get(decision, RESPONSES["UNKNOWN"])
    nhs_html = render_nhs_cards(session.get("selected_items", []))
    audit_log("triage", {"decision": decision, "source": "followups", "details": str(dbg)})

    age_display = "Unknown"
    ay = session.get("age_years", "")
    if isinstance(ay, int):
        age_display = f"{ay} years"

    return render_template_string(
        RESULT_HTML,
        decision=decision,
        service_type="clinical",
        gp_office=session.get("gp_office", "Unknown GP"),
        age_display=age_display,
        user_input=user_input,
        response=response,
        debug=str(dbg),
        matches="",
        nhs_html=nhs_html,
    )


@app.route("/triage", methods=["POST"])
def triage():
    """
    Main triage endpoint (handles both service types).

    NON-CLINICAL:
      - returns gp_non_clinical message

    CLINICAL PIPELINE (in order):
      1) Age rule override (e.g infant fever)
      2) Pain severity gate (if pain keywords found)
      3) Rule override (red flags etc.)
      4) Follow-up safety questions trigger
      5) Retrieval (TF-IDF match against dataset)
    """
    if not session.get("verified"):
        return redirect(url_for("login"))

    service_type = request.form.get("service_type", session.get("service_type", ""))
    gp_office = session.get("gp_office", "Unknown GP")

    # interpret age stored in session
    age_years = session.get("age_years", None)
    age_days = session.get("age_days", None)
    age_years = age_years if isinstance(age_years, int) else None
    age_days = age_days if isinstance(age_days, int) else None

    age_display = "Unknown"
    if age_years is not None:
        age_display = f"{age_years} years"
    elif age_days is not None:
        age_display = f"{age_days} days"

    # -------------------------
    # Non-clinical triage
    # -------------------------
    if service_type == "non_clinical":
        selected_item = (request.form.get("selected_item", "") or "").strip()
        user_input = selected_item if selected_item else "(no selection)"
        session["last_input"] = user_input

        decision = "gp_non_clinical"
        response = RESPONSES["gp_non_clinical"]
        debug = {"source": "ui_non_clinical", "selected_item": selected_item}
        audit_log("triage", {"decision": decision, "source": "ui_non_clinical", "details": str(debug)})

        nhs_html = "<div class='muted'>NHS info is shown for clinical symptoms only.</div>"
        return render_template_string(
            RESULT_HTML,
            decision=decision,
            service_type=service_type,
            gp_office=gp_office,
            age_display=age_display,
            user_input=user_input,
            response=response,
            debug=str(debug),
            matches="",
            nhs_html=nhs_html,
        )

    # -------------------------
    # Clinical triage
    # -------------------------
    selected_items = request.form.getlist("selected_items")
    selected_items = [s.strip() for s in selected_items if str(s).strip()]
    custom_text = (request.form.get("custom_text", "") or "").strip()

    session["selected_items"] = selected_items

    # Build a combined user_input string used by all downstream logic
    parts = []
    if selected_items:
        parts.append("Selected symptoms: " + ", ".join(selected_items))
    if custom_text:
        parts.append("User notes: " + custom_text)
    user_input = " | ".join(parts) if parts else "(no symptom provided)"
    session["last_input"] = user_input

    # NHS card area uses selected items only
    nhs_html = render_nhs_cards(selected_items)

    # 1) Age rule override
    age_label, age_debug = age_rule_override(user_input, age_days)
    if age_label:
        decision = age_label
        response = RESPONSES.get(decision, RESPONSES["UNKNOWN"])
        audit_log("triage", {"decision": decision, "source": "age_rules", "details": str(age_debug)})

        return render_template_string(
            RESULT_HTML,
            decision=decision,
            service_type="clinical",
            gp_office=gp_office,
            age_display=age_display,
            user_input=user_input,
            response=response,
            debug=str(age_debug),
            matches="",
            nhs_html=nhs_html,
        )

    # 2) Pain severity step (only once)
    if contains_pain(user_input) and not session.get("pain_severity_done", False):
        session["pain_original_input"] = user_input
        return render_template_string(PAIN_SEVERITY_HTML, user_input=user_input)

    # 3) Rule overrides (red flags, mild illness shortcuts)
    rule_label, rule_debug = rule_override(user_input)
    if rule_label:
        decision = rule_label
        response = (
            f"Your appointment is booked with your Registered GP: {gp_office}."
            if decision == "gp_clinical"
            else RESPONSES.get(decision, RESPONSES["UNKNOWN"])
        )
        audit_log("triage", {"decision": decision, "source": "rules", "details": str(rule_debug)})

        return render_template_string(
            RESULT_HTML,
            decision=decision,
            service_type="clinical",
            gp_office=gp_office,
            age_display=age_display,
            user_input=user_input,
            response=response,
            debug=str(rule_debug),
            matches="",
            nhs_html=nhs_html,
        )

    # 4) Follow-up safety questions
    trigger = detect_followup_trigger(user_input)
    if trigger:
        session["followup_trigger"] = trigger
        session["followup_input"] = user_input
        return render_template_string(
            FOLLOWUP_HTML,
            trigger=trigger,
            questions=FOLLOW_UP_QUESTIONS[trigger],
            user_input=user_input,
        )

    # 5) Retrieval-based decision
    t111, t999, thresh_debug = adjusted_thresholds(age_years, age_days)
    matches = engine.search(user_input, top_k=6)
    decision, debug = engine.decide(matches, t111=t111, t999=t999)

    # build readable retrieval debug list
    lines = []
    for i, m in enumerate(matches, 1):
        lines.append(
            f"{i}) sim={m.similarity:.3f} | intensity={m.intensity:.1f} | "
            f"{normalize_clinical_flag(m.clinical_flag)} | {m.category} | {m.text}"
        )
    matches_str = "\n".join(lines)

    # map decision to response message
    if decision == "gp_clinical":
        response = f"Your appointment is booked with your Registered GP: {gp_office}."
    elif decision in RESPONSES:
        response = RESPONSES[decision]
    else:
        response = RESPONSES["UNKNOWN"]

    merged_debug = {"age_thresholds": thresh_debug, "retrieval": debug}
    audit_log("triage", {"decision": decision, "source": "retrieval_age_adjusted", "details": str(merged_debug)})

    return render_template_string(
        RESULT_HTML,
        decision=decision,
        service_type="clinical",
        gp_office=gp_office,
        age_display=age_display,
        user_input=user_input,
        response=response,
        debug=str(merged_debug),
        matches=matches_str,
        nhs_html=nhs_html,
    )


@app.route("/logout", methods=["POST"])
def logout():
    """
    Logout route:
    - clears session
    - redirects to login page
    """
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
