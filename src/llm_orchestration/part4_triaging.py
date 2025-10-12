from models import AgentState, TriageSummary
from prompts import BASE_PROMPT, TRIAGE_SUMMARY_PROMPT, ACKNOWLEDGEMENT_PROMPT
from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(model="gpt-4.1", temperature=0)
final_llm = llm.with_structured_output(TriageSummary)

def triage_summary(state: AgentState) -> AgentState:
    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=TRIAGE_SUMMARY_PROMPT),
        *state["messages"],
    ]
    parsed = final_llm.invoke(msgs)
    return {"generated_summary": parsed}

def acknowledgement(state: AgentState) -> AgentState:
    msgs = [
        SystemMessage(content=BASE_PROMPT),
        SystemMessage(content=ACKNOWLEDGEMENT_PROMPT),
        *state["messages"],
    ]
    resp = llm.invoke(msgs)
    return {"messages": [resp]}