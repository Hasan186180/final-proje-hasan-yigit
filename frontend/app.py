import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import uuid
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from backend import planner as db
from backend import agent
from backend.models import Task, WorkingHours, Schedule
from backend.config import AI_PROVIDER

# ── Sayfa Yapılandırması ────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Kişisel Planlama Asistanı",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dm = st.session_state.dark_mode

# ── Renk Paleti ─────────────────────────────────────────────────────────────
if dm:
    BG     = "#0f172a"
    BG2    = "#1e293b"
    BG3    = "#334155"
    BORDER = "#334155"
    T1     = "#f1f5f9"
    T2     = "#94a3b8"
    T3     = "#64748b"
    INPUT  = "#000000"
    SHADOW = "0 4px 14px rgba(0,0,0,0.4)"
    INSIGHT_BG  = "rgba(99,102,241,0.15)"
    INSIGHT_BOR = "rgba(168,85,247,0.35)"
    UNASS_BG    = "#1a1000"
    BTN_TXT     = "#f1f5f9"
    BTN_BG      = "#1e293b"
    BTN_BORDER  = "#334155"
    
    # Rozet Renkleri
    BADGE_YUKSEK_BG  = "rgba(239, 68, 68, 0.2)"
    BADGE_YUKSEK_TXT = "#ff8787"
    BADGE_ORTA_BG    = "rgba(245, 158, 11, 0.2)"
    BADGE_ORTA_TXT   = "#ffd43b"
    BADGE_DUSUK_BG   = "rgba(16, 185, 129, 0.2)"
    BADGE_DUSUK_TXT  = "#63e6be"
    BADGE_TAMAM_BG   = "rgba(2, 132, 199, 0.2)"
    BADGE_TAMAM_TXT  = "#66d9e8"
    BADGE_BEKLE_BG   = "rgba(148, 163, 184, 0.2)"
    BADGE_BEKLE_TXT  = "#c1c9d2"
else:
    BG     = "#f8fafc"
    BG2    = "#ffffff"
    BG3    = "#f1f5f9"
    BORDER = "#e2e8f0"
    T1     = "#1e293b"
    T2     = "#475569"
    T3     = "#94a3b8"
    INPUT  = "#ffffff"
    SHADOW = "0 4px 12px rgba(0,0,0,0.06)"
    INSIGHT_BG  = "rgba(99,102,241,0.06)"
    INSIGHT_BOR = "rgba(168,85,247,0.22)"
    UNASS_BG    = "#fffbeb"
    BTN_TXT     = "#1e293b"
    BTN_BG      = "#ffffff"
    BTN_BORDER  = "#e2e8f0"
    
    # Rozet Renkleri
    BADGE_YUKSEK_BG  = "#fee2e2"
    BADGE_YUKSEK_TXT = "#ef4444"
    BADGE_ORTA_BG    = "#fef3c7"
    BADGE_ORTA_TXT   = "#d97706"
    BADGE_DUSUK_BG   = "#d1fae5"
    BADGE_DUSUK_TXT  = "#059669"
    BADGE_TAMAM_BG   = "#e0f2fe"
    BADGE_TAMAM_TXT  = "#0284c7"
    BADGE_BEKLE_BG   = "#f1f5f9"
    BADGE_BEKLE_TXT  = "#64748b"

# ── CSS'i JavaScript ile <head>'e enjekte et (Streamlit CSS'inden sonra gelir) ──
THEME_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* ===== TEMEL ARKA PLAN ===== */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.main, section.main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {BG} !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ===== HEADER ===== */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{
    background-color: {BG} !important;
    border-bottom: 1px solid {BORDER} !important;
}}

/* ===== SİDEBAR ===== */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {{
    background-color: {BG2} !important;
    border-right: 1px solid {BORDER} !important;
}}

