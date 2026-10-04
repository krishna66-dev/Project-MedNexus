"""
MedNexus Triage Engine
-----------------------
A transparent, rule-based Early Warning Score (EWS) adapted from widely used
clinical scoring frameworks (in the spirit of NEWS2 / MEWS) for use by
community health workers (ASHA/ANM) and individuals for PERSONAL MONITORING.

IMPORTANT: This is a decision-support aid only. It does NOT diagnose disease
and does NOT replace clinical judgement, a doctor, or emergency services.
Every result carries a clear disclaimer and a recommendation to escalate to
a PHC/CHC/hospital or call 108 (national ambulance) when severity is high.

Scoring approach
-----------------
Each vital parameter is scored 0-3 based on how far it deviates from a normal
adult range. Points are summed into a total score, which maps to one of four
triage bands:

    GREEN  (0-2)   -> Stable / routine monitoring
    YELLOW (3-5)   -> Monitor closely / consider PHC visit
    ORANGE (6-8)   -> Needs prompt medical attention (CHC/hospital)
    RED    (9+)    -> Emergency - seek immediate care / call 108

Any single "red-flag" symptom or a critically abnormal vital escalates the
band directly regardless of the numeric total (a safety net so no dangerous
single value gets diluted by otherwise-normal readings).
"""

from typing import Optional, List, Dict, Any

# Symptom codes considered "red flag" -> force at least ORANGE (or RED for the worst)
RED_FLAG_SYMPTOMS = {
    "chest_pain": "red",
    "severe_breathlessness": "red",
    "unconscious": "red",
    "seizure": "red",
    "severe_bleeding": "red",
    "blue_lips_face": "red",
    "stroke_signs": "red",          # facial droop / slurred speech / limb weakness
    "severe_dehydration": "orange",
    "high_fever_with_rash": "orange",
    "persistent_vomiting": "orange",
    "severe_abdominal_pain": "orange",
}

SYMPTOM_LABELS = {
    "fever": {"en": "Fever", "hi": "\u092c\u0941\u0916\u093e\u0930"},
    "cough": {"en": "Cough", "hi": "\u0916\u093e\u0902\u0938\u0940"},
    "breathlessness": {"en": "Breathlessness", "hi": "\u0938\u093e\u0902\u0938 \u092b\u0942\u0932\u0928\u093e"},
    "severe_breathlessness": {"en": "Severe breathlessness", "hi": "\u0917\u0902\u092d\u0940\u0930 \u0938\u093e\u0902\u0938 \u0932\u0947\u0928\u0947 \u092e\u0947\u0902 \u0915\u0920\u093f\u0928\u093e\u0908"},
    "chest_pain": {"en": "Chest pain", "hi": "\u0938\u0940\u0928\u0947 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926"},
    "headache": {"en": "Headache", "hi": "\u0938\u093f\u0930\u0926\u0930\u094d\u0926"},
    "body_ache": {"en": "Body ache", "hi": "\u0936\u0930\u0940\u0930 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926"},
    "diarrhea": {"en": "Diarrhea", "hi": "\u0926\u0938\u094d\u0924"},
    "vomiting": {"en": "Vomiting", "hi": "\u0909\u0932\u094d\u091f\u0940"},
    "persistent_vomiting": {"en": "Persistent vomiting", "hi": "\u0932\u0917\u093e\u0924\u093e\u0930 \u0909\u0932\u094d\u091f\u0940"},
    "dizziness": {"en": "Dizziness", "hi": "\u091a\u0915\u094d\u0915\u0930 \u0906\u0928\u093e"},
    "fatigue": {"en": "Fatigue / weakness", "hi": "\u0925\u0915\u093e\u0928/\u0915\u092e\u095b\u094b\u0930\u0940"},
    "severe_abdominal_pain": {"en": "Severe abdominal pain", "hi": "\u092a\u0947\u091f \u092e\u0947\u0902 \u0917\u0902\u092d\u0940\u0930 \u0926\u0930\u094d\u0926"},
    "severe_dehydration": {"en": "Signs of severe dehydration", "hi": "\u0917\u0902\u092d\u0940\u0930 \u091c\u0932\u0940\u092f \u0915\u092e\u0940 \u0915\u0947 \u0932\u0915\u094d\u0937\u0923"},
    "unconscious": {"en": "Unconsciousness / unresponsive", "hi": "\u092c\u0947\u0939\u094b\u0936\u0940 / \u0905\u092a\u094d\u0930\u0924\u093f\u0915\u094d\u0930\u093f\u092f\u0936\u0940\u0932\u0924\u093e"},
    "seizure": {"en": "Seizure / convulsions", "hi": "\u0926\u094c\u0930\u093e / \u092e\u093f\u0930\u0917\u0940"},
    "severe_bleeding": {"en": "Severe bleeding", "hi": "\u0917\u0902\u092d\u0940\u0930 \u0930\u0915\u094d\u0924\u0938\u094d\u0930\u093e\u0935"},
    "blue_lips_face": {"en": "Bluish lips or face", "hi": "\u0939\u094b\u0902\u0920 \u092f\u093e \u091a\u0947\u0939\u0930\u0947 \u0915\u093e \u0928\u0940\u0932\u093e \u092a\u0921\u093c\u0928\u093e"},
    "stroke_signs": {"en": "Facial droop / slurred speech / limb weakness", "hi": "\u091a\u0947\u0939\u0930\u0947 \u0915\u093e \u091d\u0941\u0915\u0928\u093e / \u0932\u0921\u093c\u0916\u0921\u093c\u093e\u0924\u0940 \u092c\u094b\u0932\u0940 / \u0905\u0902\u0917 \u0915\u092e\u095b\u094b\u0930\u0940"},
    "high_fever_with_rash": {"en": "High fever with skin rash", "hi": "\u0924\u0947\u091c \u092c\u0941\u0916\u093e\u0930 \u0915\u0947 \u0938\u093e\u0925 \u0924\u094d\u0935\u091a\u093e \u092a\u0930 \u091a\u0915\u0924\u094d\u0924\u0947"},
    "loss_of_appetite": {"en": "Loss of appetite", "hi": "\u092d\u0942\u0916 \u0928 \u0932\u0917\u0928\u093e"},
    "swelling": {"en": "Swelling (limbs/face)", "hi": "\u0938\u0942\u091c\u0928"},
    "urination_issues": {"en": "Urination problems", "hi": "\u092a\u0947\u0936\u093e\u092c \u0938\u0902\u092c\u0902\u0927\u0940 \u0938\u092e\u0938\u094d\u092f\u093e"},
}


