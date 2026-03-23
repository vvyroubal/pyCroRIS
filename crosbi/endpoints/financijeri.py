from typing import Optional

from ..client import CrorisClient, get_client
from ..models.financijer import Financijer


def get_financijer(
    financijer_id: int, client: Optional[CrorisClient] = None
) -> Financijer:
    """Dohvati financijera po internom ID-u."""
    c = client or get_client()
    return Financijer.from_dict(c.get(f"/financijer/{financijer_id}"))


def get_financijeri_projekta(
    projekt_id: int, client: Optional[CrorisClient] = None
) -> list[Financijer]:
    """Dohvati sve financijere vezane uz projekt."""
    c = client or get_client()
    items = c.get_embedded(f"/financijer/projekt/{projekt_id}", "financijeri")
    return [Financijer.from_dict(item) for item in items]
