from models import AgentState, PatientInfoPartial
from prompts import BASE_PROMPT, PATIENT_INFO_ASKING_PROMPT, PATIENT_INFO_EXTRACTION_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(model="gpt-4.1", temperature=0)
extract_llm = llm.with_structured_output(PatientInfoPartial)

def ask_patient_info(state: AgentState) -> AgentState: 
    print("Asking patient info")
    missing = []
    if state.get("patient_name") is None: missing.append("name")
    if state.get("patient_age") is None: missing.append("age")
    if state.get("patient_sex") is None: missing.append("sex")

    known_bits = []
    if state.get("patient_name") is not None: known_bits.append(f"name={state['patient_name']}")
    if state.get("patient_age") is not None: known_bits.append(f"age={state['patient_age']}")
    if state.get("patient_sex") is not None: known_bits.append(f"sex={state['patient_sex']}")

    steering = (
        "You are collecting basic patient demographic information for triage.\n"
        f"Known so far: {', '.join(known_bits) if known_bits else 'none'}.\n"
        f"Missing (in order): {', '.join(missing) if missing else 'none'}.\n"
        "- If anything is missing, ask ONLY for the first missing field with one concise question.\n"
        "- Keep it friendly and brief."
    )

    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=PATIENT_INFO_ASKING_PROMPT),
        SystemMessage(content=steering),
        *state["messages"],
    ]
    resp = llm.invoke(msgs)

    return {"messages": [resp]}

def extract_patient_info(state: AgentState) -> AgentState:
    print("Extracting patient info")
    human_only = [m for m in state.get("messages", []) if isinstance(m, HumanMessage)]
    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=(
            PATIENT_INFO_EXTRACTION_PROMPT +
            "\nOnly extract info stated by the patient. If not present, leave that field null. Use the right capitalization for names (eg. Jon Ang instead of jon ang)."
        )),
        *human_only,
    ]
    parsed: PatientInfoPartial = extract_llm.invoke(msgs)

    updates = {}
    if parsed.name is not None and state.get("patient_name") is None:
        updates["patient_name"] = parsed.name.upper()
    if parsed.age is not None and state.get("patient_age") is None:
        updates["patient_age"] = parsed.age
    if parsed.sex is not None and state.get("patient_sex") is None:
        updates["patient_sex"] = parsed.sex
    return updates

def route_after_patient_info(state: AgentState) -> str:
    """Check if Phase 1 is complete, route to Phase 2 or loop back"""
    has_name = state.get("patient_name") is not None
    has_age = state.get("patient_age") is not None
    has_sex = state.get("patient_sex") is not None
    
    if has_name and has_age and has_sex:
        # Phase 1 complete → move to Phase 2
        return "ask_symptoms"
    else:
        # Phase 1 incomplete → loop back
        return "ask_patient_info"

def human_patient_info_node(state: AgentState) -> AgentState:
    user_input = interrupt("Waiting for patient info")
    return {"messages": [HumanMessage(content=user_input)]}