import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "أنت مساعد ذكي عام. أجب بلغة المستخدم، وكن واضحاً ومفيداً. "
    "إذا لم تكن متأكداً فقل ذلك ولا تخترع معلومات. لا تدّعِ أنك إنسان."
)

_whisper_model = None


def ask_ai(user_text: str, history: list[dict[str, str]]) -> str:
    if not GEMINI_API_KEY:
        return "لم يتم إعداد مفتاح Gemini API بعد. أضِف GEMINI_API_KEY إلى ملف .env."

    contents = []
    for item in history[-10:]:
        role = "model" if item.get("role") == "assistant" else "user"
        content = str(item.get("content", "")).strip()
        if content:
            contents.append({"role": role, "parts": [{"text": content}]})
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    try:
        response = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json={
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": contents,
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 700},
            },
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        answer = "\n".join(
            part.get("text", "") for part in parts if part.get("text")
        ).strip()
        return answer or "لم أستطع إنشاء إجابة الآن. جرّب مرة أخرى."
    except requests.RequestException as exc:
        print(f"Gemini API error: {type(exc).__name__}: {exc}")
        return "تعذر الاتصال بخدمة الذكاء الاصطناعي حالياً. تحقق من الإنترنت ومفتاح API ثم أعد المحاولة."
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"Gemini response error: {type(exc).__name__}: {exc}")
        return "وصل رد غير متوقع من خدمة الذكاء الاصطناعي. جرّب مرة أخرى."


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
