# services.py — Business logic & operasi antar objek
# File ini adalah lapisan perantara antara UI (main.py) dan data (storage.py + models/).
# Semua fungsi dibungkus try/except — error domain di-raise, error tak terduga dibungkus RestoEaseError.
# TIDAK ada import Streamlit di sini.

import datetime
import random
import storage
from models import Menu, MenuSpesial, Meja, Pesanan, Transaksi, ItemKatalog
from exceptions import (
    RestoEaseError,
    MenuTidakDitemukanError,
    MejaTidakTersediaError,
    PesananTidakAdaError,
    InputTidakValidError,
    ItemPesananTidakAdaError,
)


# ============================================================
# HELPER INTERNAL
# ============================================================

def _generate_id_pesanan() -> str:
    """Generate ID pesanan unik berbasis timestamp + random suffix.
    
    [PERBAIKAN CELAH 3]: Menggunakan milidetik + random 3 digit
    untuk menghindari tabrakan ID jika dua aksi terjadi di detik yang sama.
    """
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]  # hingga milidetik
    suffix = str(random.randint(100, 999))
    return f"PSN-{ts}-{suffix}"


def _generate_id_transaksi() -> str:
    """Generate ID transaksi unik berbasis timestamp + random suffix."""
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
    suffix = str(random.randint(100, 999))
    return f"TRX-{ts}-{suffix}"


# ============================================================
# MENU MANAGEMENT
# ============================================================

def get_semua_menu() -> list[ItemKatalog]:
    """READ — Ambil semua menu dari daftar_menu (tersedia dan tidak tersedia)."""
    try:
        return list(storage.daftar_menu.values())
    except Exception as e:
        raise RestoEaseError(f"Gagal mengambil daftar menu: {e}") from e


def get_menu_tersedia() -> list[ItemKatalog]:
    """READ — Ambil hanya menu yang statusnya tersedia (is_tersedia = True)."""
    try:
        return [m for m in storage.daftar_menu.values() if m.is_tersedia]
    except Exception as e:
        raise RestoEaseError(f"Gagal mengambil menu tersedia: {e}") from e


def get_menu_by_kategori(kategori: str) -> list[ItemKatalog]:
    """READ — Ambil menu berdasarkan kategori ('Makanan' atau 'Minuman')."""
    try:
        return [
            m for m in storage.daftar_menu.values()
            if m.kategori == kategori and m.is_tersedia
        ]
    except Exception as e:
        raise RestoEaseError(f"Gagal mengambil menu per kategori: {e}") from e


def get_menu_by_id(id_menu: str) -> ItemKatalog:
    """READ — Ambil satu menu berdasarkan id_menu.
    
    Raise MenuTidakDitemukanError jika ID tidak ada di daftar_menu.
    """
    try:
        if id_menu not in storage.daftar_menu:
            raise MenuTidakDitemukanError(f"Menu dengan ID '{id_menu}' tidak ditemukan")
        return storage.daftar_menu[id_menu]
    except MenuTidakDitemukanError:
        raise
    except Exception as e:
        raise RestoEaseError(f"Kesalahan tidak terduga saat mencari menu: {e}") from e


def tambah_menu(nama: str, harga: float, kategori: str,
                persen_diskon: float = 0) -> ItemKatalog:
    """CREATE — Tambah menu baru ke daftar_menu, lalu simpan ke JSON.
    
    Jika persen_diskon > 0, buat MenuSpesial. Jika tidak, buat Menu biasa.
    Raise InputTidakValidError jika validasi gagal (ditangani di constructor model).
    """
    try:
        # Generate ID otomatis dari nama
        id_menu = Menu.buat_id(nama)

        # Hindari duplikat ID — tambahkan counter jika sudah ada
        counter = 1
        original_id = id_menu
        while id_menu in storage.daftar_menu:
            id_menu = f"{original_id}-{counter}"
            counter += 1

        # Buat objek Menu atau MenuSpesial
        if persen_diskon > 0:
            menu_baru = MenuSpesial(id_menu, nama, harga, kategori, persen_diskon)
        else:
            menu_baru = Menu(id_menu, nama, harga, kategori)

        # Simpan ke state dan ke JSON
        storage.daftar_menu[id_menu] = menu_baru
        storage.save_menu()
        return menu_baru

    except InputTidakValidError:
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal menambah menu: {e}") from e


def update_harga_menu(id_menu: str, harga_baru: float) -> None:
    """UPDATE — Ubah harga menu yang sudah ada.
    
    Raise MenuTidakDitemukanError jika ID tidak ada.
    Raise InputTidakValidError jika harga tidak valid (ditangani di setter model).
    """
    try:
        menu = get_menu_by_id(id_menu)
        menu.update_harga(harga_baru)
        storage.save_menu()
    except (MenuTidakDitemukanError, InputTidakValidError):
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal mengupdate harga menu: {e}") from e


