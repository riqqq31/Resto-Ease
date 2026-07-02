# storage.py — Global in-memory state + JSON persistence
# File ini mengelola sinkronisasi data dari memori RAM ke file JSON persisten.

import json
from pathlib import Path
from models import Menu, MenuSpesial, Meja, Pesanan, Transaksi

DATA_DIR = Path("data")

# --- In-memory state (Global State sharing) ---
daftar_menu: dict[str, Menu] = {}
# key: id_menu (str), value: objek Menu/MenuSpesial

daftar_meja: dict[int, Meja] = {}
# key: nomor_meja (int), value: objek Meja

pesanan_aktif: dict[int, Pesanan] = {}
# key: nomor_meja (int), value: objek Pesanan yang sedang berjalan

riwayat_transaksi: list[Transaksi] = []
# list semua transaksi yang sudah selesai


# ============================================================
# FUNGSI SAVE KE JSON
# ============================================================

def save_menu() -> None:
    """Simpan daftar_menu ke data/menu.json."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "menu.json", "w", encoding="utf-8") as f:
        # Menggunakan to_dict() untuk serialization
        json.dump([m.to_dict() for m in daftar_menu.values()], f, indent=2, ensure_ascii=False)


def save_meja() -> None:
    """Simpan daftar_meja ke data/meja.json."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "meja.json", "w", encoding="utf-8") as f:
        json.dump([m.to_dict() for m in daftar_meja.values()], f, indent=2, ensure_ascii=False)


def save_pesanan() -> None:
    """Simpan pesanan_aktif ke data/pesanan.json.
    
    [PERBAIKAN CELAH 1]: Menjaga data pesanan aktif agar tidak hilang 
    ketika server Streamlit auto-reload atau browser di-refresh.
    """
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "pesanan.json", "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in pesanan_aktif.values()], f, indent=2, ensure_ascii=False)


def save_transaksi() -> None:
    """Simpan riwayat_transaksi ke data/transaksi.json."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "transaksi.json", "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in riwayat_transaksi], f, indent=2, ensure_ascii=False)


# ============================================================
# FUNGSI LOAD DARI JSON
# ============================================================

def load_menu() -> None:
    """Membaca data/menu.json dan mengisi daftar_menu.
    
    [PERBAIKAN CELAH 2]: Memastikan polimorfisme bekerja saat loading.
    Mendeteksi apakah data bertipe 'MenuSpesial' atau 'Menu' biasa.
    """
    path = DATA_DIR / "menu.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    tipe = item.get("tipe", "Menu")
                    if tipe == "MenuSpesial":
                        m = MenuSpesial.from_dict(item)
                    else:
                        m = Menu.from_dict(item)
                    daftar_menu[m.id_menu] = m
        except (json.JSONDecodeError, KeyError):
            # File kosong atau korup, biarkan daftar_menu kosong
            pass


def load_meja() -> None:
    """Membaca data/meja.json dan mengisi daftar_meja."""
    path = DATA_DIR / "meja.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    m = Meja.from_dict(item)
                    daftar_meja[m.nomor_meja] = m
        except (json.JSONDecodeError, KeyError):
            pass


def load_pesanan() -> None:
    """Membaca data/pesanan.json dan mengisi pesanan_aktif.
    
    [PERBAIKAN CELAH 1]: Mengembalikan pesanan aktif yang belum dicheckout.
    """
    path = DATA_DIR / "pesanan.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    p = Pesanan.from_dict(item)
                    pesanan_aktif[p.meja_aktif.nomor_meja] = p
        except (json.JSONDecodeError, KeyError):
            pass


def load_transaksi() -> None:
    """Membaca data/transaksi.json dan mengisi riwayat_transaksi."""
    path = DATA_DIR / "transaksi.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    riwayat_transaksi.append(Transaksi.from_dict(item))
        except (json.JSONDecodeError, KeyError):
            pass


# ============================================================
# INISIALISASI STORAGE AWAL
# ============================================================

def init_storage() -> None:
    """Dipanggil sekali di main.py saat aplikasi pertama kali berjalan.
    
    Memuat seluruh data persisten dari disk ke memori RAM.
    Jika meja kosong (belum pernah dibuat), inisialisasi 8 meja default.
    """
    load_menu()
    load_meja()
    load_pesanan()
    load_transaksi()

    # Inisialisasi 8 meja default jika database meja kosong
    if not daftar_meja:
        for i in range(1, 9):  # 8 meja default
            daftar_meja[i] = Meja(i)
        save_meja()


def hapus_semua_data() -> None:
    """Menghapus seluruh data dari memori dan file JSON persisten."""
    global daftar_menu, daftar_meja, pesanan_aktif, riwayat_transaksi
    
    # Hapus dari memori
    daftar_menu.clear()
    daftar_meja.clear()
    pesanan_aktif.clear()
    riwayat_transaksi.clear()
    
    # Hapus file fisik
    files_to_delete = ["menu.json", "meja.json", "pesanan.json", "transaksi.json"]
    for filename in files_to_delete:
        path = DATA_DIR / filename
        if path.exists():
            path.unlink()
            
    # Inisialisasi ulang meja default setelah dihapus
    init_storage()
