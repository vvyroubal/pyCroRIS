"""Testovi za crosbi.endpoints.znanstvenici."""

import pytest

from crosbi.endpoints.znanstvenici import (
    get_znanstvenik_by_oib,
    get_znanstvenik_by_mbz,
    list_znanstvenici,
    get_akreditacije_ustanove,
    get_radni_odnosi_ustanove,
    get_osobe_updated_last_month,
    get_osobe_deleted_last_month,
    get_osobe_created_last_month,
)
from crosbi.models.znanstvenik import OsobaAkreditacija, RadniOdnos, Znanstvenik
from crosbi.config import ZNANSTVENICI_BASE_URL


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def akreditacija_raw():
    return {
        "id": 99,
        "oib": "12345678901",
        "ime": "Ana",
        "prezime": "Kovač",
        "poveznica": "https://bib.irb.hr/korisnik/1",
        "vrstaZaposlenjaHr": "Redovan",
        "vrstaRadnogOdnosaHr": "Puno radno vrijeme",
        "podrucjeHr": "Prirodne znanosti",
        "poljeHr": "Biologija",
    }


@pytest.fixture
def radni_odnos_raw():
    return {
        "hrPersRadniOdnosId": 55,
        "oib": "12345678901",
        "mbz": "654321",
        "ime": "Ivan",
        "prezime": "Horvat",
        "datumOd": "2020-01-01",
        "datumDo": None,
        "radnoMjesto": "Istraživač",
        "vrstaZaposlenja": "Redovito",
        "_links": {},
    }


class TestGetZnanstvenikByOib:
    def test_poziva_ispravan_url(self, mock_client, znanstvenik_raw):
        mock_client.get.return_value = znanstvenik_raw
        get_znanstvenik_by_oib("12345678901", client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{ZNANSTVENICI_BASE_URL}/znanstvenik",
            params={"oib": "12345678901"},
        )

    def test_vraca_znanstvenik(self, mock_client, znanstvenik_raw):
        mock_client.get.return_value = znanstvenik_raw
        result = get_znanstvenik_by_oib("12345678901", client=mock_client)
        assert isinstance(result, Znanstvenik)

    def test_iz_embedded_odgovora(self, mock_client, znanstvenik_raw):
        mock_client.get.return_value = {
            "_embedded": {"znanstvenici": [znanstvenik_raw]}
        }
        result = get_znanstvenik_by_oib("12345678901", client=mock_client)
        assert isinstance(result, Znanstvenik)

    def test_prazan_embedded_baca_value_error(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"znanstvenici": []}}
        with pytest.raises(ValueError):
            get_znanstvenik_by_oib("00000000000", client=mock_client)


class TestGetZnanstvenikByMbz:
    def test_poziva_ispravan_url(self, mock_client, znanstvenik_raw):
        mock_client.get.return_value = znanstvenik_raw
        get_znanstvenik_by_mbz("123456", client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{ZNANSTVENICI_BASE_URL}/znanstvenik",
            params={"maticniBroj": "123456"},
        )

    def test_vraca_znanstvenik(self, mock_client, znanstvenik_raw):
        mock_client.get.return_value = znanstvenik_raw
        result = get_znanstvenik_by_mbz("123456", client=mock_client)
        assert isinstance(result, Znanstvenik)


class TestListZnanstvenici:
    def test_poziva_paginate_s_ispravnim_args(self, mock_client, znanstvenik_raw):
        mock_client.paginate.return_value = iter([znanstvenik_raw])
        list(list_znanstvenici(client=mock_client))
        mock_client.paginate.assert_called_once_with(
            f"{ZNANSTVENICI_BASE_URL}/znanstvenik", "znanstvenici"
        )

    def test_vraca_znanstvenik_instance(self, mock_client, znanstvenik_raw):
        mock_client.paginate.return_value = iter([znanstvenik_raw])
        results = list(list_znanstvenici(client=mock_client))
        assert isinstance(results[0], Znanstvenik)

    def test_prazan_odgovor(self, mock_client):
        mock_client.paginate.return_value = iter([])
        assert list(list_znanstvenici(client=mock_client)) == []


class TestGetAkreditacijeUstanove:
    def test_poziva_ispravan_url(self, mock_client, akreditacija_raw):
        mock_client.get_embedded.return_value = [akreditacija_raw]
        get_akreditacije_ustanove(15, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{ZNANSTVENICI_BASE_URL}/osoba/akreditacija",
            "nastavnici",
            params={"cfOrgUnitId": 15},
        )

    def test_vraca_listu_akreditacija(self, mock_client, akreditacija_raw):
        mock_client.get_embedded.return_value = [akreditacija_raw]
        result = get_akreditacije_ustanove(15, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], OsobaAkreditacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_akreditacije_ustanove(15, client=mock_client) == []


class TestGetRadniOdnosiUstanove:
    def test_poziva_ispravan_url(self, mock_client, radni_odnos_raw):
        mock_client.get_embedded.return_value = [radni_odnos_raw]
        get_radni_odnosi_ustanove("35249830363", "01.01.2024.", client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{ZNANSTVENICI_BASE_URL}/radniOdnos/ustanova",
            "radniOdnos",
            params={"oib": "35249830363", "datumPocetka": "01.01.2024."},
        )

    def test_vraca_listu_radnih_odnosa(self, mock_client, radni_odnos_raw):
        mock_client.get_embedded.return_value = [radni_odnos_raw]
        result = get_radni_odnosi_ustanove("35249830363", "01.01.2024.", client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], RadniOdnos)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_radni_odnosi_ustanove("35249830363", "01.01.2024.", client=mock_client) == []


class TestGetOsobeLastMonth:
    def test_updated_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"osobeIds": [1, 2, 3]}}
        result = get_osobe_updated_last_month(client=mock_client)
        assert result == [1, 2, 3]

    def test_deleted_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"osobeIds": [5]}}
        result = get_osobe_deleted_last_month(client=mock_client)
        assert result == [5]

    def test_created_vraca_listu_id(self, mock_client):
        mock_client.get.return_value = {"_embedded": {"osobeIds": [10, 20]}}
        result = get_osobe_created_last_month(client=mock_client)
        assert result == [10, 20]

    def test_prazan_embedded(self, mock_client):
        mock_client.get.return_value = {}
        assert get_osobe_updated_last_month(client=mock_client) == []