def _score_systolic_bp(v: Optional[int]) -> (int, Optional[str]):
    if v is None:
        return 0, None
    if v < 70:
        return 3, "Systolic BP critically low"
    if v < 90:
        return 3, "Systolic BP very low (possible shock)"
    if v < 100:
        return 1, "Systolic BP low"
    if v <= 139:
        return 0, None
    if v <= 159:
        return 1, "Systolic BP mildly elevated"
    if v <= 179:
        return 2, "Systolic BP high"
    return 3, "Systolic BP critically high (hypertensive crisis range)"


def _score_diastolic_bp(v: Optional[int]) -> (int, Optional[str]):
    if v is None:
        return 0, None
    if v < 60:
        return 1, "Diastolic BP low"
    if v <= 89:
        return 0, None
    if v <= 99:
        return 1, "Diastolic BP mildly elevated"
    if v <= 109:
        return 2, "Diastolic BP high"
    return 3, "Diastolic BP critically high"


def _score_heart_rate(v: Optional[int]) -> (int, Optional[str]):
    if v is None:
        return 0, None
    if v < 40:
        return 3, "Heart rate critically low"
    if v < 50:
        return 1, "Heart rate low"
    if v <= 100:
        return 0, None
    if v <= 110:
        return 1, "Heart rate mildly elevated"
    if v <= 130:
        return 2, "Heart rate high"
    return 3, "Heart rate critically high"


def _score_respiratory_rate(v: Optional[int]) -> (int, Optional[str]):
    if v is None:
        return 0, None
    if v < 9:
        return 3, "Respiratory rate critically low"
    if v <= 11:
        return 1, "Respiratory rate low"
    if v <= 20:
        return 0, None
    if v <= 24:
        return 2, "Respiratory rate high"
    return 3, "Respiratory rate critically high"


def _score_temperature(v: Optional[float]) -> (int, Optional[str]):
    if v is None:
        return 0, None
    if v < 35.0:
        return 3, "Hypothermia (very low body temperature)"
    if v <= 37.5:
        return 0, None
    if v <= 38.5:
        return 1, "Mild fever"
    if v <= 39.5:
        return 2, "High fever"
    return 3, "Very high fever"


def _score_spo2(v: Optional[int]) -> (int, Optional[str]):
    if v is None:
        return 0, None
    if v >= 95:
        return 0, None
    if v >= 92:
        return 2, "SpO2 mildly low"
    return 3, "SpO2 critically low (hypoxia)"


