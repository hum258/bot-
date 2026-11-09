# WhatsApp AI Assistant

A starter Python webhook for the official WhatsApp Cloud API. It accepts text and audio messages, transcribes audio locally with optional faster-whisper, and generates text replies using the Gemini API.

## Important status

This repository contains the bot application code; it is **not connected to WhatsApp yet**. A working WhatsApp connection still requires:
- An eligible phone number and Meta WhatsApp Business Platform setup.
- A public HTTPS address for this app's webhook.
- Meta's access token, Phone Number ID, and webhook verification.
- An always-on hosting service or computer.
- A Gemini API key configured privately in the environment.

GitHub stores the code; it does not run this webhook as an always-on server. Never commit your real `.env` file or share API keys and WhatsApp tokens.

## 1. Install Python packages

Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## 2. Get Gemini API access

Use Google AI Studio to create an API key: https://aistudio.google.com/app/apikey

The Gemini API offers a free tier for eligible accounts and models, with usage limits. Do not enable paid billing if you want to keep this project free. Availability and eligibility depend on Google's account, region, and current rules. A parent or guardian should handle account setup if required by the service's age terms.

Copy `.env.example` to `.env`, then set `GEMINI_API_KEY` in your private `.env` file. Never paste the key into GitHub or this chat.

## 3. Configure WhatsApp later

Fill in `VERIFY_TOKEN`, `WHATSAPP_TOKEN`, and `PHONE_NUMBER_ID` only after completing Meta's official WhatsApp Cloud API setup. Do not put real credentials in this repository.

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

The first run downloads the Whisper model. Audio transcription is processed on the machine running this app and is optional. Without it, text messages can still be handled.

## Current limitations

- Conversation history is held in RAM and resets when the app restarts.
- Only text and audio messages are handled in this starter version.
- Gemini free-tier access has rate and usage limits; it is not unlimited.
- Voice transcription requires the optional local Whisper package and model download.
- It does not bypass Meta verification, phone-number eligibility, supported-country rules, or WhatsApp messaging policies.
- The app should be disclosed as an automated assistant to people messaging the number.
