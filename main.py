# main.py — Entry Point CLI RestoEase
# Berisi program utama berbasis Command Line Interface (CLI) / Konsol.
# Berbagi logic & storage yang sama dengan gui.py.

import os
import sys
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

def clear_screen():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def tampilkan_header(sub_title: str = ""):
    """Tampilkan header aplikasi RestoEase."""
    print("=" * 65)
    print("🍽️  RESTOEASE - SISTEM PEMESANAN DIGITAL RESTORAN  🍽️")
    print("=" * 65)
    if sub_title:
        print(f"📌 {sub_title.upper()}")
        print("-" * 65)


def pause():
    """Menunggu input user sebelum lanjut."""
    print("\nTekan Enter untuk melanjutkan...")
    input()


def input_integer(prompt: str) -> int:
    """Membaca input integer dengan validasi format."""
    while True:
        try:
            val = input(prompt)
            if not val.strip():
                return 0
            return int(val)
        except ValueError:
            print("❌ Input harus berupa angka bulat!")


def input_float(prompt: str) -> float:
    """Membaca input float dengan validasi format."""
    while True:
        try:
            val = input(prompt)
            if not val.strip():
                return 0.0
            return float(val)
        except ValueError:
            print("❌ Input harus berupa angka desimal/bulat!")


# ============================================================
# FITUR MENU 1 — LIHAT PETA MEJA
# ============================================================

def menu_peta_meja():
    clear_screen()
    tampilkan_header("PETA MEJA")
    
    semua_meja = service.get_semua_meja()
    semua_meja_sorted = sorted(semua_meja, key=lambda m: m.nomor_meja)
    
    # Menampilkan meja dalam bentuk grid 4 kolom
    n_cols = 4
    for i in range(0, len(semua_meja_sorted), n_cols):
        baris_meja = semua_meja_sorted[i:i+n_cols]
        tampilan_baris = []
        for meja in baris_meja:
            status = "🟢 KOSONG" if meja.is_tersedia else "🔴 TERISI"
            tampilan_baris.append(f"[ Meja {meja.nomor_meja} : {status} ]")
        print("   ".join(tampilan_baris))
    
    print("-" * 65)
    print("Keterangan: 🟢 KOSONG = Siap pakai | 🔴 TERISI = Ada pesanan aktif")


# ============================================================
# FITUR MENU 2 — KELOLA PESANAN MEJA (CRUD UTAMA)
# ============================================================

def tampilkan_detail_pesanan(nomor_meja: int) -> bool:
    """Tampilkan ringkasan pesanan aktif meja. Return True jika ada pesanan."""
    try:
        pesanan = service.get_pesanan_aktif(nomor_meja)
        print(f"\nID Pesanan : {pesanan.id_pesanan}")
        print(f"Status     : {pesanan.status_pesanan.upper()}")
        print("-" * 65)
        print(f"{'Nama Menu':<30} | {'Qty':<5} | {'Harga':<10} | {'Subtotal':<12}")
        print("-" * 65)
        for detail in pesanan.list_detail:
            nama = detail.item_menu.nama_menu
            qty = detail.kuantitas
            harga = detail.item_menu.harga_efektif()
            sub = detail.sub_total
            print(f"{nama:<30} | {qty:<5} | {harga:<10,.0f} | {sub:<12,.0f}")
        
        print("-" * 65)
        subtotal = pesanan.hitung_total_sementara()
        pajak = subtotal * 0.1
        total = subtotal + pajak
        print(f"Subtotal       : Rp {subtotal:,.0f}")
        print(f"Pajak (10%)    : Rp {pajak:,.0f}")
        print(f"Estimasi Total : Rp {total:,.0f}")
        return True
    except PesananTidakAdaError:
        print(f"❌ Tidak ada pesanan aktif di Meja {nomor_meja}.")
        return False
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
        return False


