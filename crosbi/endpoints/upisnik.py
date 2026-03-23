"""Endpointi za CroRIS Ustanove API (ustanove-api).

Pokriva:
- MZO upisnik ustanova (/upisnik-ustanova/*)
- PPG klasifikacija (/evidencija-ppg/*)
- CroRIS ustanove (/croris-ustanove/*)
"""
from typing import Optional

from ..client import CrorisClient, get_client
from ..config import USTANOVE_BASE_URL
from ..models.ustanova_reg import Grana, Podrucje, Polje, UstanovaReg


def _url(path: str) -> str:
    return f"{USTANOVE_BASE_URL}{path}"


# --- MZO Upisnik ustanova ---


def get_ustanova_by_id(
    ustanova_id: int, client: Optional[CrorisClient] = None
) -> UstanovaReg:
    """Dohvati ustanovu iz MZO upisnika po internom ID-u."""
    c = client or get_client()
    return UstanovaReg.from_dict(c.get(_url(f"/upisnik-ustanova/ustanova/{ustanova_id}")))


def get_ustanova_by_mbu(
    mbu: str, client: Optional[CrorisClient] = None
) -> UstanovaReg:
    """Dohvati ustanovu iz MZO upisnika po MBU kodu."""
    c = client or get_client()
    data = c.get(_url("/upisnik-ustanova/ustanova"), params={"mbu": mbu})
    # Može vratiti jedan objekt ili kolekciju
    if "_embedded" in data:
        items = data["_embedded"].get("ustanove", [])
        return UstanovaReg.from_dict(items[0]) if items else None
    return UstanovaReg.from_dict(data)


def get_sve_aktivne_ustanove(
    client: Optional[CrorisClient] = None,
) -> list[UstanovaReg]:
    """Dohvati sve aktivne ustanove iz MZO upisnika."""
    c = client or get_client()
    items = c.get_embedded(_url("/upisnik-ustanova/ustanova"), "ustanove")
    return [UstanovaReg.from_dict(item) for item in items]


def get_znanstvene_ustanove(
    client: Optional[CrorisClient] = None,
) -> list[UstanovaReg]:
    """Dohvati sve znanstvene ustanove."""
    c = client or get_client()
    items = c.get_embedded(_url("/upisnik-ustanova/ustanova/znanstvena"), "ustanove")
    return [UstanovaReg.from_dict(item) for item in items]


def get_visoka_ucilista(
    client: Optional[CrorisClient] = None,
) -> list[UstanovaReg]:
    """Dohvati sva visoka učilišta."""
    c = client or get_client()
    items = c.get_embedded(_url("/upisnik-ustanova/ustanova/visoko-uciliste"), "ustanove")
    return [UstanovaReg.from_dict(item) for item in items]


def get_neaktivne_ustanove(
    client: Optional[CrorisClient] = None,
) -> list[UstanovaReg]:
    """Dohvati sve neaktivne ustanove iz MZO upisnika."""
    c = client or get_client()
    items = c.get_embedded(_url("/upisnik-ustanova/ustanova/neaktivna"), "ustanove")
    return [UstanovaReg.from_dict(item) for item in items]


def get_ustanova_by_mzo_id(
    mzo_id: int, client: Optional[CrorisClient] = None
) -> UstanovaReg:
    """Dohvati ustanovu po legacy MZO ID-u."""
    c = client or get_client()
    return UstanovaReg.from_dict(c.get(_url(f"/upisnik-ustanova/ustanova/mzo/{mzo_id}")))


# --- CroRIS ustanove ---


def get_croris_ustanove(
    client: Optional[CrorisClient] = None,
) -> list[UstanovaReg]:
    """Dohvati sve ustanove iz CroRIS registra."""
    c = client or get_client()
    items = c.get_embedded(_url("/croris-ustanove/ustanova"), "ustanove")
    return [UstanovaReg.from_dict(item) for item in items]


def get_croris_ustanova(
    ustanova_id: int, client: Optional[CrorisClient] = None
) -> UstanovaReg:
    """Dohvati CroRIS ustanovu po ID-u."""
    c = client or get_client()
    return UstanovaReg.from_dict(c.get(_url(f"/croris-ustanove/ustanova/{ustanova_id}")))


def get_javni_znanstveni_instituti(
    client: Optional[CrorisClient] = None,
) -> list[UstanovaReg]:
    """Dohvati sve javne znanstvene institute (JZI)."""
    c = client or get_client()
    items = c.get_embedded(_url("/croris-ustanove/ustanova/jzi"), "ustanove")
    return [UstanovaReg.from_dict(item) for item in items]


def get_ustanove_updated_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """Dohvati ID-ove ustanova ažuriranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/croris-ustanove/ustanova/updated-last-month"))
    return data.get("_embedded", {}).get("ustanoveIds", [])


def get_ustanove_created_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """Dohvati ID-ove ustanova kreiranih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/croris-ustanove/ustanova/created-last-month"))
    return data.get("_embedded", {}).get("ustanoveIds", [])


def get_ustanove_deleted_last_month(
    client: Optional[CrorisClient] = None,
) -> list[int]:
    """Dohvati ID-ove ustanova obrisanih prošli mjesec."""
    c = client or get_client()
    data = c.get(_url("/croris-ustanove/ustanova/deleted-last-month"))
    return data.get("_embedded", {}).get("ustanoveIds", [])


# --- PPG klasifikacija ---


def get_sva_podrucja(client: Optional[CrorisClient] = None) -> list[Podrucje]:
    """Dohvati sva PPG znanstvena područja."""
    c = client or get_client()
    items = c.get_embedded(_url("/evidencija-ppg/podrucje"), "podrucja")
    return [Podrucje.from_dict(item) for item in items]


def get_podrucje(
    podrucje_id: int, client: Optional[CrorisClient] = None
) -> Podrucje:
    """Dohvati jedno PPG područje po ID-u."""
    c = client or get_client()
    return Podrucje.from_dict(c.get(_url(f"/evidencija-ppg/podrucje/{podrucje_id}")))


def get_polje_s_granama(
    podrucje_id: int, polje_id: int, client: Optional[CrorisClient] = None
) -> Polje:
    """Dohvati PPG polje s granama."""
    c = client or get_client()
    return Polje.from_dict(
        c.get(_url(f"/evidencija-ppg/podrucje/{podrucje_id}/polje/{polje_id}"))
    )
