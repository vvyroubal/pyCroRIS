from typing import Optional

from ..client import CrorisClient, get_client
from ..models.publikacija import Publikacija


def get_publikacija(
    publikacija_id: int, client: Optional[CrorisClient] = None
) -> Publikacija:
    """Dohvati publikaciju po internom ID-u."""
    c = client or get_client()
    return Publikacija.from_dict(c.get(f"/publikacija/{publikacija_id}"))


def get_publikacije_projekta(
    projekt_id: int, client: Optional[CrorisClient] = None
) -> list[Publikacija]:
    """Dohvati sve publikacije vezane uz projekt."""
    c = client or get_client()
    items = c.get_embedded(f"/publikacija/projekt/{projekt_id}", "publikacije")
    return [Publikacija.from_dict(item) for item in items]
