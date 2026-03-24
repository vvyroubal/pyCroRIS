"""HTTP klijent za CroRIS REST API-je s podrškom za HAL+JSON i paginaciju."""
from typing import Any, Generator, Iterator, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config, config as default_config


class CrorisClient:
    """HTTP klijent za CroRIS Projekti API (HAL+JSON)."""

    def __init__(self, cfg: Optional[Config] = None) -> None:
        """Inicijalizira klijenta s danom konfiguracijom ili globalnom zadanom."""
        self.cfg = cfg or default_config
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        """Izgraditi requests.Session s autentikacijom, zaglavljima i retry adapterom."""
        session = requests.Session()
        if self.cfg.username and self.cfg.password:
            session.auth = (self.cfg.username, self.cfg.password)
        session.headers.update({"Accept": "application/hal+json"})
        retry = Retry(
            total=self.cfg.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get(self, path: str, params: Optional[dict] = None) -> dict[str, Any]:
        """GET zahtjev na zadanu putanju, vraća parsed JSON."""
        url = path if path.startswith("http") else f"{self.cfg.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.cfg.timeout)
        response.raise_for_status()
        return response.json()

    def get_embedded(
        self, path: str, key: str, params: Optional[dict] = None
    ) -> list[dict]:
        """Dohvati `_embedded.<key>` listu iz HAL+JSON odgovora."""
        data = self.get(path, params=params)
        return data.get("_embedded", {}).get(key, [])

    def paginate(self, path: str, key: str) -> Generator[dict, None, None]:
        """Generator koji prolazi sve stranice paginiranog endpointa."""
        page = 1
        while True:
            params = {"pageNumber": page, "pageSize": self.cfg.page_size}
            data = self.get(path, params=params)
            items: list = data.get("_embedded", {}).get(key, [])
            if not items:
                break
            yield from items
            if "next" not in data.get("_links", {}):
                break
            page += 1

    def index(self) -> dict[str, Any]:
        """Dohvati HATEOAS index sa svim dostupnim linkovima."""
        return self.get("/")


_default_client: Optional[CrorisClient] = None


def get_client() -> CrorisClient:
    """Vrati globalnu instancu klijenta (lazy inicijalizacija)."""
    global _default_client
    if _default_client is None:
        _default_client = CrorisClient()
    return _default_client


def set_client(client: CrorisClient) -> None:
    """Postavi globalnu instancu klijenta (npr. s custom konfiguracijom)."""
    global _default_client
    _default_client = client