def menu_kelola_pesanan():
    while True:
        clear_screen()
        tampilkan_header("KELOLA PESANAN MEJA")
        
        # Tampilkan peta meja singkat
        semua_meja = service.get_semua_meja()
        meja_str = []
        for m in sorted(semua_meja, key=lambda x: x.nomor_meja):
            status = "🔴" if not m.is_tersedia else f"{m.nomor_meja}"
            meja_str.append(status)
        print("Peta Meja: [ " + " | ".join(meja_str) + " ]  (🔴 = Terisi)")
        print("-" * 65)
        
        nomor_meja = input_integer("Pilih Nomor Meja (1-8, atau 0 untuk kembali): ")
        if nomor_meja == 0:
            break
            
        # Validasi nomor meja
        meja_list = [m.nomor_meja for m in semua_meja]
        if nomor_meja not in meja_list:
            print(f"❌ Meja nomor {nomor_meja} tidak terdaftar!")
            pause()
            continue
            
        meja = next(m for m in semua_meja if m.nomor_meja == nomor_meja)
        
        # Alur Submenu Pesanan
        if meja.is_tersedia:
            print(f"\nMeja {nomor_meja} sedang KOSONG.")
            pilihan = input("Apakah ingin membuka pesanan baru? (y/n): ").strip().lower()
            if pilihan == 'y':
                try:
                    service.buat_pesanan_baru(nomor_meja)
                    print(f"✅ Berhasil membuat pesanan baru untuk Meja {nomor_meja}!")
                except RestoEaseError as e:
                    print(f"❌ Gagal: {e}")
                pause()
        else:
            # Meja terisi, kelola pesanan
            while True:
                clear_screen()
                tampilkan_header(f"PESANAN MEJA {nomor_meja}")
                ada = tampilkan_detail_pesanan(nomor_meja)
                if not ada:
                    pause()
                    break
                    
                print("\nOpsi Kelola Pesanan:")
                print("1. Tambah Menu ke Pesanan")
                print("2. Ubah Jumlah (Kuantitas) Item")
                print("3. Hapus Item dari Pesanan")
                print("4. Batalkan Seluruh Pesanan")
                print("0. Kembali ke Menu Sebelumnya")
                opt = input("Pilih Opsi: ").strip()
                
                if opt == "1":
                    # Tambah Menu
                    clear_screen()
                    tampilkan_header(f"TAMBAH MENU KE MEJA {nomor_meja}")
                    menu_tersedia = service.get_menu_tersedia()
                    if not menu_menu_list(menu_tersedia):
                        pause()
                        continue
                    
                    id_menu = input("\nMasukkan ID Menu yang ingin dipesan: ").strip().upper()
                    qty = input_integer("Masukkan Jumlah (Qty): ")
                    try:
                        service.tambah_item_ke_pesanan(nomor_meja, id_menu, qty)
                        print(f"✅ Item berhasil ditambahkan ke Meja {nomor_meja}!")
                    except RestoEaseError as e:
                        print(f"❌ Gagal menambahkan item: {e}")
                    pause()
                    
                elif opt == "2":
                    # Ubah Kuantitas
                    id_menu = input("\nMasukkan ID Menu yang ingin diubah kuantitasnya: ").strip().upper()
                    qty_baru = input_integer("Masukkan Jumlah Baru (Qty): ")
                    try:
                        service.update_item_pesanan(nomor_meja, id_menu, qty_baru)
                        print(f"✅ Kuantitas item berhasil diupdate!")
                    except RestoEaseError as e:
                        print(f"❌ Gagal mengupdate kuantitas: {e}")
                    pause()
                    
                elif opt == "3":
                    # Hapus Item
                    id_menu = input("\nMasukkan ID Menu yang ingin dihapus dari pesanan: ").strip().upper()
                    try:
                        service.hapus_item_dari_pesanan(nomor_meja, id_menu)
                        print(f"✅ Item berhasil dihapus dari pesanan!")
                    except RestoEaseError as e:
                        print(f"❌ Gagal menghapus item: {e}")
                    pause()
                    
                elif opt == "4":
                    # Batalkan pesanan
                    konfirmasi = input(f"⚠️ Apakah Anda yakin ingin membatalkan pesanan Meja {nomor_meja}? (y/n): ").strip().lower()
                    if konfirmasi == 'y':
                        try:
                            service.batalkan_pesanan(nomor_meja)
                            print(f"✅ Pesanan Meja {nomor_meja} telah dibatalkan!")
                            pause()
                            break  # keluar dari submenu meja karena pesanan sudah dibatalkan
                        except RestoEaseError as e:
                            print(f"❌ Gagal membatalkan pesanan: {e}")
                            pause()
                            
                elif opt == "0":
                    break


