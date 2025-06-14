# Rubric Web App Design

This repository contains a high-level plan for a web application that assists teachers in creating lesson plans, assessments, and rubrics using the Gemini API.

## Workflow Overview

1. **Pre-Step: Teaching Philosophy and Direction**
   - Teachers upload one or more files (PDF, HWP, Docs, TXT, etc.) along with notes describing the overall teaching philosophy.
   - The server stores the files, extracts any readable text (PDF, DOCX and basic HWP support), and summarizes the combined notes. This summary is used as context in later stages.

2. **Lesson Design Chat**
   - Teachers chat with the system using the Gemini API to discuss lesson structure and assessments.

3. **Lesson Plan Generation**
   - Once planning is complete, Gemini generates a lesson plan document. Teachers can save it as **HWP** or **TXT**.

4. **Assessment Creation**
   - After the lesson plan, teachers continue the conversation to craft assessments.
   - Assessments are also downloadable as **HWP** or **TXT** files.

5. **Rubric Design**
   - Gemini helps create a rubric for the assessments.
   - Rubrics can be saved as **HWP** or **TXT** files.

## Optional Steps

Teachers may skip any of the steps above. For example, a teacher can jump directly to rubric design, in which case the system asks for enough information to generate the rubric.


## Running the App

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. The API will be available at `http://127.0.0.1:8000`.

The server stores conversation history and the background summary in **Firebase**.
The default configuration in `app/main.py` uses a sample Firebase project.
You can override these settings by providing a JSON string in the
`FIREBASE_CONFIG_JSON` environment variable.

There is also a `/reset` endpoint to clear any stored conversation and background summary.

These endpoints are minimal placeholders that save uploaded files and generate
simple text outputs. Integrate the Gemini API to replace the stub logic.
