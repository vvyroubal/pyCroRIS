"""Testovi za preostale modele — Osoba, Ustanova, Publikacija, Financijer,
Casopis, Dogadanje, UstanovaReg i MOZVAG modeli."""

import pytest

from crosbi.models.casopis import Casopis, PublikacijaCasopis
from crosbi.models.dogadanje import Dogadanje, Drzava, MjestoOdrzavanja
from crosbi.models.financijer import Financijer, FinancijerProgram
from crosbi.models.mozvag import OsobaMozvag, ProjektMozvag, UstanovaMozvag
from crosbi.models.osoba import Osoba
from crosbi.models.publikacija import Publikacija
from crosbi.models.ustanova import Ustanova
from crosbi.models.ustanova_reg import Adresa, Grana, Kontakt, Podrucje, Polje, UstanovaReg


# ---------------------------------------------------------------------------
# Osoba
# ---------------------------------------------------------------------------


class TestOsoba:
    def test_from_dict(self, osoba_raw):
        o = Osoba.from_dict(osoba_raw)
        assert o.pers_id == 7
        assert o.ime == "Ana"
        assert o.prezime == "Kovač"
        assert o.oib == "98765432109"
        assert o.klasifikacija.naziv == "Voditelj projekta"
        assert o.ustanova_naziv == "Institut Ruđer Bošković"

    def test_puno_ime(self, osoba_raw):
        o = Osoba.from_dict(osoba_raw)
        assert o.puno_ime == "Ana Kovač"

    def test_puno_ime_only_prezime(self, osoba_raw):
        osoba_raw["ime"] = None
        assert Osoba.from_dict(osoba_raw).puno_ime == "Kovač"

    def test_puno_ime_both_none(self, osoba_raw):
        osoba_raw["ime"] = None
        osoba_raw["prezime"] = None
        assert Osoba.from_dict(osoba_raw).puno_ime == ""

    def test_to_dict_keys(self, osoba_raw):
        d = Osoba.from_dict(osoba_raw).to_dict()
        for key in ("pers_id", "ime", "prezime", "puno_ime", "oib", "mbz", "uloga", "ustanova"):
            assert key in d

    def test_missing_klasifikacija(self, osoba_raw):
        osoba_raw["klasifikacija"] = None
        o = Osoba.from_dict(osoba_raw)
        assert o.klasifikacija is None
        assert o.to_dict()["uloga"] is None


# ---------------------------------------------------------------------------
# Ustanova (projekti-api verzija)
# ---------------------------------------------------------------------------


class TestUstanova:
    def test_from_dict(self, ustanova_raw):
        u = Ustanova.from_dict(ustanova_raw)
        assert u.id == 10
        assert u.mbu == "0010001"
        assert u.amount == 50000.0
        assert u.currency_code == "EUR"
        assert u.klasifikacija.naziv == "Nositelj"

    def test_to_dict(self, ustanova_raw):
        d = Ustanova.from_dict(ustanova_raw).to_dict()
        assert d["mbu"] == "0010001"
        assert d["amount"] == 50000.0

    def test_missing_klasifikacija(self, ustanova_raw):
        ustanova_raw["klasifikacija"] = None
        u = Ustanova.from_dict(ustanova_raw)
        assert u.klasifikacija is None
        assert u.to_dict()["uloga"] is None


# ---------------------------------------------------------------------------
# Publikacija (projekti-api verzija)
# ---------------------------------------------------------------------------


class TestPublikacija:
    def test_from_dict(self, publikacija_raw):
        p = Publikacija.from_dict(publikacija_raw)
        assert p.cf_res_publ_id == 42
        assert p.naslov == "Rezultati istraživanja"
        assert p.doi == "10.1234/test.2022"
        assert p.issn == "1234-5678"
        assert p.klasifikacija.naziv == "A1"

    def test_to_dict_keys(self, publikacija_raw):
        d = Publikacija.from_dict(publikacija_raw).to_dict()
        for key in ("id", "naslov", "autori", "vrsta", "doi", "issn"):
            assert key in d