def _score_blood_sugar(v: Optional[float], test_type: Optional[str]) -> (int, Optional[str]):
    if v is None:
        return 0, None
    test_type = (test_type or "random").lower()
    if test_type == "fasting":
        if v < 54:
            return 3, "Severe hypoglycemia (fasting)"
        if v < 70:
            return 2, "Low fasting blood sugar"
        if v <= 100:
            return 0, None
        if v <= 125:
            return 1, "Fasting sugar in pre-diabetic range"
        if v <= 180:
            return 2, "Fasting sugar high"
        return 3, "Fasting sugar critically high"
    else:  # random / postprandial
        if v < 54:
            return 3, "Severe hypoglycemia"
        if v < 70:
            return 2, "Low blood sugar"
        if v <= 140:
            return 0, None
        if v <= 199:
            return 1, "Blood sugar mildly elevated"
        if v <= 300:
            return 2, "Blood sugar high"
        return 3, "Blood sugar critically high"


def _score_consciousness(v: Optional[str]) -> (int, Optional[str]):
    if not v:
        return 0, None
    v = v.upper()
    mapping = {"A": (0, None), "V": (2, "Responds only to voice"),
               "P": (3, "Responds only to pain"), "U": (3, "Unresponsive")}
    return mapping.get(v, (0, None))


def _band_from_score(score: int) -> str:
    if score >= 9:
        return "red"
    if score >= 6:
        return "orange"
    if score >= 3:
        return "yellow"
    return "green"


_BAND_RANK = {"green": 0, "yellow": 1, "orange": 2, "red": 3}

_BAND_LABEL = {
    "green": {"en": "Stable", "hi": "\u0938\u094d\u0925\u093f\u0930"},
    "yellow": {"en": "Monitor Closely", "hi": "\u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0938\u0947 \u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0930\u0916\u0947\u0902"},
    "orange": {"en": "Needs Prompt Medical Attention", "hi": "\u0924\u0941\u0930\u0902\u0924 \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u0915\u0940\u092f \u0927\u094d\u092f\u093e\u0928 \u0906\u0935\u0936\u094d\u092f\u0915"},
    "red": {"en": "Emergency - Seek Immediate Care", "hi": "\u0906\u092a\u093e\u0924\u0915\u093e\u0932 - \u0924\u0941\u0930\u0902\u0924 \u0938\u0939\u093e\u092f\u0924\u093e \u0932\u0947\u0902"},
}

