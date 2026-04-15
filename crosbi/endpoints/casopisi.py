"""Endpointi za CroRIS Časopisi API (casopisi-api)."""
from typing import Generator, Optional

from ..client import CrorisClient, get_client
from ..config import CASOPISI_BASE_URL
from ..models.casopis import Casopis, PublikacijaCasopis


def _url(path: str) -> str:
    return f"{CASOPISI_BASE_URL}{path}"


def get_casopis(casopis_id: int, client: Optional[CrorisClient] = None) -> Casopis:
    """Dohvati jedan časopis po ID-u."""
    c = client or get_client()
    return Casopis.from_dict(c.get(_url(f"/casopis/{casopis_id}")))


def list_casopisi(
    client: Optional[CrorisClient] = None,
) -> Generator[Casopis, None, None]:
    """Generator koji prolazi sve časopise (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/casopis"), "casopis"):
        yield Casopis.from_dict(item)


def get_casopisi_ustanove(
    ustanova_id: int, client: Optional[CrorisClient] = None
) -> Generator[Casopis, None, None]:
    """Generator koji prolazi sve časopise odabrane ustanove (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/casopis"), "casopis", params={"ustanovaId": ustanova_id}):
        yield Casopis.from_dict(item)


def get_casopisi_updated_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi časopisa ažuriranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/casopis/updated-last-month"))
    return data.get("_embedded", {}).get("casopisiIds", [])


def get_casopisi_deleted_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi časopisa obrisanih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/casopis/deleted-last-month"))
    return data.get("_embedded", {}).get("casopisiIds", [])


def get_casopisi_created_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """ID-ovi časopisa kreiranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/casopis/created-last-month"))
    return data.get("_embedded", {}).get("casopisiIds", [])


def get_publikacije_casopisa(
    casopis_id: int, client: Optional[CrorisClient] = None
) -> list[PublikacijaCasopis]:
    """Dohvati sve publikacije objavljene u zadanom časopisu."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/publikacija/casopis/{casopis_id}"), "publikacije")
    return [PublikacijaCasopis.from_dict(item) for item in items]


def get_casopis_publikacije(
    pub_id: int, client: Optional[CrorisClient] = None
) -> PublikacijaCasopis:
    """Dohvati vezu između publikacije i časopisa po ID-u publikacije."""
    c = client or get_client()
    return PublikacijaCasopis.from_dict(c.get(_url(f"/publikacija/{pub_id}")))
