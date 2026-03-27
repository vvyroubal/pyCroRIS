"""Integracijski testovi za CrorisClient — zahtijevaju mrežni pristup."""
from typing import cast

import pytest
import requests
from requests.adapters import HTTPAdapter

from crosbi.client import CrorisClient, get_client, set_client
from crosbi.config import Config, PROJEKTI_BASE_URL, USTANOVE_BASE_URL


# ---------------------------------------------------------------------------
# Helperi
# ---------------------------------------------------------------------------

PROJEKT_ID = 1
NEPOSTOJECI_ID = 999_999_999


# ---------------------------------------------------------------------------
# Inicijalizacija i konfiguracija sesije (bez mrežnih poziva)
# ---------------------------------------------------------------------------


class TestClientInit:
    def test_default_config_koristi_projekti_base_url(self):
        client = CrorisClient()
        assert client.cfg.base_url == PROJEKTI_BASE_URL

    def test_custom_config_se_zadrzava(self):
        cfg = Config(base_url=USTANOVE_BASE_URL, timeout=10, page_size=25)
        client = CrorisClient(cfg)
        assert client.cfg.base_url == USTANOVE_BASE_URL
        assert client.cfg.timeout == 10
        assert client.cfg.page_size == 25

    def test_session_se_kreira_na_init(self):
        client = CrorisClient()
        assert isinstance(client.session, requests.Session)


class TestSessionConfig:
    def setup_method(self):
        self.client = CrorisClient()

    def test_accept_header_je_hal_json(self):
        assert self.client.session.headers["Accept"] == "application/hal+json"

    def test_bez_auth_po_defaultu(self):
        assert self.client.session.auth is None

    def test_auth_se_postavlja_kad_su_zadane_vjerodajnice(self):
        cfg = Config(username="korisnik", password="lozinka")
        client = CrorisClient(cfg)
        assert client.session.auth == ("korisnik", "lozinka")

    def test_prazan_username_ne_postavlja_auth(self):
        cfg = Config(username="", password="lozinka")
        client = CrorisClient(cfg)
        assert client.session.auth is None

    def test_retry_adapter_montiran_za_https(self):
        adapter = self.client.session.get_adapter("https://example.com")
        assert isinstance(adapter, HTTPAdapter)

    def test_retry_adapter_montiran_za_http(self):
        adapter = self.client.session.get_adapter("http://example.com")
        assert isinstance(adapter, HTTPAdapter)

    def _http_adapter(self, url: str = "https://example.com") -> HTTPAdapter:
        return cast(HTTPAdapter, self.client.session.get_adapter(url))

    def test_retry_ukupni_broj(self):
        assert self._http_adapter().max_retries.total == 3

    def test_retry_status_lista(self):
        assert set(self._http_adapter().max_retries.status_forcelist) == {429, 500, 502, 503, 504}

    def test_retry_dozvoljene_metode(self):
        allowed = self._http_adapter().max_retries.allowed_methods
        assert allowed is not None and "GET" in allowed

    def test_custom_max_retries(self):
        cfg = Config(max_retries=5)
        client = CrorisClient(cfg)
        adapter = cast(HTTPAdapter, client.session.get_adapter("https://example.com"))
        assert adapter.max_retries.total == 5


# ---------------------------------------------------------------------------
# Mrežni pozivi — stvarni API
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestIndex:
    def setup_method(self):
        self.client = CrorisClient()

    def test_index_vraca_dict(self):
        result = self.client.index()
        assert isinstance(result, dict)

    def test_index_sadrzi_links(self):
        result = self.client.index()
        assert "_links" in result

    def test_index_links_sadrze_projekti(self):
        result = self.client.index()
        assert "projekti" in result["_links"]

    def test_index_links_sadrze_self(self):
        result = self.client.index()
        assert "self" in result["_links"]

    def test_index_links_sadrze_dokumentaciju(self):
        result = self.client.index()
        assert "dokumentacija" in result["_links"]

    def test_index_href_projekti_je_ispravan_url(self):
        result = self.client.index()
        href = result["_links"]["projekti"]["href"]
        assert href.startswith("https://")
        assert "projekt" in href


@pytest.mark.integration
class TestGet:
    def setup_method(self):
        self.client = CrorisClient()

    def test_relativna_putanja_vraca_dict(self):
        result = self.client.get(f"/projekt/{PROJEKT_ID}")
        assert isinstance(result, dict)

    def test_relativna_putanja_sadrzi_id(self):
        result = self.client.get(f"/projekt/{PROJEKT_ID}")
        assert result["id"] == PROJEKT_ID

    def test_apsolutni_url_radi(self):
        url = f"{PROJEKTI_BASE_URL}/projekt/{PROJEKT_ID}"
        result = self.client.get(url)
        assert result["id"] == PROJEKT_ID

    def test_relativna_i_apsolutna_putanja_daju_isti_rezultat(self):
        rel = self.client.get(f"/projekt/{PROJEKT_ID}")
        aps = self.client.get(f"{PROJEKTI_BASE_URL}/projekt/{PROJEKT_ID}")
        assert rel["id"] == aps["id"]

    def test_query_parametri_se_prosljeduju(self):
        # pageSize i pageNumber su standardni paginacijski parametri
        result = self.client.get("/projekt", params={"pageNumber": 1, "pageSize": 5})
        assert isinstance(result, dict)

    def test_nepostojeci_resurs_pokrece_http_error(self):
        with pytest.raises(requests.HTTPError):
            self.client.get(f"/projekt/{NEPOSTOJECI_ID}")

    def test_odgovor_sadrzi_links(self):
        result = self.client.get(f"/projekt/{PROJEKT_ID}")
        assert "_links" in result

    def test_razlicite_base_url_konfiguracije(self):
        cfg = Config(base_url=USTANOVE_BASE_URL)
        client = CrorisClient(cfg)
        result = client.get("/croris-ustanove/ustanova")
        assert isinstance(result, dict)


