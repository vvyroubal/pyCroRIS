"""Testovi za crosbi.endpoints.publikacije_crosbi."""

import pytest

from crosbi.endpoints.publikacije_crosbi import (
    get_publikacija,
    list_publikacije,
    get_publikacije_updated_last_month,
    get_publikacije_deleted_last_month,
    get_publikacije_created_last_month,
    get_publikacije_ustanove,
    get_ustanove_publikacije,
    get_publikacije_projekta,
)
from crosbi.models.publikacija_crosbi import (
    PublikacijaCrosbi,
    UstanovaPublikacija,
    ProjektPublikacija,
)
from crosbi.config import CROSBI_BASE_URL


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def publikacija_crosbi_raw():
    return {
        "crosbiId": 42,
        "naslov": "Rezultati istraživanja",
        "vrstaPublikacije": "Rad u časopisu",
        "tipPublikacije": "Izvorni znanstveni rad",
        "godina": 2022,
        "doi": "10.1234/test.2022",
        "_links": {"self": {"href": f"{CROSBI_BASE_URL}/publikacija/42"}},
    }


@pytest.fixture
def ustanova_publikacija_raw():
    return {
        "crorisId": 15,
        "naziv": "FER",
        "mbu": 1234567,
        "_links": {},
    }


@pytest.fixture
def projekt_publikacija_raw():
    return {
        "crorisId": 100,
        "naziv": "Testni projekt",
        "_links": {},
    }


class TestGetPublikacija:
    def test_poziva_ispravan_url(self, mock_client, publikacija_crosbi_raw):
        mock_client.get.return_value = publikacija_crosbi_raw
        get_publikacija(42, client=mock_client)
        mock_client.get.assert_called_once_with(f"{CROSBI_BASE_URL}/publikacija/42")

    def test_vraca_publikacija_crosbi(self, mock_client, publikacija_crosbi_raw):
        mock_client.get.return_value = publikacija_crosbi_raw
        result = get_publikacija(42, client=mock_client)
        assert isinstance(result, PublikacijaCrosbi)


class TestListPublikacije:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, publikacija_crosbi_raw):
        mock_client.paginate.return_value = iter([publikacija_crosbi_raw])
        list(list_publikacije(client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{CROSBI_BASE_URL}/publikacija", "publikacije"
        )

    def test_vraca_publikacija_instance(self, mock_client, publikacija_crosbi_raw):
        mock_client.paginate.return_value = iter([publikacija_crosbi_raw])
        results = list(list_publikacije(client=mock_client))
        assert isinstance(results[0], PublikacijaCrosbi)

    def test_prazan_odgovor(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(list_publikacije(client=mock_client)) == []


class TestGetPublikacijeUpdatedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"publikacijeIds": [1, 2]}}
        result = get_publikacije_updated_last_month(client=mock_client)
        assert result == [1, 2]

    def test_prazan_embedded(self, mock_client):
        mock_client.get.return_value = {}
        assert get_publikacije_updated_last_month(client=mock_client) == []


class TestGetPublikacijeDeletedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"publikacijeIds": [5]}}
        assert get_publikacije_deleted_last_month(client=mock_client) == [5]


class TestGetPublikacijeCreatedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"publikacijeIds": [10, 20]}}
        assert get_publikacije_created_last_month(client=mock_client) == [10, 20]


class TestGetPublikacijeUstanove:
    def test_poziva_ispravan_url(self, mock_client, ustanova_publikacija_raw):
        mock_client.get.return_value = ustanova_publikacija_raw
        get_publikacije_ustanove(15, client=mock_client)
        mock_client.get.assert_called_once_with(f"{CROSBI_BASE_URL}/ustanova/15")

    def test_vraca_ustanova_publikacija(self, mock_client, ustanova_publikacija_raw):
        mock_client.get.return_value = ustanova_publikacija_raw
        result = get_publikacije_ustanove(15, client=mock_client)
        assert isinstance(result, UstanovaPublikacija)
        assert result.croris_id == 15