_BAND_RECOMMENDATION = {
    "green": {
        "en": "Vitals appear within a normal range. Continue routine self-monitoring and healthy habits. Recheck if symptoms change.",
        "hi": "\u092e\u0939\u0924\u094d\u0935\u092a\u0942\u0930\u094d\u0923 \u0938\u0902\u0915\u0947\u0924 \u0938\u093e\u092e\u093e\u0928\u094d\u092f \u0938\u0940\u092e\u093e \u092e\u0947\u0902 \u0939\u0948\u0902\u0964 \u0928\u093f\u092f\u092e\u093f\u0924 \u0938\u094d\u0935-\u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u091c\u093e\u0930\u0940 \u0930\u0916\u0947\u0902\u0964 \u0932\u0915\u094d\u0937\u0923 \u092c\u0926\u0932\u0928\u0947 \u092a\u0930 \u092a\u0941\u0928: \u091c\u093e\u0902\u091a \u0915\u0930\u0947\u0902\u0964",
    },
    "yellow": {
        "en": "Some readings are outside normal range. Monitor closely over the next few hours and consider visiting the nearest PHC/Sub-Centre if symptoms persist or worsen.",
        "hi": "\u0915\u0941\u091b \u0930\u0940\u0921\u093f\u0902\u0917 \u0938\u093e\u092e\u093e\u0928\u094d\u092f \u0938\u0940\u092e\u093e \u0938\u0947 \u092c\u093e\u0939\u0930 \u0939\u0948\u0902\u0964 \u0905\u0917\u0932\u0947 \u0915\u0941\u091b \u0918\u0902\u091f\u094b\u0902 \u0924\u0915 \u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0938\u0947 \u0928\u093f\u0917\u0930\u093e\u0928\u0940 \u0930\u0916\u0947\u0902 \u0914\u0930 \u092f\u0926\u093f \u0932\u0915\u094d\u0937\u0923 \u092c\u0928\u0947 \u0930\u0939\u0947\u0902 \u092f\u093e \u092c\u0922\u093c\u0947\u0902 \u0924\u094b \u0928\u091c\u0926\u0940\u0915\u0940 PHC/\u0909\u092a-\u0915\u0947\u0902\u0926\u094d\u0930 \u091c\u093e\u090f\u0902\u0964",
    },
    "orange": {
        "en": "Readings indicate a concerning condition. Please visit the nearest CHC/hospital for medical evaluation as soon as possible.",
        "hi": "\u0930\u0940\u0921\u093f\u0902\u0917 \u091a\u093f\u0902\u0924\u093e\u091c\u0928\u0915 \u0938\u094d\u0925\u093f\u0924\u093f \u0915\u093e \u0938\u0902\u0915\u0947\u0924 \u0926\u0947\u0924\u0940 \u0939\u0948\u0902\u0964 \u0915\u0943\u092a\u092f\u093e \u091c\u0932\u094d\u0926 \u0938\u0947 \u091c\u0932\u094d\u0926 \u0928\u091c\u0926\u0940\u0915\u0940 CHC/\u0905\u0938\u094d\u092a\u0924\u093e\u0932 \u091c\u093e\u0915\u0930 \u091c\u093e\u0902\u091a \u0915\u0930\u093e\u090f\u0902\u0964",
    },
    "red": {
        "en": "This may be a medical emergency. Seek immediate care - go to the nearest hospital or call 108 (national ambulance) right away.",
        "hi": "\u092f\u0939 \u090f\u0915 \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u093e \u0906\u092a\u093e\u0924\u0915\u093e\u0932 \u0939\u094b \u0938\u0915\u0924\u093e \u0939\u0948\u0964 \u0924\u0941\u0930\u0902\u0924 \u0938\u0939\u093e\u092f\u0924\u093e \u0932\u0947\u0902 - \u0924\u0941\u0930\u0902\u0924 \u0928\u091c\u0926\u0940\u0915\u0940 \u0905\u0938\u094d\u092a\u0924\u093e\u0932 \u091c\u093e\u090f\u0902 \u092f\u093e 108 (\u0930\u093e\u0937\u094d\u091f\u094d\u0930\u0940\u092f \u090f\u0902\u092c\u0941\u0932\u0947\u0902\u0938) \u092a\u0930 \u0915\u0949\u0932 \u0915\u0930\u0947\u0902\u0964",
    },
}


