"""Testovi za crosbi.endpoints.oprema_api."""

import pytest

from crosbi.endpoints.oprema_api import (
    get_oprema,
    list_oprema,
    get_usluga,
    list_usluge,
    get_usluge_opreme,
    get_osobe_opreme,
)
from crosbi.models.oprema import Oprema, Usluga, OpremaOsoba
from crosbi.config import OPREMA_BASE_URL


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def oprema_raw():
    return {
        "id": 77,
        "model": "Model X",
        "proizvodjac": "Siemens",
        "inventarniBroj": "INV-001",
    }


@pytest.fixture
def usluga_raw():
    return {
        "id": 33,
        "trajanje": 60,
        "opremaId": 77,
        "_links": {},
    }


@pytest.fixture
def oprema_osoba_raw():
    return {
        "id": 11,
        "ime": "Marko",
        "prezime": "Novak",
        "email": "marko.novak@fer.hr",
        "_links": {},
    }


class TestGetOprema:
    def test_poziva_ispravan_url(self, mock_client, oprema_raw):
        mock_client.get.return_value = oprema_raw
        get_oprema(77, client=mock_client)
        mock_client.get.assert_called_once_with(f"{OPREMA_BASE_URL}/oprema/77")

    def test_vraca_oprema(self, mock_client, oprema_raw):
        mock_client.get.return_value = oprema_raw
        result = get_oprema(77, client=mock_client)
        assert isinstance(result, Oprema)

    def test_id_se_mapira_ispravno(self, mock_client, oprema_raw):
        mock_client.get.return_value = oprema_raw
        result = get_oprema(77, client=mock_client)
        assert result.id == 77


class TestListOprema:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, oprema_raw):
        mock_client.paginate.return_value = iter([oprema_raw])
        list(list_oprema(client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{OPREMA_BASE_URL}/oprema", "opreme"
        )

    def test_vraca_oprema_instance(self, mock_client, oprema_raw):
        mock_client.paginate.return_value = iter([oprema_raw])
        results = list(list_oprema(client=mock_client))
        assert isinstance(results[0], Oprema)

    def test_prazan_odgovor(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(list_oprema(client=mock_client)) == []


class TestGetUsluga:
    def test_poziva_ispravan_url(self, mock_client, usluga_raw):
        mock_client.get.return_value = usluga_raw
        get_usluga(33, client=mock_client)
        mock_client.get.assert_called_once_with(f"{OPREMA_BASE_URL}/usluga/33")

    def test_vraca_usluga(self, mock_client, usluga_raw):
        mock_client.get.return_value = usluga_raw
        result = get_usluga(33, client=mock_client)
        assert isinstance(result, Usluga)


class TestListUsluge:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, usluga_raw):
        mock_client.paginate.return_value = iter([usluga_raw])
        list(list_usluge(client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{OPREMA_BASE_URL}/usluga", "usluge"
        )

    def test_vraca_usluga_instance(self, mock_client, usluga_raw):
        mock_client.paginate.return_value = iter([usluga_raw])
        results = list(list_usluge(client=mock_client))
        assert isinstance(results[0], Usluga)


class TestGetUslugeOpreme:
    def test_poziva_ispravan_url(self, mock_client, usluga_raw):
        mock_client.get_embedded.return_value = [usluga_raw]
        get_usluge_opreme(77, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{OPREMA_BASE_URL}/usluga/oprema/77", "usluge"
        )

    def test_vraca_listu_usluga(self, mock_client, usluga_raw):
        mock_client.get_embedded.return_value = [usluga_raw]
        result = get_usluge_opreme(77, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Usluga)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_usluge_opreme(77, client=mock_client) == []


class TestGetOsobeOpreme:
    def test_poziva_ispravan_url(self, mock_client, oprema_osoba_raw):
        mock_client.get_embedded.return_value = [oprema_osoba_raw]
        get_osobe_opreme(77, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{OPREMA_BASE_URL}/osoba/oprema/77", "osobe"
        )

    def test_vraca_listu_osoba(self, mock_client, oprema_osoba_raw):
        mock_client.get_embedded.return_value = [oprema_osoba_raw]
        result = get_osobe_opreme(77, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], OpremaOsoba)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_osobe_opreme(77, client=mock_client) == []
