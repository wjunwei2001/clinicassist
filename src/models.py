from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
from langgraph.graph import MessagesState

# Models for building langgraph worflow
class PatientInfoPartial(BaseModel):
    name: Optional[str] = Field(description="The name of the patient")
    age: Optional[int] = Field(description="The age of the patient")
    sex: Optional[Literal["M", "F"]] = Field(description="The biological sex of the patient")

class SymptomsPartial(BaseModel):
    main_symptoms: Optional[list[str]] = Field(description="Primary symptom(s) patient is experiencing")
    symptom_onset: Optional[str] = Field(description="When symptoms started (e.g., '3 days ago', 'this morning')")
    associated_symptoms: Optional[list[str]] = Field(description="Related or secondary symptoms")
    additional_symptom_info: Optional[list[str]] = Field(description="Other relevant details: severity, triggers, alleviating factors etc.")

class SymptomSufficiencyCheck(BaseModel):
    is_sufficient: bool = Field(description="Whether the information provided is sufficient for first assessment by doctor")
    reason: Optional[str] = Field(description="Why more info is needed, or None if sufficient")

class MedHistoryFact(BaseModel):
    category: Literal["allergy","medication","past_condition","surgery",
                      "family_history","social","immunization","obgyn","other"]
    question: str = Field(description="Question for medical/health history. Eg. (Do you have diabetes?)")
    answer: str
    additional_details: Optional[str] = None

class MedHistorySufficiencyCheck(BaseModel):
    is_sufficient: bool
    reason: Optional[str] = None

class TriageSummary(BaseModel):
    probable_diagnosis: str = Field(description="The likely diagnosis for the patient based on the conversation and medical history.")
    reason_for_diagnosis: str = Field(description="The reason for the diagnosis, based on the conversation and medical history.")
    urgency: Literal["EMERGENCY", "URGENT", "SEMI-URGENT", "NON-URGENT"]
    reason_for_urgency: str = Field(description="The reason for the urgency of the diagnosis, based on the conversation and medical history.")
  

class AgentState(MessagesState):
    """State for the chatbot"""
    patient_name: str
    patient_age: int
    patient_sex: Literal["M", "F"]
    main_symptoms: list[str]
    symptom_onset: str
    associated_symptoms: list[str]
    additional_symptom_info: list[str]
    medical_history: List[MedHistoryFact]
    generated_summary: TriageSummary


# Models for FastAPI endpoints
class StartResponse(BaseModel):
    session_id: str
    assistant_message: Optional[str]
    state: Dict[str, Any]
    phase: str
    is_complete: bool

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    assistant_message: Optional[str]
    state: Dict[str, Any]
    phase: str
    is_complete: bool