def menu_menu_list(daftar_menu: list) -> bool:
    """Helper untuk menampilkan daftar menu."""
    if not daftar_menu:
        print("❌ Tidak ada menu tersedia dalam kategori ini.")
        return False
    
    print(f"{'ID':<15} | {'Nama Menu':<25} | {'Kategori':<10} | {'Harga':<10}")
    print("-" * 65)
    for menu in daftar_menu:
        from models import MenuSpesial
        is_spesial = isinstance(menu, MenuSpesial)
        harga_display = f"Rp {menu.harga_efektif():,.0f}"
        if is_spesial:
            harga_display += f" (Diskon {menu.persen_diskon:.0f}%)"
            
        print(f"{menu.id_menu:<15} | {menu.nama_menu:<25} | {menu.kategori:<10} | {harga_display}")
    return True


# ============================================================
# FITUR MENU 3 — KASIR / CHECKOUT
# ============================================================

def menu_kasir():
    clear_screen()
    tampilkan_header("KASIR / CHECKOUT")
    
    # List meja terisi
    semua_meja = service.get_semua_meja()
    meja_terisi = [m for m in semua_meja if not m.is_tersedia]
    
    if not meja_terisi:
        print("ℹ️ Tidak ada meja yang terisi saat ini.")
        pause()
        return
        
    print("Meja terisi aktif: " + ", ".join([f"Meja {m.nomor_meja}" for m in meja_terisi]))
    print("-" * 65)
    
    nomor_meja = input_integer("Pilih nomor meja untuk Checkout (0 untuk kembali): ")
    if nomor_meja == 0:
        return
        
    if nomor_meja not in [m.nomor_meja for m in meja_terisi]:
        print(f"❌ Meja {nomor_meja} tidak terisi atau tidak ditemukan!")
        pause()
        return
        
    clear_screen()
    tampilkan_header(f"CHECKOUT MEJA {nomor_meja}")
    
    try:
        pesanan = service.get_pesanan_aktif(nomor_meja)
        if not pesanan.list_detail:
            print("❌ Pesanan kosong. Tambahkan item sebelum melakukan checkout.")
            pause()
            return
            
        tampilkan_detail_pesanan(nomor_meja)
        print("-" * 65)
        
        subtotal = pesanan.hitung_total_sementara()
        pajak = subtotal * 0.1
        total = subtotal + pajak
        
        uang_diterima = input_float(f"Masukkan Uang Diterima (Total: Rp {total:,.0f}): ")
        
        # Proses checkout
        transaksi = service.proses_checkout(nomor_meja, uang_diterima)
        
        clear_screen()
        tampilkan_header("PEMBAYARAN BERHASIL")
        print("✅ Transaksi selesai! Struk digital dicetak di bawah ini:\n")
        print(transaksi.cetak_struk_digital())
        print("=" * 65)
        
    except RestoEaseError as e:
        print(f"\n❌ Transaksi Gagal: {e}")
        
    pause()


# ============================================================
# FITUR MENU 4 — KELOLA MENU RESTORAN
# ============================================================

