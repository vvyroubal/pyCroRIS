"""Zajednički modeli koji se koriste u svim CroRIS API modulima."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranslatedText:
    """Višejezični tekst s oznakom jezika (HAL+JSON ml zapis)."""

    lang_code: str
    naziv: str
    lang_name: Optional[str] = None
    original: bool = False
    ml_record_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "TranslatedText":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            lang_code=data.get("cfLangCode", ""),
            naziv=data.get("naziv", ""),
            lang_name=data.get("cfLangName"),
            original=data.get("original", False),
            ml_record_id=data.get("mlRecordId"),
        )


@dataclass
class Klasifikacija:
    """Generički klasifikacijski zapis s identifikatorom i nazivom."""

    id: int
    naziv: str

    @classmethod
    def from_dict(cls, data: dict) -> "Klasifikacija":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(id=data.get("id", 0), naziv=data.get("naziv", ""))


def get_text(items: list[TranslatedText], lang: str = "hr") -> str:
    """Vrati tekst za zadani jezik; fallback na prvi dostupni."""
    for item in items:
        if item.lang_code == lang:
            return item.naziv
    return items[0].naziv if items else ""
