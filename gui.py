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
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── FONT: Plus Jakarta Sans ── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

    html, body, [class*="css"], .stApp, .stMarkdown, p, span, div,
    input, label, button, textarea, select {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0d0d0d; }
    ::-webkit-scrollbar-thumb { background: #2e2e2e; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #444; }

    /* ── CANVAS & SIDEBAR ── */
    .stApp { background-color: #0a0a0a !important; color: #cccccc !important; }
    [data-testid="stSidebar"] {
        background-color: #0d0d0d !important;
        border-right: 1px solid #1e1e1e !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px; font-size: 0.85rem;
    }

    /* ── TYPOGRAPHY ── */
    .page-header {
        color: #ffffff; font-size: 1.85rem; font-weight: 800;
        text-transform: uppercase; letter-spacing: 3px; margin-bottom: 0.25rem;
    }
    .page-subheader {
        color: #555; font-size: 0.85rem; margin-bottom: 1.5rem;
        font-weight: 400; letter-spacing: 0.3px;
    }

    /* ── STRIPE DIVIDER ── */
    .m-stripe {
        height: 3px;
        background: linear-gradient(90deg, #1c69d4 0%, #1c69d4 50%, #e22718 50%, #e22718 100%);
        margin: 8px 0 24px 0; border-radius: 2px;
    }

    /* ── TABLE CARDS ── */
    .meja-kosong {
        background: linear-gradient(145deg, #111, #161616);
        border: 1px solid #1e1e1e; border-top: 3px solid #0fa336;
        border-radius: 6px; padding: 22px 12px;
        text-align: center; margin-bottom: 8px; transition: all 0.22s ease;
    }
    .meja-kosong:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 28px rgba(15, 163, 54, 0.18);
        border-color: #0fa336;
    }
    .meja-terisi {
        background: linear-gradient(145deg, #111, #161616);
        border: 1px solid #1e1e1e; border-top: 3px solid #e22718;
        border-radius: 6px; padding: 22px 12px;
        text-align: center; margin-bottom: 8px; transition: all 0.22s ease;
    }
    .meja-terisi:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 28px rgba(226, 39, 24, 0.18);
        border-color: #e22718;
    }
    .item-badge {
        display: inline-block;
        background: rgba(226,39,24,0.15); color: #e22718;
        border: 1px solid rgba(226,39,24,0.35); border-radius: 10px;
        font-size: 0.65rem; font-weight: 700; padding: 2px 8px;
        letter-spacing: 0.5px; margin-top: 4px; text-transform: uppercase;
    }

    /* ── MENU CARDS ── */
    .menu-card {
        background: linear-gradient(145deg, #111, #161616);
        border: 1px solid #1e1e1e; border-radius: 6px;
        padding: 14px 16px; margin-bottom: 6px; transition: all 0.18s ease;
    }
    .menu-card:hover { background: #181818; border-color: #333; }

    /* ── BADGES ── */
    .badge-makanan {
        background: rgba(28,105,212,0.12); color: #5599ff;
        padding: 2px 10px; border-radius: 4px;
        font-size: 0.66rem; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; border: 1px solid rgba(28,105,212,0.35);
    }
    .badge-minuman {
        background: rgba(139,92,246,0.12); color: #a78bfa;
        padding: 2px 10px; border-radius: 4px;
        font-size: 0.66rem; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; border: 1px solid rgba(139,92,246,0.35);
    }
    .badge-diskon {
        background: rgba(226,39,24,0.12); color: #ff6b5b;
        padding: 2px 10px; border-radius: 4px;
        font-size: 0.66rem; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; border: 1px solid rgba(226,39,24,0.35);
    }
    .badge-nonaktif {
        background: rgba(255,255,255,0.04); color: #555;
        padding: 2px 8px; border-radius: 4px;
        font-size: 0.66rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; border: 1px solid #222;
    }

    /* ── METRIC CARDS ── */
    .metric-card {
        background: linear-gradient(145deg, #0d0d0d, #111);
        border: 1px solid #1e1e1e; border-radius: 6px;
        padding: 16px 20px; text-align: center;
    }
    .metric-label {
        color: #555; font-size: 0.68rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1.5px;
    }
    .metric-value {
        color: #ffffff; font-size: 1.5rem; font-weight: 800; margin-top: 4px;
    }
    .metric-sub {
        color: #444; font-size: 0.7rem; margin-top: 2px;
    }

    /* ── SIDEBAR METRIC ── */
    .sidebar-metric {
        background: #111; border: 1px solid #1e1e1e; border-radius: 6px;
        padding: 10px 14px; margin-bottom: 8px;
    }
    .sidebar-metric-label {
        color: #444; font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1.2px;
    }
    .sidebar-metric-value {
        color: #fff; font-size: 1.05rem; font-weight: 800; margin-top: 3px;
    }

    /* ── BUTTONS: default (secondary/outlined) ── */
    .stButton > button {
        background: transparent !important; color: #888 !important;
        border: 1px solid #2a2a2a !important; border-radius: 5px !important;
        font-weight: 600 !important; font-size: 0.82rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: 0.4px !important; padding: 10px 20px !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button:hover {
        background: #181818 !important; color: #fff !important;
        border-color: #444 !important; transform: translateY(-1px) !important;
    }

    /* Accent (primary / blue) */
    .btn-accent .stButton > button {
        background: linear-gradient(135deg, #1c69d4, #1650a8) !important;
        color: #fff !important; border: none !important;
        border-radius: 5px !important; font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(28,105,212,0.3) !important;
    }
    .btn-accent .stButton > button:hover {
        background: linear-gradient(135deg, #2277e8, #1c69d4) !important;
        box-shadow: 0 6px 22px rgba(28,105,212,0.45) !important;
        transform: translateY(-2px) !important;
    }

    /* Danger (red) */
    .btn-danger .stButton > button {
        background: rgba(226,39,24,0.08) !important; color: #e22718 !important;
        border: 1px solid rgba(226,39,24,0.35) !important; border-radius: 5px !important;
        font-weight: 700 !important;
    }
    .btn-danger .stButton > button:hover {
        background: rgba(226,39,24,0.2) !important;
        border-color: #e22718 !important; transform: translateY(-1px) !important;
    }

    /* Success (green) */
    .btn-success .stButton > button {
        background: linear-gradient(135deg, #0fa336, #0a7928) !important;
        color: #fff !important; border: none !important;
        border-radius: 5px !important; font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(15,163,54,0.28) !important;
    }
    .btn-success .stButton > button:hover {
        box-shadow: 0 6px 22px rgba(15,163,54,0.45) !important;
        transform: translateY(-2px) !important;
    }

    /* ── INPUT FIELDS ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: #111 !important; border: 1px solid #222 !important;
        color: #fff !important; border-radius: 5px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #1c69d4 !important;
        box-shadow: 0 0 0 2px rgba(28,105,212,0.18) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #333 !important; }

    /* ── STRUK ── */
    .struk-container {
        background: #0d0d0d; color: #ccc; border-radius: 6px;
        padding: 24px; font-family: 'Courier New', monospace;
        font-size: 0.85rem; white-space: pre;
        box-shadow: 0 4px 28px rgba(0,0,0,0.6);
        border: 1px solid #1e1e1e; border-top: 3px solid #1c69d4;
    }

    /* ── DIVIDERS ── */
    hr { border-color: #181818 !important; margin: 1.5rem 0 !important; }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #0d0d0d !important; border-radius: 0 !important;
        padding: 0 !important; gap: 0 !important;
        border-bottom: 1px solid #1e1e1e !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0 !important; color: #444 !important;
        font-weight: 700 !important; letter-spacing: 0.5px !important;
        padding: 10px 20px !important; font-size: 0.82rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        transition: color 0.18s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important; color: #fff !important;
        border-bottom: 2px solid #1c69d4 !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #bbb !important; }

    /* ── ALERTS ── */
    .stSuccess { background: rgba(15,163,54,0.08) !important; border-color: rgba(15,163,54,0.4) !important; color: #0fa336 !important; border-radius: 6px !important; }
    .stError   { background: rgba(226,39,24,0.08)  !important; border-color: rgba(226,39,24,0.4) !important; color: #e22718 !important; border-radius: 6px !important; }
    .stWarning { background: rgba(255,165,0,0.08)  !important; border-color: rgba(255,165,0,0.4) !important; color: #ffa500 !important; border-radius: 6px !important; }
    .stInfo    { background: rgba(28,105,212,0.08) !important; border-color: rgba(28,105,212,0.4) !important; color: #5599ff !important; border-radius: 6px !important; }

    /* ── EMPTY STATES ── */
    .empty-state { text-align: center; padding: 48px 24px; color: #333; }
    .empty-state-icon {
        width: 52px; height: 52px; border-radius: 50%;
        background: #111; border: 1px solid #1e1e1e;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 1.4rem; margin-bottom: 14px; color: #333;
    }
    .empty-state-title { font-size: 1rem; font-weight: 700; color: #444; margin-bottom: 6px; }
    .empty-state-desc  { font-size: 0.82rem; color: #2e2e2e; }

    /* ── EXPANDERS ── */
    .stExpander { border: 1px solid #1e1e1e !important; border-radius: 6px !important; }
    .stExpander header { background: #111 !important; color: #bbb !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }

    /* ── FORM ── */
    [data-testid="stForm"] {
        background: #0d0d0d; border: 1px solid #1e1e1e;
        border-radius: 8px; padding: 20px;
    }

    /* ── SIDEBAR NAV BUTTON ── */
    .nav-btn .stButton > button {
        background: transparent !important; color: #555 !important;
        border: none !important; border-radius: 5px !important;
        text-align: left !important; font-size: 0.85rem !important;
        font-weight: 600 !important; letter-spacing: 0.3px !important;
        padding: 10px 14px !important; width: 100% !important;
        transition: all 0.15s ease !important;
    }
    .nav-btn .stButton > button:hover {
        background: #161616 !important; color: #fff !important;
        transform: none !important;
    }
    .nav-btn-active .stButton > button {
        background: rgba(28,105,212,0.12) !important;
        color: #5599ff !important;
        border-left: 2px solid #1c69d4 !important;
        padding-left: 12px !important;
    }

    /* ── CONFIRM BOX ── */
    .confirm-box {
        background: rgba(226,39,24,0.06); border: 1px solid rgba(226,39,24,0.25);
        border-radius: 6px; padding: 14px 16px; margin: 10px 0;
    }
    .confirm-box-title { color: #e22718; font-weight: 700; font-size: 0.88rem; margin-bottom: 4px; }
    .confirm-box-desc  { color: #666; font-size: 0.8rem; }

    /* ── PAYMENT BOXES ── */
    .kembalian-box {
        background: rgba(15,163,54,0.08); border: 1px solid rgba(15,163,54,0.35);
        border-radius: 8px; padding: 20px; text-align: center; margin: 12px 0;
    }
    .kurang-box {
        background: rgba(226,39,24,0.08); border: 1px solid rgba(226,39,24,0.35);
        border-radius: 8px; padding: 20px; text-align: center; margin: 12px 0;
    }
    .pay-label  { font-size: 0.68rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
    .pay-amount { font-size: 2rem; font-weight: 800; }
    .pay-hint   { font-size: 0.72rem; margin-top: 6px; opacity: 0.5; }

    /* ── SIDEBAR FOOTER ── */
    .sidebar-footer {
        color: #2a2a2a; font-size: 0.68rem; text-align: center;
        padding: 12px 0 4px 0; border-top: 1px solid #181818; margin-top: 16px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* ── HIDE STREAMLIT BRANDING ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
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
        st.session_state.halaman = "peta_meja"
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
        <div style='text-align:center; padding: 20px 0 12px 0;'>
            <div style='font-size:1.6rem; font-weight:800; color:#fff;
                        text-transform:uppercase; letter-spacing:3px;
                        font-family:"Plus Jakarta Sans",sans-serif;'>RestoEase</div>
            <div style='font-size:0.68rem; color:#333; text-transform:uppercase;
                        letter-spacing:2px; margin-top:4px;
                        font-family:"Plus Jakarta Sans",sans-serif;'>Sistem Pemesanan Digital</div>
        </div>
        <div class="m-stripe" style="margin: 8px 0 18px 0;"></div>
        <div style='text-align:center; margin-bottom:20px;'>
            <div style='font-size:0.7rem; color:#3a3a3a; letter-spacing:0.5px;
                        font-family:"Plus Jakarta Sans",sans-serif;'>{tgl_str}</div>
            <div style='font-size:1.5rem; font-weight:800; color:#1c69d4;
                        letter-spacing:3px; margin-top:2px;
                        font-family:"Plus Jakarta Sans",sans-serif;'>{jam_str}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size:0.65rem; color:#333; font-weight:700; "
                    "text-transform:uppercase; letter-spacing:1.8px; "
                    "margin-bottom:6px; font-family:\"Plus Jakarta Sans\",sans-serif;'>Navigasi</p>",
                    unsafe_allow_html=True)

        nav_items = [
            ("peta_meja",   "Peta Meja"),
            ("kelola_menu", "Kelola Menu"),
            ("riwayat",     "Riwayat Transaksi"),
        ]

        halaman_aktif = st.session_state.halaman
        for key, label in nav_items:
            is_aktif = (halaman_aktif == key) or (
                key == "peta_meja" and halaman_aktif in ["pesanan", "kasir", "struk"]
            )
            css_class = "nav-btn-active nav-btn" if is_aktif else "nav-btn"
            st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.halaman = key if key != "peta_meja" else "peta_meja"
                st.session_state.meja_dipilih = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#181818; margin:18px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.65rem; color:#333; font-weight:700; "
                    "text-transform:uppercase; letter-spacing:1.8px; "
                    "margin-bottom:10px; font-family:\"Plus Jakarta Sans\",sans-serif;'>Status Hari Ini</p>",
                    unsafe_allow_html=True)

        semua_meja = service.get_semua_meja()
        meja_terisi = [m for m in semua_meja if not m.is_tersedia]
        total_trx = len(storage.riwayat_transaksi)
        total_pendapatan = sum(t.total_akhir for t in storage.riwayat_transaksi)

        st.markdown(f"""
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Meja Terisi</div>
            <div class="sidebar-metric-value">{len(meja_terisi)} / {len(semua_meja)}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Transaksi</div>
            <div class="sidebar-metric-value">{total_trx}</div>
        </div>
        <div class="sidebar-metric">
            <div class="sidebar-metric-label">Pendapatan</div>
            <div class="sidebar-metric-value" style="font-size:0.9rem;">Rp {total_pendapatan:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sidebar-footer">
            RestoEase v1.0 &nbsp;&middot;&nbsp; OOP Project
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


# ============================================================
# HALAMAN 1 — PETA MEJA
# ============================================================

def render_peta_meja():
    st.markdown('<div class="page-header">Peta Meja</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Pilih meja untuk membuat atau mengelola pesanan aktif</div>',
                unsafe_allow_html=True)

    tampilkan_notif()

    semua_meja = service.get_semua_meja()
    semua_meja_sorted = sorted(semua_meja, key=lambda m: m.nomor_meja)

    n_kosong = sum(1 for m in semua_meja_sorted if m.is_tersedia)
    n_terisi = len(semua_meja_sorted) - n_kosong

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Meja</div>
            <div class="metric-value">{len(semua_meja_sorted)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label" style="color:#0fa336;">Kosong</div>
            <div class="metric-value" style="color:#0fa336;">{n_kosong}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label" style="color:#e22718;">Terisi</div>
            <div class="metric-value" style="color:#e22718;">{n_terisi}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    n_cols = 4
    rows = [semua_meja_sorted[i:i+n_cols] for i in range(0, len(semua_meja_sorted), n_cols)]

    for row in rows:
        cols = st.columns(n_cols)
        for col, meja in zip(cols, row):
            with col:
                nomor = meja.nomor_meja
                kosong = meja.is_tersedia
                status_label = "Kosong" if kosong else "Terisi"
                class_meja = "meja-kosong" if kosong else "meja-terisi"
                status_color = "#0fa336" if kosong else "#e22718"

                badge_html = ""
                if not kosong:
                    n_items = _get_jumlah_item_meja(nomor)
                    if n_items > 0:
                        badge_html = f"<div><span class='item-badge'>{n_items} item</span></div>"

                st.markdown(f"""
                <div class='{class_meja}'>
                    <div style='font-size:0.72rem; font-weight:700; color:#333;
                                text-transform:uppercase; letter-spacing:2px; margin-bottom:6px;'>
                        Meja
                    </div>
                    <div style='font-size:1.8rem; font-weight:800; color:#fff; line-height:1;'>
                        {nomor}
                    </div>
                    <div style='font-size:0.7rem; color:{status_color}; margin-top:6px;
                                text-transform:uppercase; letter-spacing:1.5px; font-weight:700;'>
                        {status_label}
                    </div>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)

                if kosong:
                    st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
                    if st.button("Buka Pesanan", key=f"buka_meja_{nomor}", use_container_width=True):
                        try:
                            service.buat_pesanan_baru(nomor)
                            st.session_state.meja_dipilih = nomor
                            st.session_state.halaman = "pesanan"
                            st.rerun()
                        except MejaTidakTersediaError as e:
                            set_notif("error", str(e)); st.rerun()
                        except RestoEaseError as e:
                            set_notif("error", str(e)); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    if st.button("Lihat Pesanan", key=f"lihat_meja_{nomor}", use_container_width=True):
                        st.session_state.meja_dipilih = nomor
                        st.session_state.halaman = "pesanan"
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex; gap:24px; font-size:0.78rem; color:#333;
                border-top:1px solid #181818; padding-top:12px;'>
        <span><span style='color:#0fa336; font-weight:700;'>&#9679;</span>
              <span style='color:#444;'> Kosong &mdash; Siap dipakai</span></span>
        <span><span style='color:#e22718; font-weight:700;'>&#9679;</span>
              <span style='color:#444;'> Terisi &mdash; Ada pesanan aktif</span></span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HALAMAN 2 — PESANAN MEJA (CRUD UTAMA)
# ============================================================

def render_pesanan():
    nomor_meja = st.session_state.meja_dipilih

    col_back, col_title = st.columns([1, 7])
    with col_back:
        if st.button("Kembali", key="back_pesanan"):
            st.session_state.halaman = "peta_meja"
            st.session_state.meja_dipilih = None
            st.session_state.confirm_hapus_item = None
            st.rerun()
    with col_title:
        st.markdown(f'<div class="page-header">Pesanan Meja {nomor_meja}</div>', unsafe_allow_html=True)
        st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)

    tampilkan_notif()

    try:
        pesanan = service.get_pesanan_aktif(nomor_meja)
    except PesananTidakAdaError:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">!</div>
            <div class="empty-state-title">Tidak ada pesanan aktif</div>
            <div class="empty-state-desc">Meja ini belum memiliki pesanan yang terbuka.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Kembali ke Peta Meja"):
            st.session_state.halaman = "peta_meja"
            st.session_state.meja_dipilih = None
            st.rerun()
        return

    st.markdown(f"<span style='font-size:0.75rem; color:#333; font-family:monospace;'>"
                f"ID: {pesanan.id_pesanan}</span>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

    n_keranjang = sum(d.kuantitas for d in pesanan.list_detail)
    tab_label_cart = f"Keranjang  ({n_keranjang} item)" if n_keranjang > 0 else "Keranjang"

    tab_tambah, tab_keranjang = st.tabs(["Tambah Menu", tab_label_cart])

    # ── TAB TAMBAH ITEM ──
    with tab_tambah:
        st.markdown("<p style='font-size:0.88rem; color:#fff; font-weight:700; "
                    "text-transform:uppercase; letter-spacing:1.5px; margin-bottom:12px;'>"
                    "Katalog Menu</p>", unsafe_allow_html=True)

        col_search, col_filter = st.columns([3, 2])
        with col_search:
            search_q = st.text_input("Cari menu", placeholder="Ketik nama menu...",
                                     key="search_menu_input", label_visibility="collapsed")
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
            not_found_msg = (f"Tidak ada menu yang cocok dengan \"{search_q}\""
                             if search_q else "Tidak ada menu tersedia.")
            st.markdown(f"""
            <div class="empty-state">
                <div class="empty-state-icon">?</div>
                <div class="empty-state-title">Menu tidak ditemukan</div>
                <div class="empty-state-desc">{not_found_msg}</div>
            </div>""", unsafe_allow_html=True)
        else:
            for menu in daftar:
                from models import MenuSpesial
                is_spesial = isinstance(menu, MenuSpesial)

                with st.container():
                    c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
                    with c1:
                        kat_key = "minuman" if menu.kategori == "Minuman" else "makanan"
                        badge = f'<span class="badge-{kat_key}">{menu.kategori}</span>'
                        if is_spesial:
                            badge += f' <span class="badge-diskon">Diskon {menu.persen_diskon:.0f}%</span>'
                        st.markdown(f"**{menu.nama_menu}**")
                        st.markdown(badge, unsafe_allow_html=True)
                    with c2:
                        if is_spesial:
                            st.markdown(
                                f"<span style='color:#444; text-decoration:line-through; "
                                f"font-size:0.8rem;'>Rp {menu.harga:,.0f}</span>",
                                unsafe_allow_html=True)
                            st.markdown(
                                f"<span style='color:#fff; font-weight:700;'>"
                                f"Rp {menu.harga_efektif():,.0f}</span>",
                                unsafe_allow_html=True)
                        else:
                            st.markdown(f"**Rp {menu.harga:,.0f}**")
                    with c3:
                        qty_input = st.number_input(
                            "Qty", min_value=1, max_value=99, value=1,
                            key=f"qty_{menu.id_menu}",
                            label_visibility="collapsed",
                            help="Jumlah yang ingin dipesan"
                        )
                    with c4:
                        st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
                        if st.button("Tambah", key=f"add_{menu.id_menu}", use_container_width=True):
                            try:
                                service.tambah_item_ke_pesanan(nomor_meja, menu.id_menu, qty_input)
                                set_notif("success", f"{menu.nama_menu} x{qty_input} ditambahkan.")
                                st.rerun()
                            except InputTidakValidError as e:
                                set_notif("error", f"Input tidak valid: {e}"); st.rerun()
                            except RestoEaseError as e:
                                set_notif("error", str(e)); st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<hr style='margin:6px 0; border-color:#181818;'>", unsafe_allow_html=True)

    # ── TAB KERANJANG ──
    with tab_keranjang:
        pesanan = service.get_pesanan_aktif(nomor_meja)
        list_detail = pesanan.list_detail

        if not list_detail:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">0</div>
                <div class="empty-state-title">Keranjang masih kosong</div>
                <div class="empty-state-desc">Tambahkan menu dari tab <b>Tambah Menu</b>.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:0.88rem; color:#fff; font-weight:700; "
                        "text-transform:uppercase; letter-spacing:1.5px; margin-bottom:12px;'>"
                        "Item Pesanan</p>", unsafe_allow_html=True)

            # Konfirmasi hapus
            if st.session_state.confirm_hapus_item:
                id_konfirm = st.session_state.confirm_hapus_item
                nama_konfirm = next(
                    (d.item_menu.nama_menu for d in list_detail if d.item_menu.id_menu == id_konfirm),
                    id_konfirm
                )
                st.markdown(f"""
                <div class="confirm-box">
                    <div class="confirm-box-title">Konfirmasi Hapus</div>
                    <div class="confirm-box-desc">
                        Hapus <b style="color:#ccc;">{nama_konfirm}</b> dari keranjang?
                    </div>
                </div>""", unsafe_allow_html=True)
                cc1, cc2, _ = st.columns([1, 1, 4])
                with cc1:
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button("Ya, Hapus", key="konfirm_ya_hapus", use_container_width=True):
                        try:
                            service.hapus_item_dari_pesanan(nomor_meja, id_konfirm)
                            set_notif("info", f"{nama_konfirm} dihapus dari pesanan.")
                            st.session_state.confirm_hapus_item = None
                            st.rerun()
                        except RestoEaseError as e:
                            set_notif("error", str(e))
                            st.session_state.confirm_hapus_item = None
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with cc2:
                    if st.button("Batal", key="konfirm_batal_hapus", use_container_width=True):
                        st.session_state.confirm_hapus_item = None
                        st.rerun()

            for detail in list_detail:
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 1, 1])
                    with c1:
                        st.markdown(f"**{detail.item_menu.nama_menu}**")
                        st.markdown(
                            f"<small style='color:#444;'>@ Rp {detail.item_menu.harga_efektif():,.0f} / item</small>",
                            unsafe_allow_html=True)
                    with c2:
                        st.markdown(
                            f"<span style='font-weight:700; color:#fff;'>"
                            f"Rp {detail.sub_total:,.0f}</span>",
                            unsafe_allow_html=True)
                    with c3:
                        qty_edit = st.number_input(
                            "Qty", min_value=1, max_value=99,
                            value=detail.kuantitas,
                            key=f"edit_{detail.item_menu.id_menu}",
                            label_visibility="collapsed",
                            help="Ubah jumlah item"
                        )
                    with c4:
                        if st.button("Ubah", key=f"upd_{detail.item_menu.id_menu}",
                                     help="Update kuantitas"):
                            try:
                                service.update_item_pesanan(nomor_meja, detail.item_menu.id_menu, qty_edit)
                                set_notif("success",
                                          f"{detail.item_menu.nama_menu} diubah menjadi x{qty_edit}.")
                                st.rerun()
                            except (InputTidakValidError, ItemPesananTidakAdaError) as e:
                                set_notif("error", str(e)); st.rerun()
                    with c5:
                        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                        if st.button("Hapus", key=f"del_{detail.item_menu.id_menu}",
                                     help="Hapus item dari pesanan"):
                            st.session_state.confirm_hapus_item = detail.item_menu.id_menu
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<hr style='margin:6px 0; border-color:#181818;'>", unsafe_allow_html=True)

            subtotal = pesanan.hitung_total_sementara()
            pajak_est = subtotal * 0.1
            total_est = subtotal + pajak_est

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Subtotal</div>
                    <div class="metric-value" style="font-size:1.15rem;">Rp {subtotal:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Pajak (10%)</div>
                    <div class="metric-value" style="font-size:1.15rem;">Rp {pajak_est:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label" style="color:#1c69d4;">Estimasi Total</div>
                    <div class="metric-value" style="color:#5599ff; font-size:1.15rem;">
                        Rp {total_est:,.0f}
                    </div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    pesanan = service.get_pesanan_aktif(nomor_meja)
    ada_item = len(pesanan.list_detail) > 0

    col_batal, col_spacer, col_kasir = st.columns([2, 4, 2])
    with col_batal:
        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
        if st.button("Batalkan Pesanan", key="btn_batal", use_container_width=True):
            try:
                service.batalkan_pesanan(nomor_meja)
                set_notif("info", f"Pesanan meja {nomor_meja} telah dibatalkan.")
                st.session_state.halaman = "peta_meja"
                st.session_state.meja_dipilih = None
                st.rerun()
            except PesananTidakAdaError as e:
                set_notif("error", str(e)); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col_kasir:
        st.markdown("<div class='btn-success'>", unsafe_allow_html=True)
        if st.button(
            "Lanjut ke Kasir",
            key="btn_kasir", use_container_width=True,
            disabled=not ada_item,
            help="Tambahkan minimal 1 item untuk lanjut ke kasir" if not ada_item else "Proses pembayaran"
        ):
            st.session_state.halaman = "kasir"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if not ada_item:
        st.markdown("<p style='text-align:right; font-size:0.75rem; color:#444; margin-top:4px;'>"
                    "Tambahkan minimal satu item untuk bisa lanjut ke kasir.</p>",
                    unsafe_allow_html=True)


# ============================================================
# HALAMAN 3 — KASIR / CHECKOUT
# ============================================================

def render_kasir():
    nomor_meja = st.session_state.meja_dipilih

    col_back, col_title = st.columns([1, 7])
    with col_back:
        if st.button("Kembali", key="back_kasir"):
            st.session_state.halaman = "pesanan"
            st.rerun()
    with col_title:
        st.markdown(f'<div class="page-header">Kasir — Meja {nomor_meja}</div>', unsafe_allow_html=True)
        st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subheader">Ringkasan tagihan dan proses pembayaran</div>',
                    unsafe_allow_html=True)

    tampilkan_notif()

    try:
        pesanan = service.get_pesanan_aktif(nomor_meja)
    except PesananTidakAdaError:
        st.error("Tidak ada pesanan aktif. Kembali ke peta meja.")
        if st.button("Ke Peta Meja"):
            st.session_state.halaman = "peta_meja"
            st.session_state.meja_dipilih = None
            st.rerun()
        return

    subtotal = pesanan.hitung_total_sementara()
    pajak = subtotal * 0.1
    total = subtotal + pajak

    col_detail, col_bayar = st.columns([3, 2], gap="large")

    with col_detail:
        st.markdown("<p style='font-size:0.88rem; color:#fff; font-weight:700; "
                    "text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px;'>"
                    "Ringkasan Pesanan</p>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:0.72rem; color:#333; font-family:monospace;'>"
                    f"{pesanan.id_pesanan}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:10px 0; border-color:#181818;'>", unsafe_allow_html=True)

        for detail in pesanan.list_detail:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**{detail.item_menu.nama_menu}** x {detail.kuantitas}")
                st.markdown(f"<small style='color:#444;'>@ Rp {detail.item_menu.harga_efektif():,.0f}</small>",
                            unsafe_allow_html=True)
            with c2:
                st.markdown(f"<span style='font-weight:700;'>Rp {detail.sub_total:,.0f}</span>",
                            unsafe_allow_html=True)
            st.markdown("<hr style='margin:6px 0; border-color:#161616;'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:#0d0d0d; border:1px solid #1e1e1e; border-radius:6px; padding:18px;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                <span style='color:#555; font-size:0.85rem;'>Subtotal</span>
                <span style='color:#bbb;'>Rp {subtotal:,.0f}</span>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:12px;'>
                <span style='color:#555; font-size:0.85rem;'>Pajak (10%)</span>
                <span style='color:#bbb;'>Rp {pajak:,.0f}</span>
            </div>
            <div style='border-top:1px solid #1e1e1e; padding-top:12px;
                        display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:#fff; font-weight:700; font-size:0.9rem;
                             text-transform:uppercase; letter-spacing:1.5px;'>Total</span>
                <span style='color:#5599ff; font-weight:800; font-size:1.5rem;'>Rp {total:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_bayar:
        st.markdown("<p style='font-size:0.88rem; color:#fff; font-weight:700; "
                    "text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px;'>"
                    "Pembayaran</p>", unsafe_allow_html=True)

        st.markdown(f"<p style='font-size:0.75rem; color:#444; margin-bottom:4px;'>"
                    f"Minimal: <b style='color:#666;'>Rp {total:,.0f}</b></p>",
                    unsafe_allow_html=True)

        uang_diterima = st.number_input(
            "Uang Diterima (Rp)",
            min_value=0, max_value=100_000_000,
            value=int(total), step=1000,
            key="input_uang",
            help=f"Masukkan nominal uang yang diberikan pelanggan (minimal Rp {total:,.0f})"
        )

        kembalian = uang_diterima - total
        if uang_diterima >= total:
            st.markdown(f"""
            <div class="kembalian-box">
                <div class="pay-label" style="color:#0fa336;">Kembalian</div>
                <div class="pay-amount" style="color:#0fa336;">Rp {kembalian:,.0f}</div>
                <div class="pay-hint">Uang kembali ke pelanggan</div>
            </div>""", unsafe_allow_html=True)
        else:
            kurang = total - uang_diterima
            st.markdown(f"""
            <div class="kurang-box">
                <div class="pay-label" style="color:#e22718;">Kurang</div>
                <div class="pay-amount" style="color:#e22718;">Rp {kurang:,.0f}</div>
                <div class="pay-hint">Tambahkan uang yang kurang</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        bayar_disabled = uang_diterima < total
        st.markdown("<div class='btn-success'>", unsafe_allow_html=True)
        if st.button(
            "Selesaikan Pembayaran",
            key="btn_bayar", use_container_width=True,
            disabled=bayar_disabled,
            help="Uang diterima masih kurang dari total tagihan" if bayar_disabled
                 else "Klik untuk memproses pembayaran"
        ):
            try:
                trx = service.proses_checkout(nomor_meja, float(uang_diterima))
                st.session_state.struk_terakhir = trx.cetak_struk_digital()
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
    st.markdown('<div class="page-header">Pembayaran Berhasil</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Transaksi selesai. Meja sudah dikosongkan secara otomatis.</div>',
                unsafe_allow_html=True)

    st.success("Transaksi berhasil diproses.")

    struk = st.session_state.get("struk_terakhir", "")
    if struk:
        st.markdown("<p style='font-size:0.88rem; color:#fff; font-weight:700; "
                    "text-transform:uppercase; letter-spacing:1.5px; margin: 16px 0 8px 0;'>"
                    "Struk Digital</p>", unsafe_allow_html=True)
        st.markdown(f'<div class="struk-container">{struk}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
    if st.button("Kembali ke Peta Meja", key="back_to_peta"):
        st.session_state.halaman = "peta_meja"
        st.session_state.meja_dipilih = None
        st.session_state.struk_terakhir = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# HALAMAN 5 — KELOLA MENU (CRUD Menu)
# ============================================================

def render_kelola_menu():
    st.markdown('<div class="page-header">Kelola Menu</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Tambah, ubah harga, dan kelola ketersediaan menu restoran</div>',
                unsafe_allow_html=True)

    tampilkan_notif()

    tab_list, tab_tambah = st.tabs(["Daftar Menu", "Tambah Menu Baru"])

    # ── TAB DAFTAR MENU ──
    with tab_list:
        from models import MenuSpesial
        semua_menu = service.get_semua_menu()

        if not semua_menu:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">0</div>
                <div class="empty-state-title">Belum ada menu</div>
                <div class="empty-state-desc">Tambahkan menu baru melalui tab <b>Tambah Menu Baru</b>.</div>
            </div>""", unsafe_allow_html=True)
        else:
            col_s, col_f = st.columns([3, 2])
            with col_s:
                search_kelola = st.text_input("Cari menu",
                                              placeholder="Cari nama menu...",
                                              key="search_kelola",
                                              label_visibility="collapsed")
            with col_f:
                filter_kel = st.radio("Filter", ["Semua", "Tersedia", "Tidak Tersedia"],
                                      horizontal=True, key="filter_menu_kel",
                                      label_visibility="collapsed")

            if filter_kel == "Tersedia":
                tampil = [m for m in semua_menu if m.is_tersedia]
            elif filter_kel == "Tidak Tersedia":
                tampil = [m for m in semua_menu if not m.is_tersedia]
            else:
                tampil = semua_menu

            if search_kelola:
                tampil = [m for m in tampil if search_kelola.lower() in m.nama_menu.lower()]

            if not tampil:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">?</div>
                    <div class="empty-state-title">Tidak ada hasil</div>
                    <div class="empty-state-desc">Coba ubah filter atau kata kunci pencarian.</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:#333; font-size:0.78rem; margin-bottom:12px;'>"
                            f"Menampilkan {len(tampil)} menu</p>", unsafe_allow_html=True)

                # Konfirmasi nonaktif
                if st.session_state.confirm_nonaktif_menu:
                    id_nonaktif = st.session_state.confirm_nonaktif_menu
                    nama_nonaktif = next(
                        (m.nama_menu for m in tampil if m.id_menu == id_nonaktif), id_nonaktif
                    )
                    st.markdown(f"""
                    <div class="confirm-box">
                        <div class="confirm-box-title">Konfirmasi Nonaktifkan</div>
                        <div class="confirm-box-desc">
                            Nonaktifkan <b style="color:#ccc;">{nama_nonaktif}</b>
                            dari katalog? Menu tidak akan muncul di pesanan baru.
                        </div>
                    </div>""", unsafe_allow_html=True)
                    cc1, cc2, _ = st.columns([1, 1, 5])
                    with cc1:
                        st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                        if st.button("Ya, Nonaktifkan", key="konfirm_nonaktif_ya"):
                            try:
                                service.hapus_menu(id_nonaktif)
                                set_notif("info", f"{nama_nonaktif} telah dinonaktifkan dari katalog.")
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

                for menu in tampil:
                    is_spesial = isinstance(menu, MenuSpesial)
                    is_tersedia = menu.is_tersedia
                    status_str = "Aktif" if is_tersedia else "Nonaktif"
                    diskon_str = f"  [Diskon {int(menu.persen_diskon)}%]" if is_spesial else ""

                    with st.expander(
                        f"{status_str}  —  {menu.nama_menu}  "
                        f"|  {menu.kategori}  "
                        f"|  Rp {menu.harga_efektif():,.0f}{diskon_str}",
                        expanded=False
                    ):
                        ec1, ec2, ec3 = st.columns([2, 2, 2])
                        with ec1:
                            st.markdown("<p style='color:#444; font-size:0.68rem; "
                                        "text-transform:uppercase; letter-spacing:1px; "
                                        "margin-bottom:4px;'>ID Menu</p>", unsafe_allow_html=True)
                            st.code(menu.id_menu, language=None)

                            kat_key = "minuman" if menu.kategori == "Minuman" else "makanan"
                            badges = f'<span class="badge-{kat_key}">{menu.kategori}</span>'
                            if is_spesial:
                                badges += f' <span class="badge-diskon">Diskon {menu.persen_diskon:.0f}%</span>'
                            if not is_tersedia:
                                badges += ' <span class="badge-nonaktif">Nonaktif</span>'
                            st.markdown(badges, unsafe_allow_html=True)

                        with ec2:
                            st.markdown("<p style='color:#444; font-size:0.68rem; "
                                        "text-transform:uppercase; letter-spacing:1px; "
                                        "margin-bottom:4px;'>Update Harga</p>", unsafe_allow_html=True)
                            harga_baru = st.number_input(
                                "Harga baru (Rp)",
                                min_value=500, max_value=10_000_000,
                                value=int(menu.harga), step=500,
                                key=f"harga_{menu.id_menu}",
                                label_visibility="collapsed",
                                help="Masukkan harga baru lalu klik Simpan"
                            )
                            if is_spesial:
                                harga_efektif_baru = harga_baru * (1 - menu.persen_diskon / 100)
                                st.markdown(
                                    f"<small style='color:#444;'>Setelah diskon: "
                                    f"<b style='color:#666;'>Rp {harga_efektif_baru:,.0f}</b></small>",
                                    unsafe_allow_html=True)
                            st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
                            if st.button("Simpan Harga", key=f"upd_harga_{menu.id_menu}",
                                         use_container_width=True):
                                try:
                                    service.update_harga_menu(menu.id_menu, float(harga_baru))
                                    set_notif("success",
                                              f"Harga {menu.nama_menu} diperbarui menjadi Rp {harga_baru:,.0f}.")
                                    st.rerun()
                                except (MenuTidakDitemukanError, InputTidakValidError) as e:
                                    set_notif("error", str(e)); st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

                        with ec3:
                            st.markdown("<p style='color:#444; font-size:0.68rem; "
                                        "text-transform:uppercase; letter-spacing:1px; "
                                        "margin-bottom:4px;'>Status dan Aksi</p>", unsafe_allow_html=True)
                            toggle_label = "Aktif — Klik untuk nonaktifkan" if is_tersedia \
                                else "Nonaktif — Klik untuk aktifkan"
                            if st.button(toggle_label, key=f"toggle_{menu.id_menu}",
                                         use_container_width=True):
                                try:
                                    status_baru = service.toggle_ketersediaan_menu(menu.id_menu)
                                    label_status = "diaktifkan" if status_baru else "dinonaktifkan"
                                    set_notif("info", f"{menu.nama_menu} {label_status}.")
                                    st.rerun()
                                except RestoEaseError as e:
                                    set_notif("error", str(e)); st.rerun()

                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                            if st.button("Nonaktifkan Permanen", key=f"hapus_{menu.id_menu}",
                                         use_container_width=True,
                                         help="Menu akan dihapus dari katalog pelanggan"):
                                st.session_state.confirm_nonaktif_menu = menu.id_menu
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB TAMBAH MENU ──
    with tab_tambah:
        st.markdown("<p style='font-size:0.88rem; color:#fff; font-weight:700; "
                    "text-transform:uppercase; letter-spacing:1.5px; margin-bottom:16px;'>"
                    "Tambah Menu Baru</p>", unsafe_allow_html=True)

        with st.form("form_tambah_menu", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nama_input = st.text_input(
                    "Nama Menu *",
                    placeholder="Contoh: Nasi Goreng Spesial",
                    help="Nama menu yang akan ditampilkan ke pelanggan"
                )
                kategori_input = st.selectbox(
                    "Kategori *", ["Makanan", "Minuman"],
                    help="Pilih kategori menu"
                )
            with c2:
                harga_input = st.number_input(
                    "Harga (Rp) *",
                    min_value=500, max_value=10_000_000, value=15000, step=500,
                    help="Harga sebelum diskon"
                )
                tipe_menu = st.radio(
                    "Tipe Menu",
                    ["Menu Biasa", "Menu Spesial (Ada Diskon)"],
                    horizontal=True,
                    help="Pilih Menu Spesial jika ada potongan harga"
                )

            diskon_input = 0.0
            if tipe_menu == "Menu Spesial (Ada Diskon)":
                diskon_input = st.slider("Persentase Diskon (%)", min_value=1, max_value=99, value=10)
                harga_setelah = harga_input * (1 - diskon_input / 100)
                st.info(f"Harga setelah diskon {diskon_input}%: **Rp {harga_setelah:,.0f}**")

            # Preview
            if nama_input:
                st.markdown("<hr style='border-color:#181818; margin:12px 0;'>", unsafe_allow_html=True)
                st.markdown("<p style='color:#444; font-size:0.68rem; text-transform:uppercase; "
                            "letter-spacing:1px; margin-bottom:8px;'>Preview</p>",
                            unsafe_allow_html=True)
                kat_key = "minuman" if kategori_input == "Minuman" else "makanan"
                badge_prev = f'<span class="badge-{kat_key}">{kategori_input}</span>'
                if tipe_menu == "Menu Spesial (Ada Diskon)":
                    badge_prev += f' <span class="badge-diskon">Diskon {diskon_input:.0f}%</span>'
                harga_eff_prev = harga_input * (1 - diskon_input / 100)
                st.markdown(f"""
                <div class="menu-card" style="max-width:400px;">
                    <div style="font-weight:700; color:#fff; margin-bottom:4px;">{nama_input}</div>
                    <div style="margin-bottom:6px;">{badge_prev}</div>
                    <div style="color:#5599ff; font-weight:700;">Rp {harga_eff_prev:,.0f}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='btn-accent'>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Tambah Menu", use_container_width=True)
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
                        set_notif("success",
                                  f"Menu '{menu_baru.nama_menu}' berhasil ditambahkan. "
                                  f"(ID: {menu_baru.id_menu})")
                        st.rerun()
                    except InputTidakValidError as e:
                        set_notif("error", f"Input tidak valid: {e}"); st.rerun()
                    except RestoEaseError as e:
                        set_notif("error", str(e)); st.rerun()


# ============================================================
# HALAMAN 6 — RIWAYAT TRANSAKSI
# ============================================================

def render_riwayat():
    st.markdown('<div class="page-header">Riwayat Transaksi</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Semua transaksi yang telah diselesaikan</div>',
                unsafe_allow_html=True)

    tampilkan_notif()

    riwayat = service.get_riwayat_transaksi()

    if not riwayat:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">0</div>
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

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Transaksi</div>
            <div class="metric-value">{len(riwayat)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Pendapatan</div>
            <div class="metric-value" style="font-size:1.05rem;">Rp {total_pendapatan:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Rata-rata / Transaksi</div>
            <div class="metric-value" style="font-size:1.05rem;">Rp {rata:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label" style="color:#ffa500;">Terlaris</div>
            <div class="metric-value" style="font-size:0.85rem; color:#ffa500;">{terlaris_nama}</div>
            <div class="metric-sub">{terlaris_qty} porsi terjual</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    semua_nomor_meja = sorted(set(
        t.pesanan_terkait.meja_aktif.nomor_meja for t in riwayat
    ))
    col_filt_rw, _ = st.columns([2, 5])
    with col_filt_rw:
        pilihan_meja = st.selectbox(
            "Filter per Meja",
            options=["Semua Meja"] + [f"Meja {n}" for n in semua_nomor_meja],
            key="filter_riwayat_meja",
            help="Filter transaksi berdasarkan nomor meja"
        )

    if pilihan_meja != "Semua Meja":
        nomor_filter = int(pilihan_meja.replace("Meja ", ""))
        tampil_riwayat = [t for t in riwayat
                          if t.pesanan_terkait.meja_aktif.nomor_meja == nomor_filter]
    else:
        tampil_riwayat = list(riwayat)

    if not tampil_riwayat:
        st.info(f"Tidak ada transaksi untuk {pilihan_meja}.")
    else:
        st.markdown(f"<p style='color:#333; font-size:0.78rem; margin-bottom:8px;'>"
                    f"Menampilkan {len(tampil_riwayat)} transaksi (terbaru di atas)</p>",
                    unsafe_allow_html=True)
        for trx in reversed(tampil_riwayat):
            meja_no = trx.pesanan_terkait.meja_aktif.nomor_meja
            n_items = sum(d.kuantitas for d in trx.pesanan_terkait.list_detail)
            with st.expander(
                f"{trx.id_transaksi}  |  Meja {meja_no}  |  "
                f"{n_items} item  |  Rp {trx.total_akhir:,.0f}",
                expanded=False
            ):
                col_struk, col_info = st.columns([3, 1])
                with col_struk:
                    st.markdown(f'<div class="struk-container">{trx.cetak_struk_digital()}</div>',
                                unsafe_allow_html=True)
                with col_info:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:8px;">
                        <div class="metric-label">Total Tagihan</div>
                        <div class="metric-value" style="font-size:0.95rem;">Rp {trx.total_akhir:,.0f}</div>
                    </div>
                    <div class="metric-card" style="margin-bottom:8px;">
                        <div class="metric-label" style="color:#0fa336;">Kembalian</div>
                        <div class="metric-value" style="font-size:0.95rem; color:#0fa336;">
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

    if halaman == "peta_meja":
        render_peta_meja()
    elif halaman == "pesanan":
        if st.session_state.meja_dipilih is None:
            st.session_state.halaman = "peta_meja"
            st.rerun()
        else:
            render_pesanan()
    elif halaman == "kasir":
        if st.session_state.meja_dipilih is None:
            st.session_state.halaman = "peta_meja"
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
        st.session_state.halaman = "peta_meja"
        st.rerun()


if __name__ == "__main__":
    main()
