"""Testovi za crosbi.models.oprema."""
import pytest
from crosbi.models.oprema import (
    TranslatedTextML,
    Cijena,
    OpremaUstanova,
    OpremaProjekt,
    OpremaOsoba,
    Oprema,
    Usluga,
    UslugaCjenik,
)


class TestTranslatedTextML:
    def test_get_vraca_tekst_na_zadanom_jeziku(self):
        t = TranslatedTextML(records=[
            {"langCode": "hr", "naziv": "Spektrometar"},
            {"langCode": "en", "naziv": "Spectrometer"},
        ])
        assert t.get("hr") == "Spektrometar"
        assert t.get("en") == "Spectrometer"

    def test_get_fallback_na_prvi_zapis(self):
        t = TranslatedTextML(records=[{"langCode": "en", "naziv": "Spectrometer"}])
        assert t.get("hr") == "Spectrometer"

    def test_get_prazni_records_vraca_prazan_string(self):
        assert TranslatedTextML().get("hr") == ""

    def test_from_dict_s_records(self):
        t = TranslatedTextML.from_dict({"records": [{"langCode": "hr", "naziv": "Test"}]})
        assert t.get("hr") == "Test"

    def test_from_dict_none_vraca_prazan(self):
        t = TranslatedTextML.from_dict(None)
        assert t.records == []


class TestCijena:
    def test_from_dict_mapira_polja(self):
        c = Cijena.from_dict({"iznos": 50000.0, "jedinicaMjere": "kom", "valuta": "EUR"})
        assert c.iznos == 50000.0
        assert c.jedinica_mjere == "kom"
        assert c.valuta == "EUR"

    def test_from_dict_optional_polja_su_none(self):
        c = Cijena.from_dict({})
        assert c.iznos is None
        assert c.valuta is None


class TestOpremaUstanova:
    def test_from_dict(self):
        u = OpremaUstanova.from_dict({"id": 10, "naziv": "IRB", "mbu": 1234567})
        assert u.id == 10
        assert u.naziv == "IRB"


class TestOpremaProjekt:
    def test_from_dict(self):
        p = OpremaProjekt.from_dict({"id": 5, "naziv": "Projekt X"})
        assert p.id == 5
        assert p.naziv == "Projekt X"


class TestOpremaOsoba:
    def test_from_dict_mapira_polja(self):
        o = OpremaOsoba.from_dict({
            "id": 11,
            "ime": "Marko",
            "prezime": "Novak",
            "titulaIspredImena": "dr. sc.",
            "funkcija": {"id": 1, "naziv": "Voditelj"},
        })
        assert o.id == 11
        assert o.ime == "Marko"
        assert o.titula == "dr. sc."
        assert o.funkcija.naziv == "Voditelj"

    def test_puno_ime(self):
        o = OpremaOsoba(id=1, ime="Marko", prezime="Novak")
        assert o.puno_ime == "Marko Novak"

    def test_puno_ime_bez_prezimena(self):
        o = OpremaOsoba(id=1, ime="Marko", prezime=None)
        assert o.puno_ime == "Marko"

    def test_to_dict(self):
        o = OpremaOsoba(id=1, ime="Marko", prezime="Novak", titula="dr. sc.")
        d = o.to_dict()
        assert d["id"] == 1
        assert d["puno_ime"] == "Marko Novak"
        assert d["titula"] == "dr. sc."


class TestOprema:
    def test_from_dict_minimalni(self):
        o = Oprema.from_dict({"id": 77})
        assert o.id == 77
        assert o.model is None
        assert o.naziv is not None  # TranslatedTextML prazan

    def test_from_dict_potpuni(self, oprema_raw):
        o = Oprema.from_dict(oprema_raw)
        assert o.id == 77
        assert o.model == "Model X"
        assert o.proizvodjac == "Siemens"
        assert o.inventarni_broj == "INV-001"
        assert o.godina_proizvodnje == 2019
        assert o.nabavna_cijena.iznos == 50000.0
        assert o.nabavna_cijena.valuta == "EUR"
        assert o.kategorija.naziv == "srednja (od 55.000 do 400.000 EUR)"
        assert o.stanje.naziv == "ispravna"
        assert o.nacin_koristenja.naziv == "javno dostupna"
        assert o.ustanova_vlasnik.naziv == "IRB"
        assert o.projekt.naziv == "Projekt X"

    def test_get_naziv_hr(self, oprema_raw):
        o = Oprema.from_dict(oprema_raw)
        assert o.get_naziv("hr") == "Spektrometar"

    def test_get_naziv_en(self, oprema_raw):
        o = Oprema.from_dict(oprema_raw)
        assert o.get_naziv("en") == "Spectrometer"

    def test_to_dict_sadrzi_kljucna_polja(self, oprema_raw):
        d = Oprema.from_dict(oprema_raw).to_dict()
        assert d["id"] == 77
        assert d["model"] == "Model X"
        assert d["kategorija"] == "srednja (od 55.000 do 400.000 EUR)"
        assert d["cijena"] == 50000.0
        assert d["valuta"] == "EUR"


class TestUsluga:
    def test_from_dict_mapira_polja(self):
        u = Usluga.from_dict({
            "id": 33,
            "ustanova": {"id": 176, "naziv": "VUKA"},
            "pocetak": "2020-01-01",
            "kraj": None,
            "aktivnost": True,
            "naziv": {"records": [{"langCode": "hr", "naziv": "Analiza piva"}]},
            "opis": None,
        })
        assert u.id == 33
        assert u.ustanova_id == 176
        assert u.ustanova_naziv == "VUKA"
        assert u.aktivnost is True
        assert u.get_naziv("hr") == "Analiza piva"

    def test_from_dict_bez_ustanove(self):
        u = Usluga.from_dict({"id": 1})
        assert u.ustanova_id is None

    def test_to_dict(self):
        u = Usluga.from_dict({"id": 33, "ustanova": {"id": 1, "naziv": "IRB"}, "aktivnost": True})
        d = u.to_dict()
        assert d["id"] == 33
        assert d["ustanova"] == "IRB"
        assert d["aktivnost"] is True


class TestUslugaCjenik:
    def test_from_dict_mapira_polja(self, usluga_cjenik_raw):
        c = UslugaCjenik.from_dict(usluga_cjenik_raw)
        assert c.id == 9
        assert c.vrsta_korisnika.naziv == "Akademska institucija"
        assert c.cijena.iznos == 200.0

    def test_from_dict_bez_opcionalnih(self):
        c = UslugaCjenik.from_dict({"id": 1})
        assert c.vrsta_korisnika is None
        assert c.cijena is None

    def test_to_dict(self, usluga_cjenik_raw):
        d = UslugaCjenik.from_dict(usluga_cjenik_raw).to_dict()
        assert d["id"] == 9
        assert d["vrsta_korisnika"] == "Akademska institucija"
        assert d["iznos"] == 200.0
        assert d["valuta"] == "EUR"
