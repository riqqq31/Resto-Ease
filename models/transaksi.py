# models/transaksi.py
from .pesanan import Pesanan
from .validator import Validator

class Transaksi:
    """Blueprint transaksi pembayaran.
    
    Menghitung pajak (10%), memproses pembayaran, dan
    menghasilkan struk digital dari pesanan yang diselesaikan.
    """

    PERSEN_PAJAK = 10  # Pajak restoran 10%

    def __init__(self, id_transaksi: str, pesanan_terkait: Pesanan):
        self.__id_transaksi = id_transaksi
        self.__pesanan_terkait = pesanan_terkait
        self.__total_akhir = 0.0
        self.__pajak = 0.0
        self.__uang_diterima = 0.0
        self.__kembalian = 0.0

    # --- Properties ---

    @property
    def id_transaksi(self) -> str:
        return self.__id_transaksi

    @property
    def pesanan_terkait(self) -> Pesanan:
        return self.__pesanan_terkait

    @property
    def total_akhir(self) -> float:
        return self.__total_akhir

    @property
    def pajak(self) -> float:
        return self.__pajak

    @property
    def uang_diterima(self) -> float:
        return self.__uang_diterima

    @property
    def kembalian(self) -> float:
        return self.__kembalian

    # --- Methods ---

    def hitung_pajak(self) -> float:
        """Hitung pajak 10% dari subtotal pesanan."""
        subtotal = self.__pesanan_terkait.hitung_total_sementara()
        self.__pajak = subtotal * self.PERSEN_PAJAK / 100
        self.__total_akhir = subtotal + self.__pajak
        return self.__total_akhir

    def proses_pembayaran(self, uang_diterima: float) -> float:
        """Proses pembayaran: validasi uang, hitung kembalian.
        
        Raise UangKurangError jika uang tidak cukup.
        Return nilai kembalian.
        """
        if self.__total_akhir == 0.0:
            self.hitung_pajak()

        # Validasi uang diterima
        Validator.validasi_uang(uang_diterima, self.__total_akhir)

        self.__uang_diterima = uang_diterima
        self.__kembalian = uang_diterima - self.__total_akhir

        # Set status pesanan menjadi selesai
        self.__pesanan_terkait.set_status("selesai")

        return self.__kembalian

    def cetak_struk_digital(self) -> str:
        """Generate struk digital dalam format teks."""
        garis = "=" * 50
        garis_tipis = "-" * 50
        lines = [
            garis,
            "           RESTOEASE — STRUK DIGITAL",
            garis,
            f"  No. Transaksi : {self.__id_transaksi}",
            f"  No. Pesanan   : {self.__pesanan_terkait.id_pesanan}",
            f"  Meja          : {self.__pesanan_terkait.meja_aktif.nomor_meja}",
            garis_tipis,
            "  DETAIL PESANAN:",
            garis_tipis,
        ]

        for detail in self.__pesanan_terkait.list_detail:
            nama = detail.item_menu.nama_menu
            qty = detail.kuantitas
            harga_satuan = detail.item_menu.harga_efektif()
            subtotal = detail.sub_total
            lines.append(f"  {nama}")
            lines.append(
                f"    {qty} x {Transaksi.format_rupiah(harga_satuan)}"
                f"  =  {Transaksi.format_rupiah(subtotal)}"
            )

        subtotal_all = self.__pesanan_terkait.hitung_total_sementara()
        lines.extend([
            garis_tipis,
            f"  Subtotal       : {Transaksi.format_rupiah(subtotal_all)}",
            f"  Pajak ({self.PERSEN_PAJAK}%)    : {Transaksi.format_rupiah(self.__pajak)}",
            garis_tipis,
            f"  TOTAL AKHIR    : {Transaksi.format_rupiah(self.__total_akhir)}",
            f"  Uang Diterima  : {Transaksi.format_rupiah(self.__uang_diterima)}",
            f"  Kembalian      : {Transaksi.format_rupiah(self.__kembalian)}",
            garis,
            "        Terima kasih atas kunjungan Anda!",
            garis,
        ])

        return "\n".join(lines)

    @staticmethod
    def format_rupiah(nilai: float) -> str:
        """Format angka ke string Rupiah."""
        return f"Rp {nilai:,.0f}"

    @classmethod
    def from_dict(cls, data: dict) -> "Transaksi":
        """Factory method untuk membuat objek Transaksi dari dictionary."""
        pesanan_obj = Pesanan.from_dict(data["pesanan_terkait"])
        obj = cls(data["id_transaksi"], pesanan_obj)
        obj._Transaksi__total_akhir = data.get("total_akhir", 0.0)
        obj._Transaksi__pajak = data.get("pajak", 0.0)
        obj._Transaksi__uang_diterima = data.get("uang_diterima", 0.0)
        obj._Transaksi__kembalian = data.get("kembalian", 0.0)
        return obj

    def to_dict(self) -> dict:
        """Konversi ke dictionary — JSON-serializable."""
        return {
            "id_transaksi": self.__id_transaksi,
            "pesanan_terkait": self.__pesanan_terkait.to_dict(),
            "total_akhir": self.__total_akhir,
            "pajak": self.__pajak,
            "uang_diterima": self.__uang_diterima,
            "kembalian": self.__kembalian,
        }

    def __repr__(self) -> str:
        return (
            f"Transaksi(id={self.__id_transaksi}, "
            f"total={Transaksi.format_rupiah(self.__total_akhir)})"
        )
