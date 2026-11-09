import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "أنت مساعد ذكي عام. أجب بلغة المستخدم، وكن واضحاً ومفيداً. "
    "إذا لم تكن متأكداً فقل ذلك ولا تخترع معلومات. لا تدّعِ أنك إنسان."
)

_whisper_model = None


def ask_ai(user_text: str, history: list[dict[str, str]]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_text})

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "").strip()
        return answer or "لم أستطع إنشاء إجابة الآن. جرّب مرة أخرى."
    except requests.RequestException as exc:
        print(f"Local AI error: {type(exc).__name__}: {exc}")
        return (
            "خدمة الذكاء الاصطناعي غير متصلة حالياً. "
            "تأكد أن Ollama يعمل على الكمبيوتر ثم أعد المحاولة."
        )


def transcribe_audio(audio_path: str) -> str:
    global _whisper_model
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError(
            "التعرف على الصوت غير مثبت. ثبّت الحزمة الاختيارية faster-whisper."
        )

    if _whisper_model is None:
        model_name = os.getenv("WHISPER_MODEL", "tiny")
        _whisper_model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
        )

    segments, _ = _whisper_model.transcribe(audio_path, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()