def menu_kelola_menu_restoran():
    while True:
        clear_screen()
        tampilkan_header("KELOLA MENU RESTORAN")
        print("1. Tampilkan Daftar Menu")
        print("2. Tambah Menu Baru")
        print("3. Update Harga Menu")
        print("4. Toggle Status Ketersediaan Menu")
        print("5. Hapus Menu (Soft Delete)")
        print("0. Kembali ke Menu Utama")
        print("-" * 65)
        
        opt = input("Pilih Opsi: ").strip()
        
        if opt == "1":
            # Tampilkan menu
            clear_screen()
            tampilkan_header("DAFTAR MENU RESTORAN")
            semua_menu = service.get_semua_menu()
            
            # Sub-filter
            print("Filter Menu:")
            print("1. Semua Menu (Aktif & Nonaktif)")
            print("2. Menu Aktif/Tersedia Saja")
            print("3. Menu Makanan Saja")
            print("4. Menu Minuman Saja")
            f_opt = input("Pilih filter: ").strip()
            
            clear_screen()
            tampilkan_header("DAFTAR MENU RESTORAN")
            if f_opt == "2":
                menu_list = service.get_menu_tersedia()
            elif f_opt == "3":
                menu_list = service.get_menu_by_kategori("Makanan")
            elif f_opt == "4":
                menu_list = service.get_menu_by_kategori("Minuman")
            else:
                menu_list = semua_menu
                
            if not menu_list:
                print("ℹ️ Tidak ada menu yang terdaftar.")
            else:
                print(f"{'ID':<15} | {'Nama Menu':<25} | {'Kategori':<10} | {'Harga':<10} | {'Status':<10}")
                print("-" * 65)
                for menu in menu_list:
                    from models import MenuSpesial
                    is_spesial = isinstance(menu, MenuSpesial)
                    status_str = "Tersedia" if menu.is_tersedia else "Nonaktif"
                    harga_str = f"Rp {menu.harga_efektif():,.0f}"
                    if is_spesial:
                        harga_str += f" (-{menu.persen_diskon:.0f}%)"
                    print(f"{menu.id_menu:<15} | {menu.nama_menu:<25} | {menu.kategori:<10} | {harga_str:<10} | {status_str:<10}")
            pause()
            
        elif opt == "2":
            # Tambah Menu Baru
            clear_screen()
            tampilkan_header("TAMBAH MENU BARU")
            nama = input("Masukkan Nama Menu: ").strip()
            if not nama:
                print("❌ Nama menu tidak boleh kosong!")
                pause()
                continue
                
            kat_opt = input("Pilih Kategori (1. Makanan | 2. Minuman): ").strip()
            kategori = "Makanan" if kat_opt == "1" else "Minuman"
            
            harga = input_float("Masukkan Harga (Rp): ")
            
            is_special_opt = input("Apakah menu ini Spesial / Ada Diskon? (y/n): ").strip().lower()
            persen_diskon = 0.0
            if is_special_opt == 'y':
                persen_diskon = input_float("Masukkan Persentase Diskon (1 - 99): ")
            
            try:
                menu_baru = service.tambah_menu(nama, harga, kategori, persen_diskon)
                print(f"\n✅ Menu baru berhasil ditambahkan!")
                print(f"ID Menu  : {menu_baru.id_menu}")
                print(f"Nama     : {menu_baru.nama_menu}")
                print(f"Kategori : {menu_baru.kategori}")
                print(f"Harga Ef : Rp {menu_baru.harga_efektif():,.0f}")
            except RestoEaseError as e:
                print(f"\n❌ Gagal menambahkan menu: {e}")
            pause()
            
        elif opt == "3":
            # Update Harga Menu
            clear_screen()
            tampilkan_header("UPDATE HARGA MENU")
            id_menu = input("Masukkan ID Menu: ").strip().upper()
            harga_baru = input_float("Masukkan Harga Baru (Rp): ")
            try:
                service.update_harga_menu(id_menu, harga_baru)
                print("✅ Harga menu berhasil diupdate!")
            except RestoEaseError as e:
                print(f"❌ Gagal update harga: {e}")
            pause()
            
        elif opt == "4":
            # Toggle Status Ketersediaan
            clear_screen()
            tampilkan_header("TOGGLE STATUS KETERSEDIAAN")
            id_menu = input("Masukkan ID Menu: ").strip().upper()
            try:
                status_baru = service.toggle_ketersediaan_menu(id_menu)
                status_str = "Tersedia" if status_baru else "Tidak Tersedia"
                print(f"✅ Status ketersediaan menu diubah menjadi: {status_str}")
            except RestoEaseError as e:
                print(f"❌ Gagal mengubah status: {e}")
            pause()
            
        elif opt == "5":
            # Hapus Menu (Soft Delete)
            clear_screen()
            tampilkan_header("HAPUS MENU (SOFT DELETE)")
            id_menu = input("Masukkan ID Menu yang ingin dinonaktifkan: ").strip().upper()
            konfirmasi = input(f"Apakah yakin ingin menonaktifkan menu '{id_menu}' dari katalog? (y/n): ").strip().lower()
            if konfirmasi == 'y':
                try:
                    service.hapus_menu(id_menu)
                    print("✅ Menu berhasil dinonaktifkan dari katalog penjualan.")
                except RestoEaseError as e:
                    print(f"❌ Gagal menghapus menu: {e}")
            pause()
            
        elif opt == "0":
            break


