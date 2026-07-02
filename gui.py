# gui.py — Entry point Streamlit RestoEase
# Berisi HANYA kode UI Streamlit (st.*).
# Import dari services & storage — TIDAK langsung dari models.

import streamlit as st
import storage
import service
from datetime import datetime
from exceptions import (
    RestoEaseError,
    MenuTidakDitemukanError,
    MejaTidakTersediaError,
    PesananTidakAdaError,
    InputTidakValidError,
    ItemPesananTidakAdaError,
    UangKurangError,
)

# ============================================================
# KONFIGURASI HALAMAN & CSS
# ============================================================

st.set_page_config(
    page_title="RestoEase — Sistem Pemesanan Digital",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── FONT ── */
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz@1,9..144&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="st-"] { font-family: 'IBM Plex Sans', sans-serif !important; }
    .resto-display, h1, h2, h3, .section-title { font-family: 'Fraunces', serif !important; font-style: italic; }
    .resto-data, .meja-num { font-family: 'IBM Plex Mono', monospace !important; font-variant-numeric: tabular-nums; }

    /* Streamlit membulatkan semua container secara default — kecilkan agar sesuai konsep kertas */
    div[data-testid="stVerticalBlockBorderWrapper"],
    button[kind], .stButton>button {
        border-radius: 4px !important;
        box-shadow: none !important;
    }

    /* Sembunyikan chrome default Streamlit yang tidak relevan untuk software kasir */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── KELAS KUSTOM BERDASARKAN DESIGN.MD ── */
    :root {
        --bg-base: #171310;
        --bg-surface: #241E17;
        --bg-surface-raised: #2E271D;
        --accent-ember: #E2963A;
        --accent-ember-dim: #8A5A22;
        --ink-primary: #F3ECE0;
        --ink-muted: #C4B9AD;
        --ink-dim: #8F8577;
        --rule-hairline: rgba(243,236,224,0.15);
        --status-kosong: #6E8F6A;
        --status-terisi: #C1573B;
        --status-reserved: #C9A227;
        --paper: #EFE7D8;
        --paper-ink: #2A241C;
    }

    
    /* Target specifically the column containing ticket-rail-bg */
    div[data-testid="column"]:has(.ticket-rail-bg) {
        background-color: var(--paper) !important;
        color: var(--paper-ink) !important;
        border-radius: 4px !important;
        padding: 16px !important;
        mask-image: radial-gradient(circle at 10px 0px, transparent 10px, black 11px),
                    radial-gradient(circle at 10px 100%, transparent 10px, black 11px);
        mask-size: 20px 100%;
        mask-position: 0 0, 0 100%;
        mask-repeat: repeat-x;
    }
    
    div[data-testid="column"]:has(.ticket-rail-bg) * {
        color: var(--paper-ink) !important;
    }
    
    div[data-testid="column"]:has(.ticket-rail-bg) .stButton > button {
        border-color: var(--paper-ink) !important;
    }

    /* Ticket Rail (Cart) */
    .ticket-rail {
        background-color: var(--paper) !important;
        color: var(--paper-ink) !important;
        border-radius: 4px;
        padding: 16px;
        /* Perforasi bergerigi atas & bawah */
        mask-image: radial-gradient(circle at 10px 0px, transparent 10px, black 11px),
                    radial-gradient(circle at 10px 100%, transparent 10px, black 11px);
        mask-size: 20px 100%;
        mask-position: 0 0, 0 100%;
        mask-repeat: repeat-x;
    }
    .ticket-rail-header {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 12px;
        border-bottom: 1px solid var(--paper-ink);
        padding-bottom: 8px;
        color: var(--paper-ink);
    }
    .ticket-rail-item {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 14px;
        display: flex;
        justify-content: space-between;
        border-bottom: 1px dotted var(--paper-ink);
        margin-bottom: 8px;
        padding-bottom: 4px;
    }
    .ticket-rail-total {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 18px;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        margin-top: 12px;
        border-top: 2px solid var(--paper-ink);
        padding-top: 8px;
    }
    .empty-cart { text-align: center; padding: 48px 16px; color: var(--paper-ink); font-size: 0.9rem; }
    .empty-cart-icon { font-size: 14px; margin-bottom: 12px; color: var(--paper-ink); font-weight: 700; }

    /* Nota / Struk */
    .struk-container {
        max-width: 420px;
        margin: 0 auto;
        background-color: var(--paper);
        color: var(--paper-ink);
        padding: 28px 24px;
        font-family: 'IBM Plex Sans', sans-serif;
        border-radius: 8px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    }
    .struk-header {
        text-align: center;
        border-bottom: 2px dashed #c8bfa9;
        padding-bottom: 16px;
        margin-bottom: 16px;
    }
    .struk-header h2 {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 1.4rem;
        margin: 0 0 4px 0;
        color: var(--paper-ink);
    }
    .struk-header .struk-subtitle {
        font-size: 0.7rem;
        color: #8a8070;
        letter-spacing: 0.5px;
    }
    .struk-meta {
        font-size: 0.78rem;
        color: #6b6156;
        margin-bottom: 16px;
        line-height: 1.7;
    }
    .struk-meta span.struk-meta-label {
        display: inline-block;
        width: 110px;
        font-weight: 600;
        color: var(--paper-ink);
    }
    .struk-divider {
        border: none;
        border-top: 1px dashed #c8bfa9;
        margin: 14px 0;
    }
    .struk-items-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        margin-bottom: 4px;
    }
    .struk-items-table th {
        text-align: left;
        font-weight: 700;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #8a8070;
        padding: 4px 0;
        border-bottom: 1px solid #d9d0c2;
    }
    .struk-items-table th:last-child { text-align: right; }
    .struk-items-table td {
        padding: 6px 0;
        vertical-align: top;
        color: var(--paper-ink);
    }
    .struk-items-table td:last-child {
        text-align: right;
        font-family: 'IBM Plex Mono', monospace;
        white-space: nowrap;
    }
    .struk-items-table .item-qty {
        font-size: 0.72rem;
        color: #8a8070;
    }
    .struk-totals {
        font-size: 0.82rem;
        line-height: 2;
    }
    .struk-totals .struk-row {
        display: flex;
        justify-content: space-between;
    }
    .struk-totals .struk-row span:last-child {
        font-family: 'IBM Plex Mono', monospace;
    }
    .struk-totals .struk-grand-total {
        font-size: 1rem;
        font-weight: 700;
        color: var(--paper-ink);
        border-top: 2px solid var(--paper-ink);
        padding-top: 6px;
        margin-top: 4px;
    }
    .struk-footer {
        text-align: center;
        border-top: 2px dashed #c8bfa9;
        padding-top: 14px;
        margin-top: 16px;
        font-size: 0.75rem;
        color: #8a8070;
        line-height: 1.6;
    }

    
    /* Meja Grid Colors */
    .meja-kosong, .meja-terisi {
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        margin-bottom: 8px;
        font-family: 'IBM Plex Sans', sans-serif;
        height: 155px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-sizing: border-box;
    }
    .meja-kosong {
        background-color: rgba(110, 143, 106, 0.15);
        border: 2px solid var(--status-kosong);
    }
    .meja-terisi {
        background-color: rgba(193, 87, 59, 0.15);
        border: 2px solid var(--status-terisi);
    }
    .meja-num {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 8px 0;
        font-family: 'IBM Plex Mono', monospace;
        color: var(--ink-primary);
    }
    .meja-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--ink-muted);
        font-weight: 600;
    }

    /* Meja Chips — target via Streamlit key classes */
    /* Kosong = hijau (keys: dash_kosong_*, buka_meja_*) */
    [class*="st-key-dash_kosong_"] button,
    [class*="st-key-buka_meja_"] button {
        background-color: rgba(110,143,106,0.15) !important;
        border: 1.5px solid var(--status-kosong) !important;
        color: var(--ink-primary) !important;
    }
    [class*="st-key-dash_kosong_"] button:hover,
    [class*="st-key-buka_meja_"] button:hover {
        background-color: rgba(110,143,106,0.30) !important;
        border-color: var(--status-kosong) !important;
        color: var(--status-kosong) !important;
    }
    /* Terisi = merah (keys: dash_terisi_*, lihat_meja_*) */
    [class*="st-key-dash_terisi_"] button,
    [class*="st-key-lihat_meja_"] button {
        background-color: rgba(193,87,59,0.15) !important;
        border: 1.5px solid var(--status-terisi) !important;
        color: var(--ink-primary) !important;
    }
    [class*="st-key-dash_terisi_"] button:hover,
    [class*="st-key-lihat_meja_"] button:hover {
        background-color: rgba(193,87,59,0.30) !important;
        border-color: var(--status-terisi) !important;
        color: var(--status-terisi) !important;
    }
    /* Tombol Primer */
    .btn-primary .stButton > button {
        background-color: var(--accent-ember) !important;
        color: var(--paper-ink) !important;
        border: none !important;
    }

    /* General Layout tweaks */
    .section-title {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 22px;
        color: var(--ink-primary);
        margin-bottom: 16px;
        margin-top: 24px;
    }
    .activity-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--rule-hairline);
        border-radius: 4px;
        padding: 12px;
    }
    .activity-item {
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid var(--rule-hairline);
    }
    .activity-item:last-child { border-bottom: none; }
    .activity-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background-color: var(--accent-ember);
        margin-right: 12px;
    }
    .activity-meja { color: var(--ink-primary); font-weight: 600; font-size: 0.9rem; }
    .activity-id { color: var(--ink-muted); font-size: 0.78rem; font-family: 'IBM Plex Mono', monospace; }
    .activity-total { color: var(--accent-ember); font-weight: 600; font-family: 'IBM Plex Mono', monospace; }

    /* Dashboard Stats */
    .stat-label { color: var(--ink-muted); font-size: 0.78rem; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }
    .stat-value { font-family: 'IBM Plex Mono', monospace !important; font-size: 1.8rem; font-weight: 700; color: var(--ink-primary); line-height: 1.1; }
    .stat-value-currency { font-family: 'IBM Plex Mono', monospace !important; font-size: 1.25rem; font-weight: 700; color: var(--accent-ember); line-height: 1.1; }
    .stat-value-sm { font-family: 'IBM Plex Mono', monospace !important; font-size: 1.3rem; font-weight: 600; color: var(--accent-ember); }
    .stat-sub { color: var(--ink-muted); font-size: 0.8rem; margin-top: 4px; }
    .stat-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--rule-hairline);
        border-radius: 8px;
        padding: 18px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-sizing: border-box;
    }
    .stat-card-accent {
        border-color: var(--accent-ember-dim);
        background-color: rgba(226,150,58,0.06);
    }
    /* Force equal-height stat card columns via Streamlit column selectors */
    div[data-testid="stHorizontalBlock"]:has(.stat-card) {
        align-items: stretch !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.stat-card) > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.stat-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.stat-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.stat-card) .stat-card {
        flex: 1 !important;
    }

    /* Meja Status Elements */
    .meja-status {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 4px;
    }
    .dot-dim {
        background-color: var(--status-kosong);
    }
    .dot-accent {
        background-color: var(--status-terisi);
        box-shadow: 0 0 6px var(--status-terisi);
    }
    .item-badge {
        display: inline-block;
        background-color: var(--accent-ember);
        color: var(--paper-ink);
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
        margin-top: 6px;
    }

    /* Button Variants */
    .btn-accent .stButton > button {
        background-color: var(--accent-ember) !important;
        color: var(--paper-ink) !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .btn-accent .stButton > button:hover {
        background-color: var(--accent-ember-dim) !important;
    }
    .btn-danger .stButton > button {
        background-color: var(--status-terisi) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .btn-danger .stButton > button:hover {
        background-color: #a04530 !important;
    }
    .btn-sm .stButton > button {
        padding: 4px 12px !important;
        font-size: 0.8rem !important;
    }

    /* Confirmation Box */
    .confirm-box {
        background-color: rgba(193, 87, 59, 0.15);
        border: 1px solid var(--status-terisi);
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .confirm-box-title {
        font-weight: 700;
        font-size: 1rem;
        color: var(--status-terisi);
        margin-bottom: 6px;
    }
    .confirm-box-desc {
        font-size: 0.9rem;
        color: var(--ink-muted);
    }

    /* Quick Access Buttons (Dashboard) */
    .qa-btn .stButton > button {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--rule-hairline) !important;
        color: var(--ink-primary) !important;
        font-weight: 500 !important;
    }
    .qa-btn .stButton > button:hover {
        border-color: var(--accent-ember) !important;
        color: var(--accent-ember) !important;
    }

    /* Dashboard Hero */
    .dash-hero {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 24px 0;
        border-bottom: 1px solid var(--rule-hairline);
        margin-bottom: 24px;
    }
    .dash-greeting {
        font-size: 0.9rem;
        color: var(--ink-muted);
        letter-spacing: 0.5px;
    }
    .dash-title {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 2rem;
        color: var(--ink-primary);
    }
    .dash-subtitle {
        font-size: 0.85rem;
        color: var(--ink-muted);
        margin-top: 4px;
    }
    .dash-clock {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--ink-muted);
    }
    .dash-clock {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--ink-muted);
    }
    .dash-clock-accent { color: var(--accent-ember); }

    /* Menu Management Cards */
    .menu-mgmt-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--rule-hairline);
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 8px;
    }
    .menu-mgmt-card.inactive {
        opacity: 0.5;
    }
    .menu-mgmt-nama {
        font-weight: 700;
        font-size: 1rem;
        color: var(--ink-primary);
        margin-bottom: 6px;
    }
    .menu-mgmt-harga {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        color: var(--accent-ember);
    }

    /* Badges */
    .badge-makanan {
        display: inline-block;
        background-color: rgba(226, 150, 58, 0.2);
        color: var(--accent-ember);
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        margin-right: 4px;
    }
    .badge-minuman {
        display: inline-block;
        background-color: rgba(110, 143, 106, 0.2);
        color: var(--status-kosong);
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        margin-right: 4px;
    }
    .badge-diskon {
        display: inline-block;
        background-color: rgba(201, 162, 39, 0.2);
        color: var(--status-reserved);
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        margin-right: 4px;
    }
    .badge-aktif {
        display: inline-block;
        background-color: rgba(110, 143, 106, 0.2);
        color: var(--status-kosong);
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .badge-nonaktif {
        display: inline-block;
        background-color: rgba(193, 87, 59, 0.2);
        color: var(--status-terisi);
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* Page Header */
    .page-header {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 1.8rem;
        color: var(--ink-primary);
    }
    .page-subheader {
        color: var(--ink-muted);
        font-size: 0.9rem;
        margin-bottom: 16px;
    }
    .m-stripe {
        width: 48px;
        height: 3px;
        background-color: var(--accent-ember);
        border-radius: 2px;
        margin: 8px 0 12px 0;
    }

    /* Sidebar */
    .sidebar-metric {
        padding: 6px 4px;
    }
    .sidebar-metric-label {
        font-size: 0.72rem;
        color: var(--ink-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }
    .sidebar-metric-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.0rem;
        font-weight: 600;
        color: var(--ink-primary);
    }
    .sidebar-footer {
        text-align: center;
        color: var(--ink-muted);
        font-size: 0.7rem;
        padding: 20px 0 8px 0;
        letter-spacing: 0.5px;
    }

    /* Nav Buttons */
    .nav-btn .stButton > button {
        background: transparent !important;
        border: none !important;
        color: var(--ink-muted) !important;
        text-align: left !important;
        padding: 6px 8px !important;
        font-size: 0.9rem !important;
    }
    .nav-btn .stButton > button:hover {
        color: var(--accent-ember) !important;
    }
    .nav-btn-active .stButton > button {
        color: var(--accent-ember) !important;
        font-weight: 600 !important;
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 48px 16px;
        color: var(--ink-muted);
    }
    .empty-state-icon { font-size: 2rem; margin-bottom: 12px; }
    .empty-state-title { font-size: 1.1rem; font-weight: 600; color: var(--ink-primary); margin-bottom: 6px; }
    .empty-state-desc { font-size: 0.9rem; }

    /* Payment card */
    .pay-label { font-size: 0.85rem; color: var(--ink-muted); margin-bottom: 4px; }
    .pay-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.1rem; font-weight: 600; color: var(--ink-primary); }

    /* Metric cards (kasir, riwayat) */
    .metric-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--rule-hairline);
        border-radius: 6px;
        padding: 12px;
    }
    .metric-label { font-size: 0.8rem; color: var(--ink-muted); }
    .metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.1rem; font-weight: 600; color: var(--ink-primary); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INISIALISASI SESSION STATE & STORAGE
