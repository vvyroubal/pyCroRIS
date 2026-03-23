"""Testovi za crosbi.models.znanstvenik — Znanstvenik i srodni modeli."""

import pytest

from crosbi.models.znanstvenik import (
    AkademskiStupanj,
    OsobaAkreditacija,
    RadniOdnos,
    Zaposlenje,
    Znanstvenik,
    Zvanje,
    ZnanstvenikUstanova,
)


class TestZnanstvenikFromDict:
    def test_full_dict(self, znanstvenik_raw):
        z = Znanstvenik.from_dict(znanstvenik_raw)
        assert z.id == 42
        assert z.ime == "Ivan"
        assert z.prezime == "Horvat"
        assert z.oib == "12345678901"
        assert z.maticni_broj == "123456"
        assert z.orcid == "0000-0001-2345-6789"
        assert z.email == "ivan.horvat@unizg.hr"
        assert z.max_zvanje == "Redoviti profesor"
        assert z.aktivan is True
        assert z.godina_prvog_zaposlenja == 2002

    def test_zvanja_parsed(self, znanstvenik_raw):
        z = Znanstvenik.from_dict(znanstvenik_raw)
        assert len(z.zvanja) == 1
        assert z.zvanja[0].naziv == "Redoviti profesor"
        assert z.zvanja[0].aktivan is True
        assert z.zvanja[0].ustanova.naziv == "Sveučilište u Zagrebu"

    def test_akademski_stupnjevi_parsed(self, znanstvenik_raw):
        z = Znanstvenik.from_dict(znanstvenik_raw)
        assert len(z.akademski_stupnjevi) == 1
        assert z.akademski_stupnjevi[0].naziv == "Doktor znanosti"

    def test_zaposlenja_parsed(self, znanstvenik_raw):
        z = Znanstvenik.from_dict(znanstvenik_raw)
        assert len(z.zaposlenja) == 2

    def test_missing_embedded_resources_returns_empty_lists(self):
        z = Znanstvenik.from_dict({"id": 1, "ime": "Test", "prezime": "User"})
        assert z.zvanja == []
        assert z.akademski_stupnjevi == []
        assert z.zaposlenja == []

    def test_empty_embedded_wrapper_returns_empty_lists(self):
        raw = {
            "id": 1,
            "zvanjeResources": {},
            "akademskiStupanjResources": {},
            "zaposlenjeResources": {},
        }
        z = Znanstvenik.from_dict(raw)
        assert z.zvanja == []
        assert z.zaposlenja == []


class TestZnanstvenikPunoIme:
    def test_both_names(self, znanstvenik_raw):
        z = Znanstvenik.from_dict(znanstvenik_raw)
        assert z.puno_ime == "Ivan Horvat"

    def test_only_prezime(self, znanstvenik_raw):
        znanstvenik_raw["ime"] = None
        z = Znanstvenik.from_dict(znanstvenik_raw)
        assert z.puno_ime == "Horvat"

    def test_only_ime(self, znanstvenik_raw):
        znanstvenik_raw["prezime"] = None
        z = Znanstvenik.from_dict(znanstvenik_raw)
        assert z.puno_ime == "Ivan"

    def test_no_name(self):
        z = Znanstvenik.from_dict({"id": 1})
        assert z.puno_ime == ""


class TestZnanstvenikToDict:
    def test_to_dict_keys(self, znanstvenik_raw):
        d = Znanstvenik.from_dict(znanstvenik_raw).to_dict()
        for key in ("id", "ime", "prezime", "oib", "mbz", "orcid", "max_zvanje",
                    "aktivan", "ustanova", "radno_mjesto"):
            assert key in d

    def test_aktivno_zaposlenje_selected(self, znanstvenik_raw):
        d = Znanstvenik.from_dict(znanstvenik_raw).to_dict()
        assert d["ustanova"] == "Sveučilište u Zagrebu"
        assert d["radno_mjesto"] == "Profesor"

    def test_no_zaposlenja_returns_none(self):
        z = Znanstvenik.from_dict({"id": 1})
        d = z.to_dict()
        assert d["ustanova"] is None
        assert d["radno_mjesto"] is None

    def test_no_aktivno_zaposlenje_returns_none(self, znanstvenik_raw):
        for z in znanstvenik_raw["zaposlenjeResources"]["_embedded"]["zaposlenja"]:
            z["aktivno"] = False
        d = Znanstvenik.from_dict(znanstvenik_raw).to_dict()
        assert d["ustanova"] is None


