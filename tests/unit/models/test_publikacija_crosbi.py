"""Testovi za crosbi.models.publikacija_crosbi."""
import pytest
from crosbi.models.publikacija_crosbi import (
    Citat,
    Poveznica,
    Skup,
    DisciplinaCrosbi,
    OsobaPublikacija,
    UstanovaPublikacija,
    ProjektPublikacija,
    PublikacijaCrosbi,
)


class TestCitat:
    def test_from_dict(self):
        c = Citat.from_dict({"vrstaCitataId": 1, "vrstaCitataNaziv": "CROSBI", "citat": "Horvat, 2022"})
        assert c.vrsta_id == 1
        assert c.vrsta_naziv == "CROSBI"
        assert c.citat == "Horvat, 2022"

    def test_from_dict_prazno(self):
        c = Citat.from_dict({})
        assert c.vrsta_id is None


class TestPoveznica:
    def test_from_dict(self):
        p = Poveznica.from_dict({"urlId": 1, "urlVrstaId": 2, "urlVrstaNaziv": "DOI", "url": "https://doi.org/10.1234"})
        assert p.url_id == 1
        assert p.url == "https://doi.org/10.1234"


class TestSkup:
    def test_from_dict(self):
        s = Skup.from_dict({"cfEventId": 5, "naziv": "MIPRO 2022", "href": "https://mipro.hr"})
        assert s.cf_event_id == 5
        assert s.naziv == "MIPRO 2022"


class TestDisciplinaCrosbi:
    def test_from_dict(self):
        d = DisciplinaCrosbi.from_dict({"id": 1, "naziv": "Fizika", "sifra": "1.03"})
        assert d.id == 1
        assert d.sifra == "1.03"


class TestOsobaPublikacija:
    def test_from_dict_mapira_polja(self):
        o = OsobaPublikacija.from_dict({
            "crorisId": 9,
            "titulaIspredImena": "dr. sc.",
            "ime": "Ana",
            "prezime": "Kovač",
            "funkcija": {"id": 1, "naziv": "Autor"},
        })
        assert o.croris_id == 9
        assert o.titula == "dr. sc."
        assert o.funkcija.naziv == "Autor"

    def test_puno_ime(self):
        o = OsobaPublikacija(ime="Ana", prezime="Kovač")
        assert o.puno_ime == "Ana Kovač"

    def test_puno_ime_bez_prezimena(self):
        assert OsobaPublikacija(ime="Ana").puno_ime == "Ana"

    def test_from_dict_bez_funkcije(self):
        o = OsobaPublikacija.from_dict({"crorisId": 1})
        assert o.funkcija is None


class TestUstanovaPublikacija:
    def test_from_dict_mapira_polja(self):
        u = UstanovaPublikacija.from_dict({
            "crorisId": 176,
            "naziv": "VUKA",
            "mbu": 248,
            "funkcija": {"id": 1, "naziv": "Nositelj"},
        })
        assert u.croris_id == 176
        assert u.naziv == "VUKA"
        assert u.mbu == 248
        assert u.funkcija.naziv == "Nositelj"

    def test_from_dict_bez_funkcije(self):
        u = UstanovaPublikacija.from_dict({"crorisId": 1})
        assert u.funkcija is None


class TestProjektPublikacija:
    def test_from_dict(self):
        p = ProjektPublikacija.from_dict({"crorisId": 5, "naziv": "Projekt X"})
        assert p.croris_id == 5
        assert p.naziv == "Projekt X"
        assert p.funkcija is None

    def test_from_dict_s_funkcijom(self):
        p = ProjektPublikacija.from_dict({
            "crorisId": 5,
            "naziv": "Projekt X",
            "funkcija": {"id": 2, "naziv": "Srodni projekt"},
        })
        assert p.funkcija.naziv == "Srodni projekt"


class TestPublikacijaCrosbi:
    def test_from_dict_mapira_obavezno_polje(self, publikacija_crosbi_raw):
        p = PublikacijaCrosbi.from_dict(publikacija_crosbi_raw)
        assert p.crosbi_id == 192111

    def test_from_dict_mapira_sva_polja(self, publikacija_crosbi_raw):
        p = PublikacijaCrosbi.from_dict(publikacija_crosbi_raw)
        assert p.autori == "Horvat, Ivan; Kovač, Ana"
        assert p.naslov == "Testna publikacija"
        assert p.vrsta == "prilog u časopisu"
        assert p.doi == "10.1234/test"
        assert p.casopis == "Test Journal"
        assert p.indeksiranost == ["WoS", "Scopus"]

    def test_from_dict_parsira_ugnjezdene_liste(self, publikacija_crosbi_raw):
        p = PublikacijaCrosbi.from_dict(publikacija_crosbi_raw)
        assert len(p.citati) == 1
        assert isinstance(p.citati[0], Citat)
        assert len(p.poveznice) == 1
        assert isinstance(p.poveznice[0], Poveznica)
        assert len(p.discipline) == 1
        assert isinstance(p.discipline[0], DisciplinaCrosbi)

    def test_from_dict_minimalni(self):
        p = PublikacijaCrosbi.from_dict({"crosbiId": 1})
        assert p.crosbi_id == 1
        assert p.citati == []
        assert p.discipline == []

    def test_to_dict_sadrzi_kljucna_polja(self, publikacija_crosbi_raw):
        d = PublikacijaCrosbi.from_dict(publikacija_crosbi_raw).to_dict()
        assert d["crosbi_id"] == 192111
        assert d["doi"] == "10.1234/test"
        assert d["indeksiranost"] == "WoS, Scopus"
        assert d["status"] == "objavljeno"
