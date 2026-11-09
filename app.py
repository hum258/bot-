import os
import tempfile
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from ai_engine import ask_ai, transcribe_audio

load_dotenv()
app = FastAPI(title="WhatsApp AI Assistant")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v23.0")

# Simple in-memory conversation history. It resets when the server restarts.
histories: dict[str, list[dict[str, str]]] = {}


@app.get("/")
async def health():
    return {"status": "running", "service": "WhatsApp AI Assistant"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
        and VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge", ""))
    raise HTTPException(status_code=403, detail="Webhook verification failed")


async def download_whatsapp_audio(media_id: str) -> tuple[bytes, str]:
    if not WHATSAPP_TOKEN:
        raise RuntimeError("WHATSAPP_TOKEN is not configured")
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient(timeout=60) as client:
        meta = await client.get(
            f"https://graph.facebook.com/{GRAPH_API_VERSION}/{media_id}",
            headers=headers,
        )
        meta.raise_for_status()
        media_url = meta.json()["url"]
        media = await client.get(media_url, headers=headers)
        media.raise_for_status()
        mime = meta.json().get("mime_type", "audio/ogg")
        return media.content, mime


async def send_whatsapp_text(to: str, text: str):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        raise RuntimeError("WhatsApp API credentials are not configured")
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text[:4000]},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json=payload,
        )
        response.raise_for_status()


async def handle_message(message: dict[str, Any]):
    sender = message.get("from")
    if not sender:
        return

    message_type = message.get("type")
    user_text = ""

    if message_type == "text":
        user_text = message.get("text", {}).get("body", "").strip()
    elif message_type == "audio":
        media_id = message.get("audio", {}).get("id")
        if not media_id:
            return
        audio_bytes, mime = await download_whatsapp_audio(media_id)
        suffix = ".ogg" if "ogg" in mime else ".audio"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(audio_bytes)
            audio_path = temp.name
        try:
            user_text = transcribe_audio(audio_path)
        finally:
            try:
                os.unlink(audio_path)
            except OSError:
                pass
        if not user_text:
            await send_whatsapp_text(sender, "لم أتمكن من فهم التسجيل. جرّب إرساله بوضوح مرة أخرى أو اكتب سؤالك.")
            return
    else:
        return

    history = histories.setdefault(sender, [])
    reply = ask_ai(user_text, history)
    history.extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": reply},
    ])
    histories[sender] = history[-12:]
    await send_whatsapp_text(sender, reply)


@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    try:
        entries = data.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for message in value.get("messages", []):
                    try:
                        await handle_message(message)
                    except Exception as exc:
                        # Avoid exposing credentials or stack traces to WhatsApp.
                        print(f"Message processing error: {type(exc).__name__}: {exc}")
    except Exception as exc:
        print(f"Webhook payload error: {type(exc).__name__}: {exc}")
    return {"ok": True}
