import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine import compose_brain, run_lookup

STORAGE_ROOT = Path("workspace_docs")
STORAGE_ROOT.mkdir(exist_ok=True)

service = FastAPI(title="UniBot API", version="3.0.0")
service.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory_spaces = {}
app = service


class QueryPayload(BaseModel):
    space_id: str
    prompt: str


class AskPayload(BaseModel):
    question: str
    space_id: str


@service.get("/health")
def ping():
    return {"status": "ok", "service": "unibot-api"}


@service.get("/")
def overview():
    return {
        "message": "UniBot API hazir.",
        "workspace_endpoint": "/knowledge-bases",
        "query_endpoint": "/chat",
    }


@service.post("/knowledge-bases")
async def assemble_space(
    files: list[UploadFile] = File(...),
    label: str = Form("Yeni calisma alani"),
):
    accepted_uploads = [
        item for item in files if item.filename and item.filename.lower().endswith(".pdf")
    ]
    if not accepted_uploads:
        raise HTTPException(status_code=400, detail="En az bir PDF dosyasi yuklemelisiniz.")

    space_id = str(uuid4())
    bucket_path = STORAGE_ROOT / space_id
    bucket_path.mkdir(parents=True, exist_ok=True)

    local_paths = []
    try:
        for incoming_file in accepted_uploads:
            target_file = bucket_path / Path(incoming_file.filename).name
            with target_file.open("wb") as target_stream:
                shutil.copyfileobj(incoming_file.file, target_stream)
            local_paths.append(str(target_file))

        brain_bundle = compose_brain(local_paths)
        memory_spaces[space_id] = {
            "title": label,
            "assets": [Path(saved).name for saved in local_paths],
            "brain": brain_bundle["brain"],
            "page_total": brain_bundle["page_total"],
            "segment_total": brain_bundle["segment_total"],
        }
    except Exception as exc:
        shutil.rmtree(bucket_path, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Calisma alani hazirlanamadi: {exc}") from exc

    current_space = memory_spaces[space_id]
    return {
        "space_id": space_id,
        "label": current_space["title"],
        "files": current_space["assets"],
        "document_count": current_space["page_total"],
        "chunk_count": current_space["segment_total"],
    }


@service.get("/knowledge-bases/{space_id}")
def inspect_space(space_id: str):
    selected_space = memory_spaces.get(space_id)
    if not selected_space:
        raise HTTPException(status_code=404, detail="Bilgi alani bulunamadi.")

    return {
        "space_id": space_id,
        "label": selected_space["title"],
        "files": selected_space["assets"],
        "document_count": selected_space["page_total"],
        "chunk_count": selected_space["segment_total"],
    }


@service.post("/chat")
def respond(payload: QueryPayload):
    if not payload.prompt or not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Soru alani bos birakilamaz.")

    selected_space = memory_spaces.get(payload.space_id)
    if not selected_space:
        raise HTTPException(status_code=404, detail="Soru sorulacak bilgi alani bulunamadi.")

    try:
        reply_text = run_lookup(selected_space["brain"], payload.prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Yanit uretilirken hata olustu: {exc}") from exc

    return {
        "kb_id": payload.space_id,
        "question": payload.prompt,
        "answer": reply_text,
        "label": selected_space["title"],
    }


@service.post("/ask")
def ask_question(payload: AskPayload):
    chat_payload = QueryPayload(space_id=payload.space_id, prompt=payload.question)
    return respond(chat_payload)
