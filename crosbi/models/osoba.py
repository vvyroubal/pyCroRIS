from dataclasses import dataclass
from typing import Optional

from .common import Klasifikacija


@dataclass
class Osoba:
    pers_id: int
    ime: Optional[str] = None
    prezime: Optional[str] = None
    oib: Optional[str] = None
    maticni_broj_znanstvenika: Optional[str] = None
    klasifikacija: Optional[Klasifikacija] = None
    pocetak: Optional[str] = None
    kraj: Optional[str] = None
    ustanova_id: Optional[int] = None
    ustanova_naziv: Optional[str] = None
    email: Optional[str] = None
    osoba_poirot_id: Optional[int] = None

    @property
    def puno_ime(self) -> str:
        parts = [self.ime, self.prezime]
        return " ".join(p for p in parts if p)

    @classmethod
    def from_dict(cls, data: dict) -> "Osoba":
        return cls(
            pers_id=data["persId"],
            ime=data.get("ime"),
            prezime=data.get("prezime"),
            oib=data.get("oib"),
            maticni_broj_znanstvenika=data.get("maticniBrojZnanstvenika"),
            klasifikacija=(
                Klasifikacija.from_dict(data["klasifikacija"])
                if data.get("klasifikacija")
                else None
            ),
            pocetak=data.get("pocetak"),
            kraj=data.get("kraj"),
            ustanova_id=data.get("ustanovaId"),
            ustanova_naziv=data.get("ustanovaNaziv"),
            email=data.get("email"),
            osoba_poirot_id=data.get("osobaPoirotId"),
        )

    def to_dict(self) -> dict:
        return {
            "pers_id": self.pers_id,
            "ime": self.ime,
            "prezime": self.prezime,
            "puno_ime": self.puno_ime,
            "oib": self.oib,
            "mbz": self.maticni_broj_znanstvenika,
            "uloga": self.klasifikacija.naziv if self.klasifikacija else None,
            "ustanova": self.ustanova_naziv,
            "email": self.email,
            "pocetak": self.pocetak,
            "kraj": self.kraj,
        }