class TestGetUstanovePublikacije:
    def test_poziva_ispravan_url(self, mock_client, ustanova_publikacija_raw):
        mock_client.get_embedded.return_value = [ustanova_publikacija_raw]
        get_ustanove_publikacije(42, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CROSBI_BASE_URL}/ustanova/publikacija/42", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_publikacija_raw):
        mock_client.get_embedded.return_value = [ustanova_publikacija_raw]
        result = get_ustanove_publikacije(42, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], UstanovaPublikacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_ustanove_publikacije(42, client=mock_client) == []


class TestGetPublikacijeProjekata:
    def test_poziva_ispravan_url(self, mock_client, projekt_publikacija_raw):
        mock_client.get.return_value = projekt_publikacija_raw
        get_publikacije_projekta(100, client=mock_client)
        mock_client.get.assert_called_once_with(f"{CROSBI_BASE_URL}/projekt/100")

    def test_vraca_projekt_publikacija(self, mock_client, projekt_publikacija_raw):
        mock_client.get.return_value = projekt_publikacija_raw
        result = get_publikacije_projekta(100, client=mock_client)
        assert isinstance(result, ProjektPublikacija)
        assert result.croris_id == 100


import responses as resp_lib
from crosbi.endpoints.publikacije_crosbi import (
    get_projekti_publikacije,
    get_publikacije_osobe,
    get_publikacije_osobe_by_mbz,
    get_osobe_publikacije,
    import_casopis_rad,
)
from crosbi.models.publikacija_crosbi import OsobaPublikacija


class TestGetProjektiPublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get_embedded.return_value = []
        get_projekti_publikacije(100, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CROSBI_BASE_URL}/projekt/publikacija/100", "projekti"
        )

    def test_vraca_listu_projekt_publikacija(self, mock_client):
        mock_client.get_embedded.return_value = [{"crorisId": 5, "naziv": "Proj"}]
        result = get_projekti_publikacije(100, client=mock_client)
        assert isinstance(result[0], ProjektPublikacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_projekti_publikacije(100, client=mock_client) == []


class TestGetPublikacijeOsobe:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9}
        get_publikacije_osobe(9, client=mock_client)
        mock_client.get.assert_called_once_with(f"{CROSBI_BASE_URL}/osoba/9")

    def test_vraca_osoba_publikacija_instancu(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9, "ime": "Ana"}
        result = get_publikacije_osobe(9, client=mock_client)
        assert isinstance(result, OsobaPublikacija)


class TestGetPublikacijeOsobeByMbz:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9}
        get_publikacije_osobe_by_mbz("123456", client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{CROSBI_BASE_URL}/osoba/maticni-broj/123456"
        )

    def test_vraca_osoba_publikacija_instancu(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9, "ime": "Ana"}
        result = get_publikacije_osobe_by_mbz("123456", client=mock_client)
        assert isinstance(result, OsobaPublikacija)


class TestGetOsobePublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get_embedded.return_value = []
        get_osobe_publikacije(192111, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CROSBI_BASE_URL}/osoba/publikacija/192111", "osobe"
        )

    def test_vraca_listu_osoba(self, mock_client):
        mock_client.get_embedded.return_value = [{"crorisId": 9, "ime": "Ana"}]
        result = get_osobe_publikacije(192111, client=mock_client)
        assert isinstance(result[0], OsobaPublikacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_osobe_publikacije(192111, client=mock_client) == []


class TestImportCasopisRad:
    @resp_lib.activate
    def test_salje_post_zahtjev(self, test_config):
        from crosbi.client import CrorisClient
        url = f"{CROSBI_BASE_URL}/publikacija/import/casopisi-rad"
        resp_lib.add(resp_lib.POST, url, json={"saved": 1, "skipped": 0}, status=200)
        client = CrorisClient(test_config)
        result = import_casopis_rad([{"tip": 760, "godina": "2024"}], client=client)
        assert result == {"saved": 1, "skipped": 0}

    def test_baca_error_za_vise_od_100_zapisa(self, mock_client):
        import pytest as _pytest
        with _pytest.raises(ValueError, match="100"):
            import_casopis_rad([{}] * 101, client=mock_client)