def build_action_plan(severity_level: str, lang: str = "en") -> Dict[str, Any]:
    """Return an ASHA-facing action plan based on triage severity.

    This is intentionally guidance, not a diagnosis or prescription. It tells a
    community worker what to do next, when to refer, and what follow-up to record.
    """
    lang = lang if lang in ("en", "hi") else "en"
    plans = {
        "green": {
            "en": {
                "title": "ASHA Care & Action Plan",
                "urgency": "Routine community follow-up",
                "immediate_actions": [
                    "Record the assessment and explain the result to the patient.",
                    "Continue routine health monitoring and preventive-health counselling within your training and local protocol.",
                    "Advise the patient to return for reassessment if symptoms appear, persist, or worsen.",
                ],
                "avoid": ["Do not prescribe or recommend medicines outside your approved role or local protocol."],
                "referral": "Referral is not indicated by this screening result unless symptoms worsen or another clinical concern is present.",
                "follow_up": "Schedule routine follow-up according to the local programme or the patient's care plan.",
            },
            "hi": {
                "title": "आशा देखभाल और कार्य योजना",
                "urgency": "नियमित सामुदायिक फॉलो-अप",
                "immediate_actions": [
                    "जांच का परिणाम दर्ज करें और मरीज को सरल भाषा में समझाएं।",
                    "अपने प्रशिक्षण और स्थानीय प्रोटोकॉल के अनुसार नियमित स्वास्थ्य निगरानी और स्वास्थ्य-परामर्श जारी रखें।",
                    "लक्षण दिखाई देने, बने रहने या बढ़ने पर दोबारा जांच की सलाह दें।",
                ],
                "avoid": ["अपनी स्वीकृत भूमिका या स्थानीय प्रोटोकॉल से बाहर दवा लिखने या सुझाने से बचें।"],
                "referral": "इस स्क्रीनिंग परिणाम के आधार पर तत्काल रेफरल आवश्यक नहीं दिखता, लेकिन लक्षण बढ़ने या अन्य चिकित्सकीय चिंता होने पर रेफर करें।",
                "follow_up": "स्थानीय कार्यक्रम या मरीज की देखभाल योजना के अनुसार नियमित फॉलो-अप तय करें।",
            },
        },
        "yellow": {
            "en": {
                "title": "ASHA Care & Action Plan",
                "urgency": "Monitor closely",
                "immediate_actions": [
                    "Recheck the abnormal vital(s) when appropriate and confirm the reading is reliable.",
                    "Ask about worsening symptoms and document any change.",
                    "Provide only counselling/support that is within your training and the approved local protocol.",
                ],
                "avoid": ["Do not delay referral if danger signs develop.", "Do not start unapproved medicines based only on this score."],
                "referral": "Consider PHC/Sub-Centre evaluation if symptoms persist, readings remain abnormal, or the patient's condition worsens.",
                "follow_up": "Create a follow-up task and record the next review date.",
            },
            "hi": {
                "title": "आशा देखभाल और कार्य योजना",
                "urgency": "नज़दीकी निगरानी रखें",
                "immediate_actions": [
                    "जहां उचित हो, असामान्य vital को दोबारा जांचें और रीडिंग की पुष्टि करें।",
                    "बढ़ते लक्षणों के बारे में पूछें और किसी भी बदलाव को दर्ज करें।",
                    "केवल अपने प्रशिक्षण और स्वीकृत स्थानीय प्रोटोकॉल के अनुसार परामर्श/सहायता दें।",
                ],
                "avoid": ["चेतावनी वाले लक्षण विकसित होने पर रेफरल में देरी न करें।", "केवल इस स्कोर के आधार पर बिना स्वीकृति वाली दवा शुरू न करें।"],
                "referral": "यदि लक्षण बने रहें, रीडिंग असामान्य बनी रहे या स्थिति बिगड़े, तो PHC/उप-केंद्र में जांच पर विचार करें।",
                "follow_up": "फॉलो-अप कार्य बनाएं और अगली समीक्षा की तारीख दर्ज करें।",
            },
        },
        "orange": {
            "en": {
                "title": "ASHA Care & Action Plan",
                "urgency": "Prompt medical evaluation",
                "immediate_actions": [
                    "Keep the patient accompanied and arrange prompt evaluation at the appropriate health facility.",
                    "Carry/share the recorded vitals, symptoms, contributing factors, and assessment summary with the receiving clinician.",
                    "Continue appropriate observation while arranging referral and escalate immediately if danger signs appear.",
                ],
                "avoid": ["Do not delay referral to try an unapproved home treatment or medicine.", "Do not present the screening result as a diagnosis."],
                "referral": "Prompt referral to the appropriate PHC/CHC/hospital is recommended based on the screening result.",
                "follow_up": "Record the referral and schedule follow-up to confirm that the patient reached appropriate care.",
            },
            "hi": {
                "title": "आशा देखभाल और कार्य योजना",
                "urgency": "शीघ्र चिकित्सकीय जांच",
                "immediate_actions": [
                    "मरीज को अकेला न छोड़ें और उचित स्वास्थ्य केंद्र पर शीघ्र जांच की व्यवस्था करें।",
                    "दर्ज किए गए vital, लक्षण, कारण और जांच सारांश को चिकित्सक/स्वास्थ्यकर्मी के साथ साझा करें।",
                    "रेफरल की व्यवस्था करते समय उचित निगरानी रखें और चेतावनी वाले लक्षण दिखने पर तुरंत स्तर बढ़ाएं।",
                ],
                "avoid": ["बिना स्वीकृति वाले घरेलू उपचार या दवा आजमाने के लिए रेफरल में देरी न करें।", "स्क्रीनिंग परिणाम को अंतिम निदान के रूप में प्रस्तुत न करें।"],
                "referral": "स्क्रीनिंग परिणाम के आधार पर उचित PHC/CHC/अस्पताल में शीघ्र रेफरल की सलाह दी जाती है।",
                "follow_up": "रेफरल दर्ज करें और यह सुनिश्चित करने के लिए फॉलो-अप तय करें कि मरीज उचित देखभाल तक पहुंचा।",
            },
        },
        "red": {
            "en": {
                "title": "ASHA Emergency Action Plan",
                "urgency": "Immediate emergency referral",
                "immediate_actions": [
                    "Treat this as an urgent warning from the screening tool and seek emergency medical care immediately.",
                    "Keep the patient accompanied; monitor responsiveness and breathing while help is being arranged.",
                    "Call 108 or use the locally appropriate emergency pathway when immediate ambulance support is needed.",
                    "Take the MedNexus assessment summary and recorded vital readings to the receiving health facility.",
                ],
                "avoid": ["Do not delay emergency referral for a home remedy or unapproved medicine.", "Do not leave an unwell patient alone.", "Do not treat this screening result as a confirmed diagnosis."],
                "referral": "Immediate emergency evaluation at the nearest appropriate health facility is required.",
                "follow_up": "After emergency care, record the referral outcome and schedule follow-up according to the treating clinician's plan.",
            },
            "hi": {
                "title": "आशा आपातकालीन कार्य योजना",
                "urgency": "तत्काल आपातकालीन रेफरल",
                "immediate_actions": [
                    "इस स्क्रीनिंग चेतावनी को गंभीरता से लें और तुरंत आपातकालीन चिकित्सकीय सहायता लें।",
                    "मरीज को अकेला न छोड़ें; सहायता की व्यवस्था होने तक चेतना और सांस की निगरानी करें।",
                    "तुरंत एम्बुलेंस सहायता की जरूरत हो तो 108 या स्थानीय आपातकालीन व्यवस्था का उपयोग करें।",
                    "MedNexus जांच सारांश और दर्ज vital readings को स्वास्थ्य केंद्र तक साथ ले जाएं।",
                ],
                "avoid": ["घरेलू उपचार या बिना स्वीकृति वाली दवा के लिए आपातकालीन रेफरल में देरी न करें।", "अस्वस्थ मरीज को अकेला न छोड़ें।", "इस स्क्रीनिंग परिणाम को अंतिम निदान न मानें।"],
                "referral": "निकटतम उपयुक्त स्वास्थ्य केंद्र में तत्काल आपातकालीन जांच आवश्यक है।",
                "follow_up": "आपातकालीन देखभाल के बाद रेफरल का परिणाम दर्ज करें और चिकित्सक की योजना के अनुसार फॉलो-अप तय करें।",
            },
        },
    }
    return plans.get(severity_level, plans["yellow"])[lang]


