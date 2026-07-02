# models/validator.py
from exceptions import InputTidakValidError, UangKurangError

class Validator:
    """Kelas utilitas validasi input — semua method adalah @staticmethod.
    
    Menyembunyikan detail logika validasi di balik method yang sederhana
    sehingga caller cukup memanggil satu baris tanpa menulis if/else sendiri.
    Ini merupakan penerapan prinsip ABSTRACTION.
    """

    @staticmethod
    def wajib_isi(nilai: str, nama_field: str) -> None:
        """Raise InputTidakValidError jika string kosong atau hanya spasi."""
        if not nilai or not nilai.strip():
            raise InputTidakValidError(f"{nama_field} tidak boleh kosong")

    @staticmethod
    def wajib_positif(nilai: float, nama_field: str) -> None:
        """Raise InputTidakValidError jika nilai <= 0."""
        if nilai <= 0:
            raise InputTidakValidError(f"{nama_field} harus lebih dari 0, diterima: {nilai}")

    @staticmethod
    def wajib_rentang(nilai: float, min_val: float, max_val: float, nama_field: str) -> None:
        """Raise InputTidakValidError jika nilai berada di luar [min_val, max_val] (inklusif)."""
        if not (min_val <= nilai <= max_val):
            raise InputTidakValidError(
                f"{nama_field} harus antara {min_val} dan {max_val}, diterima: {nilai}"
            )

    @staticmethod
    def wajib_kategori(kategori: str) -> None:
        """Raise InputTidakValidError jika kategori bukan Makanan/Minuman."""
        valid = {"Makanan", "Minuman"}
        if kategori not in valid:
            raise InputTidakValidError(f"Kategori harus salah satu dari {valid}")

    @staticmethod
    def validasi_uang(uang: float, total: float) -> None:
        """Raise UangKurangError jika uang < total."""
        if uang < total:
            raise UangKurangError(
                f"Uang diterima Rp {uang:,.0f} kurang dari total Rp {total:,.0f}"
            )
