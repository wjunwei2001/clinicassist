from models import AgentState, MedHistoryFact, MedHistorySufficiencyCheck
from prompts import BASE_PROMPT, MEDICAL_HISTORY_EXTRACTION_PROMPT, MEDICAL_HISTORY_ASKING_PROMPT, MEDICAL_HISTORY_SUFFICIENCY_CHECK_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from typing import List
from utils import get_current_time
from langgraph.types import interrupt

from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(model="gpt-4.1", temperature=0)
medhist_llm = llm.with_structured_output(MedHistoryFact)
medhist_sufficiency_llm = llm.with_structured_output(MedHistorySufficiencyCheck)

def format_medhist_facts(facts: List[MedHistoryFact]) -> str:
    return "\n".join([f"{fact.category}: {fact.question} - {fact.answer} {f'({fact.additional_details})' if fact.additional_details else ''}" for fact in facts])

def extract_medhist(state: AgentState) -> AgentState:
    print("Extracting medical history")
    existing_facts = state.get("medical_history", [])

    facts_summary = format_medhist_facts(existing_facts)
    recent_messages = state.get("messages", [])[-4:]

    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=MEDICAL_HISTORY_EXTRACTION_PROMPT.format(
            current_time=get_current_time(),
            extracted_patient_info={
                "name": state["patient_name"],
                "age": state["patient_age"],
                "sex": state["patient_sex"]
            },
            extracted_symptoms={
                "main_symptoms": state["main_symptoms"],
                "symptom_onset": state["symptom_onset"],
                "associated_symptoms": state["associated_symptoms"],
                "additional_symptom_info": state["additional_symptom_info"]
            },
            extracted_medical_history=facts_summary
        )),
        *recent_messages,
    ]

    parsed = medhist_llm.invoke(msgs)
    updates = {}
    if parsed.category is not None and parsed.question is not None and parsed.answer is not None:
        updates["medical_history"] = existing_facts + [parsed]
    
    return updates

def ask_medhist(state: AgentState) -> AgentState:
    print("Asking medical history")
    existing_facts = state.get("medical_history", [])

    facts_summary = format_medhist_facts(existing_facts)

    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=MEDICAL_HISTORY_ASKING_PROMPT.format(
            current_time=get_current_time(),
            extracted_patient_info={
                "name": state["patient_name"],
                "age": state["patient_age"],
                "sex": state["patient_sex"]
            },
            extracted_symptoms={
                "main_symptoms": state["main_symptoms"],
                "symptom_onset": state["symptom_onset"],
                "associated_symptoms": state["associated_symptoms"],
                "additional_symptom_info": state["additional_symptom_info"]
            },
            extracted_medical_history=facts_summary
        ))
    ]

    resp = llm.invoke(msgs)
    return {"messages": [resp]}

def route_after_med_history(state):
    facts = state.get("medical_history_facts", [])
    
    # Check mandatory items
    # has_past_condition_info = any(f.category == "past_condition" for f in facts)
    # has_medication_info = any(f.category == "medication" for f in facts)
    
    # if not (has_past_condition_info and has_medication_info):
    #     return "ask_medhist"  # Keep asking
    
    # LLM sufficiency check for everything else
    check = check_medhist_sufficiency(state)
    return "triage_summary" if check.is_sufficient else "ask_medhist"

def check_medhist_sufficiency(state):
    print("Checking medical history sufficiency")
    facts = state.get("medical_history_facts", [])
    
    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=MEDICAL_HISTORY_SUFFICIENCY_CHECK_PROMPT.format(
            extracted_medical_history=format_medhist_facts(facts)
        )),
        *state["messages"],
    ]

    resp = medhist_sufficiency_llm.invoke(msgs)
    return resp

def human_medhist_node(state: AgentState) -> AgentState:
    user_input = interrupt("Waiting for medical history")
    return {"messages": [HumanMessage(content=user_input)]}