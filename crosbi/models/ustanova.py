from dataclasses import dataclass
from typing import Optional

from .common import Klasifikacija


@dataclass
class Ustanova:
    id: int
    naziv: Optional[str] = None
    mbu: Optional[str] = None
    klasifikacija: Optional[Klasifikacija] = None
    pocetak: Optional[str] = None
    kraj: Optional[str] = None
    amount: Optional[float] = None
    currency_code: Optional[str] = None
    aai_domain: Optional[str] = None
    ustanova_poirot_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Ustanova":
        return cls(
            id=data["id"],
            naziv=data.get("naziv"),
            mbu=data.get("mbu"),
            klasifikacija=(
                Klasifikacija.from_dict(data["klasifikacija"])
                if data.get("klasifikacija")
                else None
            ),
            pocetak=data.get("pocetak"),
            kraj=data.get("kraj"),
            amount=data.get("amount"),
            currency_code=data.get("currencyCode"),
            aai_domain=data.get("aaiDomain"),
            ustanova_poirot_id=data.get("ustanovaPoirotId"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "naziv": self.naziv,
            "mbu": self.mbu,
            "uloga": self.klasifikacija.naziv if self.klasifikacija else None,
            "amount": self.amount,
            "currency_code": self.currency_code,
            "aai_domain": self.aai_domain,
            "pocetak": self.pocetak,
            "kraj": self.kraj,
        }