class TestZvanje:
    def test_from_dict(self):
        raw = {
            "id": 1,
            "naziv": "Docent",
            "kratica": "doc.",
            "datumIzbora": "2010-01-01",
            "aktivan": False,
            "ustanova": {"id": 5, "naziv": "FKIT"},
        }
        z = Zvanje.from_dict(raw)
        assert z.id == 1
        assert z.naziv == "Docent"
        assert z.aktivan is False
        assert z.ustanova.naziv == "FKIT"

    def test_from_dict_without_ustanova(self):
        z = Zvanje.from_dict({"id": 1, "naziv": "Prof"})
        assert z.ustanova is None

    def test_to_dict(self):
        d = Zvanje.from_dict({
            "id": 1, "naziv": "Prof", "kratica": "prof.",
            "datumIzbora": "2020-01-01", "aktivan": True,
            "ustanova": {"id": 1, "naziv": "UNIZG"},
        }).to_dict()
        assert d["naziv"] == "Prof"
        assert d["ustanova"] == "UNIZG"


class TestAkademskiStupanj:
    def test_from_dict(self):
        s = AkademskiStupanj.from_dict({
            "id": 2, "naziv": "Magistar", "kratica": "mr.", "datumStjecanja": "2002-07-01"
        })
        assert s.id == 2
        assert s.kratica == "mr."


class TestZaposlenje:
    def test_from_dict(self):
        raw = {
            "id": 3,
            "ustanova": {"id": 10, "naziv": "IRB"},
            "datumOd": "2010-01-01",
            "datumDo": "2015-12-31",
            "radnoMjesto": "Viši asistent",
            "vrstaZaposlenja": "Redovno",
            "aktivno": False,
        }
        z = Zaposlenje.from_dict(raw)
        assert z.id == 3
        assert z.ustanova.naziv == "IRB"
        assert z.aktivno is False

    def test_to_dict(self):
        d = Zaposlenje.from_dict({
            "id": 1,
            "ustanova": {"id": 1, "naziv": "FER"},
            "datumOd": "2020-01-01", "datumDo": None,
            "radnoMjesto": "Profesor", "vrstaZaposlenja": "Redovno", "aktivno": True,
        }).to_dict()
        assert d["ustanova"] == "FER"
        assert d["aktivno"] is True


class TestRadniOdnos:
    def test_from_dict_maps_hr_pers_radni_odnos_id(self):
        raw = {
            "hrPersRadniOdnosId": 99,
            "cfPersId": 42,
            "oibOsobe": "11111111111",
            "imeOsobe": "Maja",
            "prezimeOsobe": "Novak",
            "cfOrgUnitId": 5,
            "vrstaRadnogOdnosa": "Radni odnos",
            "oblikRadnogVremena": "Puno radno vrijeme",
            "kategorijaRadnogMjesta": "I. vrsta",
            "radnoMjestoNaziv": "Redoviti profesor",
            "datumPocetka": "01.01.2020.",
        }
        r = RadniOdnos.from_dict(raw)
        assert r.id == 99
        assert r.puno_ime == "Maja Novak"
        assert r.datum_pocetka == "01.01.2020."

    def test_to_dict_keys(self):
        raw = {"hrPersRadniOdnosId": 1, "imeOsobe": "A", "prezimeOsobe": "B"}
        d = RadniOdnos.from_dict(raw).to_dict()
        assert "puno_ime" in d
        assert "vrsta_radnog_odnosa" in d


class TestOsobaAkreditacija:
    def test_from_dict(self):
        raw = {
            "id": 10,
            "oib": "22222222222",
            "ime": "Pero",
            "prezime": "Perić",
            "poveznica": "https://...",
            "vrstaZaposlenjaHr": "Redovno",
            "vrstaRadnogOdnosaHr": "Radni odnos",
            "podrucjeHr": "Tehničke znanosti",
            "poljeHr": "Računarstvo",
        }
        o = OsobaAkreditacija.from_dict(raw)
        assert o.puno_ime == "Pero Perić"
        assert o.polje_hr == "Računarstvo"
