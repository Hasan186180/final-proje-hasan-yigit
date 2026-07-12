import os
from dotenv import load_dotenv

# Projenin kök dizinindeki .env dosyasını yükle
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

# Aktif AI sağlayıcısı: "gemini" veya "groq"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

# API Anahtarları
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
