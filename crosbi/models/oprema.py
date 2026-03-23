"""Modeli za CroRIS Oprema API (oprema-api)."""
from dataclasses import dataclass, field
from typing import Optional

from .common import Klasifikacija


@dataclass
class TranslatedTextML:
    """Višejezični tekst u formatu oprema-api (drugačiji od projekti-api)."""

    records: list[dict] = field(default_factory=list)

    def get(self, lang: str = "hr") -> str:
        for r in self.records:
            if r.get("langCode") == lang:
                return r.get("naziv", "")
        return self.records[0].get("naziv", "") if self.records else ""

    @classmethod
    def from_dict(cls, data: dict | None) -> "TranslatedTextML":
        if not data:
            return cls()
        return cls(records=data.get("records", []))


@dataclass
class Cijena:
    iznos: Optional[float] = None
    jedinica_mjere: Optional[str] = None
    valuta: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Cijena":
        return cls(
            iznos=data.get("iznos"),
            jedinica_mjere=data.get("jedinicaMjere"),
            valuta=data.get("valuta"),
        )


@dataclass
class OpremaUstanova:
    id: Optional[int] = None
    naziv: Optional[str] = None
    mbu: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "OpremaUstanova":
        return cls(id=data.get("id"), naziv=data.get("naziv"), mbu=data.get("mbu"))


@dataclass
class OpremaProjekt:
    id: Optional[int] = None
    naziv: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "OpremaProjekt":
        return cls(id=data.get("id"), naziv=data.get("naziv"))


@dataclass
class OpremaOsoba:
    id: int
    ime: Optional[str] = None
    prezime: Optional[str] = None
    titula: Optional[str] = None
    funkcija: Optional[Klasifikacija] = None

    @property
    def puno_ime(self) -> str:
        return " ".join(p for p in [self.ime, self.prezime] if p)

    @classmethod
    def from_dict(cls, data: dict) -> "OpremaOsoba":
        return cls(
            id=data["id"],
            ime=data.get("ime"),
            prezime=data.get("prezime"),
            titula=data.get("titulaIspredImena"),
            funkcija=(
                Klasifikacija.from_dict(data["funkcija"]) if data.get("funkcija") else None
            ),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "puno_ime": self.puno_ime,
            "titula": self.titula,
            "funkcija": self.funkcija.naziv if self.funkcija else None,
        }


