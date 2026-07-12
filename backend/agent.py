import json
import re
from backend.config import AI_PROVIDER, GEMINI_API_KEY, GROQ_API_KEY
from backend.models import Task, WorkingHours, Schedule
from backend.prompts import PLANNER_SYSTEM_PROMPT, REARRANGE_SYSTEM_PROMPT


def _extract_json(text: str) -> dict:
    """Ham metin yanıtından JSON bloğunu çıkarır ve parse eder."""
    # ```json ... ``` veya ``` ... ``` bloklarını temizle
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    # Sadece ilk { ... } bloğunu al
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("AI yanıtında geçerli bir JSON bloğu bulunamadı.")
    return json.loads(text[start:end])


def _call_gemini(system_prompt: str, user_payload: dict) -> dict:
    """Google Gemini API'sini çağırır ve JSON dict döner."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY .env dosyasında tanımlanmamış!")

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.3,
        )
    )

    user_content = json.dumps(user_payload, ensure_ascii=False, indent=2)
    response = model.generate_content(user_content)
    return _extract_json(response.text)


def _call_groq(system_prompt: str, user_payload: dict) -> dict:
    """Groq API'sini çağırır ve JSON dict döner."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY .env dosyasında tanımlanmamış!")

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    user_content = json.dumps(user_payload, ensure_ascii=False, indent=2)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    return _extract_json(raw)


def _call_ai(system_prompt: str, user_payload: dict) -> dict:
    """Aktif AI sağlayıcısına göre doğru API'yi çağırır."""
    if AI_PROVIDER == "groq":
        return _call_groq(system_prompt, user_payload)
    else:
        return _call_gemini(system_prompt, user_payload)


def generate_schedule(tasks: list[Task], working_hours: WorkingHours) -> Schedule:
    """Verilen görevler ve çalışma saatlerine göre günlük plan üretir."""
    user_payload = {
        "tasks": [task.model_dump() for task in tasks],
        "working_hours": working_hours.model_dump()
    }
    result = _call_ai(PLANNER_SYSTEM_PROMPT, user_payload)
    return Schedule(**result)


def rearrange_schedule(
    tasks: list[Task],
    current_schedule: Schedule,
    prompt: str,
    working_hours: WorkingHours
) -> Schedule:
    """Mevcut planı kullanıcının serbest metin talebiyle yeniden düzenler."""
    user_payload = {
        "tasks": [task.model_dump() for task in tasks],
        "current_schedule": current_schedule.model_dump(),
        "prompt": prompt,
        "working_hours": working_hours.model_dump()
    }
    result = _call_ai(REARRANGE_SYSTEM_PROMPT, user_payload)
    return Schedule(**result)
