"""Testovi za crosbi.endpoints.osobe."""
import pytest
from crosbi.endpoints.osobe import (
    get_osoba,
    get_osoba_by_oib,
    get_voditelj_by_oib,
    get_osobe_projekta,
)
from crosbi.models.osoba import Osoba


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetOsoba:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        get_osoba(7, client=mock_client)
        mock_client.get.assert_called_once_with("/osoba/7")

    def test_vraca_osoba_instancu(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        result = get_osoba(7, client=mock_client)
        assert isinstance(result, Osoba)


class TestGetOsobaByOib:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        get_osoba_by_oib("98765432109", client=mock_client)
        mock_client.get.assert_called_once_with("/osoba/oib/98765432109")

    def test_vraca_osoba_instancu(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        result = get_osoba_by_oib("98765432109", client=mock_client)
        assert isinstance(result, Osoba)


class TestGetVoditeljByOib:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        get_voditelj_by_oib("98765432109", client=mock_client)
        mock_client.get.assert_called_once_with("/osoba/voditelj/oib/98765432109")

    def test_vraca_osoba_instancu(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        result = get_voditelj_by_oib("98765432109", client=mock_client)
        assert isinstance(result, Osoba)


class TestGetOsobeProjekta:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get_embedded.return_value = [osoba_raw]
        get_osobe_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with("/osoba/projekt/1", "osobe")

    def test_vraca_listu_osoba(self, mock_client, osoba_raw):
        mock_client.get_embedded.return_value = [osoba_raw]
        result = get_osobe_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Osoba)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_osobe_projekta(1, client=mock_client) == []
