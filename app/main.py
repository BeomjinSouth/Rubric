import json
import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import pyrebase

from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
try:
    import olefile  # for basic HWP text extraction
except Exception:  # pragma: no cover - optional dependency
    olefile = None


def extract_text_from_file(path: Path) -> str:
    """Extract text from PDF, DOCX, TXT, or HWP files."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_pdf_text(str(path))
    if ext in {".docx", ".doc"}:
        try:
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""
    if ext == ".hwp" and olefile is not None:
        try:
            ole = olefile.OleFileIO(str(path))
            encoded = ole.openstream("PrvText").read()
            ole.close()
            return encoded.decode("utf-16")
        except Exception:
            return ""
    if ext == ".txt":
        return path.read_text(errors="ignore")
    # Unsupported file types are ignored
    return ""

def summarize_text(text: str, word_limit: int = 50) -> str:
    """Return the first `word_limit` words from the provided text."""
    words = text.split()
    return " ".join(words[:word_limit])

DEFAULT_FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAnN08UzeuiltabBhYex9eq74W8HyAiXPw",
    "authDomain": "project-self-coaching.firebaseapp.com",
    "projectId": "project-self-coaching",
    "storageBucket": "project-self-coaching.firebasestorage.app",
    "messagingSenderId": "326207593603",
    "appId": "1:326207593603:web:2fcc8d826b01e5efbc0fb6",
    "measurementId": "G-NVWCYERX8T",
    "databaseURL": "https://project-self-coaching.firebaseio.com",
}
FIREBASE_CONFIG = DEFAULT_FIREBASE_CONFIG
if os.environ.get("FIREBASE_CONFIG_JSON"):
    try:
        FIREBASE_CONFIG = json.loads(os.environ["FIREBASE_CONFIG_JSON"])
    except json.JSONDecodeError:
        FIREBASE_CONFIG = DEFAULT_FIREBASE_CONFIG

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
db = firebase.database()

app = FastAPI(title="Rubric Web App")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory storage
conversation: List[str] = []
background_summary: str = ""


def save_conversation(message: str) -> None:
    """Save a message locally and in Firebase."""
    conversation.append(message)
    try:
        db.child("conversation").push(message)
    except Exception:
        pass


def load_conversation() -> List[str]:
    """Fetch conversation from Firebase if available."""
    try:
        data = db.child("conversation").get().val() or {}
        return [v for v in data.values()]
    except Exception:
        return conversation


def save_background(summary: str) -> None:
    """Persist background summary in Firebase."""
    global background_summary
    background_summary = summary
    try:
        db.child("background_summary").set(summary)
    except Exception:
        pass


def load_background() -> str:
    """Retrieve background summary from Firebase."""
    global background_summary
    if background_summary:
        return background_summary
    try:
        val = db.child("background_summary").get().val()
        if val:
            background_summary = val
    except Exception:
        pass
    return background_summary


@app.post("/reset")
async def reset_state():
    """Clear conversation history and background summary."""
    conversation.clear()
    global background_summary
    background_summary = ""
    try:
        db.child("conversation").remove()
        db.child("background_summary").remove()
    except Exception:
        pass
    return {"status": "reset"}

@app.post("/upload-philosophy")
async def upload_philosophy(
    files: List[UploadFile] = File(...), notes: str = Form("")
):
    """Upload teaching philosophy materials and optional notes."""
    uploaded = []
    combined_text = notes
    for file in files:
        filepath = UPLOAD_DIR / file.filename
        with filepath.open("wb") as f:
            content = await file.read()
            f.write(content)
        uploaded.append(file.filename)
        combined_text += "\n" + extract_text_from_file(filepath)

    summary = summarize_text(combined_text)
    save_background(summary)
    return {"uploaded": uploaded, "summary": summary}

@app.post("/chat")
async def chat(message: str = Form(...)):
    """Chat about lesson design."""
    save_conversation(message)
    summary = load_background()
    # Placeholder response instead of Gemini API
    if summary:
        response = (
            f"Response placeholder using background: {summary[:30]}..."
        )
    else:
        response = "Response placeholder"
    return {"message": message, "response": response}

@app.post("/generate-plan")
async def generate_plan(filetype: str = Form("txt")):
    """Generate a lesson plan from conversation."""
    content = "Lesson plan placeholder\n"
    summary = load_background()
    convo = load_conversation()
    if summary:
        content += f"Background summary:\n{summary}\n\n"
    content += "\n".join(convo)
    filename = f"lesson_plan.{filetype}"
    Path(filename).write_text(content)
    return FileResponse(filename, media_type="text/plain", filename=filename)

@app.post("/generate-assessment")
async def generate_assessment(filetype: str = Form("txt")):
    """Generate an assessment."""
    content = "Assessment placeholder\n"
    summary = load_background()
    if summary:
        content += f"Background summary:\n{summary}\n"
    filename = f"assessment.{filetype}"
    Path(filename).write_text(content)
    return FileResponse(filename, media_type="text/plain", filename=filename)

@app.post("/generate-rubric")
async def generate_rubric(filetype: str = Form("txt")):
    """Generate a rubric for the assessment."""
    content = "Rubric placeholder\n"
    summary = load_background()
    if summary:
        content += f"Background summary:\n{summary}\n"
    filename = f"rubric.{filetype}"
    Path(filename).write_text(content)
    return FileResponse(filename, media_type="text/plain", filename=filename)
