"""Testovi za crosbi.endpoints.publikacije (projekti-api)."""
import pytest
from crosbi.endpoints.publikacije import get_publikacija, get_publikacije_projekta
from crosbi.models.publikacija import Publikacija


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetPublikacija:
    def test_poziva_ispravan_url(self, mock_client, publikacija_raw):
        mock_client.get.return_value = publikacija_raw
        get_publikacija(42, client=mock_client)
        mock_client.get.assert_called_once_with("/publikacija/42")

    def test_vraca_publikacija_instancu(self, mock_client, publikacija_raw):
        mock_client.get.return_value = publikacija_raw
        result = get_publikacija(42, client=mock_client)
        assert isinstance(result, Publikacija)

    def test_id_se_mapira_ispravno(self, mock_client, publikacija_raw):
        mock_client.get.return_value = publikacija_raw
        result = get_publikacija(42, client=mock_client)
        assert result.cf_res_publ_id == 42


class TestGetPublikacijeProjekta:
    def test_poziva_ispravan_url(self, mock_client, publikacija_raw):
        mock_client.get_embedded.return_value = [publikacija_raw]
        get_publikacije_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            "/publikacija/projekt/1", "publikacije"
        )

    def test_vraca_listu_publikacija(self, mock_client, publikacija_raw):
        mock_client.get_embedded.return_value = [publikacija_raw]
        result = get_publikacije_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Publikacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_publikacije_projekta(1, client=mock_client) == []
