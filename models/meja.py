# models/meja.py
from exceptions import InputTidakValidError

class Meja:
    """Blueprint meja restoran.
    
    Menerapkan ENCAPSULATION dengan atribut private dan akses via property.
    """

    def __init__(self, nomor_meja: int):
        if nomor_meja < 1:
            raise InputTidakValidError("Nomor meja harus >= 1")
        self.__nomor_meja = nomor_meja  # private — ENCAPSULATION
        self.__is_tersedia = True

    @property
    def nomor_meja(self) -> int:
        return self.__nomor_meja

    @property
    def is_tersedia(self) -> bool:
        return self.__is_tersedia

    def set_status_meja(self, status: bool) -> None:
        """Set status ketersediaan meja secara eksplisit."""
        self.__is_tersedia = status

    def get_status_meja(self) -> bool:
        """Kembalikan status ketersediaan meja saat ini."""
        return self.__is_tersedia

    @staticmethod
    def label_status(is_tersedia: bool) -> str:
        """Return label string status meja untuk ditampilkan di UI.
        
        @staticmethod karena tidak memerlukan akses ke instance.
        """
        return "🟢 Kosong" if is_tersedia else "🔴 Terisi"

    @classmethod
    def from_dict(cls, data: dict) -> "Meja":
        """Factory method untuk membuat objek Meja dari dictionary."""
        obj = cls(data["nomor_meja"])
        obj._Meja__is_tersedia = data.get("is_tersedia", True)
        return obj

    def to_dict(self) -> dict:
        """Konversi ke dictionary — JSON-serializable."""
        return {
            "nomor_meja": self.__nomor_meja,
            "is_tersedia": self.__is_tersedia,
        }

    def __repr__(self) -> str:
        status = "Kosong" if self.__is_tersedia else "Terisi"
        return f"Meja(no={self.__nomor_meja}, status={status})"
