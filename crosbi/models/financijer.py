"""Modeli financijera i programa iz CroRIS Projekti API-ja."""
from dataclasses import dataclass, field
from typing import Optional

from .common import TranslatedText, get_text


@dataclass
class FinancijerProgram:
    """Program financiranja unutar financijera projekta."""

    id: Optional[int] = None
    naziv_hr: Optional[str] = None
    naziv_en: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FinancijerProgram":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            id=data.get("id"),
            naziv_hr=data.get("nazivHr"),
            naziv_en=data.get("nazivEn"),
        )


@dataclass
class Financijer:
    """Financijer projekta s iznosom, programom i višejezičnim nazivom."""

    id: int
    amount: Optional[float] = None
    currency_code: Optional[str] = None
    entity_id: Optional[int] = None
    entity_name_hr: Optional[str] = None
    entity_name_en: Optional[str] = None
    tip_id: Optional[int] = None
    tip_naziv: Optional[str] = None
    vrsta_izvora_id: Optional[int] = None
    vrsta_izvora_naziv: Optional[str] = None
    poziv_id: Optional[int] = None
    poziv_naziv: Optional[str] = None
    naziv: list[TranslatedText] = field(default_factory=list)
    nadleznost: list[TranslatedText] = field(default_factory=list)
    program: Optional[FinancijerProgram] = None
    financijer_poirot_id: Optional[int] = None

    def get_naziv(self, lang: str = "hr") -> str:
        """Vrati naziv financijera na zadanom jeziku; fallback na entity_name."""
        if self.naziv:
            return get_text(self.naziv, lang)
        return self.entity_name_hr or self.entity_name_en or ""

    @classmethod
    def from_dict(cls, data: dict) -> "Financijer":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            id=data["id"],
            amount=data.get("amount"),
            currency_code=data.get("currencyCode"),
            entity_id=data.get("entityId"),
            entity_name_hr=data.get("entityNameHr"),
            entity_name_en=data.get("entityNameEn"),
            tip_id=data.get("tipId"),
            tip_naziv=data.get("tipNaziv"),
            vrsta_izvora_id=data.get("vrstaIzvoraFinanciranjaId"),
            vrsta_izvora_naziv=data.get("vrstaIzvoraFinanciranjaName"),
            poziv_id=data.get("pozivId"),
            poziv_naziv=data.get("pozivNaziv"),
            naziv=[TranslatedText.from_dict(t) for t in data.get("financijer", [])],
            nadleznost=[TranslatedText.from_dict(t) for t in data.get("nadleznost", [])],
            program=(
                FinancijerProgram.from_dict(data["program"])
                if data.get("program")
                else None
            ),
            financijer_poirot_id=data.get("financijerPoirotId"),
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "id": self.id,
            "naziv": self.get_naziv("hr"),
            "tip": self.tip_naziv,
            "vrsta_izvora": self.vrsta_izvora_naziv,
            "poziv": self.poziv_naziv,
            "amount": self.amount,
            "currency_code": self.currency_code,
            "program": self.program.naziv_hr if self.program else None,
        }
