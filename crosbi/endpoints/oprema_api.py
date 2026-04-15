"""Endpointi za CroRIS Oprema API (oprema-api)."""
from typing import Generator, Optional

from ..client import CrorisClient, get_client
from ..config import OPREMA_BASE_URL
from ..models.oprema import Oprema, OpremaOsoba, Usluga, UslugaCjenik


def _url(path: str) -> str:
    return f"{OPREMA_BASE_URL}{path}"


# --- Oprema ---


def get_oprema(oprema_id: int, client: Optional[CrorisClient] = None) -> Oprema:
    """Dohvati jednu opremu po ID-u."""
    c = client or get_client()
    return Oprema.from_dict(c.get(_url(f"/oprema/{oprema_id}")))


def list_oprema(
    client: Optional[CrorisClient] = None,
) -> Generator[Oprema, None, None]:
    """Generator koji prolazi svu opremu (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/oprema"), "opreme"):
        yield Oprema.from_dict(item)


# --- Usluge ---


def get_usluga(usluga_id: int, client: Optional[CrorisClient] = None) -> Usluga:
    """Dohvati jednu uslugu po ID-u."""
    c = client or get_client()
    return Usluga.from_dict(c.get(_url(f"/usluga/{usluga_id}")))


def list_usluge(
    client: Optional[CrorisClient] = None,
) -> Generator[Usluga, None, None]:
    """Generator koji prolazi sve usluge (automatska paginacija)."""
    c = client or get_client()
    for item in c.paginate(_url("/usluga"), "usluge"):
        yield Usluga.from_dict(item)


def get_oprema_hrefs(
    ustanova_id: int, client: Optional[CrorisClient] = None
) -> list[str]:
    """Dohvati listu href URL-ova pridruzene opreme za odabranu ustanovu."""
    c = client or get_client()
    data = c.get(_url(f"/ustanova/{ustanova_id}"))
    return [item["href"] for item in data.get("pridruzenaOprema", [])]


def fetch_oprema_by_href(href: str) -> Oprema:
    """Dohvati jednu opremu po punom URL-u (svaki poziv kreira vlastiti klijent)."""
    return Oprema.from_dict(CrorisClient().get(href))


def get_oprema_ustanove(
    ustanova_id: int,
    client: Optional[CrorisClient] = None,
    max_workers: int = 10,
) -> tuple[list[Oprema], list[str]]:
    """Dohvati svu opremu odabrane ustanove paralelnim HTTP zahtjevima.

    Returns:
        (oprema_list, errors) — errors sadrži hrefs stavki koje su neuspješno dohvaćene.
    """
    import warnings
    from concurrent.futures import ThreadPoolExecutor, as_completed

    hrefs = get_oprema_hrefs(ustanova_id, client)
    results: list[Oprema] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fetch_oprema_by_href, href): href for href in hrefs}
        for future in as_completed(futures):
            href = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                warnings.warn(f"Neuspješan dohvat {href}: {exc}")
                errors.append(href)
    return results, errors


def get_usluge_ustanove(
    ustanova_id: int, client: Optional[CrorisClient] = None
) -> Generator[Usluga, None, None]:
    """Generator koji prolazi usluge odabrane ustanove.

    API ne podržava server-side filter po ustanovi za usluge; dohvaćamo sve
    (ukupno ~50) i filtriramo client-side po ustanova_id.
    """
    c = client or get_client()
    for item in c.paginate(_url("/usluga"), "usluge"):
        usluga = Usluga.from_dict(item)
        if usluga.ustanova_id == ustanova_id:
            yield usluga


def get_usluge_opreme(
    oprema_id: int, client: Optional[CrorisClient] = None
) -> list[Usluga]:
    """Dohvati sve usluge vezane uz zadanu opremu."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/usluga/oprema/{oprema_id}"), "usluge")
    return [Usluga.from_dict(item) for item in items]


# --- Osobe ---


def get_osobe_opreme(
    oprema_id: int, client: Optional[CrorisClient] = None
) -> list[OpremaOsoba]:
    """Dohvati sve kontaktne osobe za zadanu opremu."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/osoba/oprema/{oprema_id}"), "osobe")
    return [OpremaOsoba.from_dict(item) for item in items]


def get_osoba_opreme(
    osoba_id: int, client: Optional[CrorisClient] = None
) -> OpremaOsoba:
    """Dohvati jednu kontaktnu osobu za opremu po ID-u."""
    c = client or get_client()
    return OpremaOsoba.from_dict(c.get(_url(f"/osoba/oprema/osoba/{osoba_id}")))


# --- Cjenik ---


def get_cjenik_usluge(
    usluga_id: int, client: Optional[CrorisClient] = None
) -> list[UslugaCjenik]:
    """Dohvati cjenik za zadanu uslugu."""
    c = client or get_client()
    items = c.get_embedded(_url(f"/cjenik/usluga/{usluga_id}"), "cjenici")
    return [UslugaCjenik.from_dict(item) for item in items]


# --- Lookup endpointi (vraćaju sirove dict-ove) ---


def get_vrste_opreme(oprema_id: int, client: Optional[CrorisClient] = None) -> list[dict]:
    """Dohvati vrste opreme za zadanu opremu."""
    c = client or get_client()
    return c.get_embedded(_url(f"/vrsta-opreme/oprema/{oprema_id}"), "vrsteOpreme")


def get_vrste_analize(oprema_id: int, client: Optional[CrorisClient] = None) -> list[dict]:
    """Dohvati vrste analize za zadanu opremu."""
    c = client or get_client()
    return c.get_embedded(_url(f"/vrsta-analize/oprema/{oprema_id}"), "vrsteAnalize")


def get_primjene_opreme(oprema_id: int, client: Optional[CrorisClient] = None) -> list[dict]:
    """Dohvati primjene za zadanu opremu."""
    c = client or get_client()
    return c.get_embedded(_url(f"/primjena-opreme/oprema/{oprema_id}"), "primjeneOpreme")


def get_discipline_opreme(oprema_id: int, client: Optional[CrorisClient] = None) -> list[dict]:
    """Dohvati discipline za zadanu opremu."""
    c = client or get_client()
    return c.get_embedded(_url(f"/disciplina/oprema/{oprema_id}"), "discipline")


def get_poveznice_opreme(oprema_id: int, client: Optional[CrorisClient] = None) -> list[dict]:
    """Dohvati vanjske poveznice za zadanu opremu."""
    c = client or get_client()
    return c.get_embedded(_url(f"/poveznica/oprema/{oprema_id}"), "poveznice")


def download_file(file_id: int, client: Optional[CrorisClient] = None) -> bytes:
    """Preuzmi datoteku kao binarne podatke."""
    c = client or get_client()
    url = _url(f"/file/{file_id}/download")
    response = c.session.get(url, timeout=c.cfg.timeout)
    response.raise_for_status()
    return response.content


def get_image_base64(file_id: int, client: Optional[CrorisClient] = None) -> str:
    """Dohvati sliku kao base64 string."""
    c = client or get_client()
    data = c.get(_url(f"/file/img/{file_id}"))
    return data if isinstance(data, str) else str(data)
