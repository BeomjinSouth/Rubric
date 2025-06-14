from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List

from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document


def extract_text_from_file(path: Path) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    if path.suffix.lower() == ".pdf":
        return extract_pdf_text(str(path))
    if path.suffix.lower() in {".docx", ".doc"}:
        try:
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""
    if path.suffix.lower() in {".txt"}:
        return path.read_text(errors="ignore")
    # Unsupported file types are ignored
    return ""

def summarize_text(text: str, word_limit: int = 50) -> str:
    """Return the first `word_limit` words from the provided text."""
    words = text.split()
    return " ".join(words[:word_limit])

app = FastAPI(title="Rubric Web App")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory storage
conversation: List[str] = []
background_summary: str = ""


@app.post("/reset")
async def reset_state():
    """Clear conversation history and background summary."""
    conversation.clear()
    global background_summary
    background_summary = ""
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

    global background_summary
    background_summary = summarize_text(combined_text)
    return {"uploaded": uploaded, "summary": background_summary}

@app.post("/chat")
async def chat(message: str = Form(...)):
    """Chat about lesson design."""
    conversation.append(message)
    # Placeholder response instead of Gemini API
    if background_summary:
        response = (
            f"Response placeholder using background: {background_summary[:30]}..."
        )
    else:
        response = "Response placeholder"
    return {"message": message, "response": response}

@app.post("/generate-plan")
async def generate_plan(filetype: str = Form("txt")):
    """Generate a lesson plan from conversation."""
    content = "Lesson plan placeholder\n"
    if background_summary:
        content += f"Background summary:\n{background_summary}\n\n"
    content += "\n".join(conversation)
    filename = f"lesson_plan.{filetype}"
    Path(filename).write_text(content)
    return FileResponse(filename, media_type="text/plain", filename=filename)

@app.post("/generate-assessment")
async def generate_assessment(filetype: str = Form("txt")):
    """Generate an assessment."""
    content = "Assessment placeholder\n"
    if background_summary:
        content += f"Background summary:\n{background_summary}\n"
    filename = f"assessment.{filetype}"
    Path(filename).write_text(content)
    return FileResponse(filename, media_type="text/plain", filename=filename)

@app.post("/generate-rubric")
async def generate_rubric(filetype: str = Form("txt")):
    """Generate a rubric for the assessment."""
    content = "Rubric placeholder\n"
    if background_summary:
        content += f"Background summary:\n{background_summary}\n"
    filename = f"rubric.{filetype}"
    Path(filename).write_text(content)
    return FileResponse(filename, media_type="text/plain", filename=filename)
