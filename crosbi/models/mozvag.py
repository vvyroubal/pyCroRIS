"""Modeli za MOZVAG agregirane podatke o projektima (projekti-api /mozvag)."""
from dataclasses import dataclass, field
from typing import Optional

from .common import TranslatedText, get_text


@dataclass
class ProgramMozvag:
    """Program financiranja u MOZVAG direktoriju."""

    program_id: Optional[int] = None
    naziv_hr: Optional[str] = None
    naziv_en: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ProgramMozvag":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            program_id=data.get("programId"),
            naziv_hr=data.get("nazivHr"),
            naziv_en=data.get("nazivEn"),
        )


@dataclass
class FinancijerMozvag:
    """Financijer s popisom programa iz MOZVAG direktorija."""

    financijer_id: int
    naziv_hr: Optional[str] = None
    naziv_en: Optional[str] = None
    nadleznost: Optional[str] = None
    programi: list[ProgramMozvag] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "FinancijerMozvag":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            financijer_id=data["financijerId"],
            naziv_hr=data.get("nazivHr"),
            naziv_en=data.get("nazivEn"),
            nadleznost=data.get("nadleznost"),
            programi=[ProgramMozvag.from_dict(p) for p in data.get("programi", [])],
        )


@dataclass
class UstanovaMozvag:
    """Ustanova iz MOZVAG direktorija s višejezičnim nazivom i kontaktom."""

    ustanova_id: int
    adresa: Optional[str] = None
    oib: Optional[str] = None
    web: Optional[str] = None
    aai_domain: Optional[str] = None
    grad: Optional[str] = None
    naziv: list[TranslatedText] = field(default_factory=list)

    def get_naziv(self, lang: str = "hr") -> str:
        """Vrati naziv ustanove na zadanom jeziku (zadano: hr)."""
        return get_text(self.naziv, lang)

    @classmethod
    def from_dict(cls, data: dict) -> "UstanovaMozvag":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            ustanova_id=data["ustanovaId"],
            adresa=data.get("adresa"),
            oib=data.get("oib"),
            web=data.get("web"),
            aai_domain=data.get("aaiDomain"),
            grad=data.get("grad"),
            naziv=[TranslatedText.from_dict(t) for t in data.get("naziv", [])],
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "ustanova_id": self.ustanova_id,
            "naziv": self.get_naziv("hr"),
            "grad": self.grad,
            "aai_domain": self.aai_domain,
            "web": self.web,
            "oib": self.oib,
        }


@dataclass
class ProjektFinancijerMozvag:
    """Financijer unutar MOZVAG projekta s iznosom i valutom."""

    financijer_id: Optional[int] = None
    naziv_hr: Optional[str] = None
    naziv_en: Optional[str] = None
    valuta: Optional[str] = None
    iznos: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ProjektFinancijerMozvag":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            financijer_id=data.get("financijerId"),
            naziv_hr=data.get("nazivHr"),
            naziv_en=data.get("nazivEn"),
            valuta=data.get("valuta"),
            iznos=data.get("iznos"),
        )


@dataclass
class ProjektMozvag:
    """Projekt iz MOZVAG agregatora s iznosima po ustanovi i financijerima."""

    projekt_id: int
    naziv: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    uloga_id: Optional[int] = None
    uloga_naziv: Optional[str] = None
    ustanova_valuta: Optional[str] = None
    ustanova_iznos: Optional[int] = None
    projekt_valuta: Optional[str] = None
    projekt_iznos: Optional[int] = None
    vrsta_projekta_id: Optional[int] = None
    vrsta_projekta_naziv: Optional[str] = None
    financijeri: list[ProjektFinancijerMozvag] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ProjektMozvag":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            projekt_id=data["projektId"],
            naziv=data.get("naziv"),
            start_date=data.get("startDate"),
            end_date=data.get("endDate"),
            uloga_id=data.get("ulogaId"),
            uloga_naziv=data.get("ulogaNaziv"),
            ustanova_valuta=data.get("ustanovaValuta"),
            ustanova_iznos=data.get("ustanovaIznos"),
            projekt_valuta=data.get("projektValuta"),
            projekt_iznos=data.get("projektIznos"),
            vrsta_projekta_id=data.get("vrstaProjektaId"),
            vrsta_projekta_naziv=data.get("vrstaProjektaNaziv"),
            financijeri=[
                ProjektFinancijerMozvag.from_dict(f) for f in data.get("financijeri", [])
            ],
        )

    def to_dict(self) -> dict:
        """Vrati rječnik s ključnim poljima pogodnim za izvoz (CSV/JSON)."""
        return {
            "projekt_id": self.projekt_id,
            "naziv": self.naziv,
            "vrsta": self.vrsta_projekta_naziv,
            "uloga": self.uloga_naziv,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "projekt_iznos": self.projekt_iznos,
            "projekt_valuta": self.projekt_valuta,
            "ustanova_iznos": self.ustanova_iznos,
            "ustanova_valuta": self.ustanova_valuta,
            "financijeri": ", ".join(
                f.naziv_hr or "" for f in self.financijeri if f.naziv_hr
            ),
        }


@dataclass
class OsobaMozvag:
    """Sažetak projektnog angažmana osobe iz MOZVAG endpointa."""

    osoba_id: Optional[int] = None
    ustanova_id: Optional[int] = None
    ime: Optional[str] = None
    prezime: Optional[str] = None
    maticni_broj: Optional[str] = None
    znanstveni_projekti: int = 0
    ostali_projekti: int = 0

    @property
    def puno_ime(self) -> str:
        """Vrati puno ime (ime + prezime) kao jedinstven niz znakova."""
        return " ".join(p for p in [self.ime, self.prezime] if p)

    @property
    def ukupno_projekata(self) -> int:
        """Vrati ukupan broj projekata (znanstveni + ostali)."""
        return self.znanstveni_projekti + self.ostali_projekti

    @classmethod
    def from_dict(cls, data: dict) -> "OsobaMozvag":
        """Konstruiraj instancu iz sirovog rječnika API odgovora."""
        return cls(
            osoba_id=data.get("osobaId"),
            ustanova_id=data.get("ustanovaid"),
            ime=data.get("ime"),
            prezime=data.get("prezime"),
            maticni_broj=data.get("maticniBroj"),
            znanstveni_projekti=data.get("znanstveniProjekti", 0),
            ostali_projekti=data.get("ostaliProjekti", 0),
        )
