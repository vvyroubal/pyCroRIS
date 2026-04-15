"""Testovi za crosbi.endpoints.casopisi."""

import pytest

from crosbi.endpoints.casopisi import (
    get_casopis,
    list_casopisi,
    get_casopisi_updated_last_month,
    get_casopisi_deleted_last_month,
    get_casopisi_created_last_month,
    get_publikacije_casopisa,
)
from crosbi.models.casopis import Casopis, PublikacijaCasopis
from crosbi.config import CASOPISI_BASE_URL


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def publikacija_casopis_raw():
    return {
        "cfResPublId": 100,
        "hrJournalId": 88,
        "citat": "Kovač, 2022",
        "_links": {},
    }


class TestGetCasopis:
    def test_poziva_ispravan_url(self, mock_client, casopis_raw):
        mock_client.get.return_value = casopis_raw
        get_casopis(88, client=mock_client)
        mock_client.get.assert_called_once_with(f"{CASOPISI_BASE_URL}/casopis/88")

    def test_vraca_casopis(self, mock_client, casopis_raw):
        mock_client.get.return_value = casopis_raw
        result = get_casopis(88, client=mock_client)
        assert isinstance(result, Casopis)

    def test_id_se_mapira_ispravno(self, mock_client, casopis_raw):
        mock_client.get.return_value = casopis_raw
        result = get_casopis(88, client=mock_client)
        assert result.id == 88


class TestListCasopisi:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, casopis_raw):
        mock_client.paginate.return_value = iter([casopis_raw])
        list(list_casopisi(client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{CASOPISI_BASE_URL}/casopis", "casopis"
        )

    def test_vraca_casopis_instance(self, mock_client, casopis_raw):
        mock_client.paginate.return_value = iter([casopis_raw])
        results = list(list_casopisi(client=mock_client))
        assert len(results) == 1
        assert isinstance(results[0], Casopis)

    def test_prazan_odgovor(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(list_casopisi(client=mock_client)) == []


class TestGetCasopisiUpdatedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"casopisiIds": [1, 2, 3]}}
        result = get_casopisi_updated_last_month(client=mock_client)
        assert result == [1, 2, 3]

    def test_prazan_embedded(self, mock_client):
        mock_client.get.return_value = {}
        assert get_casopisi_updated_last_month(client=mock_client) == []


class TestGetCasopisiDeletedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"casopisiIds": [5]}}
        result = get_casopisi_deleted_last_month(client=mock_client)
        assert result == [5]


class TestGetCasopisiCreatedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"casopisiIds": [10, 20]}}
        result = get_casopisi_created_last_month(client=mock_client)
        assert result == [10, 20]


class TestGetPublikacijeCasopisa:
    def test_poziva_ispravan_url(self, mock_client, publikacija_casopis_raw):
        mock_client.get_embedded.return_value = [publikacija_casopis_raw]
        get_publikacije_casopisa(88, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CASOPISI_BASE_URL}/publikacija/casopis/88", "publikacije"
        )

    def test_vraca_listu_publikacija(self, mock_client, publikacija_casopis_raw):
        mock_client.get_embedded.return_value = [publikacija_casopis_raw]
        result = get_publikacije_casopisa(88, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], PublikacijaCasopis)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_publikacije_casopisa(88, client=mock_client) == []


from crosbi.endpoints.casopisi import get_casopisi_ustanove, get_casopis_publikacije


class TestGetCasopisiUstanove:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, casopis_raw):
        mock_client.paginate.return_value = iter([casopis_raw])
        list(get_casopisi_ustanove(10, client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{CASOPISI_BASE_URL}/casopis", "casopis", params={"ustanovaId": 10}
        )

    def test_vraca_casopis_instancu(self, mock_client, casopis_raw):
        mock_client.paginate.return_value = iter([casopis_raw])
        result = list(get_casopisi_ustanove(10, client=mock_client))
        assert isinstance(result[0], Casopis)

    def test_prazan_odgovor(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(get_casopisi_ustanove(10, client=mock_client)) == []


class TestGetCasopisPublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"cfResPublId": 100, "hrJournalId": 88}
        get_casopis_publikacije(100, client=mock_client)
        mock_client.get.assert_called_once_with(f"{CASOPISI_BASE_URL}/publikacija/100")

    def test_vraca_publikacija_casopis_instancu(self, mock_client):
        mock_client.get.return_value = {"cfResPublId": 100, "hrJournalId": 88}
        result = get_casopis_publikacije(100, client=mock_client)
        assert isinstance(result, PublikacijaCasopis)