STRANICA_1 = {"pageNumber": 1, "pageSize": 10}


@pytest.mark.integration
class TestGetEmbedded:
    def setup_method(self):
        self.client = CrorisClient()

    def test_vraca_listu(self):
        items = self.client.get_embedded("/projekt", "projekti", params=STRANICA_1)
        assert isinstance(items, list)

    def test_lista_nije_prazna(self):
        items = self.client.get_embedded("/projekt", "projekti", params=STRANICA_1)
        assert len(items) > 0

    def test_elementi_su_rjecnici(self):
        items = self.client.get_embedded("/projekt", "projekti", params=STRANICA_1)
        assert all(isinstance(item, dict) for item in items)

    def test_elementi_imaju_id(self):
        items = self.client.get_embedded("/projekt", "projekti", params=STRANICA_1)
        assert all("id" in item for item in items)

    def test_nepostojeci_kljuc_vraca_praznu_listu(self):
        items = self.client.get_embedded("/projekt", "nepostojeci_kljuc", params=STRANICA_1)
        assert items == []

    def test_ustanove_api(self):
        cfg = Config(base_url=USTANOVE_BASE_URL)
        client = CrorisClient(cfg)
        items = client.get_embedded("/croris-ustanove/ustanova", "ustanove")
        assert len(items) > 0

    def test_page_size_utjece_na_broj_rezultata(self):
        # API prihvaća pageSize u rasponu 5–100
        items_10 = self.client.get_embedded(
            "/projekt", "projekti", params={"pageNumber": 1, "pageSize": 10}
        )
        items_5 = self.client.get_embedded(
            "/projekt", "projekti", params={"pageNumber": 1, "pageSize": 5}
        )
        assert len(items_10) >= len(items_5)
        assert len(items_5) <= 5


@pytest.mark.integration
class TestPaginate:
    """Testovi paginacije — koriste islice da izbjegnu preuzimanje svih projekata."""

    def setup_method(self):
        # page_size=5 osigurava prijelaz stranice već nakon 6 elemenata
        self.client = CrorisClient(Config(page_size=5))

    def _uzmih(self, n: int) -> list[dict]:
        from itertools import islice
        return list(islice(self.client.paginate("/projekt", "projekti"), n))

    def test_vraca_generator(self):
        import types
        gen = self.client.paginate("/projekt", "projekti")
        assert isinstance(gen, types.GeneratorType)

    def test_generator_daje_elemente(self):
        assert len(self._uzmih(3)) == 3

    def test_elementi_su_rjecnici(self):
        assert all(isinstance(item, dict) for item in self._uzmih(5))

    def test_elementi_imaju_id(self):
        assert all("id" in item for item in self._uzmih(5))

    def test_paginacija_prelazi_prvu_stranicu(self):
        # page_size=5, uzimamo 6 → mora doći s druge stranice
        items = self._uzmih(6)
        assert len(items) == 6

    def test_nema_duplikata_id_kroz_stranice(self):
        items = self._uzmih(15)
        ids = [item["id"] for item in items]
        assert len(ids) == len(set(ids))

    def test_nepostojeci_kljuc_vraca_prazan_generator(self):
        items = list(self.client.paginate("/projekt", "nepostojeci_kljuc"))
        assert items == []


# ---------------------------------------------------------------------------
# Globalni singleton
# ---------------------------------------------------------------------------


class TestGlobalClient:
    def setup_method(self):
        # Resetiraj singleton prije svakog testa
        set_client(CrorisClient())

    def test_get_client_vraca_istu_instancu(self):
        a = get_client()
        b = get_client()
        assert a is b

    def test_set_client_zamjenjuje_singleton(self):
        novi = CrorisClient(Config(timeout=99))
        set_client(novi)
        assert get_client() is novi

    def test_get_client_nakon_set_client_vraca_novi_objekt(self):
        stari = get_client()
        novi = CrorisClient(Config(timeout=99))
        set_client(novi)
        assert get_client() is not stari

    def test_get_client_lazy_inicijalizacija(self):
        # Postavi singleton na None ručno
        import crosbi.client as mod
        mod._default_client = None
        client = get_client()
        assert client is not None
        assert isinstance(client, CrorisClient)

    def test_set_client_postavlja_custom_konfiguraciju(self):
        cfg = Config(base_url=USTANOVE_BASE_URL, page_size=10)
        set_client(CrorisClient(cfg))
        assert get_client().cfg.base_url == USTANOVE_BASE_URL
        assert get_client().cfg.page_size == 10
