from typing import Optional

from ..client import CrorisClient, get_client
from ..models.osoba import Osoba


def get_osoba(osoba_id: int, client: Optional[CrorisClient] = None) -> Osoba:
    """Dohvati osobu po internom ID-u."""
    c = client or get_client()
    return Osoba.from_dict(c.get(f"/osoba/{osoba_id}"))


def get_osoba_by_oib(oib: str, client: Optional[CrorisClient] = None) -> Osoba:
    """Dohvati osobu po OIB-u."""
    c = client or get_client()
    return Osoba.from_dict(c.get(f"/osoba/oib/{oib}"))


def get_voditelj_by_oib(oib: str, client: Optional[CrorisClient] = None) -> Osoba:
    """Dohvati voditelja projekta po OIB-u."""
    c = client or get_client()
    return Osoba.from_dict(c.get(f"/osoba/voditelj/oib/{oib}"))


def get_osobe_projekta(
    projekt_id: int, client: Optional[CrorisClient] = None
) -> list[Osoba]:
    """Dohvati sve osobe vezane uz projekt."""
    c = client or get_client()
    items = c.get_embedded(f"/osoba/projekt/{projekt_id}", "osobe")
    return [Osoba.from_dict(item) for item in items]