def toggle_ketersediaan_menu(id_menu: str) -> bool:
    """UPDATE — Toggle status ketersediaan menu (tersedia <-> tidak tersedia).
    
    Return: status is_tersedia setelah perubahan.
    """
    try:
        menu = get_menu_by_id(id_menu)
        menu.ganti_status_ketersediaan()
        storage.save_menu()
        return menu.is_tersedia
    except MenuTidakDitemukanError:
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal mengubah ketersediaan menu: {e}") from e


def hapus_menu(id_menu: str) -> None:
    """DELETE — Hapus menu secara permanen (Hard Delete).
    
    Menu tidak bisa dihapus jika sedang berada dalam pesanan aktif.
    """
    try:
        # Cek apakah menu ada di pesanan aktif
        for pesanan in storage.pesanan_aktif.values():
            for detail in pesanan.list_detail:
                if detail.item_menu.id_menu == id_menu:
                    raise RestoEaseError("Menu tidak bisa dihapus karena sedang ada di pesanan aktif.")
                
        menu = get_menu_by_id(id_menu)
        del storage.daftar_menu[id_menu]
        storage.save_menu()
    except (MenuTidakDitemukanError, RestoEaseError):
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal menghapus menu: {e}") from e


# ============================================================
# MEJA MANAGEMENT
# ============================================================

def get_semua_meja() -> list[Meja]:
    """READ — Ambil semua meja yang terdaftar."""
    try:
        return list(storage.daftar_meja.values())
    except Exception as e:
        raise RestoEaseError(f"Gagal mengambil daftar meja: {e}") from e


def get_meja_by_nomor(nomor_meja: int) -> Meja:
    """READ — Ambil satu meja berdasarkan nomor.
    
    Raise MenuTidakDitemukanError jika nomor meja tidak ada.
    """
    try:
        if nomor_meja not in storage.daftar_meja:
            raise MejaTidakTersediaError(f"Meja nomor {nomor_meja} tidak ditemukan")
        return storage.daftar_meja[nomor_meja]
    except MejaTidakTersediaError:
        raise
    except Exception as e:
        raise RestoEaseError(f"Kesalahan tidak terduga: {e}") from e


# ============================================================
# CRUD PESANAN (proses utama)
# ============================================================

def buat_pesanan_baru(nomor_meja: int) -> Pesanan:
    """CREATE — Buat pesanan baru untuk meja, set meja jadi terisi.
    
    Raise MejaTidakTersediaError jika meja sudah terisi atau belum ada.
    """
    try:
        if nomor_meja not in storage.daftar_meja:
            raise MejaTidakTersediaError(f"Meja nomor {nomor_meja} tidak ditemukan")

        meja = storage.daftar_meja[nomor_meja]

        if not meja.is_tersedia:
            raise MejaTidakTersediaError(
                f"Meja {nomor_meja} sedang terisi, tidak bisa membuat pesanan baru"
            )

        # Buat pesanan baru
        id_pesanan = _generate_id_pesanan()
        pesanan_baru = Pesanan(id_pesanan, meja)

        # Update state: meja terisi, pesanan terdaftar
        meja.set_status_meja(False)
        storage.pesanan_aktif[nomor_meja] = pesanan_baru

        # Simpan ke JSON
        storage.save_meja()
        storage.save_pesanan()

        return pesanan_baru

    except MejaTidakTersediaError:
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal membuat pesanan baru: {e}") from e


def get_pesanan_aktif(nomor_meja: int) -> Pesanan:
    """READ — Ambil pesanan aktif di meja tertentu.
    
    Raise PesananTidakAdaError jika meja tidak memiliki pesanan aktif.
    """
    try:
        if nomor_meja not in storage.pesanan_aktif:
            raise PesananTidakAdaError(
                f"Meja {nomor_meja} tidak memiliki pesanan aktif"
            )
        return storage.pesanan_aktif[nomor_meja]
    except PesananTidakAdaError:
        raise
    except Exception as e:
        raise RestoEaseError(f"Kesalahan tidak terduga: {e}") from e


def tambah_item_ke_pesanan(nomor_meja: int, id_menu: str, qty: int) -> None:
    """CREATE item — Tambah atau update item di pesanan aktif.
    
    Raise PesananTidakAdaError, MenuTidakDitemukanError, InputTidakValidError.
    """
    try:
        pesanan = get_pesanan_aktif(nomor_meja)
        menu = get_menu_by_id(id_menu)

        # Pastikan menu masih tersedia (belum di-soft-delete)
        if not menu.is_tersedia:
            raise MenuTidakDitemukanError(
                f"Menu '{menu.nama_menu}' sudah tidak tersedia"
            )

        # Delegasikan operasi ke model Pesanan (CRUD internal)
        pesanan.tambah_item(menu, qty)

        # Simpan perubahan ke JSON
        storage.save_pesanan()

    except (PesananTidakAdaError, MenuTidakDitemukanError, InputTidakValidError):
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal menambah item ke pesanan: {e}") from e