# ---------------------------------------------------------------------------
# Financijer
# ---------------------------------------------------------------------------


class TestFinancijer:
    def test_from_dict(self, financijer_raw):
        f = Financijer.from_dict(financijer_raw)
        assert f.id == 5
        assert f.amount == 75000.0
        assert f.entity_name_hr == "Hrvatska zaklada za znanost"
        assert f.program.naziv_hr == "Istraživački projekti"

    def test_get_naziv_hr(self, financijer_raw):
        f = Financijer.from_dict(financijer_raw)
        assert "zaklada" in f.get_naziv("hr").lower()

    def test_get_naziv_fallback_to_entity_name(self):
        f = Financijer.from_dict({
            "id": 1, "entityNameHr": "HZZ",
            "financijer": [], "nadleznost": [],
        })
        assert f.get_naziv("hr") == "HZZ"

    def test_to_dict(self, financijer_raw):
        d = Financijer.from_dict(financijer_raw).to_dict()
        assert d["amount"] == 75000.0
        assert d["program"] == "Istraživački projekti"


# ---------------------------------------------------------------------------
# Casopis
# ---------------------------------------------------------------------------


class TestCasopis:
    def test_from_dict(self, casopis_raw):
        c = Casopis.from_dict(casopis_raw)
        assert c.id == 88
        assert c.naziv == "Acta Adriatica"
        assert c.issn == "0001-5113"
        assert c.drzava_kod == "HR"
        assert len(c.publikacije) == 1
        assert c.publikacije[0].cf_res_publ_id == 100

    def test_to_dict(self, casopis_raw):
        d = Casopis.from_dict(casopis_raw).to_dict()
        assert d["issn"] == "0001-5113"
        assert d["drzava"] == "Hrvatska"

    def test_from_dict_no_publikacije(self, casopis_raw):
        casopis_raw["publikacijaResource"] = {}
        c = Casopis.from_dict(casopis_raw)
        assert c.publikacije == []


# ---------------------------------------------------------------------------
# Dogadanje
# ---------------------------------------------------------------------------


class TestDogadanje:
    def test_from_dict(self, dogadanje_raw):
        d = Dogadanje.from_dict(dogadanje_raw)
        assert d.id == 55
        assert d.vrsta_dogadanja == "Konferencija"
        assert d.broj_sudionika == 150
        assert len(d.mjesta_odrzavanja) == 1

    def test_get_naziv_hr(self, dogadanje_raw):
        d = Dogadanje.from_dict(dogadanje_raw)
        assert d.get_naziv("hr") == "Testna konferencija"

    def test_get_akronim(self, dogadanje_raw):
        d = Dogadanje.from_dict(dogadanje_raw)
        assert d.get_akronim("en") == "TC2023"

    def test_to_dict_lokacija(self, dogadanje_raw):
        result = Dogadanje.from_dict(dogadanje_raw).to_dict()
        assert result["lokacija"] == "Ul. Grada Vukovara 68, Zagreb"
        assert result["drzava"] == "Hrvatska"

    def test_to_dict_no_mjesta(self, dogadanje_raw):
        dogadanje_raw["mjestoOdrzavanja"] = []
        d = Dogadanje.from_dict(dogadanje_raw).to_dict()
        assert d["lokacija"] is None
        assert d["drzava"] is None

    def test_empty_naziv_list(self, dogadanje_raw):
        dogadanje_raw["naziv"] = []
        d = Dogadanje.from_dict(dogadanje_raw)
        assert d.get_naziv("hr") == ""


# ---------------------------------------------------------------------------
# UstanovaReg (ustanove-api)
# ---------------------------------------------------------------------------


