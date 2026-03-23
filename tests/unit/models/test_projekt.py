"""Testovi za crosbi.models.projekt — Projekt."""

import pytest

from crosbi.models.projekt import Projekt


class TestProjektFromDict:
    def test_full_dict(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.id == 1
        assert p.acro == "TESTPROJ"
        assert p.uri == "https://croris.hr/projekt/1"
        assert p.pocetak == "2020-01-01"
        assert p.kraj == "2023-12-31"
        assert p.currency_code == "EUR"
        assert p.total_cost == 100000.0
        assert p.hr_sifra_projekta == "HR-TEST-001"
        assert p.verified == "2020-02-01"
        assert p.last_updated_at == 1700000000
        assert p.projekt_poirot_id == 100

    def test_tip_projekta_parsed(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.tip_projekta is not None
        assert p.tip_projekta.id == 5
        assert p.tip_projekta.naziv == "Istraživački projekt"

    def test_tip_projekta_none_when_missing(self, projekt_raw):
        projekt_raw["tipProjekta"] = None
        p = Projekt.from_dict(projekt_raw)
        assert p.tip_projekta is None

    def test_title_parsed(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert len(p.title) == 2
        assert p.title[0].lang_code == "hr"
        assert p.title[1].lang_code == "en"

    def test_empty_keywords_list(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.keywords == []

    def test_minimal_dict(self, projekt_raw_minimal):
        p = Projekt.from_dict(projekt_raw_minimal)
        assert p.id == 99
        assert p.acro is None
        assert p.title == []
        assert p.tip_projekta is None

    def test_missing_id_raises(self):
        with pytest.raises(KeyError):
            Projekt.from_dict({})

    def test_camel_case_mapping(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.currency_code == projekt_raw["currencyCode"]
        assert p.total_cost == projekt_raw["totalCost"]
        assert p.hr_sifra_projekta == projekt_raw["hrSifraProjekta"]
        assert p.last_updated_at == projekt_raw["lastUpdatedAt"]


class TestProjektGetTitle:
    def test_get_title_hr(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.get_title("hr") == "Testni projekt"

    def test_get_title_en(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.get_title("en") == "Test project"

    def test_get_title_fallback(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.get_title("de") == "Testni projekt"

    def test_get_title_empty_list(self, projekt_raw_minimal):
        p = Projekt.from_dict(projekt_raw_minimal)
        assert p.get_title("hr") == ""

    def test_get_summary(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.get_summary("hr") == "Kratki sažetak."

    def test_get_keywords_empty(self, projekt_raw):
        p = Projekt.from_dict(projekt_raw)
        assert p.get_keywords("hr") == ""


class TestProjektToDict:
    def test_to_dict_keys(self, projekt_raw):
        d = Projekt.from_dict(projekt_raw).to_dict()
        for key in ("id", "acro", "hr_sifra_projekta", "title_hr", "title_en",
                    "tip_projekta", "pocetak", "kraj", "total_cost", "currency_code"):
            assert key in d

    def test_to_dict_tip_projekta_none(self, projekt_raw):
        projekt_raw["tipProjekta"] = None
        d = Projekt.from_dict(projekt_raw).to_dict()
        assert d["tip_projekta"] is None

    def test_to_dict_title_values(self, projekt_raw):
        d = Projekt.from_dict(projekt_raw).to_dict()
        assert d["title_hr"] == "Testni projekt"
        assert d["title_en"] == "Test project"
