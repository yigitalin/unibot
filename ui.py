import requests
import streamlit as st

SERVER_ROOT = "http://127.0.0.1:8000"
SPACE_URL = f"{SERVER_ROOT}/knowledge-bases"
QUERY_URL = f"{SERVER_ROOT}/chat"

st.set_page_config(page_title="UniBot", page_icon="🎓", layout="wide")

if "active_space" not in st.session_state:
    st.session_state.active_space = None
if "space_snapshot" not in st.session_state:
    st.session_state.space_snapshot = None
if "dialog_cards" not in st.session_state:
    st.session_state.dialog_cards = []
if "draft_question" not in st.session_state:
    st.session_state.draft_question = ""

st.markdown(
    """
    <style>
    /* ÜSTTEKİ SİYAH BARI VE MENÜYÜ TAMAMEN GİZLEME */
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    #MainMenu {display: none !important;}
    footer {display: none !important;}

    /* SAYFANIN KAYMASINI (SCROLL) GÜVENLİ ŞEKİLDE ENGELLEME */
    [data-testid="stAppViewContainer"] {
        overflow-y: hidden !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(73, 87, 255, 0.10), transparent 18%),
            radial-gradient(circle at 82% 12%, rgba(68, 211, 255, 0.08), transparent 14%),
            linear-gradient(180deg, #0a0f1d 0%, #0b1020 52%, #090d18 100%);
        color: #f3f6ff;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    .hero-zone {
        position: relative;
        padding-top: 2rem; 
        padding-bottom: 2rem;
        display: block; 
    }

    .hero-zone::before {
        content: "";
        position: absolute;
        inset: 0;
        background-image:
            radial-gradient(rgba(255,255,255,0.16) 1px, transparent 1px),
            radial-gradient(rgba(130,160,255,0.10) 1px, transparent 1px);
        background-size: 120px 120px, 210px 210px;
        background-position: 10px 30px, 80px 120px;
        pointer-events: none;
        opacity: 0.38;
    }

    .main-stack {
        position: relative;
        z-index: 1;
        width: min(700px, 100%);
        margin: 0 auto;
    }

    .hero-title {
        color: #f2f5ff;
        font-size: 3.2rem;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.04em;
        text-align: center;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        color: #9da8c7;
        font-size: 1.08rem;
        text-align: center;
        margin-bottom: 1.35rem;
    }

    .answer-card {
        width: 100%;
        background: rgba(21, 27, 46, 0.90);
        border: 1px solid rgba(110, 125, 170, 0.18);
        border-radius: 22px;
        padding: 22px 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.34);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }

    .answer-label {
        color: #6e8dff;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .answer-text {
        color: #eff3ff;
        font-size: 1.04rem;
        line-height: 1.8;
    }

    .side-panel {
        background: rgba(16, 21, 38, 0.88);
        border: 1px solid rgba(110, 125, 170, 0.14);
        border-radius: 28px;
        padding: 20px;
        min-height: auto;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
    }

    .side-eyebrow {
        color: #7f93ff;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .side-title {
        color: #f3f6ff;
        font-size: 1.22rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.55rem;
    }

    .side-copy {
        color: #98a5ca;
        font-size: 0.92rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .upload-tip {
        color: #cfd7f4;
        background: rgba(109, 126, 255, 0.08);
        border: 1px solid rgba(109, 126, 255, 0.16);
        border-radius: 16px;
        padding: 12px 14px;
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 1rem;
    }

    .side-heading {
        color: #7f93ff;
        font-size: 0.86rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        margin-top: 1.2rem;
    }

    .file-pill {
        border: 1px solid rgba(126, 140, 192, 0.16);
        background: rgba(255, 255, 255, 0.02);
        border-radius: 14px;
        padding: 10px 14px;
        margin-bottom: 8px;
        color: #dce3ff;
        line-height: 1.4;
        font-size: 0.9rem;
    }

    .question-hint {
        color: #98a5ca;
        font-size: 0.82rem;
        line-height: 1.4;
        margin-bottom: 10px;
        padding-left: 10px;
        border-left: 2px solid rgba(127, 147, 255, 0.3);
    }

    .status-line {
        color: #98a5ca;
        font-size: 0.95rem;
        margin-top: 0.35rem;
    }

    .stTextInput label, .stFileUploader label {
        color: #cfd7f4 !important;
    }

    .stTextInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #f2f5ff !important;
        border: 1px solid rgba(126, 140, 192, 0.15) !important;
        border-radius: 16px !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px dashed rgba(126, 140, 192, 0.28);
        border-radius: 18px;
    }

    div[data-testid="stFileUploaderDropzone"] button {
        visibility: hidden;
        position: relative;
    }

    div[data-testid="stFileUploaderDropzone"] button::after {
        content: "Dosya seç";
        visibility: visible;
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(126, 140, 192, 0.28);
        border-radius: 12px;
        background: rgba(18, 24, 42, 0.95);
        color: #f2f5ff;
        font-weight: 700;
    }

    div[data-testid="stFileUploaderDropzone"] [data-testid="stFileUploaderDropzoneInstructions"] > div:first-child,
    div[data-testid="stFileUploaderDropzone"] small {
        visibility: hidden;
        position: relative;
    }

    div[data-testid="stFileUploaderDropzone"] [data-testid="stFileUploaderDropzoneInstructions"] > div:first-child::after {
        content: "PDF dosyalarını buraya sürükleyip bırak";
        visibility: visible;
        position: absolute;
        inset: 0;
        color: #f2f5ff;
        font-weight: 600;
    }

    div[data-testid="stFileUploaderDropzone"] small::after {
        content: "En fazla 200 MB, yalnızca PDF";
        visibility: visible;
        position: absolute;
        inset: 0;
        color: #98a5ca;
    }

    .stButton > button {
        border: none;
        border-radius: 999px;
        color: white;
        font-weight: 700;
        background: linear-gradient(135deg, #4d6bff, #7b4dff);
        box-shadow: 0 10px 30px rgba(84, 104, 255, 0.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

outer_left, main_col, gutter_col, side_col, outer_right = st.columns(
    [0.18, 1.65, 0.08, 0.72, 0.12],
    gap="medium",
)

with side_col:
    st.markdown('<div class="side-panel">', unsafe_allow_html=True)
    st.markdown('<div class="side-eyebrow">İstanbul Okan Üniversitesi</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-title">UniBot İçin Belgeleri Yükle</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-copy">Bu alan; staj, burs, Erasmus, yandal, ÇAP ve mezuniyet koşulları gibi öğrenci süreçlerine ait PDF belgeleri yüklemek için kullanılır.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="upload-tip">Belgelerde cevap yoksa UniBot seni İstanbul Okan Üniversitesi resmi web sitesine yönlendirir.</div>',
        unsafe_allow_html=True,
    )

    area_name = st.text_input(
        "Alan adı",
        value=st.session_state.space_snapshot["label"] if st.session_state.space_snapshot else "",
        placeholder="Örnek: Okan Akademik Rehber",
    )
    incoming_files = st.file_uploader(
        "PDF dosyaları",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("Belgeleri Hazırla", use_container_width=True):
        if not incoming_files:
            st.warning("En az bir PDF seç.")
        else:
            multipart_payload = [("files", (doc.name, doc.getvalue(), "application/pdf")) for doc in incoming_files]
            form_fields = {"label": area_name or "UniBot Paketi"}
            with st.spinner("İşleniyor..."):
                try:
                    res = requests.post(SPACE_URL, files=multipart_payload, data=form_fields, timeout=240)
                    res.raise_for_status()
                    st.session_state.space_snapshot = res.json()
                    st.session_state.active_space = st.session_state.space_snapshot["space_id"]
                    st.session_state.dialog_cards = []
                    st.success("Hazır.")
                    st.rerun()
                except Exception as e: st.error(f"Hata: {e}")

    # İLHAM VERİCİ SORULAR (SOL PANEL)
    st.markdown('<div class="side-heading">İlham Alabileceğin Sorular</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-hint">• Başarı bursu nedir ve kimlere verilir?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-hint">• Burslar hangi durumlarda kesilir?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-hint">• ÇAP yapmanın şartları nelerdir?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-hint">• Mezuniyet için kaç AKTS tamamlanmalıdır?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-hint">• Erasmus not ortalaması (GPA) kaç olmalı?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question-hint">• Staj başvurusu için hangi belgeler gerekir?</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-heading">Yüklenen Belgeler</div>', unsafe_allow_html=True)
    if st.session_state.space_snapshot:
        for saved_name in st.session_state.space_snapshot["files"]:
            st.markdown(f'<div class="file-pill">{saved_name}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="file-pill">Dosya bulunamadı.</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with main_col:
    st.markdown('<div class="hero-zone"><div class="main-stack">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">UniBot&apos;a Hoş Geldiniz</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">İstanbul Okan Üniversitesi öğrenci bilgi asistanı</div>', unsafe_allow_html=True)

    latest_reply = st.session_state.dialog_cards[0]["reply"] if st.session_state.dialog_cards else None

    if latest_reply:
        st.markdown(f'<div class="answer-card"><div class="answer-label">Yanıt</div><div class="answer-text">{latest_reply}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="answer-card"><div class="answer-label">Yanıt</div><div class="answer-text">Belgelerini yükledikten sonra burada son yanıt görünecek.</div></div>', unsafe_allow_html=True)

    composer_left, composer_right = st.columns([8.7, 1.3], gap="small")
    with composer_left:
        st.session_state.draft_question = st.text_input("Sorunu yaz", value=st.session_state.draft_question, label_visibility="collapsed", placeholder="Soru sor...")
    with composer_right:
        if st.button("Gönder", use_container_width=True, disabled=st.session_state.active_space is None):
            if st.session_state.draft_question.strip():
                with st.spinner("..."):
                    try:
                        res = requests.post(QUERY_URL, json={"space_id": st.session_state.active_space, "prompt": st.session_state.draft_question}, timeout=180)
                        res.raise_for_status()
                        st.session_state.dialog_cards.insert(0, {"prompt": st.session_state.draft_question, "reply": res.json()["answer"]})
                        st.session_state.draft_question = ""
                        st.rerun()
                    except Exception as e: st.error("Sorgu hatası.")

    if st.session_state.active_space is None:
        st.markdown('<div class="ghost-note">Soru sormak için sağdaki panelden belgeleri eklemelisin.</div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)