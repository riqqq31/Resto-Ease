# exceptions.py — Semua custom exception untuk RestoEase
# File ini berisi hierarchy exception yang digunakan di seluruh aplikasi.
# Semua exception turunan dari RestoEaseError agar mudah ditangkap secara general.


class RestoEaseError(Exception):
    """Base exception untuk semua error di RestoEase.
    
    Semua custom exception lain harus inherit dari class ini
    agar bisa ditangkap secara umum dengan satu blok except.
    """
    pass


class MenuTidakDitemukanError(RestoEaseError):
    """Raised saat id_menu tidak ada di daftar_menu.
    
    Contoh: user mencoba mengakses menu dengan ID yang tidak terdaftar,
    atau mencoba menghapus/update menu yang sudah tidak ada.
    """
    pass


class MejaTidakTersediaError(RestoEaseError):
    """Raised saat meja sedang terisi dan tidak bisa dipilih.
    
    Contoh: user mencoba membuat pesanan baru di meja yang
    statusnya sudah 'Terisi' (is_tersedia = False).
    """
    pass


class PesananTidakAdaError(RestoEaseError):
    """Raised saat mencoba akses pesanan di meja yang tidak punya pesanan aktif.
    
    Contoh: user mencoba menambah item atau checkout di meja
    yang belum memiliki pesanan aktif.
    """
    pass


class InputTidakValidError(RestoEaseError):
    """Raised saat input gagal validasi.
    
    Contoh kasus:
    - Harga bernilai negatif atau nol
    - Kuantitas kurang dari 1
    - String nama/ID kosong atau hanya spasi
    - Kategori bukan 'Makanan' atau 'Minuman'
    - Diskon di luar rentang 0-100%
    """
    pass


class UangKurangError(RestoEaseError):
    """Raised saat uang_diterima < total_akhir saat checkout.
    
    Contoh: total tagihan Rp 150.000 tapi uang yang diberikan
    hanya Rp 100.000.
    """
    pass


class ItemPesananTidakAdaError(RestoEaseError):
    """Raised saat mencoba update/delete item yang tidak ada di pesanan.
    
    Contoh: user mencoba mengubah kuantitas atau menghapus item menu
    dari keranjang pesanan, tapi item tersebut tidak ditemukan di
    daftar detail pesanan aktif.
    """
    pass
