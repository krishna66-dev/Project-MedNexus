import type { Lang } from "./i18n";
import type { SeverityLevel } from "./types";

const LOCALES: Record<Lang, string> = { en: "en-IN", hi: "hi-IN" };

/** 10 Apr 2025 */
export function formatDate(iso: string | null | undefined, lang: Lang): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(LOCALES[lang], { day: "2-digit", month: "short", year: "numeric" });
}

/** 10 Apr 2025, 10:30 am */
export function formatDateTime(iso: string | null | undefined, lang: Lang): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const date = d.toLocaleDateString(LOCALES[lang], { day: "2-digit", month: "short", year: "numeric" });
  const time = d.toLocaleTimeString(LOCALES[lang], { hour: "2-digit", minute: "2-digit" });
  return `${date}, ${time}`;
}

/** "male" -> "M", "female" -> "F", "other" -> "O" */
export function genderShort(g: string | null | undefined): string {
  if (!g) return "";
  const v = g.toLowerCase();
  if (v.startsWith("m")) return "M";
  if (v.startsWith("f")) return "F";
  return "O";
}

/** "32 / F" (or whichever parts exist) */
export function ageGender(age: number | null | undefined, gender: string | null | undefined): string {
  const parts = [age != null ? String(age) : "", genderShort(gender)].filter(Boolean);
  return parts.length ? parts.join(" / ") : "—";
}

/** Group the 4 backend severity levels into the 3 buckets the dashboard shows. */
export function riskBucket(level: SeverityLevel): "high" | "medium" | "low" {
  if (level === "red" || level === "orange") return "high";
  if (level === "yellow") return "medium";
  return "low";
}

export function initials(name: string | null | undefined): string {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p.charAt(0).toUpperCase()).join("") || "?";
}

/** yyyy-mm-dd (local) for comparing against <input type="date"> values */
export function toDateKey(iso: string): string {
  const d = new Date(iso);
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${m}-${day}`;
}

// ---------------------------------------------------------------------------
// Display score (0-100)
// The backend returns a raw early-warning score (about 0-24) and a severity band.
// A red-flag symptom can force a high band even when the raw score is low, so the raw
// number alone can look wrong (e.g. "Emergency, score 0"). This maps level + raw score to a
// 0-100 scale where each band owns a range, so the number always agrees with the severity.
// ---------------------------------------------------------------------------
const BAND_RANGE: Record<SeverityLevel, { min: number; max: number; step: number; natural: number }> = {
  green:  { min: 5,  max: 29,  step: 10, natural: 0 },
  yellow: { min: 30, max: 54,  step: 8,  natural: 3 },
  orange: { min: 55, max: 79,  step: 8,  natural: 6 },
  red:    { min: 80, max: 100, step: 2,  natural: 9 },
};

function naturalBand(raw: number): SeverityLevel {
  if (raw >= 9) return "red";
  if (raw >= 6) return "orange";
  if (raw >= 3) return "yellow";
  return "green";
}

export function isEscalated(level: SeverityLevel, raw: number): boolean {
  const rank: Record<SeverityLevel, number> = { green: 0, yellow: 1, orange: 2, red: 3 };
  return rank[level] > rank[naturalBand(raw)];
}

export function displayScore(level: SeverityLevel, raw: number): number {
  const b = BAND_RANGE[level];
  // Normal case: position within the band follows the raw score.
  // Escalated by a red flag: start at the band floor and add the vitals contribution.
  const offset = isEscalated(level, raw) ? raw : raw - b.natural;
  return Math.max(b.min, Math.min(b.max, b.min + Math.max(0, offset) * b.step));
}