@dataclass
class Oprema:
    id: int
    model: Optional[str] = None
    proizvodjac: Optional[str] = None
    inventarni_broj: Optional[str] = None
    godina_proizvodnje: Optional[int] = None
    datum_nabave: Optional[str] = None
    nabavna_cijena: Optional[Cijena] = None
    prenosivost: Optional[bool] = None
    rad_na_daljinu: Optional[bool] = None
    adresa: Optional[str] = None
    naziv: Optional[TranslatedTextML] = None
    kratki_naziv: Optional[TranslatedTextML] = None
    opci_opis: Optional[TranslatedTextML] = None
    tehnicki_opis: Optional[TranslatedTextML] = None
    kategorija: Optional[Klasifikacija] = None
    stanje: Optional[Klasifikacija] = None
    nacin_koristenja: Optional[Klasifikacija] = None
    ustanova_vlasnik: Optional[OpremaUstanova] = None
    ustanova_lokacija: Optional[OpremaUstanova] = None
    projekt: Optional[OpremaProjekt] = None

    def get_naziv(self, lang: str = "hr") -> str:
        return self.naziv.get(lang) if self.naziv else ""

    @classmethod
    def from_dict(cls, data: dict) -> "Oprema":
        return cls(
            id=data["id"],
            model=data.get("model"),
            proizvodjac=data.get("proizvodjac"),
            inventarni_broj=data.get("inventarniBroj"),
            godina_proizvodnje=data.get("godinaProizvodnje"),
            datum_nabave=data.get("datumNabave"),
            nabavna_cijena=(
                Cijena.from_dict(data["nabavnaCijena"])
                if data.get("nabavnaCijena")
                else None
            ),
            prenosivost=data.get("prenosivost"),
            rad_na_daljinu=data.get("radNaDaljinu"),
            adresa=data.get("adresa"),
            naziv=TranslatedTextML.from_dict(data.get("naziv")),
            kratki_naziv=TranslatedTextML.from_dict(data.get("kratkiNaziv")),
            opci_opis=TranslatedTextML.from_dict(data.get("opciOpis")),
            tehnicki_opis=TranslatedTextML.from_dict(data.get("tehnickiOpis")),
            kategorija=(
                Klasifikacija.from_dict(data["kategorija"].get("klasifikacija") or data["kategorija"])
                if data.get("kategorija")
                else None
            ),
            stanje=(
                Klasifikacija.from_dict(data["stanjeOpreme"].get("klasifikacija") or data["stanjeOpreme"])
                if data.get("stanjeOpreme")
                else None
            ),
            nacin_koristenja=(
                Klasifikacija.from_dict(data["nacinKoristenja"].get("klasifikacija") or data["nacinKoristenja"])
                if data.get("nacinKoristenja")
                else None
            ),
            ustanova_vlasnik=(
                OpremaUstanova.from_dict(data["ustanovaVlasnik"])
                if data.get("ustanovaVlasnik")
                else None
            ),
            ustanova_lokacija=(
                OpremaUstanova.from_dict(data["ustanovaLokacija"])
                if data.get("ustanovaLokacija")
                else None
            ),
            projekt=(
                OpremaProjekt.from_dict(data["projekt"]) if data.get("projekt") else None
            ),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "naziv": self.get_naziv("hr"),
            "model": self.model,
            "proizvodjac": self.proizvodjac,
            "inventarni_broj": self.inventarni_broj,
            "godina_proizvodnje": self.godina_proizvodnje,
            "datum_nabave": self.datum_nabave,
            "cijena": self.nabavna_cijena.iznos if self.nabavna_cijena else None,
            "valuta": self.nabavna_cijena.valuta if self.nabavna_cijena else None,
            "kategorija": self.kategorija.naziv if self.kategorija else None,
            "stanje": self.stanje.naziv if self.stanje else None,
            "prenosivost": self.prenosivost,
            "rad_na_daljinu": self.rad_na_daljinu,
            "ustanova": self.ustanova_vlasnik.naziv if self.ustanova_vlasnik else None,
            "lokacija": self.ustanova_lokacija.naziv if self.ustanova_lokacija else None,
        }


@dataclass
class Usluga:
    id: int
    ustanova_id: Optional[int] = None
    ustanova_naziv: Optional[str] = None
    pocetak: Optional[str] = None
    kraj: Optional[str] = None
    aktivnost: Optional[bool] = None
    naziv: Optional[TranslatedTextML] = None
    opis: Optional[TranslatedTextML] = None

    def get_naziv(self, lang: str = "hr") -> str:
        return self.naziv.get(lang) if self.naziv else ""

    @classmethod
    def from_dict(cls, data: dict) -> "Usluga":
        ustanova = data.get("ustanova", {}) or {}
        return cls(
            id=data["id"],
            ustanova_id=ustanova.get("id"),
            ustanova_naziv=ustanova.get("naziv"),
            pocetak=data.get("pocetak"),
            kraj=data.get("kraj"),
            aktivnost=data.get("aktivnost"),
            naziv=TranslatedTextML.from_dict(data.get("naziv")),
            opis=TranslatedTextML.from_dict(data.get("opis")),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "naziv": self.get_naziv("hr"),
            "ustanova": self.ustanova_naziv,
            "pocetak": self.pocetak,
            "kraj": self.kraj,
            "aktivnost": self.aktivnost,
        }


@dataclass
class UslugaCjenik:
    id: int
    vrsta_korisnika: Optional[Klasifikacija] = None
    cijena: Optional[Cijena] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UslugaCjenik":
        return cls(
            id=data["id"],
            vrsta_korisnika=(
                Klasifikacija.from_dict(data["vrstaKorisnika"])
                if data.get("vrstaKorisnika")
                else None
            ),
            cijena=Cijena.from_dict(data["cijena"]) if data.get("cijena") else None,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "vrsta_korisnika": self.vrsta_korisnika.naziv if self.vrsta_korisnika else None,
            "iznos": self.cijena.iznos if self.cijena else None,
            "jedinica_mjere": self.cijena.jedinica_mjere if self.cijena else None,
            "valuta": self.cijena.valuta if self.cijena else None,
        }
