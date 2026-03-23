from typing import Generator, Optional

from ..client import CrorisClient, get_client
from ..models.projekt import Projekt


def get_projekt(projekt_id: int, client: Optional[CrorisClient] = None) -> Projekt:
    """Dohvati jedan projekt po internom ID-u."""
    c = client or get_client()
    data = c.get(f"/projekt/{projekt_id}")
    return Projekt.from_dict(data)


def list_projekti(
    client: Optional[CrorisClient] = None,
) -> Generator[Projekt, None, None]:
    """Generator koji prolazi sve projekte (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate("/projekt", "projekti"):
        yield Projekt.from_dict(item)


def get_projekti_po_ustanovi(
    mbu: str, client: Optional[CrorisClient] = None
) -> list[Projekt]:
    """Dohvati sve projekte u kojima sudjeluje ustanova s danim MBU kodom."""
    c = client or get_client()
    items = c.get_embedded(f"/projekt/ustanova/{mbu}", "projekti")
    return [Projekt.from_dict(item) for item in items]
