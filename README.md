# WhatsApp AI Assistant

A starter Python webhook for the official WhatsApp Cloud API. It accepts text and audio messages, transcribes audio locally with faster-whisper, and generates replies using a local Ollama model.

## Important status

This repository is the **bot application code**, not a live WhatsApp connection yet. A working connection still requires:
- An eligible phone number and a Meta WhatsApp Business Platform setup.
- A public HTTPS address for this app's webhook.
- Meta's access token, Phone Number ID, and webhook verification.
- A computer/server that stays online.
- Ollama installed and running on the same computer as this app (or an accessible machine).

GitHub stores the code; GitHub Pages and ordinary GitHub Actions do not run this webhook as an always-on server. No WhatsApp credentials should ever be committed to GitHub.

## 1. Install Python packages

Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Install local AI

Install Ollama from https://ollama.com/ and download a small model:

```bash
ollama pull qwen2.5:3b
```

Keep Ollama running. If your computer has limited RAM, a smaller model may be needed.

## 3. Configure environment

Copy `.env.example` to `.env` and fill the Meta values only after official API onboarding. Never share the values or commit `.env`.

## 4. Run the webhook locally

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The health check is at `http://localhost:8000/`. Meta requires a public HTTPS webhook URL; localhost alone cannot receive Meta webhook events.

## 5. Optional voice transcription

Install the optional package:

```bash
pip install faster-whisper
```

The first run downloads the Whisper model. Audio is processed on the machine running this app.

## Current limitations

- Conversation history is held in RAM and resets when the app restarts.
- Only text and audio messages are handled in this starter version.
- It does not bypass Meta verification, supported-country rules, number eligibility, or WhatsApp messaging policies.
- The app should be disclosed as an automated assistant to people messaging the number.
- Free local AI avoids per-message model API charges, but the computer, electricity, internet, and hosting are still needed.