/* ===== TÜM METİNLER ===== */
html body p,
html body span:not(.badge),
html body label,
html body div:not(.badge):not(.stButton),
html body h1, html body h2, html body h3,
html body h4, html body h5, html body h6,
html body li, html body a,
html body .stMarkdown,
html body .stMarkdown p,
html body [data-testid="stMarkdownContainer"]:not(.badge),
html body [data-testid="stMarkdownContainer"] p:not(.badge),
html body [data-testid="stMarkdownContainer"] span:not(.badge),
html body [data-testid="stMarkdownContainer"] li,
html body [data-testid="stCaptionContainer"],
html body [data-testid="stText"] {{
    color: {T1} !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ===== BUTONLAR ===== */
html body .stButton > button {{
    background-color: {BTN_BG} !important;
    color: {BTN_TXT} !important;
    border: 1px solid {BTN_BORDER} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
html body .stButton > button * {{
    color: inherit !important;
    background-color: transparent !important;
}}
html body .stButton > button:hover {{
    border-color: #6366f1 !important;
    background-color: {BG3} !important;
    color: {T1} !important;
}}
html body .stButton > button:hover * {{
    color: {T1} !important;
}}
html body .stButton > button[kind="primary"],
html body .stButton > button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}}
html body .stButton > button[kind="primary"] *,
html body .stButton > button[data-testid="baseButton-primary"] * {{
    color: #ffffff !important;
}}
html body .stButton > button[kind="primary"]:hover,
html body .stButton > button[data-testid="baseButton-primary"]:hover {{
    background: linear-gradient(135deg, #4338ca, #6d28d9) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.45) !important;
}}
html body .stButton > button[kind="secondary"],
html body .stButton > button[data-testid="baseButton-secondary"] {{
    background-color: {BG2} !important;
    color: {T1} !important;
    border: 1px solid {BORDER} !important;
}}

/* ===== INPUT ALANLARI ===== */
html body .stTextInput input,
html body .stTextInput > div > div > input,
html body .stTextArea textarea,
html body .stTextArea > div > div > textarea,
html body .stNumberInput input,
html body [data-baseweb="input"] input,
html body [data-baseweb="textarea"] textarea,
html body [data-baseweb="base-input"] input {{
    background-color: {INPUT} !important;
    color: {T1} !important;
    border-color: {BORDER} !important;
    font-family: 'Outfit', sans-serif !important;
}}
html body .stTextInput > div > div,
html body .stTextArea > div > div,
html body [data-baseweb="input"],
html body [data-baseweb="textarea"] {{
    background-color: {INPUT} !important;
    border-color: {BORDER} !important;
}}

/* ===== SELECTBOX ===== */
html body div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
    background-color: {INPUT} !important;
    border-color: {BORDER} !important;
    border-radius: 8px !important;
}}
html body div[data-testid="stSelectbox"] div[data-baseweb="select"] * {{
    background-color: transparent !important;
    color: {T1} !important;
}}
/* Dropdown popup listesi */
html body [data-baseweb="popover"],
html body [data-baseweb="popover"] *,
html body [data-baseweb="popover"] > div,
html body [data-baseweb="menu"],
html body ul[role="listbox"],
html body li[role="option"],
html body [role="option"] {{
    background-color: {BG2} !important;
    color: {T1} !important;
    border-color: {BORDER} !important;
}}
html body li[role="option"]:hover,
html body [role="option"]:hover,
html body li[role="option"][aria-selected="true"],
html body [role="option"][aria-selected="true"] {{
    background-color: {BG3} !important;
    color: {T1} !important;
}}

/* ===== NUMBER INPUT ===== */
html body div[data-testid="stNumberInputContainer"] {{
    background-color: {INPUT} !important;
    border-color: {BORDER} !important;
}}
html body div[data-testid="stNumberInputContainer"] input {{
    background-color: transparent !important;
    color: {T1} !important;
}}
html body div[data-testid="stNumberInputContainer"] button {{
    background-color: {BG3} !important;
    color: {T1} !important;
    border: 1px solid {BORDER} !important;
}}
html body div[data-testid="stNumberInputContainer"] button:hover {{
    background-color: {BG2} !important;
    border-color: #6366f1 !important;
}}
html body div[data-testid="stNumberInputContainer"] button svg,
html body div[data-testid="stNumberInputContainer"] button svg * {{
    fill: {T1} !important;
    stroke: {T1} !important;
    color: {T1} !important;
}}

/* ===== TABS ===== */
html body [data-baseweb="tab-list"],
html body .stTabs [data-baseweb="tab-list"] {{
    background-color: {BG} !important;
    border-bottom: 2px solid {BORDER} !important;
    gap: 4px !important;
}}
html body .stTabs [data-baseweb="tab"] {{
    background-color: transparent !important;
    color: {T2} !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px 8px 0 0 !important;
}}
html body .stTabs [aria-selected="true"] {{
    background-color: {BG2} !important;
    color: #818cf8 !important;
    border-bottom: 3px solid #6366f1 !important;
}}
html body [data-testid="stTabsContent"],
html body [data-baseweb="tab-panel"] {{
    background-color: {BG} !important;
}}

/* ===== ALERT / INFO / WARNING ===== */
html body [data-testid="stAlert"] {{
    background-color: {BG2} !important;
    border-color: {BORDER} !important;
    color: {T1} !important;
}}
html body [data-testid="stAlert"] p,
html body [data-testid="stAlert"] span {{
    color: {T1} !important;
}}

/* ===== DIVIDER ===== */
html body hr {{
    border-color: {BORDER} !important;
    opacity: 0.5 !important;
}}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BG3}; border-radius: 4px; }}

