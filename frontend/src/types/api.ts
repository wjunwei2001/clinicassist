// API Types matching the FastAPI backend responses

export interface MedHistoryFact {
  category: "allergy" | "medication" | "past_condition" | "surgery" | 
            "family_history" | "social" | "immunization" | "obgyn" | "other";
  question: string;
  answer: string;
  additional_details?: string;
}

export interface TriageSummary {
  probable_diagnosis: string;
  reason_for_diagnosis: string;
  urgency: "EMERGENCY" | "URGENT" | "SEMI-URGENT" | "NON-URGENT";
  reason_for_urgency: string;
}

export interface PatientState {
  patient_name?: string;
  patient_age?: number;
  patient_sex?: "M" | "F";
  main_symptoms?: string[];
  symptom_onset?: string;
  associated_symptoms?: string[];
  additional_symptom_info?: string[];
  medical_history?: MedHistoryFact[];
  generated_summary?: TriageSummary;
}

export interface StartResponse {
  session_id: string;
  assistant_message: string;
  state: PatientState;
  phase: string;
  is_complete: boolean;
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  assistant_message: string | null;
  state: PatientState;
  phase: string;
  is_complete: boolean;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

