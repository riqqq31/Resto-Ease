# models/item_katalog.py
from abc import ABC, abstractmethod

class ItemKatalog(ABC):
    """Abstract base class untuk semua item yang bisa dipesan.
    
    Mendefinisikan kontrak (interface) yang WAJIB diimplementasi oleh
    setiap subclass. Caller cukup tahu method-method ini tanpa perlu
    tahu detail implementasinya — prinsip ABSTRACTION.
    """

    @abstractmethod
    def get_info(self) -> str:
        """Kembalikan string deskripsi item untuk ditampilkan di UI."""
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        """Konversi objek ke dictionary agar bisa di-serialize ke JSON."""
        ...

    @abstractmethod
    def harga_efektif(self) -> float:
        """Kembalikan harga yang benar-benar dipakai saat menghitung pesanan.
        
        Untuk Menu biasa = harga asli.
        Untuk MenuSpesial = harga setelah diskon.
        """
        ...
