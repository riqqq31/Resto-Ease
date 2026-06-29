# models/menu.py
from .item_katalog import ItemKatalog
from .validator import Validator
from exceptions import InputTidakValidError

class Menu(ItemKatalog):
    """Blueprint menu makanan/minuman standar.
    
    Menerapkan ENCAPSULATION dengan atribut private (__) dan protected (_),
    diakses melalui @property. Validasi dilakukan di constructor dan setter.
    """

    def __init__(self, id_menu: str, nama_menu: str, harga: float, kategori: str):
        # Validasi semua input sebelum menyimpan — INPUT VALIDATION
        Validator.wajib_isi(id_menu, "ID Menu")
        Validator.wajib_isi(nama_menu, "Nama Menu")
        Validator.wajib_positif(harga, "Harga")
        Validator.wajib_kategori(kategori)

        # Atribut private — ENCAPSULATION
        self.__id_menu = id_menu
        self.__nama_menu = nama_menu
        self.__harga = harga
        self.__kategori = kategori
        self._is_tersedia = True  # protected — bisa diakses subclass

    # --- Properties (getter) — akses terkontrol ke atribut private ---

    @property
    def id_menu(self) -> str:
        return self.__id_menu

    @property
    def nama_menu(self) -> str:
        return self.__nama_menu

    @property
    def harga(self) -> float:
        return self.__harga

    @property
    def kategori(self) -> str:
        return self.__kategori

    @property
    def is_tersedia(self) -> bool:
        return self._is_tersedia

    # --- Setter dengan validasi — ENCAPSULATION ---

    @harga.setter
    def harga(self, nilai: float) -> None:
        """Set harga baru dengan validasi terlebih dahulu."""
        Validator.wajib_positif(nilai, "Harga")
        self.__harga = nilai

    @nama_menu.setter
    def nama_menu(self, nilai: str) -> None:
        """Set nama menu baru dengan validasi terlebih dahulu."""
        Validator.wajib_isi(nilai, "Nama Menu")
        self.__nama_menu = nilai

    # --- Instance methods ---

    def update_harga(self, harga_baru: float) -> None:
        """Update harga menu dengan validasi."""
        self.harga = harga_baru  # memanfaatkan setter yang sudah ada

    def ganti_status_ketersediaan(self) -> None:
        """Toggle status ketersediaan menu (tersedia <-> tidak tersedia)."""
        self._is_tersedia = not self._is_tersedia

    def set_ketersediaan(self, status: bool) -> None:
        """Set status ketersediaan secara eksplisit."""
        self._is_tersedia = status

    # --- Implementasi abstract method dari ItemKatalog ---

    def get_info(self) -> str:
        """Kembalikan string deskripsi menu — POLYMORPHISM.
        
        Output berbeda antara Menu biasa dan MenuSpesial karena
        MenuSpesial meng-override method ini.
        """
        status = "Tersedia" if self._is_tersedia else "Habis"
        return (
            f"[{self.__id_menu}] {self.__nama_menu} — "
            f"Rp {self.__harga:,.0f} ({self.__kategori}) [{status}]"
        )

    def harga_efektif(self) -> float:
        """Harga efektif Menu biasa = harga asli tanpa modifikasi."""
        return self.__harga

    def to_dict(self) -> dict:
        """Konversi ke dictionary — JSON-serializable."""
        return {
            "id_menu": self.__id_menu,
            "nama_menu": self.__nama_menu,
            "harga": self.__harga,
            "kategori": self.__kategori,
            "is_tersedia": self._is_tersedia,
            "tipe": "Menu",
        }

    # --- @staticmethod ---

    @staticmethod
    def buat_id(nama: str) -> str:
        """Generate id_menu otomatis dari nama menu.
        
        Contoh: 'Nasi Goreng' -> 'MNU-NASIGORENG'
        """
        cleaned = "".join(c for c in nama if c.isalnum())
        return f"MNU-{cleaned.upper()}"

    # --- @classmethod ---

    @classmethod
    def from_dict(cls, data: dict) -> "Menu":
        """Buat objek Menu dari dictionary."""
        obj = cls(
            id_menu=data["id_menu"],
            nama_menu=data["nama_menu"],
            harga=data["harga"],
            kategori=data["kategori"],
        )
        obj._is_tersedia = data.get("is_tersedia", True)
        return obj

    def __repr__(self) -> str:
        return f"Menu(id={self.__id_menu}, nama={self.__nama_menu})"


class MenuSpesial(Menu):
    """Menu dengan diskon persentase — subclass dari Menu.
    
    Menerapkan INHERITANCE (extends Menu) dan POLYMORPHISM
    (override get_info() dan harga_efektif()).
    """

    def __init__(self, id_menu: str, nama_menu: str, harga: float,
                 kategori: str, persen_diskon: float):
        # Panggil constructor parent — INHERITANCE
        super().__init__(id_menu, nama_menu, harga, kategori)
        # Validasi diskon
        Validator.wajib_rentang(persen_diskon, 0.01, 99.99, "Diskon")
        self.__persen_diskon = persen_diskon  # private

    @property
    def persen_diskon(self) -> float:
        return self.__persen_diskon

    @persen_diskon.setter
    def persen_diskon(self, nilai: float) -> None:
        """Set diskon baru dengan validasi."""
        Validator.wajib_rentang(nilai, 0.01, 99.99, "Diskon")
        self.__persen_diskon = nilai

    def harga_efektif(self) -> float:
        """OVERRIDE — harga setelah diskon diterapkan."""
        return self.harga * (1 - self.__persen_diskon / 100)

    def get_info(self) -> str:
        """OVERRIDE — tampilkan info menu + label diskon."""
        status = "Tersedia" if self.is_tersedia else "Habis"
        harga_diskon = self.harga_efektif()
        return (
            f"[{self.id_menu}] {self.nama_menu} — "
            f"Rp {self.harga:,.0f} → Rp {harga_diskon:,.0f} "
            f"(Diskon {self.__persen_diskon:.0f}%) "
            f"({self.kategori}) [{status}]"
        )

    def to_dict(self) -> dict:
        """Override to_dict — tambahkan field persen_diskon dan tipe."""
        data = super().to_dict()
        data["persen_diskon"] = self.__persen_diskon
        data["tipe"] = "MenuSpesial"
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "MenuSpesial":
        """Factory method untuk membuat MenuSpesial dari dictionary."""
        obj = cls(
            id_menu=data["id_menu"],
            nama_menu=data["nama_menu"],
            harga=data["harga"],
            kategori=data["kategori"],
            persen_diskon=data["persen_diskon"],
        )
        obj._is_tersedia = data.get("is_tersedia", True)
        return obj

    def __repr__(self) -> str:
        return (
            f"MenuSpesial(id={self.id_menu}, nama={self.nama_menu}, "
            f"diskon={self.__persen_diskon}%)"
        )
