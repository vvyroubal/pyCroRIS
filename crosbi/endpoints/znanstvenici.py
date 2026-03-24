"""Endpointi za CroRIS Znanstvenici API (znanstvenici-api)."""
from typing import Generator, Optional

from ..client import CrorisClient, get_client
from ..config import ZNANSTVENICI_BASE_URL
from ..models.znanstvenik import OsobaAkreditacija, RadniOdnos, Znanstvenik


def _url(path: str) -> str:
    return f"{ZNANSTVENICI_BASE_URL}{path}"


def get_znanstvenik_by_oib(
    oib: str, client: Optional[CrorisClient] = None
) -> Znanstvenik:
    """Dohvati znanstvenika po OIB-u."""
    c = client or get_client()
    data = c.get(_url("/znanstvenik"), params={"oib": oib})
    # Može vratiti jedan objekt ili kolekciju
    if "_embedded" in data:
        items = data["_embedded"].get("znanstvenici", [])
        if not items:
            raise ValueError(f"Nije pronađen znanstvenik s OIB-om: {oib}")
        return Znanstvenik.from_dict(items[0])
    return Znanstvenik.from_dict(data)


def get_znanstvenik_by_mbz(
    mbz: str, client: Optional[CrorisClient] = None
) -> Znanstvenik:
    """Dohvati znanstvenika po matičnom broju (MBZ)."""
    c = client or get_client()
    data = c.get(_url("/znanstvenik"), params={"maticniBroj": mbz})
    if "_embedded" in data:
        items = data["_embedded"].get("znanstvenici", [])
        if not items:
            raise ValueError(f"Nije pronađen znanstvenik s MBZ-om: {mbz}")
        return Znanstvenik.from_dict(items[0])
    return Znanstvenik.from_dict(data)


def list_znanstvenici(
    client: Optional[CrorisClient] = None,
) -> Generator[Znanstvenik, None, None]:
    """Generator koji prolazi sve znanstvenike (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/znanstvenik"), "znanstvenici"):
        yield Znanstvenik.from_dict(item)


def get_svi_znanstvenici(
    client: Optional[CrorisClient] = None,
) -> list[Znanstvenik]:
    """
    Dohvati sve znanstvenike bez paginacije (cached endpoint).

    Napomena: odgovor je cachiran i može biti zastario.
    Preporučuje se lokalno pohranjivanje rezultata.
    """
    c = client or get_client()
    items = c.get_embedded(_url("/znanstvenik/collect"), "znanstvenici")
    return [Znanstvenik.from_dict(item) for item in items]


def get_osobe_updated_last_month(client: Optional[CrorisClient] = None) -> list[int]:
    """ID-ovi osoba ažuriranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/osoba/updated-last-month"))
    return data.get("_embedded", {}).get("osobeIds", [])


def get_osobe_deleted_last_month(client: Optional[CrorisClient] = None) -> list[int]:
    """ID-ovi osoba obrisanih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/osoba/deleted-last-month"))
    return data.get("_embedded", {}).get("osobeIds", [])


def get_osobe_created_last_month(client: Optional[CrorisClient] = None) -> list[int]:
    """ID-ovi osoba kreiranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/osoba/created-last-month"))
    return data.get("_embedded", {}).get("osobeIds", [])


def get_akreditacije_ustanove(
    org_unit_id: int, client: Optional[CrorisClient] = None
) -> list[OsobaAkreditacija]:
    """Dohvati nastavnike (akreditacije) za zadanu organizacijsku jedinicu."""
    c = client or get_client()
    items = c.get_embedded(
        _url("/osoba/akreditacija"),
        "nastavnici",
        params={"cfOrgUnitId": org_unit_id},
    )
    return [OsobaAkreditacija.from_dict(item) for item in items]


def get_radni_odnosi_ustanove(
    oib_ustanove: str, datum_pocetka: str, client: Optional[CrorisClient] = None
) -> list[RadniOdnos]:
    """
    Dohvati radne odnose za ustanovu po OIB-u i datumu početka.

    datum_pocetka format: 'DD.MM.YYYY.'  (npr. '01.01.2024.')
    """
    c = client or get_client()
    items = c.get_embedded(
        _url("/radniOdnos/ustanova"),
        "radniOdnos",
        params={"oib": oib_ustanove, "datumPocetka": datum_pocetka},
    )
    return [RadniOdnos.from_dict(item) for item in items]