class TestUstanovaReg:
    def test_from_dict(self, ustanova_reg_raw):
        u = UstanovaReg.from_dict(ustanova_reg_raw)
        assert u.id == 15
        assert u.kratica == "FER"
        assert u.mbu == "1234567"
        assert u.oib == "11111111111"
        assert u.aktivna is True
        assert u.adresa.mjesto == "Zagreb"
        assert u.kontakt.web == "https://www.fer.unizg.hr"
        assert u.nad_ustanova.naziv == "Sveučilište u Zagrebu"
        assert u.vrsta_ustanove.naziv == "Fakultet"

    def test_to_dict(self, ustanova_reg_raw):
        d = UstanovaReg.from_dict(ustanova_reg_raw).to_dict()
        assert d["grad"] == "Zagreb"
        assert d["web"] == "https://www.fer.unizg.hr"
        assert d["vrsta"] == "Fakultet"

    def test_missing_adresa(self, ustanova_reg_raw):
        ustanova_reg_raw["adresa"] = None
        u = UstanovaReg.from_dict(ustanova_reg_raw)
        assert u.adresa is None
        assert u.to_dict()["grad"] is None


# ---------------------------------------------------------------------------
# MOZVAG modeli
# ---------------------------------------------------------------------------


class TestUstanovaMozvag:
    def test_from_dict(self):
        raw = {
            "ustanovaId": 1,
            "adresa": "Bijenička 54",
            "oib": "33333333333",
            "web": "https://irb.hr",
            "aaiDomain": "irb.hr",
            "grad": "Zagreb",
            "naziv": [{"cfLangCode": "hr", "naziv": "Institut Ruđer Bošković", "original": True}],
        }
        u = UstanovaMozvag.from_dict(raw)
        assert u.ustanova_id == 1
        assert u.get_naziv("hr") == "Institut Ruđer Bošković"
        assert u.to_dict()["grad"] == "Zagreb"


class TestProjektMozvag:
    def test_from_dict(self):
        raw = {
            "projektId": 10,
            "naziv": "Projekt X",
            "startDate": "2022-01-01",
            "endDate": "2024-12-31",
            "ulogaId": 1,
            "ulogaNaziv": "Nositelj",
            "ustanovaValuta": "EUR",
            "ustanovaIznos": 50000,
            "projektValuta": "EUR",
            "projektIznos": 200000,
            "vrstaProjektaId": 3,
            "vrstaProjektaNaziv": "Istraživački",
            "financijeri": [
                {"financijerId": 1, "nazivHr": "HZZ", "valuta": "EUR", "iznos": 150000}
            ],
        }
        p = ProjektMozvag.from_dict(raw)
        assert p.projekt_id == 10
        assert p.projekt_iznos == 200000
        assert len(p.financijeri) == 1
        d = p.to_dict()
        assert d["financijeri"] == "HZZ"


class TestOsobaMozvag:
    def test_from_dict(self):
        raw = {
            "osobaId": 5,
            "ustanovaid": 10,
            "ime": "Marko",
            "prezime": "Marković",
            "maticniBroj": "999",
            "znanstveniProjekti": 3,
            "ostaliProjekti": 1,
        }
        o = OsobaMozvag.from_dict(raw)
        assert o.ukupno_projekata == 4
        assert o.puno_ime == "Marko Marković"


# ---------------------------------------------------------------------------
# PPG modeli
# ---------------------------------------------------------------------------


class TestPPGModeli:
    def test_podrucje_from_dict(self):
        p = Podrucje.from_dict({
            "disciplinaId": 1,
            "nazivDiscipline": "Prirodne znanosti",
            "nazivDisciplineEn": "Natural Sciences",
            "sifraDiscipline": "1",
        })
        assert p.naziv == "Prirodne znanosti"
        assert p.to_dict()["sifra"] == "1"

    def test_grana_from_dict(self):
        g = Grana.from_dict({
            "disciplinaId": 101,
            "nazivDiscipline": "Kemija organskih spojeva",
            "sifraDiscipline": "1.07.01",
        })
        assert g.sifra == "1.07.01"

    def test_polje_from_dict_with_grane(self):
        raw = {
            "disciplinaId": 10,
            "nazivDiscipline": "Kemija",
            "sifraDiscipline": "1.07",
            "grane": [
                {"disciplinaId": 101, "nazivDiscipline": "Org. kemija", "sifraDiscipline": "1.07.01"},
            ],
        }
        p = Polje.from_dict(raw)
        assert len(p.grane) == 1
        assert p.to_dict()["broj_grana"] == 1
