from pydantic import BaseModel, Field
from typing import List, Optional

class Task(BaseModel):
    id: str = Field(..., description="Görevin benzersiz kimliği (UUID veya benzersiz string)")
    title: str = Field(..., description="Görevin başlığı")
    description: Optional[str] = Field(None, description="Görevin açıklaması")
    duration: int = Field(..., description="Görevin tahmini süresi (dakika olarak)")
    priority: str = Field("orta", description="Önem derecesi: 'yuksek', 'orta', 'dusuk'")
    deadline: Optional[str] = Field(None, description="Görevin son teslim/tamamlanma saati (örn: '17:00' veya '2026-07-12 18:00')")
    status: str = Field("beklemede", description="Görevin durumu: 'beklemede', 'tamamlandi'")

class WorkingHours(BaseModel):
    start_time: str = Field("09:00", description="Mesai başlangıç saati (örn: '09:00')")
    end_time: str = Field("17:00", description="Mesai bitiş saati (örn: '17:00')")

class ScheduleSlot(BaseModel):
    start_time: str = Field(..., description="Zaman dilimi başlangıcı (örn: '09:00')")
    end_time: str = Field(..., description="Zaman dilimi bitişi (örn: '10:00')")
    task_id: Optional[str] = Field(None, description="Bu dilimde yapılacak görevin ID'si (boşsa mola/boş vakittir)")
    task_title: str = Field(..., description="Görevin başlığı veya 'Mola / Dinlenme' açıklaması")
    is_break: bool = Field(False, description="Bu zaman diliminin mola/dinlenme olup olmadığı")

class Schedule(BaseModel):
    slots: List[ScheduleSlot] = Field(default=[], description="Planlanmış zaman dilimleri")
    unassigned_tasks: List[Task] = Field(default=[], description="Planlamaya sığmayan veya ertelenen görevler")
    insights: str = Field("", description="AI planlama asistanının tavsiyeleri, yorumları ve günlük değerlendirmesi")

class GenerateScheduleRequest(BaseModel):
    tasks: List[Task] = Field(..., description="Planlanacak görevlerin listesi")
    working_hours: WorkingHours = Field(default_factory=WorkingHours, description="Çalışma saatleri")

class RearrangeRequest(BaseModel):
    tasks: List[Task] = Field(..., description="Tüm görevlerin listesi")
    current_schedule: Schedule = Field(..., description="Mevcut zaman planı")
    prompt: str = Field(..., description="Kullanıcının planı yeniden düzenleme talebi (örn: '1 saat geç başlayacağım', 'Önemli toplantı ekle')")
    working_hours: WorkingHours = Field(default_factory=WorkingHours, description="Çalışma saatleri")
