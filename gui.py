# main.py — Entry point Streamlit RestoEase
# Berisi HANYA kode UI Streamlit (st.*).
# Import dari services & storage — TIDAK langsung dari models.

import streamlit as st
import storage
import service
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
    /* Import font Inter dari Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Latar belakang utama (Canvas) */
    .stApp {
        background-color: #000000 !important;
        color: #bbbbbb !important;
    }

    /* Sidebar (Surface Soft) */
    [data-testid="stSidebar"] {
        background-color: #0d0d0d !important;
        border-right: 1px solid #3c3c3c !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
    }

    /* Judul halaman (Display MD) */
    .page-header {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.25rem;
    }
    
    /* Sub-header */
    .page-subheader {
        color: #7e7e7e;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    /* M-Stripe Divider */
    .m-stripe {
        height: 4px;
        background: linear-gradient(90deg, #0066b1 0%, #0066b1 33%, #1c69d4 33%, #1c69d4 66%, #e22718 66%, #e22718 100%);
        margin: 8px 0 24px 0;
    }

    /* Kartu Meja Kosong */
    .meja-kosong {
        background-color: #1a1a1a;
        border: 1px solid #3c3c3c;
        border-top: 4px solid #0fa336 !important;
        border-radius: 0px;
        padding: 24px 12px;
        text-align: center;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    .meja-kosong:hover {
        transform: translateY(-3px);
        border-color: #ffffff;
        box-shadow: 0 4px 20px rgba(15, 163, 54, 0.15);
    }

    /* Kartu Meja Terisi */
    .meja-terisi {
        background-color: #1a1a1a;
        border: 1px solid #3c3c3c;
        border-top: 4px solid #e22718 !important;
        border-radius: 0px;
        padding: 24px 12px;
        text-align: center;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    .meja-terisi:hover {
        transform: translateY(-3px);
        border-color: #ffffff;
        box-shadow: 0 4px 20px rgba(226, 39, 24, 0.15);
    }

    /* Kartu Menu (Surface Card) */
    .menu-card {
        background-color: #1a1a1a;
        border: 1px solid #3c3c3c;
        border-radius: 0px;
        padding: 16px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .menu-card:hover {
        background-color: #262626;
        border-color: #ffffff;
    }

    /* Badge kategori (uppercase & letterspaced) */
    .badge-makanan {
        background-color: #262626;
        color: #ffffff;
        padding: 2px 10px;
        border-radius: 0px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 1px solid #3c3c3c;
    }
    .badge-minuman {
        background-color: #262626;
        color: #ffffff;
        padding: 2px 10px;
        border-radius: 0px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 1px solid #3c3c3c;
    }
    .badge-diskon {
        background-color: rgba(226, 39, 24, 0.15);
        color: #e22718;
        padding: 2px 10px;
        border-radius: 0px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 1px solid #e22718;
    }

    /* Metrik ringkasan (Spec Cells) */
    .metric-card {
        background-color: #0d0d0d;
        border: 1px solid #3c3c3c;
        border-radius: 0px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-label {
        color: #7e7e7e;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 4px;
    }

    /* Tombol (Flat, 0px border-radius, uppercase, letterspaced) */
    .stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2) !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        border: 1px solid #3c3c3c !important;
        color: #ffffff !important;
        border-radius: 0px !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #ffffff !important;
    }

    /* Struk digital */
    .struk-container {
        background-color: #0d0d0d !important;
        color: #e6e6e6 !important;
        border-radius: 0px;
        padding: 24px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        white-space: pre;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        border: 1px solid #3c3c3c;
        border-top: 4px solid #1c69d4;
    }

    /* Garis pembatas */
    hr {
        border-color: #3c3c3c !important;
        margin: 1.5rem 0 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0d0d0d !important;
        border-radius: 0px !important;
        padding: 4px !important;
        gap: 8px !important;
        border-bottom: 1px solid #3c3c3c !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0px !important;
        color: #7e7e7e !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 8px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
    }

    /* Success / Error / Warning */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 0px !important;
        border: 1px solid #3c3c3c !important;
    }
    .stSuccess {
        background-color: rgba(15, 163, 54, 0.15) !important;
        color: #0fa336 !important;
        border-color: #0fa336 !important;
    }
    .stError {
        background-color: rgba(226, 39, 24, 0.15) !important;
        color: #e22718 !important;
        border-color: #e22718 !important;
    }
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

    # State navigasi UI (Session-specific, bukan Global State)
    if "halaman" not in st.session_state:
        st.session_state.halaman = "peta_meja"     # "peta_meja" | "pesanan" | "kasir" | "kelola_menu" | "riwayat"
    if "meja_dipilih" not in st.session_state:
        st.session_state.meja_dipilih = None        # nomor meja yang sedang dikelola
    if "notif" not in st.session_state:
        st.session_state.notif = None               # ("success"|"error"|"info", "pesan")


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
        st.markdown("""
        <div style='text-align:center; padding: 16px 0 8px 0;'>
            <div style='font-size:2.5rem;'>🍽️</div>
            <div style='font-size:1.4rem; font-weight:700; color:#ffffff; text-transform: uppercase; letter-spacing: 1.5px;'>RestoEase</div>
            <div style='font-size:0.75rem; color:#7e7e7e; text-transform: uppercase; letter-spacing: 1px;'>Sistem Pemesanan Digital</div>
        </div>
        <div class="m-stripe" style="margin: 12px 0 20px 0;"></div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.75rem; color: #7e7e7e; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;'>📋 Navigasi</p>", unsafe_allow_html=True)
        menu_nav = st.radio(
            "Navigasi",
            options=["🗺️  Peta Meja", "🍳  Kelola Menu", "📜  Riwayat Transaksi"],
            label_visibility="collapsed",
            key="nav_radio"
        )

        if menu_nav == "🗺️  Peta Meja":
            # Reset ke peta_meja hanya jika halaman aktif saat ini bukan sub-halaman dari peta_meja
            if st.session_state.halaman not in ["pesanan", "kasir", "struk"]:
                st.session_state.halaman = "peta_meja"
                st.session_state.meja_dipilih = None
        elif menu_nav == "🍳  Kelola Menu":
            st.session_state.halaman = "kelola_menu"
            st.session_state.meja_dipilih = None
        elif menu_nav == "📜  Riwayat Transaksi":
            st.session_state.halaman = "riwayat"
            st.session_state.meja_dipilih = None

        # Statistik ringkas di sidebar
        st.markdown("<hr style='border-color:#3c3c3c;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.75rem; color: #7e7e7e; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;'>📊 Status Hari Ini</p>", unsafe_allow_html=True)
        semua_meja = service.get_semua_meja()
        meja_terisi = [m for m in semua_meja if not m.is_tersedia]
        total_trx = len(storage.riwayat_transaksi)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Meja Terisi", f"{len(meja_terisi)}/{len(semua_meja)}")
        with col2:
            st.metric("Transaksi", total_trx)


# ============================================================
# HALAMAN 1 — PETA MEJA
# ============================================================

def render_peta_meja():
    st.markdown('<div class="page-header">🗺️ PETA MEJA</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Pilih meja untuk membuat atau mengelola pesanan</div>', unsafe_allow_html=True)

    tampilkan_notif()

    semua_meja = service.get_semua_meja()
    semua_meja_sorted = sorted(semua_meja, key=lambda m: m.nomor_meja)

    # Grid 4 kolom
    n_cols = 4
    rows = [semua_meja_sorted[i:i+n_cols] for i in range(0, len(semua_meja_sorted), n_cols)]

    for row in rows:
        cols = st.columns(n_cols)
        for col, meja in zip(cols, row):
            with col:
                nomor = meja.nomor_meja
                kosong = meja.is_tersedia
                status_label = "🟢 Kosong" if kosong else "🔴 Terisi"
                class_meja = "meja-kosong" if kosong else "meja-terisi"

                st.markdown(f"""
                <div class='{class_meja}'>
                    <div style='font-size:1.8rem;'>🪑</div>
                    <div style='font-size:1.1rem; font-weight:700; color:white; text-transform: uppercase; letter-spacing: 1px;'>Meja {nomor}</div>
                    <div style='font-size:0.8rem; color:#bbbbbb; margin-top:4px; text-transform: uppercase; letter-spacing: 1px;'>{status_label}</div>
                </div>
                """, unsafe_allow_html=True)

                if kosong:
                    if st.button(f"➕ Buka Pesanan", key=f"buka_meja_{nomor}", use_container_width=True):
                        try:
                            service.buat_pesanan_baru(nomor)
                            st.session_state.meja_dipilih = nomor
                            st.session_state.halaman = "pesanan"
                            st.rerun()
                        except MejaTidakTersediaError as e:
                            set_notif("error", str(e))
                            st.rerun()
                        except RestoEaseError as e:
                            set_notif("error", str(e))
                            st.rerun()
                else:
                    if st.button(f"📋 Lihat Pesanan", key=f"lihat_meja_{nomor}", use_container_width=True):
                        st.session_state.meja_dipilih = nomor
                        st.session_state.halaman = "pesanan"
                        st.rerun()

    # Legend
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 5])
    with c1:
        st.markdown("<p style='font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'><span style='color: #0fa336;'>🟢</span> <b>Kosong</b> — Siap dipakai</p>", unsafe_allow_html=True)
    with c2:
        st.markdown("<p style='font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'><span style='color: #e22718;'>🔴</span> <b>Terisi</b> — Ada pesanan aktif</p>", unsafe_allow_html=True)


# ============================================================
# HALAMAN 2 — PESANAN MEJA (CRUD UTAMA)
# ============================================================

def render_pesanan():
    nomor_meja = st.session_state.meja_dipilih

    # Header + tombol kembali
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← Kembali", key="back_pesanan"):
            st.session_state.halaman = "peta_meja"
            st.session_state.meja_dipilih = None
            st.rerun()
    with col_title:
        st.markdown(f'<div class="page-header">📋 PESANAN MEJA {nomor_meja}</div>', unsafe_allow_html=True)
        st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)

    tampilkan_notif()

    # Ambil pesanan aktif
    try:
        pesanan = service.get_pesanan_aktif(nomor_meja)
    except PesananTidakAdaError:
        st.error(f"Tidak ada pesanan aktif di meja {nomor_meja}.")
        if st.button("Kembali ke Peta Meja"):
            st.session_state.halaman = "peta_meja"
            st.session_state.meja_dipilih = None
            st.rerun()
        return

    st.markdown(f"**ID Pesanan:** `{pesanan.id_pesanan}`")
    st.markdown("---")

    # Dua tab utama: Tambah Item & Keranjang
    tab_tambah, tab_keranjang = st.tabs(["➕  Tambah Menu", "🛒  Keranjang Belanja"])

    # ---- TAB TAMBAH ITEM (CREATE) ----
    with tab_tambah:
        st.markdown("<p style='font-size: 1.1rem; color: #ffffff; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>🍽️ Katalog Menu</p>", unsafe_allow_html=True)

        # Filter kategori
        kategori_filter = st.radio(
            "Filter:",
            ["Semua", "Makanan", "Minuman"],
            horizontal=True,
            key="filter_katalog"
        )

        if kategori_filter == "Semua":
            daftar = service.get_menu_tersedia()
        else:
            daftar = service.get_menu_by_kategori(kategori_filter)

        if not daftar:
            st.info("Tidak ada menu tersedia untuk kategori ini.")
        else:
            for menu in daftar:
                from models import MenuSpesial
                is_spesial = isinstance(menu, MenuSpesial)

                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                    with c1:
                        badge = f'<span class="badge-{"minuman" if menu.kategori == "Minuman" else "makanan"}">{menu.kategori}</span>'
                        if is_spesial:
                            badge += f' <span class="badge-diskon">DISKON {menu.persen_diskon:.0f}%</span>'
                        st.markdown(f"**{menu.nama_menu}**", unsafe_allow_html=False)
                        st.markdown(badge, unsafe_allow_html=True)
                    with c2:
                        if is_spesial:
                            st.markdown(f"~~Rp {menu.harga:,.0f}~~")
                            st.markdown(f"**Rp {menu.harga_efektif():,.0f}**")
                        else:
                            st.markdown(f"**Rp {menu.harga:,.0f}**")
                    with c3:
                        qty_input = st.number_input(
                            "Qty",
                            min_value=1, max_value=99, value=1,
                            key=f"qty_{menu.id_menu}",
                            label_visibility="collapsed"
                        )
                    with c4:
                        if st.button("Tambah", key=f"add_{menu.id_menu}", use_container_width=True):
                            try:
                                service.tambah_item_ke_pesanan(nomor_meja, menu.id_menu, qty_input)
                                set_notif("success", f"✅ {menu.nama_menu} x{qty_input} ditambahkan!")
                                st.rerun()
                            except InputTidakValidError as e:
                                set_notif("error", f"Input tidak valid: {e}")
                                st.rerun()
                            except RestoEaseError as e:
                                set_notif("error", str(e))
                                st.rerun()

                    st.markdown("<hr style='margin: 8px 0; border-color: #3c3c3c !important;'>", unsafe_allow_html=True)

    # ---- TAB KERANJANG (READ, UPDATE, DELETE) ----
    with tab_keranjang:
        pesanan = service.get_pesanan_aktif(nomor_meja)  # refresh
        list_detail = pesanan.list_detail

        if not list_detail:
            st.info("🛒 Keranjang masih kosong. Tambahkan menu dari tab 'Tambah Menu'.")
        else:
            st.markdown("<p style='font-size: 1.1rem; color: #ffffff; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>🛒 Item di Pesanan</p>", unsafe_allow_html=True)

            for detail in list_detail:
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 1, 1])
                    with c1:
                        st.markdown(f"**{detail.item_menu.nama_menu}**")
                        st.markdown(f"<small style='color:#7e7e7e;'>@ Rp {detail.item_menu.harga_efektif():,.0f}</small>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**Rp {detail.sub_total:,.0f}**")
                    with c3:
                        qty_edit = st.number_input(
                            "Qty",
                            min_value=1, max_value=99,
                            value=detail.kuantitas,
                            key=f"edit_{detail.item_menu.id_menu}",
                            label_visibility="collapsed"
                        )
                    with c4:
                        if st.button("✏️", key=f"upd_{detail.item_menu.id_menu}", help="Update kuantitas"):
                            try:
                                service.update_item_pesanan(nomor_meja, detail.item_menu.id_menu, qty_edit)
                                set_notif("success", f"✅ {detail.item_menu.nama_menu} diupdate menjadi x{qty_edit}")
                                st.rerun()
                            except (InputTidakValidError, ItemPesananTidakAdaError) as e:
                                set_notif("error", str(e))
                                st.rerun()
                    with c5:
                        if st.button("🗑️", key=f"del_{detail.item_menu.id_menu}", help="Hapus item"):
                            try:
                                service.hapus_item_dari_pesanan(nomor_meja, detail.item_menu.id_menu)
                                set_notif("info", f"🗑️ {detail.item_menu.nama_menu} dihapus dari pesanan")
                                st.rerun()
                            except (PesananTidakAdaError, ItemPesananTidakAdaError) as e:
                                set_notif("error", str(e))
                                st.rerun()

                    st.markdown("<hr style='margin: 8px 0; border-color: #3c3c3c !important;'>", unsafe_allow_html=True)

            # Total sementara
            subtotal = pesanan.hitung_total_sementara()
            pajak_est = subtotal * 0.1
            total_est = subtotal + pajak_est

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Subtotal</div>
                    <div class="metric-value">Rp {subtotal:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Pajak (10%)</div>
                    <div class="metric-value">Rp {pajak_est:,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Estimasi Total</div>
                    <div class="metric-value">Rp {total_est:,.0f}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tombol aksi di bawah
    pesanan = service.get_pesanan_aktif(nomor_meja)  # refresh
    ada_item = len(pesanan.list_detail) > 0

    col_batal, col_spacer, col_kasir = st.columns([2, 3, 2])
    with col_batal:
        if st.button("❌ Batalkan Pesanan", key="btn_batal", use_container_width=True, type="secondary"):
            try:
                service.batalkan_pesanan(nomor_meja)
                set_notif("info", f"Pesanan meja {nomor_meja} telah dibatalkan.")
                st.session_state.halaman = "peta_meja"
                st.session_state.meja_dipilih = None
                st.rerun()
            except PesananTidakAdaError as e:
                set_notif("error", str(e))
                st.rerun()
    with col_kasir:
        if st.button(
            "💳 Lanjut ke Kasir →",
            key="btn_kasir",
            use_container_width=True,
            disabled=not ada_item
        ):
            st.session_state.halaman = "kasir"
            st.rerun()

    if not ada_item:
        st.caption("⚠️ Tambahkan minimal satu item untuk bisa lanjut ke kasir.")


# ============================================================
# HALAMAN 3 — KASIR / CHECKOUT
# ============================================================

def render_kasir():
    nomor_meja = st.session_state.meja_dipilih

    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← Kembali", key="back_kasir"):
            st.session_state.halaman = "pesanan"
            st.rerun()
    with col_title:
        st.markdown(f'<div class="page-header">💳 KASIR — MEJA {nomor_meja}</div>', unsafe_allow_html=True)
        st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subheader">Ringkasan tagihan & proses pembayaran</div>', unsafe_allow_html=True)

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

    col_detail, col_bayar = st.columns([3, 2])

    # Kolom kiri: ringkasan pesanan
    with col_detail:
        st.markdown("<p style='font-size: 1.1rem; color: #ffffff; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>📋 Ringkasan Pesanan</p>", unsafe_allow_html=True)
        st.markdown(f"`{pesanan.id_pesanan}`")
        st.markdown("---")

        for detail in pesanan.list_detail:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**{detail.item_menu.nama_menu}** × {detail.kuantitas}")
                st.markdown(f"<small style='color:#7e7e7e;'>@ Rp {detail.item_menu.harga_efektif():,.0f}</small>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**Rp {detail.sub_total:,.0f}**")
            st.markdown("<hr style='margin: 8px 0; border-color: #3c3c3c !important;'>", unsafe_allow_html=True)

        subtotal = pesanan.hitung_total_sementara()
        pajak = subtotal * 0.1
        total = subtotal + pajak

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**Subtotal:** &nbsp;&nbsp;&nbsp;&nbsp;Rp {subtotal:,.0f}", unsafe_allow_html=True)
        st.markdown(f"**Pajak (10%):** &nbsp;Rp {pajak:,.0f}", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #ffffff; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;'>💰 Total: Rp {total:,.0f}</h3>", unsafe_allow_html=True)

    # Kolom kanan: input pembayaran
    with col_bayar:
        st.markdown("<p style='font-size: 1.1rem; color: #ffffff; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>💵 Pembayaran</p>", unsafe_allow_html=True)

        subtotal = pesanan.hitung_total_sementara()
        pajak = subtotal * 0.1
        total = subtotal + pajak

        uang_diterima = st.number_input(
            "Uang Diterima (Rp)",
            min_value=0,
            max_value=100_000_000,
            value=int(total),
            step=1000,
            key="input_uang"
        )

        kembalian = uang_diterima - total
        if uang_diterima >= total:
            st.markdown(f"""
            <div style='background:rgba(15,163,54,0.15); border:1px solid #0fa336;
                        border-radius:0px; padding:16px; text-align:center; margin:16px 0;'>
                <div style='color:#7e7e7e; font-size:0.8rem; font-weight:700; letter-spacing:1px; text-transform:uppercase;'>KEMBALIAN</div>
                <div style='color:#0fa336; font-size:1.8rem; font-weight:800;'>
                    Rp {kembalian:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            kurang = total - uang_diterima
            st.markdown(f"""
            <div style='background:rgba(226,39,24,0.15); border:1px solid #e22718;
                        border-radius:0px; padding:16px; text-align:center; margin:16px 0;'>
                <div style='color:#7e7e7e; font-size:0.8rem; font-weight:700; letter-spacing:1px; text-transform:uppercase;'>KURANG</div>
                <div style='color:#e22718; font-size:1.8rem; font-weight:800;'>
                    Rp {kurang:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        bayar_disabled = uang_diterima < total
        if st.button(
            "✅ Selesaikan Pembayaran",
            key="btn_bayar",
            use_container_width=True,
            disabled=bayar_disabled
        ):
            try:
                trx = service.proses_checkout(nomor_meja, float(uang_diterima))
                st.session_state.struk_terakhir = trx.cetak_struk_digital()
                st.session_state.halaman = "struk"
                st.rerun()
            except UangKurangError as e:
                set_notif("error", str(e))
                st.rerun()
            except RestoEaseError as e:
                set_notif("error", str(e))
                st.rerun()

        if bayar_disabled:
            st.caption("⚠️ Uang diterima kurang dari total tagihan.")


# ============================================================
# HALAMAN 4 — STRUK DIGITAL (setelah bayar)
# ============================================================

def render_struk():
    st.markdown('<div class="page-header">🧾 PEMBAYARAN BERHASIL!</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Transaksi telah diselesaikan. Meja sudah dikosongkan.</div>', unsafe_allow_html=True)

    st.success("✅ Transaksi berhasil diproses!")

    struk = st.session_state.get("struk_terakhir", "")
    if struk:
        st.markdown("<p style='font-size: 1.1rem; color: #ffffff; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>🧾 Struk Digital</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="struk-container">{struk}</div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Kembali ke Peta Meja", key="back_to_peta", use_container_width=False):
        st.session_state.halaman = "peta_meja"
        st.session_state.meja_dipilih = None
        st.session_state.struk_terakhir = None
        st.rerun()


# ============================================================
# HALAMAN 5 — KELOLA MENU (CRUD Menu)
# ============================================================

def render_kelola_menu():
    st.markdown('<div class="page-header">🍳 KELOLA MENU</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Tambah, ubah, dan kelola daftar menu restoran</div>', unsafe_allow_html=True)

    tampilkan_notif()

    tab_list, tab_tambah = st.tabs(["📋  Daftar Menu", "➕  Tambah Menu Baru"])

    # ---- TAB DAFTAR MENU ----
    with tab_list:
        from models import MenuSpesial
        semua_menu = service.get_semua_menu()

        if not semua_menu:
            st.info("Belum ada menu. Tambahkan menu baru di tab 'Tambah Menu Baru'.")
        else:
            # Filter tampilan
            filter_kel = st.radio("Tampilkan:", ["Semua", "Tersedia", "Tidak Tersedia"], horizontal=True, key="filter_menu_kel")

            if filter_kel == "Tersedia":
                tampil = [m for m in semua_menu if m.is_tersedia]
            elif filter_kel == "Tidak Tersedia":
                tampil = [m for m in semua_menu if not m.is_tersedia]
            else:
                tampil = semua_menu

            if not tampil:
                st.info("Tidak ada menu untuk filter ini.")

            for menu in tampil:
                is_spesial = isinstance(menu, MenuSpesial)
                is_tersedia = menu.is_tersedia

                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 1])

                    with c1:
                        kat_badge = f'<span class="badge-{"minuman" if menu.kategori == "Minuman" else "makanan"}">{menu.kategori}</span>'
                        if is_spesial:
                            kat_badge += f' <span class="badge-diskon">DISKON {menu.persen_diskon:.0f}%</span>'
                        if not is_tersedia:
                            kat_badge += ' <span style="background:rgba(255,255,255,0.05);color:#7e7e7e;padding:2px 8px;border: 1px solid #3c3c3c;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;">NONAKTIF</span>'
                        st.markdown(f"**{menu.nama_menu}**")
                        st.markdown(kat_badge, unsafe_allow_html=True)
                        st.markdown(f"<small style='color:#7e7e7e;'>{menu.id_menu}</small>", unsafe_allow_html=True)

                    with c2:
                        if is_spesial:
                            st.markdown(f"~~Rp {menu.harga:,.0f}~~")
                            st.markdown(f"**Rp {menu.harga_efektif():,.0f}**")
                        else:
                            st.markdown(f"**Rp {menu.harga:,.0f}**")

                    with c3:
                        harga_baru = st.number_input(
                            "Harga baru",
                            min_value=500,
                            max_value=10_000_000,
                            value=int(menu.harga),
                            step=500,
                            key=f"harga_{menu.id_menu}",
                            label_visibility="collapsed"
                        )
                        if st.button("💾 Update Harga", key=f"upd_harga_{menu.id_menu}", use_container_width=True):
                            try:
                                service.update_harga_menu(menu.id_menu, float(harga_baru))
                                set_notif("success", f"✅ Harga {menu.nama_menu} diupdate menjadi Rp {harga_baru:,.0f}")
                                st.rerun()
                            except (MenuTidakDitemukanError, InputTidakValidError) as e:
                                set_notif("error", str(e))
                                st.rerun()

                    with c4:
                        toggle_label = "✅ Aktif" if is_tersedia else "❌ Nonaktif"
                        if st.button(toggle_label, key=f"toggle_{menu.id_menu}", use_container_width=True):
                            try:
                                status_baru = service.toggle_ketersediaan_menu(menu.id_menu)
                                label_status = "diaktifkan" if status_baru else "dinonaktifkan"
                                set_notif("info", f"ℹ️ {menu.nama_menu} {label_status}")
                                st.rerun()
                            except RestoEaseError as e:
                                set_notif("error", str(e))
                                st.rerun()

                    with c5:
                        if st.button("🗑️", key=f"hapus_{menu.id_menu}", help="Nonaktifkan menu (soft delete)"):
                            try:
                                service.hapus_menu(menu.id_menu)
                                set_notif("info", f"🗑️ {menu.nama_menu} telah dinonaktifkan dari katalog")
                                st.rerun()
                            except (MenuTidakDitemukanError, RestoEaseError) as e:
                                set_notif("error", str(e))
                                st.rerun()

                    st.markdown("<hr style='margin: 8px 0; border-color: #3c3c3c !important;'>", unsafe_allow_html=True)

    # ---- TAB TAMBAH MENU ----
    with tab_tambah:
        st.markdown("<p style='font-size: 1.1rem; color: #ffffff; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>➕ Tambah Menu Baru</p>", unsafe_allow_html=True)

        with st.form("form_tambah_menu", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nama_input = st.text_input("Nama Menu *", placeholder="Contoh: Nasi Goreng Spesial")
                kategori_input = st.selectbox("Kategori *", ["Makanan", "Minuman"])
            with c2:
                harga_input = st.number_input("Harga (Rp) *", min_value=500, max_value=10_000_000, value=15000, step=500)
                tipe_menu = st.radio("Tipe Menu", ["Menu Biasa", "Menu Spesial (Ada Diskon)"], horizontal=True)

            diskon_input = 0.0
            if tipe_menu == "Menu Spesial (Ada Diskon)":
                diskon_input = st.slider("Persentase Diskon (%)", min_value=1, max_value=99, value=10)
                harga_setelah = harga_input * (1 - diskon_input / 100)
                st.info(f"💡 Harga setelah diskon {diskon_input}%: **Rp {harga_setelah:,.0f}**")

            submitted = st.form_submit_button("✅ Tambah Menu", use_container_width=True)
            if submitted:
                try:
                    menu_baru = service.tambah_menu(
                        nama=nama_input,
                        harga=float(harga_input),
                        kategori=kategori_input,
                        persen_diskon=float(diskon_input)
                    )
                    set_notif("success", f"✅ Menu '{menu_baru.nama_menu}' berhasil ditambahkan! (ID: {menu_baru.id_menu})")
                    st.rerun()
                except InputTidakValidError as e:
                    set_notif("error", f"Input tidak valid: {e}")
                    st.rerun()
                except RestoEaseError as e:
                    set_notif("error", str(e))
                    st.rerun()


# ============================================================
# HALAMAN 6 — RIWAYAT TRANSAKSI
# ============================================================

def render_riwayat():
    st.markdown('<div class="page-header">📜 RIWAYAT TRANSAKSI</div>', unsafe_allow_html=True)
    st.markdown('<div class="m-stripe"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Semua transaksi yang telah diselesaikan</div>', unsafe_allow_html=True)

    tampilkan_notif()

    riwayat = service.get_riwayat_transaksi()

    if not riwayat:
        st.info("📭 Belum ada transaksi yang selesai hari ini.")
        return

    # Statistik ringkas
    total_pendapatan = sum(t.total_akhir for t in riwayat)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Transaksi</div>
            <div class="metric-value">{len(riwayat)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Pendapatan</div>
            <div class="metric-value">Rp {total_pendapatan:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        rata = total_pendapatan / len(riwayat) if riwayat else 0
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Rata-rata per Transaksi</div>
            <div class="metric-value">Rp {rata:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Daftar transaksi (terbaru dulu)
    for trx in reversed(riwayat):
        with st.expander(
            f"🧾 {trx.id_transaksi}  |  Meja {trx.pesanan_terkait.meja_aktif.nomor_meja}  |  "
            f"Total: Rp {trx.total_akhir:,.0f}",
            expanded=False
        ):
            st.markdown(f"""
            <div class="struk-container">{trx.cetak_struk_digital()}</div>
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