# ============================================================

def init_session():
    """Inisialisasi session state Streamlit dan storage global."""
    if "storage_initialized" not in st.session_state:
        storage.init_storage()
        st.session_state.storage_initialized = True

    if "halaman" not in st.session_state:
        st.session_state.halaman = "dashboard"
    if "prev_halaman" not in st.session_state:
        st.session_state.prev_halaman = "dashboard"
    if "meja_dipilih" not in st.session_state:
        st.session_state.meja_dipilih = None
    if "notif" not in st.session_state:
        st.session_state.notif = None
    if "confirm_hapus_item" not in st.session_state:
        st.session_state.confirm_hapus_item = None
    if "confirm_nonaktif_menu" not in st.session_state:
        st.session_state.confirm_nonaktif_menu = None


def tampilkan_notif():
    """Tampilkan notifikasi sementara lalu hapus dari session."""
    if st.session_state.notif:
        tipe, pesan = st.session_state.notif
        if tipe == "success":
            st.success(pesan)
        elif tipe == "error":
            st.error(pesan)
        elif tipe == "info":
            st.info(pesan)
        elif tipe == "warning":
            st.warning(pesan)
        st.session_state.notif = None


def set_notif(tipe: str, pesan: str):
    st.session_state.notif = (tipe, pesan)


