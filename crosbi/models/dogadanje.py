"""Modeli za CroRIS Događanja API (dogadanja-api)."""
from dataclasses import dataclass, field
from typing import Optional

from .common import TranslatedText, get_text


@dataclass
class Drzava:
    """Država s kodom i nazivom (koristi se u adresi mjesta održavanja)."""

    kod: Optional[str] = None
    naziv: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Drzava":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(kod=data.get("cfCountryCode"), naziv=data.get("cfName"))


@dataclass
class MjestoOdrzavanja:
    """Mjesto održavanja događanja (grad i država)."""

    venue_id: Optional[int] = None
    lokacija: Optional[str] = None
    mjesto_naziv: Optional[str] = None
    drzava: Optional[Drzava] = None

    @classmethod
    def from_dict(cls, data: dict) -> "MjestoOdrzavanja":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        mjesto = data.get("mjesto", {}) or {}
        return cls(
            venue_id=data.get("venueId"),
            lokacija=data.get("lokacija"),
            mjesto_naziv=mjesto.get("defaultNaziv"),
            drzava=Drzava.from_dict(data["drzava"]) if data.get("drzava") else None,
        )


@dataclass
class PublikacijaDogadanje:
    """Kratki zapis publikacije vezane uz određeno događanje."""

    cf_res_publ_id: int
    dogadanje_id: Optional[int] = None
    citat: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PublikacijaDogadanje":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            cf_res_publ_id=data["cfResPublId"],
            dogadanje_id=data.get("dogadanjeId"),
            citat=data.get("citat"),
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "cf_res_publ_id": self.cf_res_publ_id,
            "dogadanje_id": self.dogadanje_id,
            "citat": self.citat,
        }


@dataclass
class Dogadanje:
    """Znanstveno ili stručno događanje (konferencija, simpozij) iz CroRIS-a."""

    id: int
    uri: Optional[str] = None
    datum_pocetka: Optional[str] = None
    datum_zavrsetka: Optional[str] = None
    broj_sudionika: Optional[int] = None
    vrsta_organizacije: Optional[str] = None
    vrsta_dogadanja: Optional[str] = None
    naziv: list[TranslatedText] = field(default_factory=list)
    akronim: list[TranslatedText] = field(default_factory=list)
    opis: list[TranslatedText] = field(default_factory=list)
    kljucne_rijeci: list[TranslatedText] = field(default_factory=list)
    mjesta_odrzavanja: list[MjestoOdrzavanja] = field(default_factory=list)

    def get_naziv(self, lang: str = "hr") -> str:
        """Vrati naziv događanja na zadanom jeziku (zadano: hr)."""
        return get_text(self.naziv, lang)

    def get_akronim(self, lang: str = "hr") -> str:
        """Vrati akronim događanja na zadanom jeziku (zadano: hr)."""
        return get_text(self.akronim, lang)

    @classmethod
    def from_dict(cls, data: dict) -> "Dogadanje":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            id=data["id"],
            uri=data.get("uri"),
            datum_pocetka=data.get("datumPocetka"),
            datum_zavrsetka=data.get("datumZavrsetka"),
            broj_sudionika=data.get("brojSudionika"),
            vrsta_organizacije=data.get("vrstaOrganizacije"),
            vrsta_dogadanja=data.get("vrstaDogadanja"),
            naziv=[TranslatedText.from_dict(t) for t in data.get("naziv", [])],
            akronim=[TranslatedText.from_dict(t) for t in data.get("akronim", [])],
            opis=[TranslatedText.from_dict(t) for t in data.get("opis", [])],
            kljucne_rijeci=[
                TranslatedText.from_dict(t) for t in data.get("kljucneRijeci", [])
            ],
            mjesta_odrzavanja=[
                MjestoOdrzavanja.from_dict(m) for m in data.get("mjestoOdrzavanja", [])
            ],
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        lokacija = self.mjesta_odrzavanja[0] if self.mjesta_odrzavanja else None
        return {
            "id": self.id,
            "naziv": self.get_naziv("hr"),
            "akronim": self.get_akronim("hr"),
            "vrsta": self.vrsta_dogadanja,
            "datum_pocetka": self.datum_pocetka,
            "datum_zavrsetka": self.datum_zavrsetka,
            "broj_sudionika": self.broj_sudionika,
            "lokacija": lokacija.lokacija if lokacija else None,
            "drzava": lokacija.drzava.naziv if lokacija and lokacija.drzava else None,
        }
