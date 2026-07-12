# 📅 AI Agent Tabanlı Kişisel Planlama Asistanı

Günlük görevlerinizi analiz eden, önceliklerine göre sıralayan, çalışma saatlerinize uygun akıllı bir zaman planı oluşturan ve gün içindeki değişimlere göre **yapay zeka** ile dinamik olarak yeniden yapılandıran kişisel planlama asistanı.

> **Desteklenen AI Motorları:** Google Gemini (`gemini-1.5-flash`) · Groq (`llama-3.3-70b-versatile`)

---

## 🗂️ Proje Yapısı

```text
personal-ai-planner/
│
├── backend/
│   ├── agent.py         # Gemini / Groq API entegrasyonu
│   ├── prompts.py       # AI sistem yönergeleri (Türkçe)
│   ├── models.py        # Pydantic veri modelleri
│   ├── planner.py       # JSON tabanlı yerel veritabanı (tasks_db.json)
│   ├── config.py        # Çevre değişkenleri yapılandırması
│   └── requirements.txt
│
├── frontend/
│   ├── app.py           # Streamlit arayüzü (karanlık/aydınlık tema)
│   └── requirements.txt
│
├── requirements.txt     # Kök dizin (Streamlit Cloud için)
├── .env                 # API anahtarları (git'e eklenmez!)
├── .gitignore
└── README.md
```

---

## ⚙️ Kurulum

### 1. Depoyu klonlayın
```bash
git clone https://github.com/kullanici/personal-ai-planner.git
cd personal-ai-planner
```

### 2. Sanal ortam oluşturun
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 4. `.env` dosyasını doldurun
Kök dizinde bulunan `.env` dosyasını açın ve anahtarlarınızı ekleyin:

```env
# "gemini" veya "groq"
AI_PROVIDER=gemini

GEMINI_API_KEY=AIzaSy...       # Google AI Studio'dan alın
GROQ_API_KEY=gsk_...           # console.groq.com'dan alın
```

---

## 🚀 Uygulamayı Çalıştırma

```bash
streamlit run frontend/app.py
```

Tarayıcınızda **http://localhost:8501** adresi otomatik açılır.

---

## 🌐 Streamlit Community Cloud'a Canlıya Alma

1. Projeyi GitHub'a yükleyin.
2. [share.streamlit.io](https://share.streamlit.io) → **Create App**
3. Şu ayarları seçin:
   - **Repository:** `kullanici/personal-ai-planner`
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`
4. **Advanced Settings → Secrets** bölümüne girin:
   ```toml
   AI_PROVIDER = "gemini"
   GEMINI_API_KEY = "AIzaSy..."
   GROQ_API_KEY = "gsk_..."
   ```
5. **Deploy** butonuna tıklayın.

---

## 🎯 Özellikler

| Özellik | Açıklama |
|---|---|
| Görev Yönetimi | Öncelik (Yüksek/Orta/Düşük), süre, son teslim tarihi |
| AI Planlama | Gemini veya Groq ile otomatik günlük zaman çizelgesi |
| Dinamik Düzenleme | "Toplantı ekle", "30 dk ertele" gibi doğal dil komutları |
| Tema Seçici | Karanlık / Aydınlık mod geçişi |
| API Güvenliği | API anahtarları kullanıcıdan tamamen gizli, sadece `.env`'den okunur |
| Veri Kalıcılığı | `tasks_db.json` ile oturum kapanınca veriler kaybolmaz |
