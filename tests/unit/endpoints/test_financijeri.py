"""Testovi za crosbi.endpoints.financijeri."""
import pytest
from crosbi.endpoints.financijeri import get_financijer, get_financijeri_projekta
from crosbi.models.financijer import Financijer


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetFinancijer:
    def test_poziva_ispravan_url(self, mock_client, financijer_raw):
        mock_client.get.return_value = financijer_raw
        get_financijer(5, client=mock_client)
        mock_client.get.assert_called_once_with("/financijer/5")

    def test_vraca_financijer_instancu(self, mock_client, financijer_raw):
        mock_client.get.return_value = financijer_raw
        result = get_financijer(5, client=mock_client)
        assert isinstance(result, Financijer)

    def test_id_se_mapira_ispravno(self, mock_client, financijer_raw):
        mock_client.get.return_value = financijer_raw
        result = get_financijer(5, client=mock_client)
        assert result.id == 5


class TestGetFinancijeriProjekta:
    def test_poziva_ispravan_url(self, mock_client, financijer_raw):
        mock_client.get_embedded.return_value = [financijer_raw]
        get_financijeri_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            "/financijer/projekt/1", "financijeri"
        )

    def test_vraca_listu_financijera(self, mock_client, financijer_raw):
        mock_client.get_embedded.return_value = [financijer_raw]
        result = get_financijeri_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Financijer)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_financijeri_projekta(1, client=mock_client) == []
