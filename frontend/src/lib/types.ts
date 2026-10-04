export interface Patient {
  id: string;
  user_id: string;
  name: string;
  dob: string | null;
  age: number | null;
  gender: string | null;
  village_ward: string | null;
  contact_number: string | null;
  created_at: string;
}

export type SeverityLevel = "green" | "yellow" | "orange" | "red";

export interface ActionPlan {
  title: string;
  urgency: string;
  immediate_actions: string[];
  avoid: string[];
  referral: string;
  follow_up: string;
}

export interface TriageResult {
  severity_score: number;
  severity_level: SeverityLevel;
  severity_label: string;
  recommendation: string;
  contributing_factors: string[];
  action_plan: { en: ActionPlan; hi: ActionPlan };
  referral_required: boolean;
  follow_up_recommended: boolean;
}

export interface VitalsRecord {
  id: string;
  patient_id: string;
  recorded_by: string;
  vitals: {
    systolic_bp: number | null;
    diastolic_bp: number | null;
    heart_rate: number | null;
    respiratory_rate: number | null;
    temperature_c: number | null;
    spo2: number | null;
    blood_sugar: number | null;
    sugar_test_type: string | null;
    body_weight_kg: number | null;
    height_cm: number | null;
    consciousness: string | null;
  };
  symptoms: string[];
  notes: string | null;
  triage: TriageResult;
  created_at: string;
}

export const SYMPTOM_CODES = [
  "fever",
  "cough",
  "breathlessness",
  "severe_breathlessness",
  "chest_pain",
  "headache",
  "body_ache",
  "diarrhea",
  "vomiting",
  "persistent_vomiting",
  "dizziness",
  "fatigue",
  "severe_abdominal_pain",
  "severe_dehydration",
  "unconscious",
  "seizure",
  "severe_bleeding",
  "blue_lips_face",
  "stroke_signs",
  "high_fever_with_rash",
  "loss_of_appetite",
  "swelling",
  "urination_issues",
] as const;

export type SymptomCode = (typeof SYMPTOM_CODES)[number];