/* ===== ÖZEL BİLEŞENLER ===== */
.header-container {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #db2777 100%);
    padding: 2.2rem 2.5rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 12px 30px -5px rgba(79,70,229,0.45);
    position: relative;
    overflow: hidden;
}}
.header-container * {{ color: #ffffff !important; }}
.header-container::before {{
    content: '';
    position: absolute;
    top: -60%; left: -60%;
    width: 220%; height: 220%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 55%);
    animation: spinBg 25s linear infinite;
}}
@keyframes spinBg {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
.header-title    {{ font-size: 2.2rem; font-weight: 700; margin: 0; padding-bottom: 0.35rem; }}
.header-subtitle {{ font-size: 1rem; font-weight: 300; opacity: 0.88; margin: 0; }}

.task-card {{
    background: {BG2} !important;
    border-radius: 16px;
    border: 1px solid {BORDER};
    padding: 1.1rem 1.2rem 1.1rem 1.55rem;
    margin-bottom: 0.8rem;
    box-shadow: {SHADOW};
    position: relative;
    transition: transform 0.22s, box-shadow 0.22s, border-color 0.22s;
}}
.task-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 24px rgba(99,102,241,0.18);
    border-color: #818cf8;
}}
.task-title {{ color: {T1} !important; font-size: 1.1rem; font-weight: 600; }}
.task-desc  {{ color: {T2} !important; font-size: 0.92rem; margin: 7px 0 5px; }}
.task-meta  {{ color: {T3} !important; font-size: 0.82rem; font-weight: 500; }}

