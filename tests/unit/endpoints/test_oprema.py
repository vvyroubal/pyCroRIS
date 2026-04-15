"""Testovi za crosbi.endpoints.oprema_api."""

import pytest

from crosbi.endpoints.oprema_api import (
    get_oprema,
    list_oprema,
    get_usluga,
    list_usluge,
    get_usluge_opreme,
    get_osobe_opreme,
    get_oprema_hrefs,
    fetch_oprema_by_href,
    get_oprema_ustanove,
    get_usluge_ustanove,
    get_osoba_opreme,
    get_cjenik_usluge,
    get_vrste_opreme,
    get_vrste_analize,
    get_primjene_opreme,
    get_discipline_opreme,
    get_poveznice_opreme,
)
from crosbi.models.oprema import Oprema, Usluga, OpremaOsoba, UslugaCjenik
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


class TestGetOpremaHrefs:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"pridruzenaOprema": [{"href": "https://x/1"}, {"href": "https://x/2"}]}
        get_oprema_hrefs(176, client=mock_client)
        mock_client.get.assert_called_once_with(f"{OPREMA_BASE_URL}/ustanova/176")

    def test_vraca_listu_hrefs(self, mock_client):
        mock_client.get.return_value = {"pridruzenaOprema": [{"href": "https://x/1"}, {"href": "https://x/2"}]}
        result = get_oprema_hrefs(176, client=mock_client)
        assert result == ["https://x/1", "https://x/2"]

    def test_prazna_ustanova(self, mock_client):
        mock_client.get.return_value = {}
        assert get_oprema_hrefs(176, client=mock_client) == []


class TestFetchOpremaByHref:
    def test_vraca_oprema_instancu(self, mocker, oprema_raw):
        mock_c = mocker.patch("crosbi.endpoints.oprema_api.CrorisClient")
        mock_c.return_value.get.return_value = oprema_raw
        result = fetch_oprema_by_href("https://x/oprema/77")
        assert isinstance(result, Oprema)
        mock_c.return_value.get.assert_called_once_with("https://x/oprema/77")


class TestGetOpremaUstanove:
    def test_vraca_tuple_s_listom_i_greskama(self, mocker, oprema_raw):
        mock_c = mocker.MagicMock()
        mock_c.get.return_value = {"pridruzenaOprema": [{"href": "https://x/77"}]}
        mocker.patch(
            "crosbi.endpoints.oprema_api.CrorisClient",
            return_value=mocker.MagicMock(**{"get.return_value": oprema_raw}),
        )
        result, errors = get_oprema_ustanove(176, client=mock_c)
        assert isinstance(result, list)
        assert isinstance(errors, list)

    def test_prazan_odgovor_vraca_prazne_liste(self, mock_client):
        mock_client.get.return_value = {"pridruzenaOprema": []}
        result, errors = get_oprema_ustanove(176, client=mock_client)
        assert result == []
        assert errors == []


class TestGetUslugeUstanove:
    def test_filtrira_po_ustanova_id(self, mock_client):
        mock_client.paginate.return_value = iter([
            {"id": 1, "ustanova": {"id": 176, "naziv": "VUKA"}, "aktivnost": True},
            {"id": 2, "ustanova": {"id": 10, "naziv": "IRB"}, "aktivnost": True},
        ])
        result = list(get_usluge_ustanove(176, client=mock_client))
        assert len(result) == 1
        assert result[0].ustanova_id == 176

    def test_prazno_ako_nema_poklapanja(self, mock_client):
        mock_client.paginate.return_value = iter([
            {"id": 1, "ustanova": {"id": 10, "naziv": "IRB"}, "aktivnost": True},
        ])
        assert list(get_usluge_ustanove(999, client=mock_client)) == []


class TestGetOsobaOpreme:
    def test_poziva_ispravan_url(self, mock_client, oprema_osoba_raw):
        mock_client.get.return_value = oprema_osoba_raw
        get_osoba_opreme(11, client=mock_client)
        mock_client.get.assert_called_once_with(f"{OPREMA_BASE_URL}/osoba/oprema/osoba/11")

    def test_vraca_oprema_osoba_instancu(self, mock_client, oprema_osoba_raw):
        mock_client.get.return_value = oprema_osoba_raw
        result = get_osoba_opreme(11, client=mock_client)
        assert isinstance(result, OpremaOsoba)


class TestGetCjenikUsluge:
    def test_poziva_ispravan_url(self, mock_client, usluga_cjenik_raw):
        mock_client.get_embedded.return_value = [usluga_cjenik_raw]
        get_cjenik_usluge(33, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(f"{OPREMA_BASE_URL}/cjenik/usluga/33", "cjenici")

    def test_vraca_listu_cjenika(self, mock_client, usluga_cjenik_raw):
        mock_client.get_embedded.return_value = [usluga_cjenik_raw]
        result = get_cjenik_usluge(33, client=mock_client)
        assert isinstance(result[0], UslugaCjenik)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_cjenik_usluge(33, client=mock_client) == []


class TestLookupEndpointi:
    """Testovi za get_vrste_opreme, get_vrste_analize, get_primjene_opreme,
    get_discipline_opreme, get_poveznice_opreme — sve vraćaju list[dict]."""

    def test_get_vrste_opreme(self, mock_client):
        mock_client.get_embedded.return_value = [{"id": 1, "naziv": "Analitička"}]
        result = get_vrste_opreme(77, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(f"{OPREMA_BASE_URL}/vrsta-opreme/oprema/77", "vrsteOpreme")
        assert result == [{"id": 1, "naziv": "Analitička"}]

    def test_get_vrste_analize(self, mock_client):
        mock_client.get_embedded.return_value = [{"id": 2}]
        result = get_vrste_analize(77, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(f"{OPREMA_BASE_URL}/vrsta-analize/oprema/77", "vrsteAnalize")
        assert result == [{"id": 2}]

    def test_get_primjene_opreme(self, mock_client):
        mock_client.get_embedded.return_value = []
        result = get_primjene_opreme(77, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(f"{OPREMA_BASE_URL}/primjena-opreme/oprema/77", "primjeneOpreme")
        assert result == []

    def test_get_discipline_opreme(self, mock_client):
        mock_client.get_embedded.return_value = []
        result = get_discipline_opreme(77, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(f"{OPREMA_BASE_URL}/disciplina/oprema/77", "discipline")
        assert result == []

    def test_get_poveznice_opreme(self, mock_client):
        mock_client.get_embedded.return_value = [{"url": "https://example.com"}]
        result = get_poveznice_opreme(77, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(f"{OPREMA_BASE_URL}/poveznica/oprema/77", "poveznice")
        assert result == [{"url": "https://example.com"}]
