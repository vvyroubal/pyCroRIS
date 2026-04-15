"""Testovi za crosbi.endpoints.upisnik."""

import pytest

from crosbi.endpoints.upisnik import (
    get_sve_aktivne_ustanove,
    get_ustanova_by_id,
    get_ustanova_by_mbu,
    get_sva_podrucja,
    get_croris_ustanove,
    get_znanstvene_ustanove,
    get_visoka_ucilista,
    get_neaktivne_ustanove,
    get_ustanova_by_mzo_id,
    get_croris_ustanova,
    get_javni_znanstveni_instituti,
    get_ustanove_updated_last_month,
    get_ustanove_created_last_month,
    get_ustanove_deleted_last_month,
    get_podrucje,
    get_polje_s_granama,
)
from crosbi.models.ustanova_reg import UstanovaReg, Podrucje, Polje
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


class TestGetZnanstveneUstanove:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        get_znanstvene_ustanove(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/upisnik-ustanova/ustanova/znanstvena", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        result = get_znanstvene_ustanove(client=mock_client)
        assert all(isinstance(u, UstanovaReg) for u in result)


class TestGetVisokaUcilista:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        get_visoka_ucilista(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/upisnik-ustanova/ustanova/visoko-uciliste", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        assert all(isinstance(u, UstanovaReg) for u in get_visoka_ucilista(client=mock_client))


class TestGetNeaktivneUstanove:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        get_neaktivne_ustanove(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/upisnik-ustanova/ustanova/neaktivna", "ustanove"
        )

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_neaktivne_ustanove(client=mock_client) == []


class TestGetUstanovaByMzoId:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        get_ustanova_by_mzo_id(200, client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/upisnik-ustanova/ustanova/mzo/200"
        )

    def test_vraca_ustanova_instancu(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        assert isinstance(get_ustanova_by_mzo_id(200, client=mock_client), UstanovaReg)


class TestGetCrorisUstanova:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        get_croris_ustanova(15, client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/croris-ustanove/ustanova/15"
        )

    def test_vraca_ustanova_instancu(self, mock_client, ustanova_reg_raw):
        mock_client.get.return_value = ustanova_reg_raw
        assert isinstance(get_croris_ustanova(15, client=mock_client), UstanovaReg)


class TestGetJavniZnanstveniInstituti:
    def test_poziva_ispravan_url(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        get_javni_znanstveni_instituti(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/croris-ustanove/ustanova/jzi", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_reg_raw):
        mock_client.get_embedded.return_value = [ustanova_reg_raw]
        assert all(isinstance(u, UstanovaReg) for u in get_javni_znanstveni_instituti(client=mock_client))


class TestGetUstanoveLastMonth:
    def test_updated_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"ustanoveIds": [1, 2]}}
        result = get_ustanove_updated_last_month(client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/croris-ustanove/ustanova/updated-last-month"
        )
        assert result == [1, 2]

    def test_created_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"ustanoveIds": [3]}}
        result = get_ustanove_created_last_month(client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/croris-ustanove/ustanova/created-last-month"
        )
        assert result == [3]

    def test_deleted_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"ustanoveIds": []}}
        result = get_ustanove_deleted_last_month(client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/croris-ustanove/ustanova/deleted-last-month"
        )
        assert result == []

    def test_vraca_praznu_listu_kad_nema_embedded(self, mock_client):
        mock_client.get.return_value = {}
        assert get_ustanove_updated_last_month(client=mock_client) == []


class TestGetPodrucje:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"disciplinaId": 1, "nazivDiscipline": "Prirodne znanosti", "sifraDiscipline": "1"}
        get_podrucje(1, client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/evidencija-ppg/podrucje/1"
        )

    def test_vraca_podrucje_instancu(self, mock_client):
        mock_client.get.return_value = {"disciplinaId": 1, "nazivDiscipline": "Prirodne znanosti", "sifraDiscipline": "1"}
        result = get_podrucje(1, client=mock_client)
        assert isinstance(result, Podrucje)


class TestGetPoljeSGranama:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"disciplinaId": 2, "nazivDiscipline": "Fizika", "sifraDiscipline": "1.02", "grane": []}
        get_polje_s_granama(1, 2, client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/evidencija-ppg/podrucje/1/polje/2"
        )

    def test_vraca_polje_instancu(self, mock_client):
        mock_client.get.return_value = {"disciplinaId": 2, "nazivDiscipline": "Fizika", "sifraDiscipline": "1.02", "grane": []}
        result = get_polje_s_granama(1, 2, client=mock_client)
        assert isinstance(result, Polje)
