"""Testovi za crosbi.endpoints.mozvag."""

import pytest

from crosbi.endpoints.mozvag import (
    get_ustanove,
    get_financijere,
    get_projekti_ustanove,
    get_osoba_po_mbz,
    get_osoba_po_oib,
    get_osoba_po_mbz_ustanova,
)
from crosbi.models.mozvag import (
    FinancijerMozvag,
    OsobaMozvag,
    ProjektMozvag,
    UstanovaMozvag,
)


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def ustanova_mozvag_raw():
    return {
        "ustanovaId": 10,
        "adresa": "Bijenička 54, Zagreb",
        "oib": "35249830363",
        "web": "https://irb.hr",
        "aaiDomain": "irb.hr",
        "grad": "Zagreb",
        "naziv": [{"cfLangCode": "hr", "naziv": "Institut Ruđer Bošković"}],
    }


@pytest.fixture
def financijer_mozvag_raw():
    return {
        "financijerId": 1,
        "nazivHr": "Hrvatska zaklada za znanost",
        "nazivEn": "Croatian Science Foundation",
        "nadleznost": "Nacionalno",
        "programi": [],
    }


@pytest.fixture
def projekt_mozvag_raw():
    return {
        "projektId": 100,
        "naziv": "Testni projekt",
        "startDate": "2020-01-01",
        "endDate": "2023-12-31",
        "ulogaId": 1,
        "ulogaNaziv": "Nositelj",
        "financijeri": [],
    }


@pytest.fixture
def osoba_mozvag_raw():
    return {
        "osobaId": 7,
        "ustanovaid": 10,
        "ime": "Ivan",
        "prezime": "Horvat",
        "maticniBroj": "123456",
        "znanstveniProjekti": 3,
        "ostaliProjekti": 1,
    }


class TestGetUstanove:
    def test_poziva_mozvag_institutions(self, mock_client, ustanova_mozvag_raw):
        mock_client.get.return_value = {"_embedded": {"institutions": [ustanova_mozvag_raw]}}
        get_ustanove(client=mock_client)
        mock_client.get.assert_called_once_with("/mozvag/institutions")

    def test_vraca_listu_ustanova(self, mock_client, ustanova_mozvag_raw):
        mock_client.get.return_value = {"_embedded": {"institutions": [ustanova_mozvag_raw]}}
        result = get_ustanove(client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], UstanovaMozvag)

    def test_vraca_ravnu_listu(self, mock_client, ustanova_mozvag_raw):
        mock_client.get.return_value = [ustanova_mozvag_raw]
        result = get_ustanove(client=mock_client)
        assert isinstance(result[0], UstanovaMozvag)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get.return_value = {}
        assert get_ustanove(client=mock_client) == []


class TestGetFinancijere:
    def test_poziva_mozvag_funders(self, mock_client, financijer_mozvag_raw):
        mock_client.get.return_value = {"_embedded": {"funders": [financijer_mozvag_raw]}}
        get_financijere(client=mock_client)
        mock_client.get.assert_called_once_with("/mozvag/funders")

    def test_vraca_listu_financijera(self, mock_client, financijer_mozvag_raw):
        mock_client.get.return_value = {"_embedded": {"funders": [financijer_mozvag_raw]}}
        result = get_financijere(client=mock_client)
        assert isinstance(result[0], FinancijerMozvag)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get.return_value = {}
        assert get_financijere(client=mock_client) == []


class TestGetProjektiUstanove:
    def test_poziva_ispravan_url(self, mock_client, projekt_mozvag_raw):
        mock_client.get.return_value = {"_embedded": {"projekti": [projekt_mozvag_raw]}}
        get_projekti_ustanove(10, 2023, client=mock_client)
        mock_client.get.assert_called_once_with("/mozvag/10/2023")

    def test_vraca_listu_projekata(self, mock_client, projekt_mozvag_raw):
        mock_client.get.return_value = {"_embedded": {"projekti": [projekt_mozvag_raw]}}
        result = get_projekti_ustanove(10, 2023, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], ProjektMozvag)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get.return_value = {}
        assert get_projekti_ustanove(10, 2023, client=mock_client) == []


class TestGetOsobaPoMbz:
    def test_poziva_ispravan_url(self, mock_client, osoba_mozvag_raw):
        mock_client.get.return_value = osoba_mozvag_raw
        get_osoba_po_mbz("123456", 2023, client=mock_client)
        mock_client.get.assert_called_once_with("/mozvag/person/123456/2023")

    def test_vraca_osoba_mozvag(self, mock_client, osoba_mozvag_raw):
        mock_client.get.return_value = osoba_mozvag_raw
        result = get_osoba_po_mbz("123456", 2023, client=mock_client)
        assert isinstance(result, OsobaMozvag)
        assert result.ime == "Ivan"


class TestGetOsobaPoOib:
    def test_poziva_ispravan_url(self, mock_client, osoba_mozvag_raw):
        mock_client.get.return_value = osoba_mozvag_raw
        get_osoba_po_oib(10, "12345678901", 2023, client=mock_client)
        mock_client.get.assert_called_once_with("/mozvag/oib/10/12345678901/2023")

    def test_vraca_osoba_mozvag(self, mock_client, osoba_mozvag_raw):
        mock_client.get.return_value = osoba_mozvag_raw
        result = get_osoba_po_oib(10, "12345678901", 2023, client=mock_client)
        assert isinstance(result, OsobaMozvag)


class TestGetOsobaPoMbzUstanova:
    def test_poziva_ispravan_url(self, mock_client, osoba_mozvag_raw):
        mock_client.get.return_value = osoba_mozvag_raw
        get_osoba_po_mbz_ustanova(10, "123456", 2023, client=mock_client)
        mock_client.get.assert_called_once_with("/mozvag/mbz/10/123456/2023")

    def test_vraca_osoba_mozvag(self, mock_client, osoba_mozvag_raw):
        mock_client.get.return_value = osoba_mozvag_raw
        result = get_osoba_po_mbz_ustanova(10, "123456", 2023, client=mock_client)
        assert isinstance(result, OsobaMozvag)
