from typing import Optional

from ..client import CrorisClient, get_client
from ..models.ustanova import Ustanova


def get_ustanova(ustanova_id: int, client: Optional[CrorisClient] = None) -> Ustanova:
    """Dohvati ustanovu po internom ID-u."""
    c = client or get_client()
    return Ustanova.from_dict(c.get(f"/ustanova/{ustanova_id}"))


def get_ustanove_projekta(
    projekt_id: int, client: Optional[CrorisClient] = None
) -> list[Ustanova]:
    """Dohvati sve ustanove koje sudjeluju u projektu."""
    c = client or get_client()
    items = c.get_embedded(f"/ustanova/projekt/{projekt_id}", "ustanove")
    return [Ustanova.from_dict(item) for item in items]
