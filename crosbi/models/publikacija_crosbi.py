"""Modeli za CroRIS CROSBI API (crosbi-api) — bibliografske publikacije."""
from dataclasses import dataclass, field
from typing import Optional

from .common import Klasifikacija, TranslatedText


@dataclass
class Citat:
    vrsta_id: Optional[int] = None
    vrsta_naziv: Optional[str] = None
    citat: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Citat":
        return cls(
            vrsta_id=data.get("vrstaCitataId"),
            vrsta_naziv=data.get("vrstaCitataNaziv"),
            citat=data.get("citat"),
        )


@dataclass
class Poveznica:
    url_id: Optional[int] = None
    url_vrsta_id: Optional[int] = None
    url_vrsta_naziv: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Poveznica":
        return cls(
            url_id=data.get("urlId"),
            url_vrsta_id=data.get("urlVrstaId"),
            url_vrsta_naziv=data.get("urlVrstaNaziv"),
            url=data.get("url"),
        )


@dataclass
class Skup:
    cf_event_id: Optional[int] = None
    naziv: Optional[str] = None
    href: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Skup":
        return cls(
            cf_event_id=data.get("cfEventId"),
            naziv=data.get("naziv"),
            href=data.get("href"),
        )


@dataclass
class DisciplinaCrosbi:
    id: Optional[int] = None
    naziv: Optional[str] = None
    sifra: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "DisciplinaCrosbi":
        return cls(id=data.get("id"), naziv=data.get("naziv"), sifra=data.get("sifra"))


@dataclass
class OsobaPublikacija:
    croris_id: Optional[int] = None
    titula: Optional[str] = None
    ime: Optional[str] = None
    prezime: Optional[str] = None
    funkcija: Optional[Klasifikacija] = None

    @property
    def puno_ime(self) -> str:
        return " ".join(p for p in [self.ime, self.prezime] if p)

    @classmethod
    def from_dict(cls, data: dict) -> "OsobaPublikacija":
        return cls(
            croris_id=data.get("crorisId"),
            titula=data.get("titulaIspredImena"),
            ime=data.get("ime"),
            prezime=data.get("prezime"),
            funkcija=(
                Klasifikacija.from_dict(data["funkcija"]) if data.get("funkcija") else None
            ),
        )


@dataclass
class UstanovaPublikacija:
    croris_id: Optional[int] = None
    naziv: Optional[str] = None
    mbu: Optional[int] = None
    funkcija: Optional[Klasifikacija] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UstanovaPublikacija":
        return cls(
            croris_id=data.get("crorisId"),
            naziv=data.get("naziv"),
            mbu=data.get("mbu"),
            funkcija=(
                Klasifikacija.from_dict(data["funkcija"]) if data.get("funkcija") else None
            ),
        )


@dataclass
class ProjektPublikacija:
    croris_id: Optional[int] = None
    naziv: Optional[str] = None
    funkcija: Optional[Klasifikacija] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ProjektPublikacija":
        return cls(
            croris_id=data.get("crorisId"),
            naziv=data.get("naziv"),
            funkcija=(
                Klasifikacija.from_dict(data["funkcija"]) if data.get("funkcija") else None
            ),
        )


@dataclass
class PublikacijaCrosbi:
    """Bibliografska publikacija iz CROSBI modula (crosbi-api)."""

    crosbi_id: int
    bib_irb_id: Optional[int] = None
    autori: Optional[str] = None
    naslov: Optional[str] = None
    vrsta: Optional[str] = None
    tip: Optional[str] = None
    mjesto: Optional[str] = None
    izdavac: Optional[str] = None
    godina: Optional[str] = None
    datum: Optional[str] = None
    datum_azuriranja: Optional[str] = None
    nadredena_publikacija: Optional[str] = None
    casopis: Optional[str] = None
    volumen: Optional[str] = None
    svescic: Optional[str] = None
    stranice: Optional[str] = None
    broj_rada: Optional[str] = None
    doi: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    eissn: Optional[str] = None
    status: Optional[str] = None
    citat: Optional[str] = None
    indeksiranost: list[str] = field(default_factory=list)
    citati: list[Citat] = field(default_factory=list)
    naslovi: list[TranslatedText] = field(default_factory=list)
    sazeci: list[TranslatedText] = field(default_factory=list)
    kljucne_rijeci: list[TranslatedText] = field(default_factory=list)
    poveznice: list[Poveznica] = field(default_factory=list)
    skupovi: list[Skup] = field(default_factory=list)
    discipline: list[DisciplinaCrosbi] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "PublikacijaCrosbi":
        return cls(
            crosbi_id=data["crosbiId"],
            bib_irb_id=data.get("bibIrbId"),
            autori=data.get("autori"),
            naslov=data.get("naslov"),
            vrsta=data.get("vrsta"),
            tip=data.get("tip"),
            mjesto=data.get("mjesto"),
            izdavac=data.get("izdavac"),
            godina=data.get("godina"),
            datum=data.get("datum"),
            datum_azuriranja=data.get("datumAzuriranja"),
            nadredena_publikacija=data.get("nadredenaPublikacija"),
            casopis=data.get("casopis"),
            volumen=data.get("volumen"),
            svescic=data.get("svescic"),
            stranice=data.get("stranice"),
            broj_rada=data.get("brojRada"),
            doi=data.get("doi"),
            isbn=data.get("isbn"),
            issn=data.get("issn"),
            eissn=data.get("eissn"),
            status=data.get("status"),
            citat=data.get("citat"),
            indeksiranost=data.get("indeksiranost", []),
            citati=[Citat.from_dict(c) for c in data.get("citati", [])],
            naslovi=[TranslatedText.from_dict(t) for t in data.get("naslovi", [])],
            sazeci=[TranslatedText.from_dict(t) for t in data.get("sazeci", [])],
            kljucne_rijeci=[
                TranslatedText.from_dict(t) for t in data.get("kljucneRijeci", [])
            ],
            poveznice=[Poveznica.from_dict(p) for p in data.get("poveznice", [])],
            skupovi=[Skup.from_dict(s) for s in data.get("skup", [])],
            discipline=[DisciplinaCrosbi.from_dict(d) for d in data.get("discipline", [])],
        )

    def to_dict(self) -> dict:
        return {
            "crosbi_id": self.crosbi_id,
            "autori": self.autori,
            "naslov": self.naslov,
            "vrsta": self.vrsta,
            "tip": self.tip,
            "godina": self.godina,
            "casopis": self.casopis,
            "volumen": self.volumen,
            "stranice": self.stranice,
            "doi": self.doi,
            "issn": self.issn,
            "isbn": self.isbn,
            "status": self.status,
            "indeksiranost": ", ".join(self.indeksiranost),
            "izdavac": self.izdavac,
            "mjesto": self.mjesto,
        }
