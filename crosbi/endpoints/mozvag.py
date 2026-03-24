from typing import Optional

from ..client import CrorisClient, get_client
from ..models.mozvag import (
    FinancijerMozvag,
    OsobaMozvag,
    ProjektMozvag,
    UstanovaMozvag,
)


def _extract_list(data: object, *keys: str) -> list:
    """Izvuci listu iz odgovora — podržava i ravnu listu i HAL+JSON omotač."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        embedded = data.get("_embedded", {})
        for key in keys:
            if key in embedded:
                return embedded[key]
        # Ako nema _embedded, vrati prazan list
        return []
    return []


def get_ustanove(client: Optional[CrorisClient] = None) -> list[UstanovaMozvag]:
    """Dohvati popis svih ustanova (MOZVAG direktorij)."""
    c = client or get_client()
    data = c.get("/mozvag/institutions")
    items = _extract_list(data, "institutions", "institucije", "ustanove")
    return [UstanovaMozvag.from_dict(item) for item in items]


def get_financijere(client: Optional[CrorisClient] = None) -> list[FinancijerMozvag]:
    """Dohvati popis svih financijera s programima (MOZVAG direktorij)."""
    c = client or get_client()
    data = c.get("/mozvag/funders")
    items = _extract_list(data, "funders", "financijeri")
    return [FinancijerMozvag.from_dict(item) for item in items]


def get_projekti_ustanove(
    ustanova_id: int, godina: int, client: Optional[CrorisClient] = None
) -> list[ProjektMozvag]:
    """Dohvati sve projekte za ustanovu u zadanoj godini."""
    c = client or get_client()
    data = c.get(f"/mozvag/{ustanova_id}/{godina}")
    items = _extract_list(data, "projekti", "projects")
    return [ProjektMozvag.from_dict(item) for item in items]


def get_osoba_po_mbz(
    mbz: str, godina: int, client: Optional[CrorisClient] = None
) -> OsobaMozvag:
    """Dohvati sažetak projekata osobe po MBZ-u i godini."""
    c = client or get_client()
    data = c.get(f"/mozvag/person/{mbz}/{godina}")
    return OsobaMozvag.from_dict(data)


def get_osoba_po_oib(
    ustanova_id: int, oib: str, godina: int, client: Optional[CrorisClient] = None
) -> OsobaMozvag:
    """Dohvati sažetak projekata osobe po OIB-u, ustanovi i godini."""
    c = client or get_client()
    data = c.get(f"/mozvag/oib/{ustanova_id}/{oib}/{godina}")
    return OsobaMozvag.from_dict(data)


def get_osoba_po_mbz_ustanova(
    ustanova_id: int, mbz: str, godina: int, client: Optional[CrorisClient] = None
) -> OsobaMozvag:
    """Dohvati sažetak projekata osobe po MBZ-u, ustanovi i godini."""
    c = client or get_client()
    data = c.get(f"/mozvag/mbz/{ustanova_id}/{mbz}/{godina}")
    return OsobaMozvag.from_dict(data)
