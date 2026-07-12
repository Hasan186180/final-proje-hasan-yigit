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

    # Güncel Gemini modelleri — tercih sırasına göre (yeniden eskiye)
    PREFERRED_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
    ]

    # Önce API'den mevcut modelleri almayı dene
    try:
        available = {
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        }
        # Tercih listesinden ilk mevcut olanı seç
        selected = next((m for m in PREFERRED_MODELS if m in available), None)
        if selected is None and available:
            selected = next(iter(available))  # İlk mevcut model
        model_name = selected or PREFERRED_MODELS[0]
    except Exception:
        # list_models başarısız olursa listeyi deneme sırasına koy
        model_name = None

    user_content = json.dumps(user_payload, ensure_ascii=False, indent=2)

    # model_name belirlendiyse doğrudan dene, değilse listeyi sırayla dene
    candidates = [model_name] if model_name else PREFERRED_MODELS

    last_error = None
    for candidate in candidates:
        try:
            model = genai.GenerativeModel(
                model_name=candidate,
                system_instruction=system_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                )
            )
            response = model.generate_content(user_content)
            return _extract_json(response.text)
        except Exception as e:
            last_error = e
            continue  # Bir sonraki modeli dene

    raise RuntimeError(
        f"Hiçbir Gemini modeli çalışmadı. Son hata: {last_error}\n"
        f"İpucu: GEMINI_API_KEY'inizin geçerli ve aktif olduğundan emin olun."
    )


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
) -> tuple[Schedule, list[Task]]:
    """Mevcut planı kullanıcının serbest metin talebiyle yeniden düzenler."""
    user_payload = {
        "tasks": [task.model_dump() for task in tasks],
        "current_schedule": current_schedule.model_dump(),
        "prompt": prompt,
        "working_hours": working_hours.model_dump()
    }
    result = _call_ai(REARRANGE_SYSTEM_PROMPT, user_payload)
    
    # Schedule modelindeki alanları ayıkla
    schedule_data = {k: result[k] for k in ["slots", "unassigned_tasks", "insights"] if k in result}
    schedule = Schedule(**schedule_data)
    
    # Güncellenmiş görev listesini ayıkla
    updated_tasks = tasks
    if "updated_tasks" in result:
        try:
            updated_tasks = [Task(**t) for t in result["updated_tasks"]]
        except Exception:
            pass
            
    return schedule, updated_tasks
