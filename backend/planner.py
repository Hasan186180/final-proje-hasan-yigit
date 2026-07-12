import os
import json
from typing import List, Optional
from backend.models import Task, Schedule

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks_db.json")

def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        default_db = {
            "tasks": [],
            "schedule": {
                "slots": [],
                "unassigned_tasks": [],
                "insights": ""
            }
        }
        save_db(default_db)
        return default_db
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Dosya bozuk veya okunamıyorsa sıfırla
        default_db = {
            "tasks": [],
            "schedule": {
                "slots": [],
                "unassigned_tasks": [],
                "insights": ""
            }
        }
        save_db(default_db)
        return default_db

def save_db(data: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_tasks() -> List[Task]:
    db = load_db()
    return [Task(**t) for t in db.get("tasks", [])]

def add_task(task: Task) -> Task:
    db = load_db()
    tasks = db.get("tasks", [])
    # ID çakışması varsa güncelle, yoksa ekle
    for idx, existing in enumerate(tasks):
        if existing["id"] == task.id:
            tasks[idx] = task.model_dump()
            db["tasks"] = tasks
            save_db(db)
            return task
            
    tasks.append(task.model_dump())
    db["tasks"] = tasks
    save_db(db)
    return task

def update_task(task_id: str, updated_task: Task) -> Optional[Task]:
    db = load_db()
    tasks = db.get("tasks", [])
    for idx, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks[idx] = updated_task.model_dump()
            db["tasks"] = tasks
            save_db(db)
            return updated_task
    return None

def delete_task(task_id: str) -> bool:
    db = load_db()
    tasks = db.get("tasks", [])
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == original_len:
        return False
    db["tasks"] = tasks
    
    # Silinen görevi aktif plandan temizle
    schedule = db.get("schedule", {})
    slots = schedule.get("slots", [])
    new_slots = []
    for slot in slots:
        if slot.get("task_id") == task_id:
            slot["task_id"] = None
            slot["task_title"] = "Boş Zaman (Görevi Sildiniz)"
            slot["is_break"] = True
        new_slots.append(slot)
    schedule["slots"] = new_slots
    
    # Planlanmamış işlerden de temizle
    unassigned = schedule.get("unassigned_tasks", [])
    schedule["unassigned_tasks"] = [t for t in unassigned if t["id"] != task_id]
    
    db["schedule"] = schedule
    save_db(db)
    return True

def get_schedule() -> Schedule:
    db = load_db()
    return Schedule(**db.get("schedule", {}))

def save_schedule(schedule: Schedule):
    db = load_db()
    db["schedule"] = schedule.model_dump()
    save_db(db)

def reset_db():
    default_db = {
        "tasks": [],
        "schedule": {
            "slots": [],
            "unassigned_tasks": [],
            "insights": ""
        }
    }
    save_db(default_db)