# ============================================================
# FITUR MENU 5 — LIHAT RIWAYAT TRANSAKSI
# ============================================================

def menu_riwayat_transaksi():
    clear_screen()
    tampilkan_header("RIWAYAT TRANSAKSI")
    
    riwayat = service.get_riwayat_transaksi()
    if not riwayat:
        print("ℹ️ Belum ada transaksi yang diselesaikan hari ini.")
        pause()
        return
        
    total_pendapatan = sum(t.total_akhir for t in riwayat)
    print(f"Total Transaksi  : {len(riwayat)}")
    print(f"Total Pendapatan : Rp {total_pendapatan:,.0f}")
    print("-" * 65)
    
    print("Daftar Transaksi Terbaru:")
    for idx, trx in enumerate(reversed(riwayat), 1):
        meja_no = trx.pesanan_terkait.meja_aktif.nomor_meja
        print(f"{idx}. {trx.id_transaksi} | Meja {meja_no} | Total: Rp {trx.total_akhir:,.0f}")
        
    print("-" * 65)
    pilih = input_integer("Pilih nomor transaksi untuk cetak struk lengkap (0 untuk kembali): ")
    if pilih == 0:
        return
        
    # Validasi input index
    if pilih < 1 or pilih > len(riwayat):
        print("❌ Transaksi tidak ditemukan!")
        pause()
        return
        
    # Ambil transaksi (diambil dari reversed)
    trx_terpilih = list(reversed(riwayat))[pilih - 1]
    
    clear_screen()
    tampilkan_header(f"STRUK {trx_terpilih.id_transaksi}")
    print(trx_terpilih.cetak_struk_digital())
    print("=" * 65)
    pause()


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    # Mengatasi UnicodeEncodeError di Windows Terminal
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            pass
            
    # Inisialisasi storage & data
    storage.init_storage()
    
    while True:
        clear_screen()
        tampilkan_header("MENU UTAMA")
        print("1. 🗺️  Lihat Peta Meja")
        print("2. 📋  Kelola Pesanan Meja")
        print("3. 💳  Kasir / Checkout")
        print("4. 🍳  Kelola Menu Restoran")
        print("5. 📜  Lihat Riwayat Transaksi")
        print("0. ❌  Keluar Aplikasi")
        print("=" * 65)
        
        opt = input("Pilih Menu: ").strip()
        
        if opt == "1":
            menu_peta_meja()
            pause()
        elif opt == "2":
            menu_kelola_pesanan()
        elif opt == "3":
            menu_kasir()
        elif opt == "4":
            menu_kelola_menu_restoran()
        elif opt == "5":
            menu_riwayat_transaksi()
        elif opt == "0":
            clear_screen()
            print("Terima kasih telah menggunakan RestoEase! Sampai jumpa.")
            sys.exit(0)
        else:
            print("❌ Pilihan tidak valid!")
            pause()


if __name__ == "__main__":
    main()