def compute_triage(payload: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    """
    payload keys (all optional except at least one vital/symptom expected):
        systolic_bp, diastolic_bp, heart_rate, respiratory_rate,
        temperature_c, spo2, blood_sugar, sugar_test_type,
        consciousness, symptoms (list[str])
    Returns dict with severity_score, severity_level, severity_label,
    recommendation, contributing_factors (list[str]).
    """
    lang = lang if lang in ("en", "hi") else "en"
    total = 0
    factors: List[str] = []

    checks = [
        (_score_systolic_bp, payload.get("systolic_bp")),
        (_score_diastolic_bp, payload.get("diastolic_bp")),
        (_score_heart_rate, payload.get("heart_rate")),
        (_score_respiratory_rate, payload.get("respiratory_rate")),
        (_score_temperature, payload.get("temperature_c")),
        (_score_spo2, payload.get("spo2")),
    ]
    for fn, val in checks:
        pts, reason = fn(val)
        total += pts
        if reason:
            factors.append(reason)

    sugar_pts, sugar_reason = _score_blood_sugar(payload.get("blood_sugar"), payload.get("sugar_test_type"))
    total += sugar_pts
    if sugar_reason:
        factors.append(sugar_reason)

    consc_pts, consc_reason = _score_consciousness(payload.get("consciousness"))
    total += consc_pts
    if consc_reason:
        factors.append(consc_reason)

    band = _band_from_score(total)

    # Red-flag symptom override (safety net)
    symptoms = payload.get("symptoms") or []
    for code in symptoms:
        forced = RED_FLAG_SYMPTOMS.get(code)
        if forced and _BAND_RANK[forced] > _BAND_RANK[band]:
            band = forced
        if code in SYMPTOM_LABELS:
            label = SYMPTOM_LABELS[code].get(lang, code)
            if forced:
                factors.append(f"{label} (red-flag symptom)" if lang == "en" else f"{label} (\u091a\u0947\u0924\u093e\u0935\u0928\u0940 \u0932\u0915\u094d\u0937\u0923)")

    return {
        "severity_score": total,
        "severity_level": band,
        "severity_label": _BAND_LABEL[band][lang],
        "recommendation": _BAND_RECOMMENDATION[band][lang],
        "contributing_factors": factors,
        "action_plan": build_action_plan(band, lang),
        "referral_required": band in ("orange", "red"),
        "follow_up_recommended": band in ("yellow", "orange", "red"),
    }
