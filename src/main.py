from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command
import uuid
import uvicorn

from llm_orchestration.clinical_assistant_graph import build_clinical_assistant_graph, thread_config
from models import StartResponse, ChatRequest, ChatResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clinical_assistant_graph = build_clinical_assistant_graph()

PHASE_BY_NODE = {
    # Phase 1
    "ask_patient_info": "Gathering patient demographic details",
    "human_patient_info_node": "Gathering patient demographic details",
    "extract_patient_info": "Gathering patient demographic details",
    # Phase 2
    "ask_symptoms": "Symptoms collection",
    "human_symptoms_node": "Symptoms collection",
    "extract_symptoms": "Symptoms collection",
    # Phase 3
    "ask_medhist": "Medical/health history",
    "human_medhist_node": "Medical/health history",
    "extract_medhist": "Medical/health history",
    # Phase 4
    "triage_summary": "Triage & summary",
    "acknowledgement": "Triage & summary",
}

def phase_from_next(snapshot) -> str:
    if not snapshot.next:
        return "Complete"
    # snapshot.next is a tuple of upcoming node names
    for node in snapshot.next:
        if node in PHASE_BY_NODE:
            return PHASE_BY_NODE[node]
    return "Unknown"

def extract_view(state: dict) -> dict:
    return {
        "patient_name": state.get("patient_name"),
        "patient_age": state.get("patient_age"),
        "patient_sex": state.get("patient_sex"),
        "main_symptoms": state.get("main_symptoms", []),
        "symptom_onset": state.get("symptom_onset"),
        "associated_symptoms": state.get("associated_symptoms", []),
        "additional_symptom_info": state.get("additional_symptom_info", []),
        "medical_history": state.get("medical_history", []),
        "generated_summary": state.get("generated_summary"),
    }

# def last_ai_from_stream(stream_iter):
#     last = None
#     for message, meta in stream_iter:
#         if message.content:
#             # Filter to user-facing nodes only
#             node = meta.get("langgraph_node")
#             if node in {"ask_patient_info", "ask_symptoms", "ask_medhist", "acknowledgement"}:
#                 last = message.content
#                 yield last
#     return last

@app.post("/api/chat/start", response_model=StartResponse)
def start_chat():
    session_id = str(uuid.uuid4())
    config = thread_config(session_id)

    for events in clinical_assistant_graph.stream({"messages": []}, config, stream_mode="updates"):
        for key, value in events.items():
            if key != '__interrupt__' and isinstance(value, dict) and 'messages' in value:
                messages = value['messages']
                break
    
    snapshot = clinical_assistant_graph.get_state(config)
    
    return StartResponse(
        session_id=session_id, 
        assistant_message=messages[-1].content, 
        state=extract_view(snapshot.values), 
        phase=phase_from_next(snapshot), 
        is_complete=not snapshot.next
    )

@app.post("/api/chat/reply", response_model=ChatResponse)
def chat_reply(request: ChatRequest):
    config = thread_config(request.session_id)

    messages = None
    for events in clinical_assistant_graph.stream(Command(resume=request.message), config, stream_mode="updates"):
        for key, value in events.items():
            if key != '__interrupt__' and isinstance(value, dict) and 'messages' in value:
                messages = value['messages'] 
                break

    snapshot = clinical_assistant_graph.get_state(config)
    is_complete = not snapshot.next

    if is_complete:
        final_state = extract_view(snapshot.values)
        clinical_assistant_graph.checkpointer.delete_thread(request.session_id)
        
        closing = (
            f"Thank you for using ClinicAssist. Your information has been captured and will be sent to the doctor. "
            f"Your queue number is XX."
        )
        return ChatResponse(
            session_id=request.session_id,
            assistant_message=closing,
            state=final_state,
            phase="Complete",
            is_complete=True,
        )

    return ChatResponse(
        session_id=request.session_id,
        assistant_message=messages[-1].content if messages else None,
        state=extract_view(snapshot.values),
        phase=phase_from_next(snapshot),
        is_complete=False,
    )

# # Manual end checkpoint
# @app.post("/api/chat/end", response_model=ChatResponse)
# def end_chat(request: ChatRequest):
#     config = thread_config(request.session_id)
#     clinical_assistant_graph.get_state(config)
#     snapshot = clinical_assistant_graph.get_state(config)
#     return ChatResponse(
#         session_id=request.session_id, 
#         assistant_message=None,
#         state=extract_view(snapshot.values), 
#         phase=phase_from_next(snapshot), 
#         is_complete=not snapshot.next
#     )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