.priority-bar {{
    position: absolute; left: 0; top: 0; bottom: 0; width: 6px;
    border-top-left-radius: 16px; border-bottom-left-radius: 16px;
}}
.pb-yuksek {{ background: linear-gradient(180deg,#ef4444,#f87171); }}
.pb-orta   {{ background: linear-gradient(180deg,#f59e0b,#fbbf24); }}
.pb-dusuk  {{ background: linear-gradient(180deg,#10b981,#34d399); }}

html body span.badge {{
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    padding: 3px 9px !important;
    border-radius: 20px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.4px !important;
    display: inline-block !important;
}}
html body span.badge.b-yuksek     {{ background-color: {BADGE_YUKSEK_BG} !important; color: {BADGE_YUKSEK_TXT} !important; }}
html body span.badge.b-orta       {{ background-color: {BADGE_ORTA_BG} !important; color: {BADGE_ORTA_TXT} !important; }}
html body span.badge.b-dusuk      {{ background-color: {BADGE_DUSUK_BG} !important; color: {BADGE_DUSUK_TXT} !important; }}
html body span.badge.b-tamamlandi {{ background-color: {BADGE_TAMAM_BG} !important; color: {BADGE_TAMAM_TXT} !important; }}
html body span.badge.b-beklemede  {{ background-color: {BADGE_BEKLE_BG} !important; color: {BADGE_BEKLE_TXT} !important; }}

.timeline-wrap {{
    background: {BG2} !important;
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 1.5rem 1rem;
    margin-top: 1.2rem;
}}
.timeline {{ position: relative; max-width: 900px; margin: 0 auto; }}
.timeline::after {{
    content: ''; position: absolute;
    width: 4px; background: linear-gradient(180deg,#6366f1,#a855f7,{BG3});
    top: 0; bottom: 0; left: 140px; margin-left: -2px; border-radius: 2px;
}}
.tl-item {{ padding: 1.05rem 0; position: relative; display: flex; align-items: center; }}
.tl-time {{ width:120px; min-width:120px; text-align:right; padding-right:25px; font-weight:700; font-size:0.87rem; color:{T2} !important; line-height:1.4; }}
.tl-dot {{
    position:absolute; width:15px; height:15px; left:140px;
    background:{BG2}; border:4px solid {BG3}; border-radius:50%; z-index:2;
    transform:translateX(-50%); box-shadow:0 0 0 3px {BG}; transition:all 0.2s;
}}
.tl-active .tl-dot {{ border-color:#a855f7; background:#a855f7; box-shadow:0 0 0 3px {BG}, 0 0 14px rgba(168,85,247,0.55); }}
.tl-card {{
    margin-left:24px; flex-grow:1; background:{BG2} !important;
    border-left:5px solid {BG3}; border-radius:13px;
    padding:1rem 1.3rem; box-shadow:{SHADOW}; transition:transform 0.2s;
}}
.tl-card:hover {{ transform:scale(1.01); }}
.tl-card-title {{ color:{T1} !important; font-size:1.06rem; font-weight:600; }}
.tl-card-desc  {{ color:{T2} !important; font-size:0.86rem; margin:4px 0 0; }}
.tl-yuksek .tl-card {{ border-left-color:#ef4444; }}
.tl-yuksek .tl-dot  {{ border-color:#ef4444; }}
.tl-orta   .tl-card {{ border-left-color:#f59e0b; }}
.tl-orta   .tl-dot  {{ border-color:#f59e0b; }}
.tl-dusuk  .tl-card {{ border-left-color:#10b981; }}
.tl-dusuk  .tl-dot  {{ border-color:#10b981; }}
.tl-break  .tl-card {{ background:{BG3} !important; border-left-color:{T3}; }}
.tl-break  .tl-dot  {{ border-color:{T3}; background:{BG2}; }}

.insight-card {{
    background:{INSIGHT_BG}; border:1px solid {INSIGHT_BOR};
    border-radius:18px; padding:1.5rem 1.75rem; margin:1.2rem 0 1.5rem;
}}
.insight-label {{ font-size:1.15rem; font-weight:700; color:#818cf8 !important; }}
.insight-text  {{ font-size:0.96rem; line-height:1.65; color:{T2} !important; font-style:italic; }}

.unass-card {{
    background:{UNASS_BG}; border:1px solid #f59e0b40;
    border-left:4px solid #f59e0b; padding:11px 18px;
    border-radius:12px; margin-bottom:10px;
}}
.unass-title {{ color:#fbbf24 !important; font-weight:600; }}
.unass-meta  {{ color:#fcd34d !important; font-size:0.83rem; margin:4px 0 0; }}
"""

# JavaScript ile CSS'i parent window'un <head>'ine enjekte et
# Bu Streamlit'in kendi CSS'inden SONRA yüklenir → her zaman kazanır
_css_escaped = THEME_CSS.replace('`', r'\`').replace('${', r'\${')
components.html(f"""
<script>
(function() {{
    var existing = window.parent.document.getElementById('app-custom-theme');
    if (existing) existing.remove();
    var style = window.parent.document.createElement('style');
    style.id = 'app-custom-theme';
    style.textContent = `{_css_escaped}`;
    window.parent.document.head.appendChild(style);
}})();
</script>
""", height=0, scrolling=False)

# ── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
  <div class="header-title">📅 AI Kişisel Planlama Asistanı</div>
  <div class="header-subtitle">
    Görevlerinizi önceliklendirin · Akıllı günlük plan oluşturun · Gününüzü dinamik olarak yönetin
  </div>
</div>
""", unsafe_allow_html=True)

# ── SİDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 Tema")
    btn_lbl = "☀️  Aydınlık Moda Geç" if dm else "🌙  Karanlık Moda Geç"
    if st.button(btn_lbl, use_container_width=True, key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.caption("Aktif: **{}**".format("🌙 Karanlık Mod" if dm else "☀️ Aydınlık Mod"))

    st.markdown("---")
    st.markdown("### ⏰ Çalışma Saatleri")
    start_h = st.text_input("Başlangıç", value="09:00", key="start_h")
    end_h   = st.text_input("Bitiş",     value="18:00", key="end_h")
    working_hours = {"start_time": start_h, "end_time": end_h}

    st.markdown("---")
    provider_label = "🔷 Google Gemini" if AI_PROVIDER == "gemini" else "⚡ Groq (LLaMA 3.3)"
    st.markdown(f"**AI Motoru:** {provider_label}")

    st.markdown("---")
    st.markdown("### 🗑️ Sıfırlama")
    if st.button("Tüm Verileri Sıfırla", type="secondary", use_container_width=True):
        db.reset_db()
        st.success("Tüm veriler silindi!")
        st.rerun()

# ── SEKMELER ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📋  Görev Yönetimi",
    "🕒  Günlük Zaman Planı",
    "🔮  AI Asistan & Dinamik Düzenleme"
])

# ════════ SEKME 1 ════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### ➕ Yeni Görev Ekle")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        title    = st.text_input("Görev Başlığı *", placeholder="Rapor yaz, Toplantı hazırla…", key="nt")
        desc     = st.text_area("Açıklama (İsteğe Bağlı)", placeholder="Detaylar…", key="nd")
    with c2:
        duration = st.number_input("Tahmini Süre (Dakika)", min_value=5, max_value=480, value=30, step=5, key="ndur")
        priority = st.selectbox("Önem Derecesi", ["yuksek","orta","dusuk"],
            format_func=lambda x: {"yuksek":"🔴 Yüksek","orta":"🟡 Orta","dusuk":"🟢 Düşük"}[x], key="np")
        deadline = st.text_input("Son Teslim Saati", placeholder="17:00", key="ndl")

    if st.button("✅  Görevi Kaydet", type="primary"):
        if not title.strip():
            st.error("Görev başlığı boş olamaz!")
        else:
            db.add_task(Task(
                id=str(uuid.uuid4())[:8], title=title.strip(),
                description=desc.strip() or None, duration=int(duration),
                priority=priority, deadline=deadline.strip() or None, status="beklemede"
            ))
            st.success("Görev eklendi!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Mevcut Görevler")

    tasks = db.get_all_tasks()
    if not tasks:
        st.info("Henüz görev yok. Yukarıdan ekleyin.")
    else:
        for t in tasks:
            td = t.model_dump()
            st.markdown(f"""
            <div class="task-card">
              <div class="priority-bar pb-{td['priority']}"></div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-left:8px">
                <span class="task-title">{td['title']}</span>
                <div>
                  <span class="badge b-{td['priority']}">{td['priority']}</span>&nbsp;
                  <span class="badge b-{td['status']}">{td['status']}</span>
                </div>
              </div>
              <div class="task-desc" style="margin-left:8px">{td['description'] or '<i>Açıklama yok</i>'}</div>
              <div class="task-meta" style="display:flex;gap:14px;margin-left:8px">
                <span>⏱️ {td['duration']} dk</span>
                {'<span>📅 '+td['deadline']+'</span>' if td['deadline'] else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)
            ca, cb, _ = st.columns([1,1,5])
            with ca:
                ns  = "tamamlandi" if td["status"]=="beklemede" else "beklemede"
                lbl = "Tamamla ✓" if td["status"]=="beklemede" else "Geri Al ↩"
                if st.button(lbl, key=f"st_{td['id']}", use_container_width=True):
                    t.status = ns; db.add_task(t); st.rerun()
            with cb:
                if st.button("Sil 🗑️", key=f"dl_{td['id']}", use_container_width=True):
                    db.delete_task(td['id']); st.rerun()
            st.markdown("<div style='margin-bottom:14px'></div>", unsafe_allow_html=True)

# ════════ SEKME 2 ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📅 Akıllı Günlük Planlama")
    col_btn, _ = st.columns([1,2])
    with col_btn:
        if st.button("🤖  AI Zaman Planı Oluştur", type="primary", use_container_width=True, key="gen_sch"):
            all_tasks = db.get_all_tasks()
            pending   = [t for t in all_tasks if t.status=="beklemede"]
            if not pending:
                st.warning("Bekleyen görev yok!")
            else:
                with st.spinner("AI Agent planınızı tasarlıyor…"):
                    try:
                        sch = agent.generate_schedule(all_tasks, WorkingHours(**working_hours))
                        db.save_schedule(sch)
                        st.success("Plan oluşturuldu!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI Hatası: {e}")

    st.markdown("---")
    schedule = db.get_schedule().model_dump()
    task_map = {t.id: t.model_dump() for t in db.get_all_tasks()}

    if not schedule.get("slots"):
        st.info("Henüz plan yok. Yukarıdaki butona tıklayın.")
    else:
        if schedule.get("insights"):
            st.markdown(f"""
            <div class="insight-card">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                <span style="font-size:1.35rem">💡</span>
                <span class="insight-label">AI Asistan Değerlendirmesi</span>
              </div>
              <div class="insight-text">"{schedule['insights']}"</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🕒 Zaman Çizelgesi")
        st.markdown('<div class="timeline-wrap"><div class="timeline">', unsafe_allow_html=True)

        for slot in schedule["slots"]:
            is_break = slot["is_break"]
            tid      = slot.get("task_id") or ""
            p_cls    = "break"; badges = ""; desc_txt = "Mola ve dinlenme süresi."
            if not is_break and tid in task_map:
                t = task_map[tid]
                p_cls  = t["priority"]
                badges = f"<span class='badge b-{t['priority']}'>{t['priority'].upper()}</span>"
                if t["status"]=="tamamlandi":
                    badges += " <span class='badge b-tamamlandi'>TAMAMLANDI ✓</span>"
                desc_txt = t.get("description") or "Açıklama yok."
            active = "tl-active" if not is_break else ""
            st.markdown(f"""
            <div class="tl-item tl-{p_cls} {active}">
              <div class="tl-time">{slot['start_time']}<br>{slot['end_time']}</div>
              <div class="tl-dot"></div>
              <div class="tl-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                  <span class="tl-card-title">{slot['task_title']}</span>
                  <div>{badges}</div>
                </div>
                <div class="tl-card-desc">{desc_txt}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

        for ut in schedule.get("unassigned_tasks",[]):
            st.markdown(f"""
            <div class="unass-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span class="unass-title">{ut['title']}</span>
                <span class="badge b-{ut['priority']}">{ut['priority']}</span>
              </div>
              <div class="unass-meta">⏱️ {ut['duration']} dk</div>
            </div>
            """, unsafe_allow_html=True)

# ════════ SEKME 3 ════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔮 AI Asistan ile Planı Yeniden Düzenle")
    st.markdown("Gün içinde bir şey değişti mi? Aşağıya yazın, AI Agent planı anında güncellesin.")

    st.markdown("#### ⚡ Hızlı İşlemler")
    qc1, qc2, qc3 = st.columns(3)
    quick = None
    with qc1:
        if st.button("🕒 30 Dak. Geciktim", use_container_width=True, key="q1"):
            quick = "Tüm kalan planı 30 dakika ileri kaydır."
    with qc2:
        if st.button("🚨 Acil Toplantı (14:00)", use_container_width=True, key="q2"):
            quick = "Saat 14:00'e 45 dakikalık acil 'Müşteri Değerlendirme Toplantısı' ekle ve planı güncelle."
    with qc3:
        if st.button("☕ Kahve Molası (15:30)", use_container_width=True, key="q3"):
            quick = "Saat 15:30'a 20 dakikalık kahve molası ekle, sonraki görevleri kaydır."

    if quick:
        st.session_state["ri"] = quick

    st.markdown("---")
    instruction = st.text_area("Kendi Talimatınızı Yazın",
        value=st.session_state.get("ri",""),
        placeholder="Örn: 'Rapor yazma görevini iptal et, yerine 30 dakikalık araştırma koy'",
        height=120, key="rta")

    if st.button("🤖  Planı Yeniden Düzenle", type="primary", key="rbtn"):
        if not instruction.strip():
            st.error("Lütfen bir talimat girin.")
        else:
            cur = db.get_schedule()
            if not cur.slots:
                st.warning("Önce 'Günlük Zaman Planı' sekmesinden bir plan oluşturun.")
            else:
                with st.spinner("AI Agent planı yeniden düzenliyor…"):
                    try:
                        new_sch = agent.rearrange_schedule(
                            db.get_all_tasks(), cur, instruction, WorkingHours(**working_hours)
                        )
                        db.save_schedule(new_sch)
                        st.session_state["ri"] = ""
                        st.success("Plan güncellendi! 'Günlük Zaman Planı' sekmesinden görebilirsiniz. 🎉")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Düzenleme Hatası: {e}")
