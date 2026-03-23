"""Modeli za CroRIS Znanstvenici API (znanstvenici-api)."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ZnanstvenikUstanova:
    id: Optional[int] = None
    naziv: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ZnanstvenikUstanova":
        return cls(id=data.get("id"), naziv=data.get("naziv"))


@dataclass
class Zvanje:
    id: int
    naziv: Optional[str] = None
    kratica: Optional[str] = None
    datum_izbora: Optional[str] = None
    aktivan: Optional[bool] = None
    ustanova: Optional[ZnanstvenikUstanova] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Zvanje":
        return cls(
            id=data["id"],
            naziv=data.get("naziv"),
            kratica=data.get("kratica"),
            datum_izbora=data.get("datumIzbora"),
            aktivan=data.get("aktivan"),
            ustanova=(
                ZnanstvenikUstanova.from_dict(data["ustanova"])
                if data.get("ustanova")
                else None
            ),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "naziv": self.naziv,
            "kratica": self.kratica,
            "datum_izbora": self.datum_izbora,
            "aktivan": self.aktivan,
            "ustanova": self.ustanova.naziv if self.ustanova else None,
        }


@dataclass
class AkademskiStupanj:
    id: int
    naziv: Optional[str] = None
    kratica: Optional[str] = None
    datum_stjecanja: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "AkademskiStupanj":
        return cls(
            id=data["id"],
            naziv=data.get("naziv"),
            kratica=data.get("kratica"),
            datum_stjecanja=data.get("datumStjecanja"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "naziv": self.naziv,
            "kratica": self.kratica,
            "datum_stjecanja": self.datum_stjecanja,
        }


@dataclass
class Zaposlenje:
    id: int
    ustanova: Optional[ZnanstvenikUstanova] = None
    datum_od: Optional[str] = None
    datum_do: Optional[str] = None
    radno_mjesto: Optional[str] = None
    vrsta_zaposlenja: Optional[str] = None
    aktivno: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Zaposlenje":
        return cls(
            id=data["id"],
            ustanova=(
                ZnanstvenikUstanova.from_dict(data["ustanova"])
                if data.get("ustanova")
                else None
            ),
            datum_od=data.get("datumOd"),
            datum_do=data.get("datumDo"),
            radno_mjesto=data.get("radnoMjesto"),
            vrsta_zaposlenja=data.get("vrstaZaposlenja"),
            aktivno=data.get("aktivno"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ustanova": self.ustanova.naziv if self.ustanova else None,
            "radno_mjesto": self.radno_mjesto,
            "vrsta_zaposlenja": self.vrsta_zaposlenja,
            "datum_od": self.datum_od,
            "datum_do": self.datum_do,
            "aktivno": self.aktivno,
        }


@dataclass
class Znanstvenik:
    id: int
    ime: Optional[str] = None
    prezime: Optional[str] = None
    oib: Optional[str] = None
    maticni_broj: Optional[str] = None
    orcid: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None
    datum_rodjenja: Optional[str] = None
    spol: Optional[str] = None
    max_zvanje: Optional[str] = None
    aktivan: Optional[bool] = None
    godina_prvog_zaposlenja: Optional[int] = None
    zvanja: list[Zvanje] = field(default_factory=list)
    akademski_stupnjevi: list[AkademskiStupanj] = field(default_factory=list)
    zaposlenja: list[Zaposlenje] = field(default_factory=list)

    @property
    def puno_ime(self) -> str:
        return " ".join(p for p in [self.ime, self.prezime] if p)

    @classmethod
    def from_dict(cls, data: dict) -> "Znanstvenik":
        zvanja_raw = (
            data.get("zvanjeResources", {})
            .get("_embedded", {})
            .get("zvanja", [])
        )
        stupnjevi_raw = (
            data.get("akademskiStupanjResources", {})
            .get("_embedded", {})
            .get("akademskiStupnjevi", [])
        )
        zaposlenja_raw = (
            data.get("zaposlenjeResources", {})
            .get("_embedded", {})
            .get("zaposlenja", [])
        )
        return cls(
            id=data["id"],
            ime=data.get("ime"),
            prezime=data.get("prezime"),
            oib=data.get("oib"),
            maticni_broj=data.get("maticniBroj"),
            orcid=data.get("orcid"),
            email=data.get("email"),
            web=data.get("web"),
            datum_rodjenja=data.get("datumRodjenja"),
            spol=data.get("spol"),
            max_zvanje=data.get("maxZvanje"),
            aktivan=data.get("aktivanZnanstvenik"),
            godina_prvog_zaposlenja=data.get("godinaPrvogZaposlenjaZnanstvenika"),
            zvanja=[Zvanje.from_dict(z) for z in zvanja_raw],
            akademski_stupnjevi=[AkademskiStupanj.from_dict(s) for s in stupnjevi_raw],
            zaposlenja=[Zaposlenje.from_dict(z) for z in zaposlenja_raw],
        )

    def to_dict(self) -> dict:
        aktivno_zaposlenje = next((z for z in self.zaposlenja if z.aktivno), None)
        return {
            "id": self.id,
            "ime": self.ime,
            "prezime": self.prezime,
            "oib": self.oib,
            "mbz": self.maticni_broj,
            "orcid": self.orcid,
            "email": self.email,
            "max_zvanje": self.max_zvanje,
            "aktivan": self.aktivan,
            "ustanova": aktivno_zaposlenje.ustanova.naziv if aktivno_zaposlenje and aktivno_zaposlenje.ustanova else None,
            "radno_mjesto": aktivno_zaposlenje.radno_mjesto if aktivno_zaposlenje else None,
        }


@dataclass
class RadniOdnos:
    id: int
    cf_pers_id: Optional[int] = None
    oib_osobe: Optional[str] = None
    ime_osobe: Optional[str] = None
    prezime_osobe: Optional[str] = None
    cf_org_unit_id: Optional[int] = None
    vrsta_radnog_odnosa: Optional[str] = None
    oblik_radnog_vremena: Optional[str] = None
    kategorija_radnog_mjesta: Optional[str] = None
    radno_mjesto_naziv: Optional[str] = None
    datum_pocetka: Optional[str] = None

    @property
    def puno_ime(self) -> str:
        return " ".join(p for p in [self.ime_osobe, self.prezime_osobe] if p)

    @classmethod
    def from_dict(cls, data: dict) -> "RadniOdnos":
        return cls(
            id=data["hrPersRadniOdnosId"],
            cf_pers_id=data.get("cfPersId"),
            oib_osobe=data.get("oibOsobe"),
            ime_osobe=data.get("imeOsobe"),
            prezime_osobe=data.get("prezimeOsobe"),
            cf_org_unit_id=data.get("cfOrgUnitId"),
            vrsta_radnog_odnosa=data.get("vrstaRadnogOdnosa"),
            oblik_radnog_vremena=data.get("oblikRadnogVremena"),
            kategorija_radnog_mjesta=data.get("kategorijaRadnogMjesta"),
            radno_mjesto_naziv=data.get("radnoMjestoNaziv"),
            datum_pocetka=data.get("datumPocetka"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "puno_ime": self.puno_ime,
            "oib": self.oib_osobe,
            "vrsta_radnog_odnosa": self.vrsta_radnog_odnosa,
            "oblik_radnog_vremena": self.oblik_radnog_vremena,
            "radno_mjesto": self.radno_mjesto_naziv,
            "datum_pocetka": self.datum_pocetka,
        }


@dataclass
class OsobaAkreditacija:
    id: int
    oib: Optional[str] = None
    ime: Optional[str] = None
    prezime: Optional[str] = None
    poveznica: Optional[str] = None
    vrsta_zaposlenja_hr: Optional[str] = None
    vrsta_radnog_odnosa_hr: Optional[str] = None
    podrucje_hr: Optional[str] = None
    polje_hr: Optional[str] = None

    @property
    def puno_ime(self) -> str:
        return " ".join(p for p in [self.ime, self.prezime] if p)

    @classmethod
    def from_dict(cls, data: dict) -> "OsobaAkreditacija":
        return cls(
            id=data["id"],
            oib=data.get("oib"),
            ime=data.get("ime"),
            prezime=data.get("prezime"),
            poveznica=data.get("poveznica"),
            vrsta_zaposlenja_hr=data.get("vrstaZaposlenjaHr"),
            vrsta_radnog_odnosa_hr=data.get("vrstaRadnogOdnosaHr"),
            podrucje_hr=data.get("podrucjeHr"),
            polje_hr=data.get("poljeHr"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "puno_ime": self.puno_ime,
            "oib": self.oib,
            "vrsta_zaposlenja": self.vrsta_zaposlenja_hr,
            "vrsta_radnog_odnosa": self.vrsta_radnog_odnosa_hr,
            "podrucje": self.podrucje_hr,
            "polje": self.polje_hr,
        }
