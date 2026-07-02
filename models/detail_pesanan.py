# models/detail_pesanan.py
from .item_katalog import ItemKatalog
from .menu import Menu, MenuSpesial
from .validator import Validator

class DetailPesanan:
    """Detail satu item dalam pesanan (menu + kuantitas + subtotal).
    
    Class ini adalah bagian dari komposisi Pesanan → DetailPesanan.
    Jika Pesanan dihapus, DetailPesanan juga ikut hilang.
    """

    def __init__(self, item_menu: ItemKatalog, kuantitas: int):
        Validator.wajib_positif(kuantitas, "Kuantitas")
        self.__item_menu = item_menu      # private — referensi ke objek Menu/MenuSpesial
        self.__kuantitas = kuantitas      # private
        self.__sub_total = self.kalkulasi_sub_total()

    @property
    def item_menu(self) -> ItemKatalog:
        return self.__item_menu

    @property
    def kuantitas(self) -> int:
        return self.__kuantitas

    @property
    def sub_total(self) -> float:
        return self.__sub_total

    def set_kuantitas(self, qty: int) -> None:
        """UPDATE kuantitas item — bagian dari CRUD pesanan.
        
        Validasi qty terlebih dahulu, lalu recalculate subtotal.
        """
        Validator.wajib_positif(qty, "Kuantitas")
        self.__kuantitas = qty
        self.__sub_total = self.kalkulasi_sub_total()

    def kalkulasi_sub_total(self) -> float:
        """Hitung subtotal = harga_efektif * kuantitas.
        
        Menggunakan harga_efektif() yang bersifat POLYMORPHIC:
        - Untuk Menu biasa: harga asli
        - Untuk MenuSpesial: harga setelah diskon
        """
        return self.__item_menu.harga_efektif() * self.__kuantitas

    def to_dict(self) -> dict:
        """Konversi ke dictionary — JSON-serializable."""
        return {
            "item_menu": self.__item_menu.to_dict(),
            "kuantitas": self.__kuantitas,
            "sub_total": self.__sub_total,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DetailPesanan":
        """Factory method: buat DetailPesanan dari dictionary.
        
        Mendeteksi tipe menu (Menu vs MenuSpesial) berdasarkan
        field 'tipe' untuk menjaga sifat POLYMORPHISM saat load data.
        """
        tipe = data["item_menu"].get("tipe", "Menu")
        if tipe == "MenuSpesial":
            menu_obj = MenuSpesial.from_dict(data["item_menu"])
        else:
            menu_obj = Menu.from_dict(data["item_menu"])
        obj = cls(menu_obj, data["kuantitas"])
        return obj

    def __repr__(self) -> str:
        return (
            f"DetailPesanan(menu={self.__item_menu.nama_menu}, "
            f"qty={self.__kuantitas}, subtotal={self.__sub_total:,.0f})"
        )