def update_item_pesanan(nomor_meja: int, id_menu: str, qty_baru: int) -> None:
    """UPDATE item — Ubah kuantitas item di pesanan aktif.
    
    Raise PesananTidakAdaError, ItemPesananTidakAdaError, InputTidakValidError.
    """
    try:
        pesanan = get_pesanan_aktif(nomor_meja)
        pesanan.update_kuantitas_item(id_menu, qty_baru)
        storage.save_pesanan()

    except (PesananTidakAdaError, ItemPesananTidakAdaError, InputTidakValidError):
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal mengupdate item pesanan: {e}") from e


def hapus_item_dari_pesanan(nomor_meja: int, id_menu: str) -> None:
    """DELETE item — Hapus item dari pesanan aktif.
    
    Raise PesananTidakAdaError, ItemPesananTidakAdaError.
    """
    try:
        pesanan = get_pesanan_aktif(nomor_meja)
        pesanan.hapus_item(id_menu)
        storage.save_pesanan()

    except (PesananTidakAdaError, ItemPesananTidakAdaError):
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal menghapus item dari pesanan: {e}") from e


def batalkan_pesanan(nomor_meja: int) -> None:
    """DELETE pesanan — Batalkan pesanan aktif dan kosongkan meja.
    
    Raise PesananTidakAdaError jika tidak ada pesanan aktif di meja ini.
    """
    try:
        pesanan = get_pesanan_aktif(nomor_meja)

        # Tandai pesanan sebagai dibatalkan
        pesanan.set_status("dibatalkan")

        # Kosongkan meja
        meja = storage.daftar_meja[nomor_meja]
        meja.set_status_meja(True)

        # Hapus dari pesanan aktif
        del storage.pesanan_aktif[nomor_meja]

        # Simpan perubahan
        storage.save_pesanan()
        storage.save_meja()

    except PesananTidakAdaError:
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal membatalkan pesanan: {e}") from e


# ============================================================
# TRANSAKSI / CHECKOUT
# ============================================================

def proses_checkout(nomor_meja: int, uang_diterima: float) -> Transaksi:
    """Selesaikan pesanan: hitung pajak, proses pembayaran, kosongkan meja.
    
    Alur lengkap:
    1. Ambil pesanan aktif meja
    2. Buat objek Transaksi dari pesanan tersebut
    3. Hitung total + pajak 10%
    4. Proses pembayaran (validasi uang, hitung kembalian)
    5. Set status pesanan = 'selesai'
    6. Kosongkan meja (is_tersedia = True)
    7. Pindahkan pesanan dari pesanan_aktif ke riwayat_transaksi
    8. Simpan semua ke JSON
    
    Raise PesananTidakAdaError, UangKurangError.
    """
    try:
        pesanan = get_pesanan_aktif(nomor_meja)

        # Pastikan ada item di pesanan sebelum checkout
        if not pesanan.list_detail:
            raise RestoEaseError("Pesanan kosong, tidak bisa checkout")

        # Buat transaksi baru
        id_transaksi = _generate_id_transaksi()
        transaksi = Transaksi(id_transaksi, pesanan)

        # Hitung total + pajak
        transaksi.hitung_pajak()

        # Proses pembayaran (raise UangKurangError jika kurang)
        transaksi.proses_pembayaran(uang_diterima)
        # Status pesanan di-set "selesai" di dalam proses_pembayaran()

        # Kosongkan meja
        meja = storage.daftar_meja[nomor_meja]
        meja.set_status_meja(True)

        # Pindahkan dari pesanan aktif ke riwayat transaksi
        del storage.pesanan_aktif[nomor_meja]
        storage.riwayat_transaksi.append(transaksi)

        # Simpan semua state ke JSON
        storage.save_meja()
        storage.save_pesanan()
        storage.save_transaksi()

        return transaksi

    except (PesananTidakAdaError, RestoEaseError):
        raise
    except Exception as e:
        raise RestoEaseError(f"Gagal memproses checkout: {e}") from e


def get_riwayat_transaksi() -> list[Transaksi]:
    """READ — Ambil seluruh riwayat transaksi yang sudah selesai."""
    try:
        return list(storage.riwayat_transaksi)
    except Exception as e:
        raise RestoEaseError(f"Gagal mengambil riwayat transaksi: {e}") from e


def hapus_semua_data() -> None:
    """Menghapus seluruh database dan mereset aplikasi."""
    try:
        storage.hapus_semua_data()
    except Exception as e:
        raise RestoEaseError(f"Gagal menghapus seluruh database: {e}") from e
