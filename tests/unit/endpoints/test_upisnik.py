"""Testovi za crosbi.endpoints.upisnik."""

import pytest

from crosbi.endpoints.upisnik import (
    get_sve_aktivne_ustanove,
    get_ustanova_by_id,
    get_ustanova_by_mbu,
    get_sva_podrucja,
    get_croris_ustanove,
)
from crosbi.models.ustanova_reg import UstanovaReg, Podrucje
from crosbi.config import USTANOVE_BASE_URL


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def podrucje_raw():
    return {
        "disciplinaId": 1,
        "nazivDiscipline": "Prirodne znanosti",
        "sifraDiscipline": "1",
        "_links": {},
    }


class TestGetUstanovaById:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        get_ustanova_by_id(15, client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/upisnik-ustanova/ustanova/15"
        )

    def test_vraca_ustanova_reg(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        result = get_ustanova_by_id(15, client=mock_client)
        assert isinstance(result, UstanovaReg)

    def test_id_se_mapira_ispravno(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        result = get_ustanova_by_id(15, client=mock_client)
        assert result.id == 15


class TestGetUstanovaByMbu:
    def test_poziva_sa_params(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        get_ustanova_by_mbu("1234567", client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/upisnik-ustanova/ustanova",
            params={"mbu": "1234567"},
        )

    def test_vraca_ustanova_reg_iz_plain_odgovora(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        result = get_ustanova_by_mbu("1234567", client=mock_client)
        assert isinstance(result, UstanovaReg)

    def test_vraca_prvu_iz_embedded_odgovora(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = {
            "_embedded": {"ustanove": [ustanova_reg_raw]}
        }
        result = get_ustanova_by_mbu("1234567", client=mock_client)
        assert isinstance(result, UstanovaReg)
        assert result.id == 15

    def test_vraca_none_za_prazan_embedded(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"ustanove": []}}
        result = get_ustanova_by_mbu("9999999", client=mock_client)
        assert result is None


class TestGetSveAktivneUstanove:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        get_sve_aktivne_ustanove(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/upisnik-ustanova/ustanova", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        result = get_sve_aktivne_ustanove(client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], UstanovaReg)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_sve_aktivne_ustanove(client=mock_client) == []

    def test_vise_ustanova(self, mock_client, ustanova_reg_raw):
        raw2 = {**ustanova_reg_raw, "id": 99}
        mock_client.get_embedded.return_value = [ustanova_reg_raw, raw2]
        result = get_sve_aktivne_ustanove(client=mock_client)
        assert len(result) == 2
        assert result[1].id == 99


class TestGetSvaPodrucja:
    def test_poziva_ispravan_url(self, mock_client, podrucje_raw):
        mock_client.get_embedded.return_value = [podrucje_raw]
        get_sva_podrucja(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/evidencija-ppg/podrucje", "podrucja"
        )

    def test_vraca_listu_podrucja(self, mock_client, podrucje_raw):
        mock_client.get_embedded.return_value = [podrucje_raw]
        result = get_sva_podrucja(client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Podrucje)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_sva_podrucja(client=mock_client) == []


class TestGetCrorisUstanove:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        get_croris_ustanove(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/croris-ustanove/ustanova", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        result = get_croris_ustanove(client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], UstanovaReg)
