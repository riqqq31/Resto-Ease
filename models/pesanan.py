# models/pesanan.py
from .meja import Meja
from .item_katalog import ItemKatalog
from .detail_pesanan import DetailPesanan
from exceptions import ItemPesananTidakAdaError, InputTidakValidError

class Pesanan:
    """Blueprint pesanan restoran — mengelola list DetailPesanan.
    
    CRUD utama proyek ada di class ini:
    - CREATE: tambah_item()
    - READ:   get_item()
    - UPDATE: update_kuantitas_item()
    - DELETE: hapus_item()
    """

    def __init__(self, id_pesanan: str, meja_aktif: Meja):
        self.__id_pesanan = id_pesanan          # private
        self.__meja_aktif = meja_aktif          # private
        self.__status_pesanan = "aktif"         # "aktif" | "selesai" | "dibatalkan"
        self.__list_detail: list[DetailPesanan] = []

    # --- Properties ---

    @property
    def id_pesanan(self) -> str:
        return self.__id_pesanan

    @property
    def meja_aktif(self) -> Meja:
        return self.__meja_aktif

    @property
    def status_pesanan(self) -> str:
        return self.__status_pesanan

    @property
    def list_detail(self) -> list[DetailPesanan]:
        return self.__list_detail

    # --- CRUD METHODS (proses utama) ---

    def tambah_item(self, menu: ItemKatalog, qty: int) -> None:
        """CREATE — Tambah item baru ke pesanan.
        
        Jika item dengan id_menu yang sama sudah ada di pesanan,
        kuantitasnya akan ditambahkan.
        """
        for detail in self.__list_detail:
            if detail.item_menu.id_menu == menu.id_menu:
                qty_baru = detail.kuantitas + qty
                detail.set_kuantitas(qty_baru)
                return
        detail_baru = DetailPesanan(menu, qty)
        self.__list_detail.append(detail_baru)

    def get_item(self, id_menu: str) -> DetailPesanan | None:
        """READ — Cari detail pesanan berdasarkan id_menu."""
        for detail in self.__list_detail:
            if detail.item_menu.id_menu == id_menu:
                return detail
        return None

    def hitung_total_sementara(self) -> float:
        """Hitung total harga semua item di pesanan (sebelum pajak)."""
        return sum(d.sub_total for d in self.__list_detail)

    def update_kuantitas_item(self, id_menu: str, qty_baru: int) -> None:
        """UPDATE — Ubah kuantitas item yang sudah ada di pesanan."""
        detail = self.get_item(id_menu)
        if detail is None:
            raise ItemPesananTidakAdaError(
                f"Item dengan ID '{id_menu}' tidak ada di pesanan {self.__id_pesanan}"
            )
        detail.set_kuantitas(qty_baru)

    def hapus_item(self, id_menu: str) -> None:
        """DELETE — Hapus satu item dari pesanan."""
        for i, detail in enumerate(self.__list_detail):
            if detail.item_menu.id_menu == id_menu:
                self.__list_detail.pop(i)
                return
        raise ItemPesananTidakAdaError(
            f"Item dengan ID '{id_menu}' tidak ada di pesanan {self.__id_pesanan}"
        )

    def set_status(self, status: str) -> None:
        """Set status pesanan: 'aktif', 'selesai', atau 'dibatalkan'."""
        valid_status = {"aktif", "selesai", "dibatalkan"}
        if status not in valid_status:
            raise InputTidakValidError(
                f"Status pesanan harus salah satu dari {valid_status}"
            )
        self.__status_pesanan = status

    def to_dict(self) -> dict:
        """Konversi ke dictionary — JSON-serializable."""
        return {
            "id_pesanan": self.__id_pesanan,
            "meja_aktif": self.__meja_aktif.to_dict(),
            "status_pesanan": self.__status_pesanan,
            "list_detail": [d.to_dict() for d in self.__list_detail],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pesanan":
        """Factory method untuk membuat objek Pesanan dari dictionary."""
        meja_obj = Meja.from_dict(data["meja_aktif"])
        obj = cls(data["id_pesanan"], meja_obj)
        obj._Pesanan__status_pesanan = data.get("status_pesanan", "aktif")
        obj._Pesanan__list_detail = [
            DetailPesanan.from_dict(d) for d in data.get("list_detail", [])
        ]
        return obj

    def __repr__(self) -> str:
        return (
            f"Pesanan(id={self.__id_pesanan}, "
            f"meja={self.__meja_aktif.nomor_meja}, "
            f"status={self.__status_pesanan}, "
            f"items={len(self.__list_detail)})"
        )
