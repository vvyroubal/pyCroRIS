"""Endpointi za CroRIS Događanja API (dogadanja-api)."""
from typing import Generator, Optional

from ..client import CrorisClient, get_client
from ..config import DOGADANJA_BASE_URL
from ..models.dogadanje import Dogadanje, PublikacijaDogadanje


def _url(path: str) -> str:
    return f"{DOGADANJA_BASE_URL}{path}"


def get_dogadanje(
    dogadanje_id: int, client: Optional[CrorisClient] = None
) -> Dogadanje:
    """Dohvati jedno događanje po ID-u."""
    c = client or get_client()
    return Dogadanje.from_dict(c.get(_url(f"/dogadanje/{dogadanje_id}")))


def list_dogadanja(
    client: Optional[CrorisClient] = None,
) -> Generator[Dogadanje, None, None]:
    """Generator koji prolazi sva događanja (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/dogadanje"), "dogadanje"):
        yield Dogadanje.from_dict(item)


def get_dogadanja_ustanove(
    ustanova_id: int, client: Optional[CrorisClient] = None
) -> Generator[Dogadanje, None, None]:
    """Generator koji prolazi sva događanja odabrane ustanove (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/dogadanje"), "dogadanje", params={"ustanovaId": ustanova_id}):
        yield Dogadanje.from_dict(item)


def get_dogadanja_created_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi događanja kreiranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/dogadanje/created-last-month"))
    return data.get("_embedded", {}).get("dogadanjaIds", [])


def get_dogadanja_updated_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi događanja ažuriranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/dogadanje/updated-last-month"))
    return data.get("_embedded", {}).get("dogadanjaIds", [])


def get_dogadanja_deleted_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi događanja obrisanih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/dogadanje/deleted-last-month"))
    return data.get("_embedded", {}).get("dogadanjaIds", [])


def get_publikacije_dogadanja(
    dogadanje_id: int, client: Optional[CrorisClient] = None
) -> list[PublikacijaDogadanje]:
    """Dohvati sve publikacije vezane uz zadano događanje."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/publikacija/dogadanje/{dogadanje_id}"), "publikacije")
    return [PublikacijaDogadanje.from_dict(item) for item in items]


def get_dogadanje_publikacije(
    pub_id: int, client: Optional[CrorisClient] = None
) -> PublikacijaDogadanje:
    """Dohvati vezu između publikacije i događanja po ID-u publikacije."""
    c = client or get_client()
    return PublikacijaDogadanje.from_dict(c.get(_url(f"/publikacija/{pub_id}")))
