from dataclasses import dataclass
from typing import Optional

from .common import Klasifikacija


@dataclass
class Publikacija:
    cf_res_publ_id: int
    naslov: Optional[str] = None
    autori: Optional[str] = None
    nadredena_publikacije: Optional[str] = None
    vrsta_publikacije: Optional[str] = None
    tip_publikacije: Optional[str] = None
    datum: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    eissn: Optional[str] = None
    doi: Optional[str] = None
    klasifikacija: Optional[Klasifikacija] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Publikacija":
        return cls(
            cf_res_publ_id=data["cfResPublId"],
            naslov=data.get("naslov"),
            autori=data.get("autori"),
            nadredena_publikacije=data.get("nadredenaPublikacije"),
            vrsta_publikacije=data.get("vrstaPublikacije"),
            tip_publikacije=data.get("tipPublikacije"),
            datum=data.get("datum"),
            isbn=data.get("isbn"),
            issn=data.get("issn"),
            eissn=data.get("eissn"),
            doi=data.get("doi"),
            klasifikacija=(
                Klasifikacija.from_dict(data["klasifikacija"])
                if data.get("klasifikacija")
                else None
            ),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.cf_res_publ_id,
            "naslov": self.naslov,
            "autori": self.autori,
            "vrsta": self.vrsta_publikacije,
            "tip": self.tip_publikacije,
            "datum": self.datum,
            "doi": self.doi,
            "issn": self.issn,
            "isbn": self.isbn,
            "casopis": self.nadredena_publikacije,
        }