# ============================================================
# SIDEBAR — NAVIGASI UTAMA
# ============================================================

def render_sidebar():
    with st.sidebar:
        now = datetime.now()
        hari = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"][now.weekday()]
        tgl_str = now.strftime(f"{hari}, %d %b %Y")
        jam_str = now.strftime("%H:%M")

        st.markdown(f"""
        <div style='text-align:center; padding: 22px 0 14px 0;'>
            <div style='font-size:10px; font-weight:700; color:var(--ink-muted);
                        text-transform:uppercase; letter-spacing:0.14em; margin-bottom:6px;
                        font-family:"Inter",sans-serif;'>SISTEM PEMESANAN</div>
            <div style='font-size:1.5rem; font-weight:900; color:#F0F0F0;
                        text-transform:uppercase; letter-spacing:2px;
                        font-family:"Inter",sans-serif;'>RestoEase</div>
            <div class="m-stripe" style="margin: 8px auto 16px auto;"></div>
            <div style='font-size:11px; color:var(--ink-muted); letter-spacing:0.4px;
                        font-family:"Inter",sans-serif;'>{tgl_str}</div>
            <div style='font-size:1.6rem; font-weight:800; color:var(--accent-ember);
                        letter-spacing:4px; margin-top:2px;
                        font-family:"Inter",sans-serif;'>{jam_str}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p class='section-title' style='padding:0 4px;'>Navigasi</p>",
                    unsafe_allow_html=True)

        nav_items = [
            ("dashboard",    "· Dashboard"),
            ("kelola_menu",  "· Kelola Menu"),
            ("riwayat",      "· Riwayat Transaksi"),
        ]

        halaman_aktif = st.session_state.halaman
        for key, label in nav_items:
            is_aktif = (halaman_aktif == key)
            css_class = "nav-btn-active nav-btn" if is_aktif else "nav-btn"
            st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.halaman = key
                st.session_state.meja_dipilih = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05); margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title' style='padding:0 4px;'>Status Hari Ini</p>",
                    unsafe_allow_html=True)

        semua_meja = service.get_semua_meja()
        meja_terisi = [m for m in semua_meja if not m.is_tersedia]
        meja_kosong = [m for m in semua_meja if m.is_tersedia]
        total_trx = len(storage.riwayat_transaksi)
        total_pendapatan = sum(t.total_akhir for t in storage.riwayat_transaksi)
        semua_menu = service.get_semua_menu()
        menu_aktif = sum(1 for m in semua_menu if m.is_tersedia)

        st.markdown(f"""
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Meja Terisi</div>
            <div class="sidebar-metric-value">{len(meja_terisi)} <span style="color:var(--ink-muted);font-size:0.8rem;font-weight:400;">/ {len(semua_meja)}</span></div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Meja Kosong</div>
            <div class="sidebar-metric-value">{len(meja_kosong)}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Transaksi</div>
            <div class="sidebar-metric-value">{total_trx}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Pendapatan</div>
            <div class="sidebar-metric-value" style="font-size:0.88rem;">Rp {total_pendapatan:,.0f}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Menu Aktif</div>
            <div class="sidebar-metric-value">{menu_aktif}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:rgba(255,255,255,0.05); margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title' style='padding:0 4px; color:#C1573B;'>⚠️ Pengaturan Bahaya</p>", unsafe_allow_html=True)
        
        if "confirm_reset_db" not in st.session_state:
            st.session_state.confirm_reset_db = False

        if not st.session_state.confirm_reset_db:
            if st.button("Hapus Seluruh Database", use_container_width=True):
                st.session_state.confirm_reset_db = True
                st.rerun()
        else:
            st.warning("Yakin hapus SEMUA data? Ini tidak bisa dibatalkan.")
            col_y, col_n = st.columns(2)
            if col_y.button("Ya, Hapus!", type="primary", use_container_width=True):
                service.hapus_semua_data()
                st.session_state.confirm_reset_db = False
                st.session_state.halaman = "dashboard"
                set_notif("success", "Database berhasil direset (Hard Delete).")
                st.rerun()
            if col_n.button("Batal", use_container_width=True):
                st.session_state.confirm_reset_db = False
                st.rerun()

        st.markdown("""
        <div class="sidebar-footer">
            RestoEase v2.0 &nbsp;&middot;&nbsp; OOP Project
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# HELPER
# ============================================================

def _get_jumlah_item_meja(nomor_meja: int) -> int:
    try:
        p = service.get_pesanan_aktif(nomor_meja)
        return sum(d.kuantitas for d in p.list_detail)
    except Exception:
        return 0


def _render_page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-header">{title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subheader">{subtitle}</div>', unsafe_allow_html=True)


def _format_rp(val):
    return f"Rp {val:,.0f}".replace(",", ".")


def _render_struk_html(trx) -> str:
    """Generate struk digital sebagai HTML terstruktur dari objek Transaksi."""
    pesanan = trx.pesanan_terkait
    meja_no = pesanan.meja_aktif.nomor_meja
    subtotal = pesanan.hitung_total_sementara()

    # Item rows — no blank lines!
    item_rows = ""
    for d in pesanan.list_detail:
        nama = d.item_menu.nama_menu
        qty = d.kuantitas
        harga = d.item_menu.harga_efektif()
        sub = d.sub_total
        item_rows += (
            f'<tr><td>{nama}<br><span class="item-qty">'
            f'{qty} x {_format_rp(harga)}</span></td>'
            f'<td>{_format_rp(sub)}</td></tr>'
        )

    # Build HTML as one continuous block — NO blank lines (Streamlit Markdown breaks on them)
    html = (
        '<div class="struk-container">'
        '<div class="struk-header">'
        '<h2>RestoEase</h2>'
        '<div class="struk-subtitle">STRUK PEMBAYARAN</div>'
        '</div>'
        '<div class="struk-meta">'
        f'<span class="struk-meta-label">No. Transaksi</span> {trx.id_transaksi}<br>'
        f'<span class="struk-meta-label">No. Pesanan</span> {pesanan.id_pesanan}<br>'
        f'<span class="struk-meta-label">Meja</span> {meja_no}'
        '</div>'
        '<hr class="struk-divider">'
        '<table class="struk-items-table">'
        '<thead><tr><th>Item</th><th>Subtotal</th></tr></thead>'
        f'<tbody>{item_rows}</tbody>'
        '</table>'
        '<hr class="struk-divider">'
        '<div class="struk-totals">'
        '<div class="struk-row">'
        f'<span>Subtotal</span><span>{_format_rp(subtotal)}</span>'
        '</div>'
        '<div class="struk-row">'
        f'<span>Pajak ({trx.PERSEN_PAJAK}%)</span><span>{_format_rp(trx.pajak)}</span>'
        '</div>'
        '<div class="struk-row struk-grand-total">'
        f'<span>TOTAL</span><span>{_format_rp(trx.total_akhir)}</span>'
        '</div>'
        '<hr class="struk-divider">'
        '<div class="struk-row">'
        f'<span>Uang Diterima</span><span>{_format_rp(trx.uang_diterima)}</span>'
        '</div>'
        '<div class="struk-row">'
        f'<span>Kembalian</span><span>{_format_rp(trx.kembalian)}</span>'
        '</div>'
        '</div>'
        '<div class="struk-footer">'
        'Terima kasih atas kunjungan Anda!<br>'
        '<span style="font-size:0.65rem;">RestoEase v2.0 &middot; OOP Project</span>'
        '</div>'
        '</div>'
    )
    return html


# ============================================================
# HALAMAN 0 — DASHBOARD (Landing Page)
# ============================================================

def render_dashboard():
    now = datetime.now()
    jam_str = now.strftime("%H:%M")
    tgl_str = now.strftime("%A, %d %B %Y")
    hour = now.hour
    if hour < 11:
        greeting = "Selamat Pagi"
    elif hour < 15:
        greeting = "Selamat Siang"
    elif hour < 18:
        greeting = "Selamat Sore"
    else:
        greeting = "Selamat Malam"

    tampilkan_notif()

    # ── Data ──
    semua_meja = service.get_semua_meja()
    meja_terisi = [m for m in semua_meja if not m.is_tersedia]
    meja_kosong = [m for m in semua_meja if m.is_tersedia]
    riwayat = service.get_riwayat_transaksi()
    total_pendapatan = sum(t.total_akhir for t in riwayat)
    semua_menu = service.get_semua_menu()
    menu_aktif = sum(1 for m in semua_menu if m.is_tersedia)

    # ── Hero Section ──
    jam_h, jam_m = jam_str.split(":")
    st.markdown(f"""
    <div class="dash-hero">
        <div>
            <div class="dash-greeting">{greeting}</div>
            <div class="dash-title">Dashboard RestoEase</div>
            <div class="dash-subtitle">{tgl_str}</div>
        </div>
        <div class="dash-clock">
            <span class="dash-clock-accent">{jam_h}</span><span style="color:#222222;">:{jam_m}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stat Cards: satu blok HTML grid — tinggi otomatis rata ──
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:8px;">
        <div class="stat-card">
            <div class="stat-label">Meja Terisi</div>
            <div class="stat-value">{len(meja_terisi)}</div>
            <div class="stat-sub">dari {len(semua_meja)} total</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Meja Kosong</div>
            <div class="stat-value">{len(meja_kosong)}</div>
            <div class="stat-sub">siap digunakan</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Transaksi</div>
            <div class="stat-value">{len(riwayat)}</div>
            <div class="stat-sub">total selesai</div>
        </div>
        <div class="stat-card stat-card-accent">
            <div class="stat-label">Pendapatan</div>
            <div class="stat-value-currency">Rp {total_pendapatan:,.0f}</div>
            <div class="stat-sub">total keseluruhan</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Menu Aktif</div>
            <div class="stat-value">{menu_aktif}</div>
            <div class="stat-sub">dari {len(semua_menu)} menu</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Peta Meja full width — desain sama seperti halaman Peta Meja ──
    st.markdown("<p class='section-title'>Peta Meja — Klik untuk Kelola</p>",
                unsafe_allow_html=True)

    semua_meja_sorted = sorted(semua_meja, key=lambda m: m.nomor_meja)
    n_cols_mini = 4
    rows_mini = [semua_meja_sorted[i:i+n_cols_mini]
                 for i in range(0, len(semua_meja_sorted), n_cols_mini)]

    for row in rows_mini:
        cols_mini = st.columns(n_cols_mini)
        for col_m, meja in zip(cols_mini, row):
            with col_m:
                nomor = meja.nomor_meja
                kosong = meja.is_tersedia
                class_meja = "meja-kosong" if kosong else "meja-terisi"
                status_color = "var(--status-kosong)" if kosong else "var(--status-terisi)"
                status_label = "Kosong" if kosong else "Terisi"
                dot_class = "dot-dim" if kosong else "dot-accent"

                badge_html = ""
                if not kosong:
                    n_items = _get_jumlah_item_meja(nomor)
                    if n_items > 0:
                        badge_html = f"<div><span class='item-badge'>{n_items} item</span></div>"

                st.markdown(f"""
                <div class="{class_meja}">
                    <div class="meja-label">Meja</div>
                    <div class="meja-num">{nomor}</div>
                    <div class="meja-status" style="color:{status_color};">
                        <span class="status-dot {dot_class}"></span>{status_label}
                    </div>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)

                if kosong:
                    if st.button("＋ Buka Pesanan", key=f"dash_kosong_{nomor}",
                                 use_container_width=True):
                        try:
                            service.buat_pesanan_baru(nomor)
                        except MejaTidakTersediaError:
                            pass
                        except RestoEaseError as e:
                            set_notif("error", str(e)); st.rerun()
                        st.session_state.prev_halaman = "dashboard"
                        st.session_state.meja_dipilih = nomor
                        st.session_state.halaman = "pesanan"
                        st.rerun()
                else:
                    if st.button("Lihat Pesanan →", key=f"dash_terisi_{nomor}",
                                 use_container_width=True):
                        st.session_state.prev_halaman = "dashboard"
                        st.session_state.meja_dipilih = nomor
                        st.session_state.halaman = "pesanan"
                        st.rerun()

    st.markdown("""
    <div style='display:flex; gap:24px; font-size:12px; margin-top:10px; align-items:center;'>
        <span style='color:var(--status-kosong); display:flex; align-items:center; gap:6px;'>
            <span style='display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--status-kosong);'></span>
            Kosong
        </span>
        <span style='color:var(--status-terisi); display:flex; align-items:center; gap:6px;'>
            <span style='display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--status-terisi); box-shadow:0 0 6px var(--status-terisi);'></span>
            Terisi
        </span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Aktivitas Terakhir ──
    st.markdown("<p class='section-title'>Aktivitas Terakhir</p>", unsafe_allow_html=True)
    if not riwayat:
        st.markdown("""
        <div class="activity-card">
            <div style="text-align:center; padding:28px 12px; color:var(--ink-muted);">
                <div style="font-size:10px; font-weight:700; text-transform:uppercase;
                            letter-spacing:0.14em; margin-bottom:10px; color:var(--ink-muted);">KOSONG</div>
                <div style="font-size:13px; font-weight:600; color:#888888;">Belum ada transaksi</div>
                <div style="font-size:11px; color:var(--ink-muted); margin-top:4px;">
                    Checkout pertama akan muncul di sini
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        recent = list(reversed(riwayat))[:6]
        items_html = ""
        for i, trx in enumerate(recent):
            meja_no = trx.pesanan_terkait.meja_aktif.nomor_meja
            n_items = sum(d.kuantitas for d in trx.pesanan_terkait.list_detail)
            dot_opacity = max(0.3, 1 - i * 0.12)
            items_html += f"""
            <div class="activity-item">
                <div class="activity-dot" style="opacity:{dot_opacity:.2f};"></div>
                <div style="flex:1;">
                    <div class="activity-meja">Meja {meja_no}
                        <span style="color:var(--ink-muted); font-weight:400; font-size:11px;">
                            &nbsp;· {n_items} item
                        </span>
                    </div>
                    <div class="activity-id">{trx.id_transaksi[:20]}…</div>
                </div>
                <div class="activity-total">Rp {trx.total_akhir:,.0f}</div>
            </div>"""
        st.markdown(f'<div class="activity-card">{items_html}</div>',
                    unsafe_allow_html=True)





# ============================================================
# HALAMAN 1 — PETA MEJA
# ============================================================

def render_peta_meja():
    if st.button("⬅ Kembali", key="back_peta"):
        st.session_state.halaman = "dashboard"
        st.rerun()
        
    _render_page_header("Peta Meja", "Pilih meja untuk membuat atau mengelola pesanan aktif")

    tampilkan_notif()

    semua_meja = service.get_semua_meja()
    semua_meja_sorted = sorted(semua_meja, key=lambda m: m.nomor_meja)

    n_kosong = sum(1 for m in semua_meja_sorted if m.is_tersedia)
    n_terisi = len(semua_meja_sorted) - n_kosong

    # ── Stat cards — satu blok HTML grid ──
    pct = int(n_terisi / len(semua_meja_sorted) * 100) if semua_meja_sorted else 0
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:8px;">
        <div class="stat-card stat-card-accent">
            <div class="stat-label">Total Meja</div>
            <div class="stat-value">{len(semua_meja_sorted)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Kosong</div>
            <div class="stat-value">{n_kosong}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Terisi</div>
            <div class="stat-value">{n_terisi}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Tingkat Hunian</div>
            <div class="stat-value">{pct}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Pemisah / Divider ──
    st.markdown("""
    <hr style="border:none; border-top:1px solid rgba(243,236,224,0.10); margin:24px 0 16px 0;">
    <p class='section-title'>Denah Meja</p>
    """, unsafe_allow_html=True)

    # ── Grid Meja ──
    n_cols = 4
    rows = [semua_meja_sorted[i:i+n_cols] for i in range(0, len(semua_meja_sorted), n_cols)]

    for row in rows:
        cols = st.columns(n_cols)
        for col, meja in zip(cols, row):
            with col:
                nomor = meja.nomor_meja
                kosong = meja.is_tersedia
                class_meja = "meja-kosong" if kosong else "meja-terisi"
                status_color = "var(--status-kosong)" if kosong else "var(--status-terisi)"
                status_label = "Kosong" if kosong else "Terisi"
                dot_class = "dot-dim" if kosong else "dot-accent"

                badge_html = ""
                if not kosong:
                    n_items = _get_jumlah_item_meja(nomor)
                    if n_items > 0:
                        badge_html = f"<div><span class='item-badge'>{n_items} item</span></div>"

                st.markdown(f"""
                <div class="{class_meja}">
                    <div class="meja-label">Meja</div>
                    <div class="meja-num">{nomor}</div>
                    <div class="meja-status" style="color:{status_color};">
                        <span class="status-dot {dot_class}"></span>{status_label}
                    </div>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)

                # Marker div agar CSS :has() bisa menarget tombol di kolom ini
                marker_cls = "meja-btn-kosong" if kosong else "meja-btn-terisi"
                st.markdown(f"<div class='{marker_cls}' style='display:none;'></div>", unsafe_allow_html=True)

                if kosong:
                    if st.button("＋ Buka Pesanan", key=f"buka_meja_{nomor}",
                                 use_container_width=True):
                        try:
                            service.buat_pesanan_baru(nomor)
                            st.session_state.prev_halaman = "peta_meja"
                            st.session_state.meja_dipilih = nomor
                            st.session_state.halaman = "pesanan"
                            st.rerun()
                        except MejaTidakTersediaError as e:
                            set_notif("error", str(e)); st.rerun()
                        except RestoEaseError as e:
                            set_notif("error", str(e)); st.rerun()
                else:
                    if st.button("Lihat Pesanan →", key=f"lihat_meja_{nomor}",
                                 use_container_width=True):
                        st.session_state.prev_halaman = "peta_meja"
                        st.session_state.meja_dipilih = nomor
                        st.session_state.halaman = "pesanan"
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex; gap:24px; font-size:12px; align-items:center;
                border-top:1px solid rgba(255,255,255,0.08); padding-top:12px;'>
        <span style='color:var(--status-kosong); display:flex; align-items:center; gap:6px;'>
            <span style='display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--status-kosong);'></span>
            Kosong — Siap dipakai
        </span>
        <span style='color:var(--status-terisi); display:flex; align-items:center; gap:6px;'>
            <span style='display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--status-terisi); box-shadow:0 0 6px var(--status-terisi);'></span>
            Terisi — Ada pesanan aktif
        </span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HALAMAN 2 — PESANAN MEJA (Split Panel)
# ============================================================

def render_pesanan():
    nomor_meja = st.session_state.meja_dipilih

    # ── Header & Back ──
    col_back, col_title = st.columns([1, 8])
    with col_back:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Kembali", key="back_pesanan"):
            st.session_state.halaman = st.session_state.get("prev_halaman", "dashboard")
            st.session_state.meja_dipilih = None
            st.session_state.confirm_hapus_item = None
            st.rerun()
    with col_title:
        _render_page_header(
            f"Pesanan — Meja {nomor_meja}",
            "Tambah menu dari katalog, kelola keranjang, lalu lanjut ke kasir"
        )

    tampilkan_notif()

    try:
        pesanan = service.get_pesanan_aktif(nomor_meja)
    except PesananTidakAdaError:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">—</div>
            <div class="empty-state-title">Tidak ada pesanan aktif</div>
            <div class="empty-state-desc">Meja ini belum memiliki pesanan yang terbuka.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
        if st.button("← Kembali"):
            st.session_state.halaman = st.session_state.get("prev_halaman", "dashboard")
            st.session_state.meja_dipilih = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Info ID pesanan ──
    st.markdown(f"<span style='font-size:11px; color:var(--ink-muted); font-family:monospace;'>"
                f"ID: {pesanan.id_pesanan}</span>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Split Panel: Katalog (kiri) | Keranjang (kanan) ──
    col_katalog, col_keranjang = st.columns([3, 2], gap="large")

    # ─────────────── KATALOG ───────────────
    with col_katalog:
        st.markdown("<p class='section-title'>Katalog Menu</p>", unsafe_allow_html=True)

        col_search, col_filter = st.columns([2, 3])
        with col_search:
            search_q = st.text_input(
                "Cari", placeholder="Cari menu...",
                key="search_menu_input", label_visibility="collapsed"
            )
        with col_filter:
            kategori_filter = st.radio(
                "Filter", ["Semua", "Makanan", "Minuman"],
                horizontal=True, key="filter_katalog",
                label_visibility="collapsed"
            )

        if kategori_filter == "Semua":
            daftar = service.get_menu_tersedia()
        else:
            daftar = service.get_menu_by_kategori(kategori_filter)

        if search_q:
            daftar = [m for m in daftar if search_q.lower() in m.nama_menu.lower()]

        if not daftar:
            not_found_msg = (f"Tidak ada hasil untuk \"{search_q}\""
                             if search_q else "Tidak ada menu tersedia.")
            st.markdown(f"""
            <div class="empty-state" style="padding:32px 16px;">
                <div class="empty-state-icon">—</div>
                <div class="empty-state-title">Menu tidak ditemukan</div>
                <div class="empty-state-desc">{not_found_msg}</div>
            </div>""", unsafe_allow_html=True)
        else:
            from models import MenuSpesial
            for menu in daftar:
                is_spesial = isinstance(menu, MenuSpesial)
                kat_key = "minuman" if menu.kategori == "Minuman" else "makanan"
                badge = f'<span class="badge-{kat_key}">{menu.kategori}</span>'
                if is_spesial:
                    badge += f' <span class="badge-diskon">Diskon {menu.persen_diskon:.0f}%</span>'

                if is_spesial:
                    harga_html = (
                        f'<span class="catalog-harga-coret">Rp {menu.harga:,.0f}</span> '
                        f'<span class="catalog-harga">Rp {menu.harga_efektif():,.0f}</span>'
                    )
                else:
                    harga_html = f'<span class="catalog-harga">Rp {menu.harga:,.0f}</span>'

                st.markdown(f"""
                <div class="catalog-item">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div class="catalog-nama">{menu.nama_menu}</div>
                            <div style="margin-top:4px;">{badge}</div>
                        </div>
                        <div style="text-align:right;">{harga_html}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

                c_qty, c_add = st.columns([1, 2])
                with c_qty:
                    qty_input = st.number_input(
                        "Qty", min_value=1, max_value=99, value=1,
                        key=f"qty_{menu.id_menu}",
                        label_visibility="collapsed",
                    )
                with c_add:
                    st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
                    if st.button(f"＋ Tambah", key=f"add_{menu.id_menu}",
                                 use_container_width=True):
                        try:
                            service.tambah_item_ke_pesanan(nomor_meja, menu.id_menu, qty_input)
                            set_notif("success", f"{menu.nama_menu} ×{qty_input} ditambahkan.")
                            st.rerun()
                        except InputTidakValidError as e:
                            set_notif("error", f"Input tidak valid: {e}"); st.rerun()
                        except RestoEaseError as e:
                            set_notif("error", str(e)); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────── KERANJANG ───────────────
    with col_keranjang:
        st.markdown('<div class="ticket-rail-bg"></div>', unsafe_allow_html=True)
        pesanan = service.get_pesanan_aktif(nomor_meja)
        list_detail = pesanan.list_detail
        n_keranjang = sum(d.kuantitas for d in list_detail)

        cart_header_txt = f"Keranjang &nbsp;<span style='color:var(--accent-ember);'>({n_keranjang} item)</span>" \
            if n_keranjang > 0 else "Keranjang"
        st.markdown(f"<div class='ticket-rail-header'>{cart_header_txt}</div>",
                    unsafe_allow_html=True)

        if not list_detail:
            st.markdown("""
            <div class="empty-cart">
                <div class="empty-cart-icon">KOSONG</div>
                <div style="font-size:13px; color:var(--ink-muted);">Keranjang masih kosong</div>
                <div style="font-size:11px; color:#222222; margin-top:4px;">
                    Tambah menu dari katalog di sebelah kiri
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            # Konfirmasi hapus
            if st.session_state.confirm_hapus_item:
                id_konfirm = st.session_state.confirm_hapus_item
                nama_konfirm = next(
                    (d.item_menu.nama_menu for d in list_detail
                     if d.item_menu.id_menu == id_konfirm),
                    id_konfirm
                )
                st.markdown(f"""
                <div class="confirm-box">
                    <div class="confirm-box-title">Konfirmasi Hapus</div>
                    <div class="confirm-box-desc">
                        Hapus <b style="color:#F0F0F0;">{nama_konfirm}</b> dari keranjang?
                    </div>
                </div>""", unsafe_allow_html=True)
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button("Ya, Hapus", key="konfirm_ya_hapus",
                                 use_container_width=True):
                        try:
                            service.hapus_item_dari_pesanan(nomor_meja, id_konfirm)
                            set_notif("info", f"{nama_konfirm} dihapus.")
                            st.session_state.confirm_hapus_item = None
                            st.rerun()
                        except RestoEaseError as e:
                            set_notif("error", str(e))
                            st.session_state.confirm_hapus_item = None
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with cc2:
                    if st.button("Batal", key="konfirm_batal_hapus",
                                 use_container_width=True):
                        st.session_state.confirm_hapus_item = None
                        st.rerun()

            for detail in list_detail:
                nama = detail.item_menu.nama_menu
                subtotal_item = detail.sub_total
                st.markdown(f"""
                <div class="ticket-rail-item"><span>{nama}</span><span>Rp {subtotal_item:,.0f}</span></div>
                </div>""", unsafe_allow_html=True)
                cq, cu, cd = st.columns([2, 1, 1])
                with cq:
                    qty_edit = st.number_input(
                        "Qty", min_value=1, max_value=99,
                        value=detail.kuantitas,
                        key=f"edit_{detail.item_menu.id_menu}",
                        label_visibility="collapsed",
                    )
                with cu:
                    st.markdown("<div class='btn-sm'>", unsafe_allow_html=True)
                    if st.button("✓", key=f"upd_{detail.item_menu.id_menu}",
                                 help="Simpan perubahan qty", use_container_width=True):
                        try:
                            service.update_item_pesanan(
                                nomor_meja, detail.item_menu.id_menu, qty_edit
                            )
                            set_notif("success", f"{nama} → ×{qty_edit}")
                            st.rerun()
                        except (InputTidakValidError, ItemPesananTidakAdaError) as e:
                            set_notif("error", str(e)); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with cd:
                    st.markdown("<div class='btn-danger btn-sm'>", unsafe_allow_html=True)
                    if st.button("✕", key=f"del_{detail.item_menu.id_menu}",
                                 help="Hapus item", use_container_width=True):
                        st.session_state.confirm_hapus_item = detail.item_menu.id_menu
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # Summary
            subtotal = pesanan.hitung_total_sementara()
            pajak_est = subtotal * 0.1
            total_est = subtotal + pajak_est

            st.markdown(f"""
            <div class="ticket-rail-item"><span>Subtotal</span><span>Rp {subtotal:,.0f}</span></div><div class="ticket-rail-item"><span>Pajak 10%</span><span>Rp {pajak_est:,.0f}</span></div><div class="ticket-rail-total"><span>TOTAL</span><span>Rp {total_est:,.0f}</span></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            ada_item = len(list_detail) > 0
            col_batal, col_kasir = st.columns(2)
            with col_batal:
                st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                if st.button("Batalkan", key="btn_batal", use_container_width=True):
                    try:
                        service.batalkan_pesanan(nomor_meja)
                        set_notif("info", f"Pesanan meja {nomor_meja} dibatalkan.")
                        st.session_state.halaman = st.session_state.get("prev_halaman", "dashboard")
                        st.session_state.meja_dipilih = None
                        st.rerun()
                    except PesananTidakAdaError as e:
                        set_notif("error", str(e)); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with col_kasir:
                st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
                if st.button(
                    "Kasir →",
                    key="btn_kasir", use_container_width=True,
                    disabled=not ada_item,
                    help="Tambahkan minimal 1 item" if not ada_item else "Proses pembayaran"
                ):
                    st.session_state.halaman = "kasir"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# HALAMAN 3 — KASIR / CHECKOUT
# ============================================================

def render_kasir():
    nomor_meja = st.session_state.meja_dipilih

    col_back, col_title = st.columns([1, 8])
    with col_back:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Kembali", key="back_kasir"):
            st.session_state.halaman = "pesanan"
            st.rerun()
    with col_title:
        _render_page_header(
            f"Kasir — Meja {nomor_meja}",
            "Ringkasan tagihan dan proses pembayaran"
        )

    tampilkan_notif()

    try:
        pesanan = service.get_pesanan_aktif(nomor_meja)
    except PesananTidakAdaError:
        st.error("Tidak ada pesanan aktif. Kembali ke halaman sebelumnya.")
        if st.button("← Kembali"):
            st.session_state.halaman = st.session_state.get("prev_halaman", "dashboard")
            st.session_state.meja_dipilih = None
            st.rerun()
        return

    subtotal = pesanan.hitung_total_sementara()
    pajak = subtotal * 0.1
    total = subtotal + pajak

    col_detail, col_bayar = st.columns([3, 2], gap="large")

    # ─────────────── DETAIL PESANAN ───────────────
    with col_detail:
        st.markdown("<p class='section-title'>Ringkasan Pesanan</p>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:11px; color:var(--ink-muted); font-family:monospace;'>"
                    f"{pesanan.id_pesanan}</span>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        for detail in pesanan.list_detail:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**{detail.item_menu.nama_menu}** &nbsp; "
                             f"<span style='color:var(--ink-muted);'>×{detail.kuantitas}</span>",
                             unsafe_allow_html=True)
                st.markdown(f"<small style='color:var(--ink-muted);'>"
                             f"@ Rp {detail.item_menu.harga_efektif():,.0f}</small>",
                             unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span style='font-weight:700; color:#888888;'>"
                             f"Rp {detail.sub_total:,.0f}</span>",
                             unsafe_allow_html=True)
            st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:#0A0A0A; border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:20px;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                <span style='color:#888888; font-size:0.85rem;'>Subtotal</span>
                <span style='color:#888888;'>Rp {subtotal:,.0f}</span>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:16px;'>
                <span style='color:#888888; font-size:0.85rem;'>Pajak (10%)</span>
                <span style='color:#888888;'>Rp {pajak:,.0f}</span>
            </div>
            <div style='border-top:1px solid rgba(255,255,255,0.05); padding-top:16px;
                        display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:#F0F0F0; font-weight:700; font-size:0.85rem;
                             text-transform:uppercase; letter-spacing:0.14em;'>Total Tagihan</span>
                <span style='color:var(--accent-ember); font-weight:900; font-size:1.8rem;'>Rp {total:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────── PEMBAYARAN ───────────────
    with col_bayar:
        st.markdown("<p class='section-title'>Pembayaran</p>", unsafe_allow_html=True)

        # Shortcut amounts
        st.markdown("<p style='font-size:11px; color:var(--ink-muted); margin-bottom:6px;'>Nominal cepat:</p>",
                    unsafe_allow_html=True)
        shortcuts = [10_000, 20_000, 50_000, 100_000]
        s_cols = st.columns(4)
        for i, amt in enumerate(shortcuts):
            with s_cols[i]:
                st.markdown("<div class='btn-sm'>", unsafe_allow_html=True)
                if st.button(f"{amt//1000}K", key=f"shortcut_{amt}",
                             use_container_width=True):
                    mult = int(total / amt) + 1
                    st.session_state["input_uang_val"] = int(amt * mult)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        default_uang = st.session_state.get("input_uang_val", int(total))
        uang_diterima = st.number_input(
            "Uang Diterima (Rp)",
            min_value=0, max_value=100_000_000,
            value=default_uang, step=1000,
            key="input_uang",
            help=f"Minimal Rp {total:,.0f}"
        )

        kembalian = uang_diterima - total
        if uang_diterima >= total:
            st.markdown(f"""
            <div class="kembalian-box">
                <div class="pay-label" style="color:#27AE60;">Kembalian</div>
                <div class="pay-amount" style="color:#27AE60;">Rp {kembalian:,.0f}</div>
                <div class="pay-hint">Uang kembali ke pelanggan</div>
            </div>""", unsafe_allow_html=True)
        else:
            kurang = total - uang_diterima
            st.markdown(f"""
            <div class="kurang-box">
                <div class="pay-label" style="color:#C0392B;">Kurang</div>
                <div class="pay-amount" style="color:#C0392B;">Rp {kurang:,.0f}</div>
                <div class="pay-hint">Tambahkan uang yang kurang</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        bayar_disabled = uang_diterima < total
        st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
        if st.button(
            "Selesaikan Pembayaran",
            key="btn_bayar", use_container_width=True,
            disabled=bayar_disabled,
            help="Uang masih kurang" if bayar_disabled else "Proses pembayaran"
        ):
            try:
                trx = service.proses_checkout(nomor_meja, float(uang_diterima))
                st.session_state.struk_terakhir = trx.cetak_struk_digital()
                st.session_state.trx_terakhir = trx  # Simpan objek untuk HTML struk
                if "input_uang_val" in st.session_state:
                    del st.session_state["input_uang_val"]
                st.session_state.halaman = "struk"
                st.rerun()
            except UangKurangError as e:
                set_notif("error", str(e)); st.rerun()
            except RestoEaseError as e:
                set_notif("error", str(e)); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# HALAMAN 4 — STRUK DIGITAL
# ============================================================

def render_struk():
    _render_page_header(
        "Pembayaran Berhasil",
        "Transaksi selesai. Meja sudah dikosongkan secara otomatis."
    )

    st.success("Transaksi berhasil diproses.")

    trx = st.session_state.get("trx_terakhir", None)
    struk_text = st.session_state.get("struk_terakhir", "")

    if trx:
        col_struk, col_side = st.columns([2, 1])
        with col_struk:
            st.markdown("<p class='section-title'>Struk Digital</p>", unsafe_allow_html=True)
            st.markdown(_render_struk_html(trx), unsafe_allow_html=True)
        with col_side:
            st.markdown("<br><br>", unsafe_allow_html=True)
            n_items = sum(d.kuantitas for d in trx.pesanan_terkait.list_detail)
            st.markdown(f"""
            <div class="stat-card" style="text-align:center;">
                <div class="stat-label" style="margin-top:8px;">Status</div>
                <div style="color:#27AE60; font-size:1rem; font-weight:700; margin-top:4px;">Lunas</div>
            </div>
            <div class="stat-card" style="text-align:center; margin-top:12px;">
                <div class="stat-label">Total Tagihan</div>
                <div class="stat-value-currency">{_format_rp(trx.total_akhir)}</div>
            </div>
            <div class="stat-card" style="text-align:center; margin-top:12px;">
                <div class="stat-label" style="color:#27AE60;">Kembalian</div>
                <div style="color:#27AE60; font-size:1.1rem; font-weight:700;">{_format_rp(trx.kembalian)}</div>
            </div>
            <div class="stat-card" style="text-align:center; margin-top:12px;">
                <div class="stat-label">Jumlah Item</div>
                <div class="stat-value">{n_items}</div>
            </div>
            """, unsafe_allow_html=True)
    elif struk_text:
        # Fallback: tampilkan teks biasa jika objek transaksi tidak tersedia
        st.markdown(f'<pre class="struk-container" style="white-space:pre-wrap;">{struk_text}</pre>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Kembali ke Dashboard", key="back_to_dash"):
        st.session_state.halaman = "dashboard"
        st.session_state.meja_dipilih = None
        st.session_state.struk_terakhir = None
        st.session_state.pop("trx_terakhir", None)
        st.rerun()


# ============================================================
# HALAMAN 5 — KELOLA MENU (CRUD Menu)
# ============================================================

def render_kelola_menu():
    if st.button("⬅ Kembali", key="back_kelola_menu"):
        st.session_state.halaman = "dashboard"
        st.rerun()

    _render_page_header("Kelola Menu",
                        "Tambah, ubah harga, dan kelola ketersediaan menu restoran")

    tampilkan_notif()

    tab_list, tab_tambah = st.tabs(["Daftar Menu", "Tambah Menu Baru"])

    # ── TAB DAFTAR MENU ──
    with tab_list:
        from models import MenuSpesial
        semua_menu = service.get_semua_menu()

        if not semua_menu:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">—</div>
                <div class="empty-state-title">Belum ada menu</div>
                <div class="empty-state-desc">Tambahkan menu baru melalui tab <b>Tambah Menu Baru</b>.</div>
            </div>""", unsafe_allow_html=True)
        else:
            # Filter row
            col_s, col_f = st.columns([3, 3])
            with col_s:
                search_kelola = st.text_input(
                    "Cari", placeholder="Cari nama menu...",
                    key="search_kelola", label_visibility="collapsed"
                )
            with col_f:
                filter_kel = st.radio(
                    "Filter", ["Semua", "Tersedia", "Tidak Tersedia"],
                    horizontal=True, key="filter_menu_kel",
                    label_visibility="collapsed"
                )

            if filter_kel == "Tersedia":
                tampil = [m for m in semua_menu if m.is_tersedia]
            elif filter_kel == "Tidak Tersedia":
                tampil = [m for m in semua_menu if not m.is_tersedia]
            else:
                tampil = semua_menu

            if search_kelola:
                tampil = [m for m in tampil
                          if search_kelola.lower() in m.nama_menu.lower()]

            if not tampil:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">—</div>
                    <div class="empty-state-title">Tidak ada hasil</div>
                    <div class="empty-state-desc">Coba ubah filter atau kata kunci pencarian.</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<p style='color:var(--ink-muted); font-size:11px; margin-bottom:14px;'>"
                    f"Menampilkan {len(tampil)} menu</p>",
                    unsafe_allow_html=True
                )

                # Konfirmasi hapus permanen
                if st.session_state.confirm_nonaktif_menu:
                    id_nonaktif = st.session_state.confirm_nonaktif_menu
                    nama_nonaktif = next(
                        (m.nama_menu for m in tampil if m.id_menu == id_nonaktif),
                        id_nonaktif
                    )
                    st.markdown(f"""
                    <div class="confirm-box">
                        <div class="confirm-box-title">⚠️ Konfirmasi Hapus Permanen</div>
                        <div class="confirm-box-desc">
                            Hapus <b style="color:#F0F0F0;">{nama_nonaktif}</b>
                            secara permanen? Data menu akan dihapus dan tidak bisa dikembalikan.
                        </div>
                    </div>""", unsafe_allow_html=True)
                    cc1, cc2, _ = st.columns([1, 1, 5])
                    with cc1:
                        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                        if st.button("Ya, Hapus!", key="konfirm_nonaktif_ya"):
                            try:
                                service.hapus_menu(id_nonaktif)
                                set_notif("success",
                                          f"{nama_nonaktif} telah dihapus permanen.")
                                st.session_state.confirm_nonaktif_menu = None
                                st.rerun()
                            except RestoEaseError as e:
                                set_notif("error", str(e))
                                st.session_state.confirm_nonaktif_menu = None
                                st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    with cc2:
                        if st.button("Batal", key="konfirm_nonaktif_batal"):
                            st.session_state.confirm_nonaktif_menu = None
                            st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)

                # ── Card Grid: 3 kolom ──
                n_card_cols = 3
                card_rows = [tampil[i:i+n_card_cols]
                             for i in range(0, len(tampil), n_card_cols)]

                for card_row in card_rows:
                    cols = st.columns(n_card_cols)
                    for col, menu in zip(cols, card_row):
                        with col:
                            is_spesial = isinstance(menu, MenuSpesial)
                            is_tersedia = menu.is_tersedia
                            kat_key = "minuman" if menu.kategori == "Minuman" else "makanan"
                            inactive_cls = "" if is_tersedia else " inactive"

                            badges = f'<span class="badge-{kat_key}">{menu.kategori}</span>'
                            if is_spesial:
                                badges += f' <span class="badge-diskon">Diskon {int(menu.persen_diskon)}%</span>'
                            badges += f' <span class="badge-{"aktif" if is_tersedia else "nonaktif"}">' \
                                      f'{"Aktif" if is_tersedia else "Nonaktif"}</span>'

                            if is_spesial:
                                harga_display = (
                                    f'<span style="color:var(--ink-muted); text-decoration:line-through; '
                                    f'font-size:0.78rem;">Rp {menu.harga:,.0f}</span><br>'
                                    f'<span class="menu-mgmt-harga">Rp {menu.harga_efektif():,.0f}</span>'
                                )
                            else:
                                harga_display = (
                                    f'<span class="menu-mgmt-harga">Rp {menu.harga_efektif():,.0f}</span>'
                                )

                            st.markdown(f"""
                            <div class="menu-mgmt-card{inactive_cls}">
                                <div class="menu-mgmt-nama">{menu.nama_menu}</div>
                                <div style="margin-bottom:8px;">{badges}</div>
                                <div>{harga_display}</div>
                            </div>""", unsafe_allow_html=True)

                            # Edit harga langsung
                            harga_baru = st.number_input(
                                "Harga baru (Rp)",
                                min_value=500, max_value=10_000_000,
                                value=int(menu.harga), step=500,
                                key=f"harga_{menu.id_menu}",
                                label_visibility="collapsed",
                                help="Masukkan harga baru lalu klik Simpan"
                            )
                            if is_spesial:
                                harga_eff_new = harga_baru * (1 - menu.persen_diskon / 100)
                                st.markdown(
                                    f"<small style='color:var(--ink-muted);'>Setelah diskon: "
                                    f"<b style='color:#888888;'>Rp {harga_eff_new:,.0f}</b></small>",
                                    unsafe_allow_html=True
                                )

                            col_save, col_toggle = st.columns(2)
                            with col_save:
                                st.markdown("<div class='btn-accent btn-sm'>",
                                            unsafe_allow_html=True)
                                if st.button("Simpan", key=f"upd_harga_{menu.id_menu}",
                                             use_container_width=True):
                                    try:
                                        service.update_harga_menu(
                                            menu.id_menu, float(harga_baru)
                                        )
                                        set_notif(
                                            "success",
                                            f"Harga {menu.nama_menu} → Rp {harga_baru:,.0f}"
                                        )
                                        st.rerun()
                                    except (MenuTidakDitemukanError, InputTidakValidError) as e:
                                        set_notif("error", str(e)); st.rerun()
                                st.markdown("</div>", unsafe_allow_html=True)
                            with col_toggle:
                                t_label = "Nonaktifkan" if is_tersedia else "Aktifkan"
                                t_css = "btn-danger btn-sm" if is_tersedia else "btn-sm"
                                st.markdown(f"<div class='{t_css}'>",
                                            unsafe_allow_html=True)
                                if st.button(t_label, key=f"toggle_{menu.id_menu}",
                                             use_container_width=True):
                                    try:
                                        status_baru = service.toggle_ketersediaan_menu(
                                            menu.id_menu
                                        )
                                        label_s = "diaktifkan" if status_baru else "dinonaktifkan"
                                        set_notif("info", f"{menu.nama_menu} {label_s}.")
                                        st.rerun()
                                    except RestoEaseError as e:
                                        set_notif("error", str(e)); st.rerun()
                                st.markdown("</div>", unsafe_allow_html=True)

                            st.markdown("<div class='btn-danger btn-sm'>",
                                        unsafe_allow_html=True)
                            if st.button("Hapus Permanen", key=f"hapus_{menu.id_menu}",
                                         use_container_width=True,
                                         help="Nonaktifkan permanen dari katalog"):
                                st.session_state.confirm_nonaktif_menu = menu.id_menu
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB TAMBAH MENU ──
    with tab_tambah:
        col_form, col_preview = st.columns([3, 2], gap="large")

        with col_form:
            st.markdown("<p class='section-title'>Informasi Menu</p>", unsafe_allow_html=True)

            tipe_menu = st.radio(
                "Tipe Menu",
                ["Menu Biasa", "Menu Spesial (Ada Diskon)"],
                horizontal=True,
                help="Pilih Menu Spesial jika ada potongan harga",
                key="radio_tipe_menu_tambah"
            )

            diskon_input = 0.0
            if tipe_menu == "Menu Spesial (Ada Diskon)":
                diskon_input = 10.0

            # ── Kategori & Harga di LUAR form agar perubahan langsung trigger rerun ──
            col_kat, col_harga = st.columns(2)
            with col_kat:
                kategori_input = st.selectbox(
                    "Kategori *", ["Makanan", "Minuman"],
                    help="Pilih kategori menu",
                    key="tambah_kategori"
                )
            with col_harga:
                harga_input = st.number_input(
                    "Harga (Rp) *",
                    min_value=500, max_value=10_000_000,
                    value=15000, step=500,
                    help="Harga sebelum diskon" if diskon_input > 0 else "Harga menu",
                    key="tambah_harga"
                )

            if diskon_input > 0:
                harga_setelah = harga_input * (1 - diskon_input / 100)
                st.info(f"Diskon tetap **10%** — Harga setelah diskon: **Rp {harga_setelah:,.0f}**")

            # ── Form hanya untuk nama + submit (agar text_input tidak rerun tiap keystroke) ──
            with st.form("form_tambah_menu", clear_on_submit=True):
                nama_input = st.text_input(
                    "Nama Menu *",
                    placeholder="Contoh: Nasi Goreng Spesial",
                    help="Nama yang ditampilkan ke pelanggan"
                )

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "Tambah Menu", use_container_width=True
                )
                st.markdown("</div>", unsafe_allow_html=True)

                if submitted:
                    if not nama_input.strip():
                        set_notif("error", "Nama menu tidak boleh kosong!")
                        st.rerun()
                    else:
                        try:
                            menu_baru = service.tambah_menu(
                                nama=nama_input,
                                harga=float(harga_input),
                                kategori=kategori_input,
                                persen_diskon=float(diskon_input)
                            )
                            set_notif(
                                "success",
                                f"Menu '{menu_baru.nama_menu}' berhasil ditambahkan. "
                                f"(ID: {menu_baru.id_menu})"
                            )
                            st.rerun()
                        except InputTidakValidError as e:
                            set_notif("error", f"Input tidak valid: {e}"); st.rerun()
                        except RestoEaseError as e:
                            set_notif("error", str(e)); st.rerun()

        with col_preview:
            st.markdown("<p class='section-title'>Preview Card</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if nama_input:
                kat_key = "minuman" if kategori_input == "Minuman" else "makanan"
                badge_prev = f'<span class="badge-{kat_key}">{kategori_input}</span>'
                if tipe_menu == "Menu Spesial (Ada Diskon)":
                    badge_prev += f' <span class="badge-diskon">Diskon {diskon_input:.0f}%</span>'
                harga_eff_prev = harga_input * (1 - diskon_input / 100)

                harga_prev_html = ""
                if diskon_input > 0:
                    harga_prev_html = (
                        f'<div style="color:var(--ink-muted); text-decoration:line-through; '
                        f'font-size:0.78rem; margin-bottom:2px;">Rp {harga_input:,.0f}</div>'
                    )
                harga_prev_html += (
                    f'<div class="menu-mgmt-harga">Rp {harga_eff_prev:,.0f}</div>'
                )

                st.markdown(f"""
                <div class="menu-mgmt-card" style="border-color:var(--accent-ember);">
                    <div class="menu-mgmt-nama">{nama_input}</div>
                    <div style="margin-bottom:8px;">{badge_prev} <span class="badge-aktif">Aktif</span></div>
                    {harga_prev_html}
                    <div style="color:var(--ink-muted); font-size:11px; margin-top:10px;">ID: akan di-generate otomatis</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center; padding:48px 16px; color:#222222; border:1px dashed rgba(255,255,255,0.05);
                            border-radius:8px;">
                    <div style="font-size:10px; font-weight:700; text-transform:uppercase;
                                letter-spacing:0.14em; color:var(--ink-muted); margin-bottom:10px;">PREVIEW</div>
                    <div style="font-size:11px;">Isi nama menu untuk melihat preview</div>
                </div>""", unsafe_allow_html=True)


# ============================================================
# HALAMAN 6 — RIWAYAT TRANSAKSI
# ============================================================

def render_riwayat():
    if st.button("⬅ Kembali", key="back_riwayat_btn"):
        st.session_state.halaman = "dashboard"
        st.rerun()

    _render_page_header("Riwayat Transaksi", "Semua pesanan yang telah dibayar dan selesai")

    tampilkan_notif()

    riwayat = service.get_riwayat_transaksi()

    if not riwayat:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">—</div>
            <div class="empty-state-title">Belum ada transaksi</div>
            <div class="empty-state-desc">
                Transaksi akan muncul di sini setelah checkout pertama selesai.
            </div>
        </div>""", unsafe_allow_html=True)
        return

    total_pendapatan = sum(t.total_akhir for t in riwayat)
    rata = total_pendapatan / len(riwayat)

    from collections import Counter
    item_counter: Counter = Counter()
    for trx in riwayat:
        for detail in trx.pesanan_terkait.list_detail:
            item_counter[detail.item_menu.nama_menu] += detail.kuantitas
    terlaris_nama, terlaris_qty = item_counter.most_common(1)[0] if item_counter else ("—", 0)

    # ── Stat Cards — satu blok HTML grid ──
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:8px;">
        <div class="stat-card">
            <div class="stat-label">Total Transaksi</div>
            <div class="stat-value">{len(riwayat)}</div>
        </div>
        <div class="stat-card stat-card-accent">
            <div class="stat-label">Total Pendapatan</div>
            <div class="stat-value-sm">Rp {total_pendapatan:,.0f}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Rata-rata / Transaksi</div>
            <div class="stat-value-sm">Rp {rata:,.0f}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Menu Terlaris</div>
            <div class="stat-value-sm" style="font-size:0.95rem;">{terlaris_nama}</div>
            <div class="stat-sub">{terlaris_qty} porsi terjual</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter ──
    semua_nomor_meja = sorted(set(
        t.pesanan_terkait.meja_aktif.nomor_meja for t in riwayat
    ))
    col_filt, _ = st.columns([2, 5])
    with col_filt:
        pilihan_meja = st.selectbox(
            "Filter per Meja",
            options=["Semua Meja"] + [f"Meja {n}" for n in semua_nomor_meja],
            key="filter_riwayat_meja",
        )

    if pilihan_meja != "Semua Meja":
        nomor_filter = int(pilihan_meja.replace("Meja ", ""))
        tampil_riwayat = [t for t in riwayat
                          if t.pesanan_terkait.meja_aktif.nomor_meja == nomor_filter]
    else:
        tampil_riwayat = list(riwayat)

    if not tampil_riwayat:
        st.info(f"Tidak ada transaksi untuk {pilihan_meja}.")
        return

    st.markdown(
        f"<p style='color:var(--ink-muted); font-size:11px; margin-bottom:8px;'>"
        f"Menampilkan {len(tampil_riwayat)} transaksi (terbaru di atas)</p>",
        unsafe_allow_html=True
    )

    for trx in reversed(tampil_riwayat):
        meja_no = trx.pesanan_terkait.meja_aktif.nomor_meja
        n_items = sum(d.kuantitas for d in trx.pesanan_terkait.list_detail)
        exp_label = (
            f"Meja {meja_no}  ·  {n_items} item  ·  Rp {trx.total_akhir:,.0f}  "
            f"  [{trx.id_transaksi[:16]}…]"
        )
        with st.expander(exp_label, expanded=False):
            col_struk, col_info = st.columns([3, 1])
            with col_struk:
                st.markdown(_render_struk_html(trx), unsafe_allow_html=True)
            with col_info:
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:8px;">
                    <div class="metric-label">Total Tagihan</div>
                    <div class="metric-value" style="font-size:0.95rem;">Rp {trx.total_akhir:,.0f}</div>
                </div>
                <div class="metric-card" style="margin-bottom:8px;">
                    <div class="metric-label" style="color:#27AE60;">Kembalian</div>
                    <div class="metric-value" style="font-size:0.95rem; color:#27AE60;">
                        Rp {trx.kembalian:,.0f}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Jumlah Item</div>
                    <div class="metric-value">{n_items}</div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# MAIN APP — ROUTING
# ============================================================

def main():
    init_session()
    render_sidebar()

    halaman = st.session_state.halaman

    if halaman == "dashboard":
        render_dashboard()
    elif halaman == "peta_meja":
        render_peta_meja()
    elif halaman == "pesanan":
        if st.session_state.meja_dipilih is None:
            st.session_state.halaman = "dashboard"
            st.rerun()
        else:
            render_pesanan()
    elif halaman == "kasir":
        if st.session_state.meja_dipilih is None:
            st.session_state.halaman = "dashboard"
            st.rerun()
        else:
            render_kasir()
    elif halaman == "struk":
        render_struk()
    elif halaman == "kelola_menu":
        render_kelola_menu()
    elif halaman == "riwayat":
        render_riwayat()
    else:
        st.session_state.halaman = "dashboard"
        st.rerun()


if __name__ == "__main__":
    main()

