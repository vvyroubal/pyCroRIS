"""Testovi za crosbi.endpoints.ustanove (projekti-api)."""
import pytest
from crosbi.endpoints.ustanove import get_ustanova, get_ustanove_projekta
from crosbi.models.ustanova import Ustanova


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetUstanova:
    def test_poziva_ispravan_url(self, mock_client, ustanova_raw):
        mock_client.get.return_value = ustanova_raw
        get_ustanova(10, client=mock_client)
        mock_client.get.assert_called_once_with("/ustanova/10")

    def test_vraca_ustanova_instancu(self, mock_client, ustanova_raw):
        mock_client.get.return_value = ustanova_raw
        result = get_ustanova(10, client=mock_client)
        assert isinstance(result, Ustanova)

    def test_id_se_mapira_ispravno(self, mock_client, ustanova_raw):
        mock_client.get.return_value = ustanova_raw
        result = get_ustanova(10, client=mock_client)
        assert result.id == 10


class TestGetUstanoveProjekta:
    def test_poziva_ispravan_url(self, mock_client, ustanova_raw):
        mock_client.get_embedded.return_value = [ustanova_raw]
        get_ustanove_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            "/ustanova/projekt/1", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_raw):
        mock_client.get_embedded.return_value = [ustanova_raw]
        result = get_ustanove_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Ustanova)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_ustanove_projekta(1, client=mock_client) == []
