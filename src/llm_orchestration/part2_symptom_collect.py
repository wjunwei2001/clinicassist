from models import AgentState, SymptomsPartial, SymptomSufficiencyCheck
from prompts import BASE_PROMPT, SYMPTOMS_ASKING_PROMPT, SYMPTOMS_EXTRACTION_PROMPT, SYMPTOMS_SUFFICIENCY_CHECK_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.types import interrupt
from utils import get_current_time

from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(model="gpt-4.1", temperature=0)
symptoms_llm = llm.with_structured_output(SymptomsPartial)
symptom_sufficiency_llm = llm.with_structured_output(SymptomSufficiencyCheck)

def ask_symptoms(state: AgentState) -> AgentState:
    print("Asking symptoms")
    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=SYMPTOMS_ASKING_PROMPT.format(current_time=get_current_time())),
        *state["messages"],
    ]
    resp = llm.invoke(msgs)
    return {"messages": [resp]}

def extract_symptoms(state: AgentState) -> AgentState:
    print("Extracting symptoms")
    # Get current state to pass as context
    extracted_symptoms = {
        "main_symptoms": state.get("main_symptoms") or [],
        "symptom_onset": state.get("symptom_onset"),
        "associated_symptoms": state.get("associated_symptoms") or [],
        "additional_symptom_info": state.get("additional_symptom_info") or []
    }
    
    # Get ALL messages for context
    all_messages = state.get("messages", [])
    
    # Get only RECENT messages (e.g., last 2 messages)
    # This prevents re-extracting old info while maintaining context
    recent_messages = all_messages[-4:] if len(all_messages) > 1 else all_messages
    
    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=(
            SYMPTOMS_EXTRACTION_PROMPT.format(
                current_time=get_current_time(), 
                extracted_symptoms=extracted_symptoms
            ) +
            "\nOnly extract NEW info from the patient's most recent message(s). "
            "Do not re-extract information already in extracted_symptoms above."
        )),
        *recent_messages,  # All recent messages
    ]
    
    parsed: SymptomsPartial = symptoms_llm.invoke(msgs)
    updates = {}
    
    # MAIN SYMPTOMS - merge lists with deduplication
    if parsed.main_symptoms is not None and len(parsed.main_symptoms) > 0:
        existing = state.get("main_symptoms") or []
        # Normalize and deduplicate (case-insensitive)
        existing_lower = [s.lower() for s in existing]
        new_symptoms = [
            s for s in parsed.main_symptoms 
            if s.lower() not in existing_lower
        ]
        if new_symptoms:
            updates["main_symptoms"] = existing + new_symptoms
    
    # ONSET - allow updates (corrections)
    if parsed.symptom_onset is not None:
        existing = state.get("symptom_onset") or []
        if parsed.symptom_onset not in existing:
            updates["symptom_onset"] = parsed.symptom_onset
    
    # ASSOCIATED SYMPTOMS - merge with deduplication
    if parsed.associated_symptoms is not None and len(parsed.associated_symptoms) > 0:
        existing = state.get("associated_symptoms") or []
        existing_lower = [s.lower() for s in existing]
        new_associated = [
            s for s in parsed.associated_symptoms 
            if s.lower() not in existing_lower
        ]
        if new_associated:
            updates["associated_symptoms"] = existing + new_associated
    
    # ADDITIONAL INFO - append new info (don't deduplicate as details may vary)
    if parsed.additional_symptom_info is not None and len(parsed.additional_symptom_info) > 0:
        existing = state.get("additional_symptom_info") or []
        # For additional info, we append (may have related but different details)
        updates["additional_symptom_info"] = existing + parsed.additional_symptom_info
    
    print("Extracted symptoms: ", updates)
    
    return updates

def check_symptom_sufficiency(dict: dict):
    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=SYMPTOMS_SUFFICIENCY_CHECK_PROMPT),
        *dict["messages"],
    ]
    resp = symptom_sufficiency_llm.invoke(msgs)
    
    return resp

def human_symptoms_node(state: AgentState) -> AgentState:
    user_input = interrupt("Waiting for symptoms")
    return {"messages": [HumanMessage(content=user_input)]}

def route_after_symptoms(state: AgentState) -> str:
    """Check if Phase 2 is complete, route to Phase 3 or loop back"""
    has_main = state.get("main_symptoms") and len(state["main_symptoms"]) > 0
    has_onset = state.get("symptom_onset") is not None
    
    if not (has_main and has_onset):
        # Missing core fields → keep asking
        return "ask_symptoms"
    
    # Check LLM sufficiency assessment
    check = check_symptom_sufficiency(state)
    
    if check.is_sufficient:
        # Phase 2 complete → move to ask_medhist 
        return "ask_medhist"
    else:
        # Need more details → loop back
        return "ask_symptoms"