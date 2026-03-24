"""Modeli za CroRIS Časopisi API (casopisi-api)."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PublikacijaCasopis:
    """Kratki zapis publikacije vezane uz određeni časopis."""

    cf_res_publ_id: int
    hr_journal_id: Optional[int] = None
    citat: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PublikacijaCasopis":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            cf_res_publ_id=data["cfResPublId"],
            hr_journal_id=data.get("hrJournalId"),
            citat=data.get("citat"),
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "cf_res_publ_id": self.cf_res_publ_id,
            "hr_journal_id": self.hr_journal_id,
            "citat": self.citat,
        }


@dataclass
class Casopis:
    """Časopis iz CroRIS Časopisi API-ja s bibliografskim podacima i popisom publikacija."""

    id: int
    naziv: Optional[str] = None
    drzava: Optional[str] = None
    drzava_kod: Optional[str] = None
    godina_pocetka: Optional[int] = None
    godina_zavrsetka: Optional[int] = None
    issn: Optional[str] = None
    eissn: Optional[str] = None
    lissn: Optional[str] = None
    coden: Optional[str] = None
    udk: Optional[str] = None
    publikacije: list[PublikacijaCasopis] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Casopis":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        embedded = data.get("publikacijaResource", {}) or {}
        pubs_raw = embedded.get("_embedded", {}).get("publikacije", [])
        return cls(
            id=data["id"],
            naziv=data.get("naziv"),
            drzava=data.get("drzava"),
            drzava_kod=data.get("drzavaKod"),
            godina_pocetka=data.get("godinaPocetka"),
            godina_zavrsetka=data.get("godinaZavrsetka"),
            issn=data.get("issn"),
            eissn=data.get("eissn"),
            lissn=data.get("lissn"),
            coden=data.get("coden"),
            udk=data.get("udk"),
            publikacije=[PublikacijaCasopis.from_dict(p) for p in pubs_raw],
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "id": self.id,
            "naziv": self.naziv,
            "drzava": self.drzava,
            "issn": self.issn,
            "eissn": self.eissn,
            "godina_pocetka": self.godina_pocetka,
            "godina_zavrsetka": self.godina_zavrsetka,
            "coden": self.coden,
            "udk": self.udk,
        }
