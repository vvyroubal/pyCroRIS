from dataclasses import dataclass, field
from typing import Optional

from .common import Klasifikacija, TranslatedText, get_text


@dataclass
class Projekt:
    id: int
    acro: Optional[str] = None
    uri: Optional[str] = None
    pocetak: Optional[str] = None
    kraj: Optional[str] = None
    currency_code: Optional[str] = None
    total_cost: Optional[float] = None
    tip_projekta: Optional[Klasifikacija] = None
    title: list[TranslatedText] = field(default_factory=list)
    summary: list[TranslatedText] = field(default_factory=list)
    keywords: list[TranslatedText] = field(default_factory=list)
    hr_sifra_projekta: Optional[str] = None
    deleted: Optional[str] = None
    verified: Optional[str] = None
    last_updated_at: Optional[int] = None
    projekt_poirot_id: Optional[int] = None

    def get_title(self, lang: str = "hr") -> str:
        return get_text(self.title, lang)

    def get_summary(self, lang: str = "hr") -> str:
        return get_text(self.summary, lang)

    def get_keywords(self, lang: str = "hr") -> str:
        return get_text(self.keywords, lang)

    @classmethod
    def from_dict(cls, data: dict) -> "Projekt":
        return cls(
            id=data["id"],
            acro=data.get("acro"),
            uri=data.get("uri"),
            pocetak=data.get("pocetak"),
            kraj=data.get("kraj"),
            currency_code=data.get("currencyCode"),
            total_cost=data.get("totalCost"),
            tip_projekta=(
                Klasifikacija.from_dict(data["tipProjekta"])
                if data.get("tipProjekta")
                else None
            ),
            title=[TranslatedText.from_dict(t) for t in data.get("title", [])],
            summary=[TranslatedText.from_dict(t) for t in data.get("summary", [])],
            keywords=[TranslatedText.from_dict(t) for t in data.get("keywords", [])],
            hr_sifra_projekta=data.get("hrSifraProjekta"),
            deleted=data.get("deleted"),
            verified=data.get("verified"),
            last_updated_at=data.get("lastUpdatedAt"),
            projekt_poirot_id=data.get("projektPoirotId"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "acro": self.acro,
            "hr_sifra_projekta": self.hr_sifra_projekta,
            "title_hr": self.get_title("hr"),
            "title_en": self.get_title("en"),
            "tip_projekta": self.tip_projekta.naziv if self.tip_projekta else None,
            "pocetak": self.pocetak,
            "kraj": self.kraj,
            "total_cost": self.total_cost,
            "currency_code": self.currency_code,
            "uri": self.uri,
            "verified": self.verified,
        }
