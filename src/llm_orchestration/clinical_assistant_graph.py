from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

from models import AgentState, PatientInfoPartial, SymptomsPartial, SymptomSufficiencyCheck, MedHistoryFact, MedHistorySufficiencyCheck, TriageSummary
from llm_orchestration.part1_patient_demo import ask_patient_info, extract_patient_info, human_patient_info_node, route_after_patient_info
from llm_orchestration.part2_symptom_collect import ask_symptoms, extract_symptoms, check_symptom_sufficiency, human_symptoms_node, route_after_symptoms
from llm_orchestration.part3_medhist_collect import ask_medhist, extract_medhist, check_medhist_sufficiency, route_after_med_history, human_medhist_node
from llm_orchestration.part4_triaging import triage_summary, acknowledgement

def build_clinical_assistant_graph():
    clinical_assistant_builder = StateGraph(AgentState)

    # Add Phase 1 nodes
    clinical_assistant_builder.add_node("ask_patient_info", ask_patient_info)
    clinical_assistant_builder.add_node("extract_patient_info", extract_patient_info)
    clinical_assistant_builder.add_node("human_patient_info_node", human_patient_info_node)

    # Add Phase 2 nodes
    clinical_assistant_builder.add_node("ask_symptoms", ask_symptoms)
    clinical_assistant_builder.add_node("extract_symptoms", extract_symptoms)
    clinical_assistant_builder.add_node("human_symptoms_node", human_symptoms_node)

    # Add Phase 3 nodes
    clinical_assistant_builder.add_node("ask_medhist", ask_medhist)
    clinical_assistant_builder.add_node("extract_medhist", extract_medhist)
    clinical_assistant_builder.add_node("human_medhist_node", human_medhist_node)

    # Add Phase 4 nodes
    clinical_assistant_builder.add_node("triage_summary", triage_summary)
    clinical_assistant_builder.add_node("acknowledgement", acknowledgement)

    # Phase 1 flow
    clinical_assistant_builder.add_edge(START, "ask_patient_info")
    clinical_assistant_builder.add_edge("ask_patient_info", "human_patient_info_node")
    clinical_assistant_builder.add_edge("human_patient_info_node", "extract_patient_info")

    # Conditional edge: Phase 1 → Phase 2 or loop
    clinical_assistant_builder.add_conditional_edges(
        "extract_patient_info",
        route_after_patient_info,
        {
            "ask_patient_info": "ask_patient_info",  # Loop back if incomplete
            "ask_symptoms": "ask_symptoms"           # Move to Phase 2 if complete
        }
    )

    # Phase 2 flow
    clinical_assistant_builder.add_edge("ask_symptoms", "human_symptoms_node")
    clinical_assistant_builder.add_edge("human_symptoms_node", "extract_symptoms")

    # Conditional edge: Phase 2 → Phase 3 or loop
    clinical_assistant_builder.add_conditional_edges(
        "extract_symptoms",
        route_after_symptoms,
        {
            "ask_symptoms": "ask_symptoms",  # Loop back if incomplete
            "ask_medhist": "ask_medhist"                         # End when complete (or Phase 3 later)
        }
    )

    # Phase 3 flow
    clinical_assistant_builder.add_edge("ask_medhist", "human_medhist_node")
    clinical_assistant_builder.add_edge("human_medhist_node", "extract_medhist")

    # Phase 4 flow
    clinical_assistant_builder.add_edge("extract_medhist", "triage_summary")
    clinical_assistant_builder.add_edge("triage_summary", "acknowledgement")
    clinical_assistant_builder.add_edge("acknowledgement", END)

    # Conditional edge: Phase 3 → END or loop
    clinical_assistant_builder.add_conditional_edges(
        "extract_medhist",
        route_after_med_history,
        {
            "ask_medhist": "ask_medhist",  # Loop back if incomplete
            "triage_summary": "triage_summary"                         # End when complete (or Phase 3 later)
        }
    )

    checkpointer = InMemorySaver()

    return clinical_assistant_builder.compile(
        checkpointer=checkpointer,
    )

def thread_config(thread_id: str):
    return {"configurable": {"thread_id": thread_id}}