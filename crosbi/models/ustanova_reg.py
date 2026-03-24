"""Modeli za CroRIS Ustanove API (ustanove-api).

Pokriva MZO upisnik ustanova, CroRIS ustanove i PPG klasifikaciju
(područja → polja → grane).
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Adresa:
    """Adresa ustanove (mjesto, ulica, poštanski broj)."""

    mjesto: Optional[str] = None
    ulica_br: Optional[str] = None
    postanskI_broj: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Adresa":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            mjesto=data.get("mjesto"),
            ulica_br=data.get("ulicaBr"),
            postanskI_broj=data.get("postanskiBroj"),
        )


@dataclass
class Kontakt:
    """Kontaktni podaci ustanove (telefon, fax, web, e-mail)."""

    telefon: Optional[str] = None
    fax: Optional[str] = None
    web: Optional[str] = None
    email: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Kontakt":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            telefon=data.get("telefon"),
            fax=data.get("fax"),
            web=data.get("web"),
            email=data.get("email"),
        )


@dataclass
class NadUstanova:
    """Nadređena ustanova u hijerarhiji (matična ustanova)."""

    id: int
    naziv: Optional[str] = None
    mbu: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "NadUstanova":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(id=data["id"], naziv=data.get("naziv"), mbu=data.get("mbu"))


@dataclass
class TipUstanove:
    """Tip ustanove prema MZO upisniku (npr. sveučilište, institut)."""

    id: int
    naziv: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "TipUstanove":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(id=data["id"], naziv=data.get("naziv"))


@dataclass
class VrstaUstanove:
    """Vrsta ustanove prema MZO upisniku (npr. javna, privatna)."""

    id: int
    naziv: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "VrstaUstanove":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(id=data["id"], naziv=data.get("naziv"))


@dataclass
class UstanovaReg:
    """Ustanova iz MZO upisnika ili CroRIS registra (ustanove-api)."""

    id: int
    naziv: Optional[str] = None
    puni_naziv: Optional[str] = None
    puni_naziv_en: Optional[str] = None
    kratki_naziv: Optional[str] = None
    naziv_en: Optional[str] = None
    kratica: Optional[str] = None
    drzava_kod: Optional[str] = None
    mbs: Optional[str] = None
    mbu: Optional[str] = None
    sifra_isvu: Optional[int] = None
    mzo_id: Optional[int] = None
    oib: Optional[str] = None
    aktivna: Optional[bool] = None
    celnik: Optional[str] = None
    tip_vlasnistva: Optional[str] = None
    zupanija: Optional[str] = None
    adresa: Optional[Adresa] = None
    kontakt: Optional[Kontakt] = None
    nad_ustanova: Optional[NadUstanova] = None
    tip_ustanove: list[TipUstanove] = field(default_factory=list)
    vrsta_ustanove: Optional[VrstaUstanove] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UstanovaReg":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            id=data["id"],
            naziv=data.get("naziv"),
            puni_naziv=data.get("puniNaziv"),
            puni_naziv_en=data.get("puniNazivEn"),
            kratki_naziv=data.get("kratkiNaziv"),
            naziv_en=data.get("nazivEn"),
            kratica=data.get("kratica"),
            drzava_kod=data.get("drzavaKod"),
            mbs=data.get("mbs"),
            mbu=data.get("mbu"),
            sifra_isvu=data.get("sifraISVU"),
            mzo_id=data.get("mzoId"),
            oib=data.get("oib"),
            aktivna=data.get("aktivna"),
            celnik=data.get("celnik"),
            tip_vlasnistva=data.get("tipVlasnistva"),
            zupanija=data.get("zupanija"),
            adresa=Adresa.from_dict(data["adresa"]) if data.get("adresa") else None,
            kontakt=Kontakt.from_dict(data["kontakt"]) if data.get("kontakt") else None,
            nad_ustanova=(
                NadUstanova.from_dict(data["nadUstanova"])
                if data.get("nadUstanova")
                else None
            ),
            tip_ustanove=[TipUstanove.from_dict(t) for t in data.get("tipUstanove", [])],
            vrsta_ustanove=(
                VrstaUstanove.from_dict(data["vrstaUstanove"])
                if data.get("vrstaUstanove")
                else None
            ),
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "id": self.id,
            "naziv": self.naziv,
            "puni_naziv": self.puni_naziv,
            "kratica": self.kratica,
            "mbu": self.mbu,
            "oib": self.oib,
            "drzava_kod": self.drzava_kod,
            "zupanija": self.zupanija,
            "aktivna": self.aktivna,
            "tip_vlasnistva": self.tip_vlasnistva,
            "vrsta": self.vrsta_ustanove.naziv if self.vrsta_ustanove else None,
            "grad": self.adresa.mjesto if self.adresa else None,
            "web": self.kontakt.web if self.kontakt else None,
            "email": self.kontakt.email if self.kontakt else None,
        }


# --- PPG klasifikacija (Područje → Polje → Grana) ---


@dataclass
class PravniAkt:
    """Pravni akt koji definira PPG klasifikaciju."""

    id: Optional[int] = None
    default_naziv: Optional[str] = None
    datum_usvojenja: Optional[str] = None
    is_aktualan: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PravniAkt":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            id=data.get("id"),
            default_naziv=data.get("defaultNaziv"),
            datum_usvojenja=data.get("datumUsvojenja"),
            is_aktualan=data.get("isAktualan"),
        )


@dataclass
class Grana:
    """Grana (najniža razina) u PPG klasifikacijskoj hijerarhiji."""

    disciplina_id: int
    naziv: Optional[str] = None
    naziv_en: Optional[str] = None
    sifra: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Grana":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            disciplina_id=data["disciplinaId"],
            naziv=data.get("nazivDiscipline"),
            naziv_en=data.get("nazivDisciplineEn"),
            sifra=data.get("sifraDiscipline"),
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "disciplina_id": self.disciplina_id,
            "naziv": self.naziv,
            "naziv_en": self.naziv_en,
            "sifra": self.sifra,
        }


@dataclass
class Polje:
    """Polje (srednja razina) u PPG klasifikacijskoj hijerarhiji — sadrži grane."""

    disciplina_id: int
    naziv: Optional[str] = None
    naziv_en: Optional[str] = None
    sifra: Optional[str] = None
    grane: list[Grana] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Polje":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            disciplina_id=data["disciplinaId"],
            naziv=data.get("nazivDiscipline"),
            naziv_en=data.get("nazivDisciplineEn"),
            sifra=data.get("sifraDiscipline"),
            grane=[Grana.from_dict(g) for g in data.get("grane", [])],
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "disciplina_id": self.disciplina_id,
            "naziv": self.naziv,
            "naziv_en": self.naziv_en,
            "sifra": self.sifra,
            "broj_grana": len(self.grane),
        }


@dataclass
class Podrucje:
    """Područje (najviša razina) u PPG klasifikacijskoj hijerarhiji."""

    disciplina_id: int
    naziv: Optional[str] = None
    naziv_en: Optional[str] = None
    sifra: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Podrucje":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            disciplina_id=data["disciplinaId"],
            naziv=data.get("nazivDiscipline"),
            naziv_en=data.get("nazivDisciplineEn"),
            sifra=data.get("sifraDiscipline"),
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "disciplina_id": self.disciplina_id,
            "naziv": self.naziv,
            "naziv_en": self.naziv_en,
            "sifra": self.sifra,
        }
