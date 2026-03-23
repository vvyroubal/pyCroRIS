"""Endpointi za CroRIS CROSBI API (crosbi-api) — bibliografske publikacije."""
from typing import Generator, Optional

import requests

from ..client import CrorisClient, get_client
from ..config import CROSBI_BASE_URL
from ..models.publikacija_crosbi import (
    OsobaPublikacija,
    ProjektPublikacija,
    PublikacijaCrosbi,
    UstanovaPublikacija,
)


def _url(path: str) -> str:
    return f"{CROSBI_BASE_URL}{path}"


def get_publikacija(
    pub_id: int, client: Optional[CrorisClient] = None
) -> PublikacijaCrosbi:
    """Dohvati jednu CROSBI publikaciju po ID-u."""
    c = client or get_client()
    return PublikacijaCrosbi.from_dict(c.get(_url(f"/publikacija/{pub_id}")))


def list_publikacije(
    client: Optional[CrorisClient] = None,
) -> Generator[PublikacijaCrosbi, None, None]:
    """Generator koji prolazi sve CROSBI publikacije (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/publikacija"), "publikacije"):
        yield PublikacijaCrosbi.from_dict(item)


def get_publikacije_updated_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi publikacija ažuriranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/publikacija/updated-last-month"))
    return data.get("_embedded", {}).get("publikacijeIds", [])


def get_publikacije_deleted_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi publikacija obrisanih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/publikacija/deleted-last-month"))
    return data.get("_embedded", {}).get("publikacijeIds", [])


def get_publikacije_created_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi publikacija kreiranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/publikacija/created-last-month"))
    return data.get("_embedded", {}).get("publikacijeIds", [])


# --- Ustanove ↔ Publikacije ---


def get_publikacije_ustanove(
    ustanova_id: int, client: Optional[CrorisClient] = None
) -> UstanovaPublikacija:
    """Dohvati publikacije za zadanu ustanovu (po ID-u)."""
    c = client or get_client()
    return UstanovaPublikacija.from_dict(c.get(_url(f"/ustanova/{ustanova_id}")))


def get_ustanove_publikacije(
    pub_id: int, client: Optional[CrorisClient] = None
) -> list[UstanovaPublikacija]:
    """Dohvati sve ustanove vezane uz zadanu publikaciju."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/ustanova/publikacija/{pub_id}"), "ustanove")
    return [UstanovaPublikacija.from_dict(item) for item in items]


# --- Projekti ↔ Publikacije ---


def get_publikacije_projekta(
    projekt_id: int, client: Optional[CrorisClient] = None
) -> ProjektPublikacija:
    """Dohvati publikacije vezane uz projekt (CROSBI)."""
    c = client or get_client()
    return ProjektPublikacija.from_dict(c.get(_url(f"/projekt/{projekt_id}")))


def get_projekti_publikacije(
    pub_id: int, client: Optional[CrorisClient] = None
) -> list[ProjektPublikacija]:
    """Dohvati sve projekte vezane uz zadanu publikaciju."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/projekt/publikacija/{pub_id}"), "projekti")
    return [ProjektPublikacija.from_dict(item) for item in items]


# --- Osobe ↔ Publikacije ---


def get_publikacije_osobe(
    osoba_id: int, client: Optional[CrorisClient] = None
) -> OsobaPublikacija:
    """Dohvati publikacije osobe po internom ID-u."""
    c = client or get_client()
    return OsobaPublikacija.from_dict(c.get(_url(f"/osoba/{osoba_id}")))


def get_publikacije_osobe_by_mbz(
    mbz: str, client: Optional[CrorisClient] = None
) -> OsobaPublikacija:
    """Dohvati publikacije osobe po matičnom broju znanstvenika (MBZ)."""
    c = client or get_client()
    return OsobaPublikacija.from_dict(c.get(_url(f"/osoba/maticni-broj/{mbz}")))


def get_osobe_publikacije(
    pub_id: int, client: Optional[CrorisClient] = None
) -> list[OsobaPublikacija]:
    """Dohvati sve osobe vezane uz zadanu publikaciju."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/osoba/publikacija/{pub_id}"), "osobe")
    return [OsobaPublikacija.from_dict(item) for item in items]


# --- Import (POST) ---


def import_casopis_rad(
    records: list[dict], client: Optional[CrorisClient] = None
) -> dict:
    """
    Uvoz radova u časopisima (batch, max 100 po pozivu).

    Svaki zapis mora sadržavati obavezna polja prema CasopisRadDto shemi.
    Zapisi s postojećim DOI-em u bazi bit će preskočeni.
    Vraća BatchSaveStatus rječnik.
    """
    if len(records) > 100:
        raise ValueError("Maksimalno 100 zapisa po pozivu.")
    c = client or get_client()
    url = _url("/publikacija/import/casopisi-rad")
    response = c.session.post(
        url,
        json=records,
        timeout=c.cfg.timeout,
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response.json()
