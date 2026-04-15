"""Testovi za crosbi.endpoints.dogadanja."""

import pytest

from crosbi.endpoints.dogadanja import (
    get_dogadanje,
    list_dogadanja,
    get_dogadanja_created_last_month,
    get_dogadanja_updated_last_month,
    get_dogadanja_deleted_last_month,
    get_publikacije_dogadanja,
)
from crosbi.models.dogadanje import Dogadanje, PublikacijaDogadanje
from crosbi.config import DOGADANJA_BASE_URL


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def publikacija_dogadanje_raw():
    return {
        "cfResPublId": 200,
        "cfEventId": 55,
        "citat": "Horvat, 2023",
        "_links": {},
    }


class TestGetDogadanje:
    def test_poziva_ispravan_url(self, mock_client, dogadanje_raw):
        mock_client.get.return_value = dogadanje_raw
        get_dogadanje(55, client=mock_client)
        mock_client.get.assert_called_once_with(f"{DOGADANJA_BASE_URL}/dogadanje/55")

    def test_vraca_dogadanje(self, mock_client, dogadanje_raw):
        mock_client.get.return_value = dogadanje_raw
        result = get_dogadanje(55, client=mock_client)
        assert isinstance(result, Dogadanje)

    def test_id_se_mapira_ispravno(self, mock_client, dogadanje_raw):
        mock_client.get.return_value = dogadanje_raw
        result = get_dogadanje(55, client=mock_client)
        assert result.id == 55


class TestListDogadanja:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, dogadanje_raw):
        mock_client.paginate.return_value = iter([dogadanje_raw])
        list(list_dogadanja(client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{DOGADANJA_BASE_URL}/dogadanje", "dogadanje"
        )

    def test_vraca_dogadanje_instance(self, mock_client, dogadanje_raw):
        mock_client.paginate.return_value = iter([dogadanje_raw])
        results = list(list_dogadanja(client=mock_client))
        assert len(results) == 1
        assert isinstance(results[0], Dogadanje)

    def test_prazan_odgovor(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(list_dogadanja(client=mock_client)) == []


class TestGetDogadanjaCreatedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"dogadanjaIds": [1, 2]}}
        result = get_dogadanja_created_last_month(client=mock_client)
        assert result == [1, 2]

    def test_prazan_embedded(self, mock_client):
        mock_client.get.return_value = {}
        assert get_dogadanja_created_last_month(client=mock_client) == []


class TestGetDogadanjaUpdatedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"dogadanjaIds": [3, 4]}}
        result = get_dogadanja_updated_last_month(client=mock_client)
        assert result == [3, 4]


class TestGetDogadanjaDeletedLastMonth:
    def test_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"dogadanjaIds": [7]}}
        result = get_dogadanja_deleted_last_month(client=mock_client)
        assert result == [7]


class TestGetPublikacijeDogadanja:
    def test_poziva_ispravan_url(self, mock_client, publikacija_dogadanje_raw):
        mock_client.get_embedded.return_value = [publikacija_dogadanje_raw]
        get_publikacije_dogadanja(55, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{DOGADANJA_BASE_URL}/publikacija/dogadanje/55", "publikacije"
        )

    def test_vraca_listu_publikacija(self, mock_client, publikacija_dogadanje_raw):
        mock_client.get_embedded.return_value = [publikacija_dogadanje_raw]
        result = get_publikacije_dogadanja(55, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], PublikacijaDogadanje)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_publikacije_dogadanja(55, client=mock_client) == []


from crosbi.endpoints.dogadanja import get_dogadanja_ustanove, get_dogadanje_publikacije


class TestGetDogadanjaUstanove:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, dogadanje_raw):
        mock_client.paginate.return_value = iter([dogadanje_raw])
        list(get_dogadanja_ustanove(10, client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{DOGADANJA_BASE_URL}/dogadanje", "dogadanje", params={"ustanovaId": 10}
        )

    def test_vraca_dogadanje_instancu(self, mock_client, dogadanje_raw):
        mock_client.paginate.return_value = iter([dogadanje_raw])
        result = list(get_dogadanja_ustanove(10, client=mock_client))
        assert isinstance(result[0], Dogadanje)

    def test_prazan_odgovor(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(get_dogadanja_ustanove(10, client=mock_client)) == []


class TestGetDogadanjePublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"cfResPublId": 100}
        get_dogadanje_publikacije(100, client=mock_client)
        mock_client.get.assert_called_once_with(f"{DOGADANJA_BASE_URL}/publikacija/100")

    def test_vraca_publikacija_dogadanje_instancu(self, mock_client):
        mock_client.get.return_value = {"cfResPublId": 100}
        result = get_dogadanje_publikacije(100, client=mock_client)
        assert isinstance(result, PublikacijaDogadanje)
