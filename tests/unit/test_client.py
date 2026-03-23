"""Testovi za crosbi.client — CrorisClient."""

import pytest
import responses as resp_lib
from requests.exceptions import HTTPError, RequestException

from crosbi.client import CrorisClient, get_client, set_client
from crosbi.config import Config

BASE = "https://www.croris.hr/projekti-api"


@pytest.fixture
def client(test_config):
    return CrorisClient(test_config)


@pytest.fixture
def anon_client():
    """Klijent bez vjerodajnica."""
    return CrorisClient(Config(username="", password=""))


# ---------------------------------------------------------------------------
# Inicijalizacija sjednice
# ---------------------------------------------------------------------------


class TestSessionSetup:
    def test_auth_set_when_credentials_provided(self, client):
        assert client.session.auth == ("testuser", "testpass")

    def test_auth_none_when_no_credentials(self, anon_client):
        assert anon_client.session.auth is None

    def test_accept_header_set(self, client):
        assert client.session.headers["Accept"] == "application/hal+json"

    def test_https_adapter_mounted(self, client):
        assert "https://" in client.session.adapters


# ---------------------------------------------------------------------------
# CrorisClient.get()
# ---------------------------------------------------------------------------


class TestGet:
    @resp_lib.activate
    def test_relative_path_prepends_base_url(self, client):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt/1", json={"id": 1}, status=200)
        result = client.get("/projekt/1")
        assert result == {"id": 1}

    @resp_lib.activate
    def test_absolute_url_used_directly(self, client):
        url = "https://www.croris.hr/ustanove-api/ustanova/5"
        resp_lib.add(resp_lib.GET, url, json={"id": 5}, status=200)
        result = client.get(url)
        assert result == {"id": 5}

    @resp_lib.activate
    def test_passes_query_params(self, client):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json={"_embedded": {}}, status=200)
        client.get("/projekt", params={"pageNumber": 1, "pageSize": 10})
        req = resp_lib.calls[0].request
        assert "pageNumber=1" in req.url
        assert "pageSize=10" in req.url

    @resp_lib.activate
    def test_raises_on_http_error(self, client):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt/999", status=404)
        with pytest.raises(HTTPError):
            client.get("/projekt/999")

    @resp_lib.activate
    def test_raises_on_server_error(self, client):
        # Retry adapter ponovi 500 ukupno max_retries+1 puta, pa baca RetryError
        # koji je podklasa RequestException, a ne HTTPError.
        for _ in range(4):  # 1 inicial + 3 retry = max_retries(3) iz test_config
            resp_lib.add(resp_lib.GET, f"{BASE}/projekt", status=500)
        with pytest.raises(RequestException):
            client.get("/projekt")


# ---------------------------------------------------------------------------
# CrorisClient.get_embedded()
# ---------------------------------------------------------------------------


class TestGetEmbedded:
    @resp_lib.activate
    def test_returns_embedded_list(self, client):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt/ustanova/123",
                     json={"_embedded": {"projekti": [{"id": 1}, {"id": 2}]}},
                     status=200)
        result = client.get_embedded("/projekt/ustanova/123", "projekti")
        assert result == [{"id": 1}, {"id": 2}]

    @resp_lib.activate
    def test_returns_empty_list_when_no_embedded(self, client):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt/ustanova/123",
                     json={"_links": {}}, status=200)
        result = client.get_embedded("/projekt/ustanova/123", "projekti")
        assert result == []

    @resp_lib.activate
    def test_returns_empty_list_when_key_missing(self, client):
        resp_lib.add(resp_lib.GET, f"{BASE}/nesto",
                     json={"_embedded": {"drugi_kljuc": []}}, status=200)
        result = client.get_embedded("/nesto", "projekti")
        assert result == []


# ---------------------------------------------------------------------------
# CrorisClient.paginate()
# ---------------------------------------------------------------------------


class TestPaginate:
    @resp_lib.activate
    def test_single_page(self, client, paginated_page2):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json=paginated_page2, status=200)
        results = list(client.paginate("/projekt", "projekti"))
        assert results == [{"id": 3}]

    @resp_lib.activate
    def test_multiple_pages(self, client, paginated_page1, paginated_page2):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json=paginated_page1, status=200)
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json=paginated_page2, status=200)
        results = list(client.paginate("/projekt", "projekti"))
        assert len(results) == 3
        assert results[0] == {"id": 1}
        assert results[2] == {"id": 3}

    @resp_lib.activate
    def test_empty_first_page_stops_immediately(self, client):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json={"_embedded": {"projekti": []}, "_links": {}},
                     status=200)
        results = list(client.paginate("/projekt", "projekti"))
        assert results == []
        assert len(resp_lib.calls) == 1

    @resp_lib.activate
    def test_page_parameters_sent(self, client, paginated_page2):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json=paginated_page2, status=200)
        list(client.paginate("/projekt", "projekti"))
        req = resp_lib.calls[0].request
        assert "pageNumber=1" in req.url
        assert "pageSize=10" in req.url  # test_config.page_size == 10

    @resp_lib.activate
    def test_page_number_increments(self, client, paginated_page1, paginated_page2):
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json=paginated_page1, status=200)
        resp_lib.add(resp_lib.GET, f"{BASE}/projekt",
                     json=paginated_page2, status=200)
        list(client.paginate("/projekt", "projekti"))
        assert "pageNumber=1" in resp_lib.calls[0].request.url
        assert "pageNumber=2" in resp_lib.calls[1].request.url


# ---------------------------------------------------------------------------
# get_client / set_client
# ---------------------------------------------------------------------------


class TestGetSetClient:
    def test_set_and_get_client(self, client):
        set_client(client)
        assert get_client() is client

    def test_get_client_lazy_init(self, monkeypatch):
        import crosbi.client as client_module
        monkeypatch.setattr(client_module, "_default_client", None)
        c = get_client()
        assert isinstance(c, CrorisClient)
