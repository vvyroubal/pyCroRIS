"""Zajednički fixtures za sve testove."""

import pytest

from crosbi.config import Config


def pytest_collection_modifyitems(items):
    for item in items:
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)


# ---------------------------------------------------------------------------
# Config fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_config():
    return Config(username="testuser", password="testpass", page_size=10, timeout=5)


# ---------------------------------------------------------------------------
# Sirovi rječnici koji simuliraju API odgovore (HAL+JSON)
# ---------------------------------------------------------------------------


@pytest.fixture
def projekt_raw():
    return {
        "id": 1,
        "acro": "TESTPROJ",
        "uri": "https://croris.hr/projekt/1",
        "pocetak": "2020-01-01",
        "kraj": "2023-12-31",
        "currencyCode": "EUR",
        "totalCost": 100000.0,
        "tipProjekta": {"id": 5, "naziv": "Istraživački projekt"},
        "title": [
            {"cfLangCode": "hr", "naziv": "Testni projekt", "cfLangName": "hrvatski", "original": True},
            {"cfLangCode": "en", "naziv": "Test project", "cfLangName": "english", "original": False},
        ],
        "summary": [
            {"cfLangCode": "hr", "naziv": "Kratki sažetak.", "original": True},
        ],
        "keywords": [],
        "hrSifraProjekta": "HR-TEST-001",
        "verified": "2020-02-01",
        "lastUpdatedAt": 1700000000,
        "projektPoirotId": 100,
        "_links": {"self": {"href": "https://croris.hr/projekt/1"}},
    }


@pytest.fixture
def projekt_raw_minimal():
    """Projekt s minimalnim obaveznim poljima."""
    return {"id": 99}


@pytest.fixture
def osoba_raw():
    return {
        "persId": 7,
        "ime": "Ana",
        "prezime": "Kovač",
        "oib": "98765432109",
        "maticniBrojZnanstvenika": "654321",
        "klasifikacija": {"id": 1, "naziv": "Voditelj projekta"},
        "pocetak": "2021-01-01",
        "kraj": None,
        "ustanovaId": 10,
        "ustanovaNaziv": "Institut Ruđer Bošković",
        "email": "ana.kovac@irb.hr",
        "osobaPoirotId": 200,
        "_links": {},
    }


@pytest.fixture
def ustanova_raw():
    return {
        "id": 10,
        "naziv": "IRB",
        "mbu": "0010001",
        "klasifikacija": {"id": 2, "naziv": "Nositelj"},
        "pocetak": "2021-01-01",
        "kraj": "2023-12-31",
        "amount": 50000.0,
        "currencyCode": "EUR",
        "aaiDomain": "irb.hr",
        "ustanovaPoirotId": 300,
        "_links": {},
    }


@pytest.fixture
def publikacija_raw():
    return {
        "cfResPublId": 42,
        "naslov": "Rezultati istraživanja",
        "autori": "Kovač, Ana; Horvat, Ivan",
        "nadredenaPublikacije": "Acta Adriatica",
        "vrstaPublikacije": "Rad u časopisu",
        "tipPublikacije": "Izvorni znanstveni rad",
        "datum": "2022-06-15",
        "isbn": None,
        "issn": "1234-5678",
        "eissn": None,
        "doi": "10.1234/test.2022",
        "klasifikacija": {"id": 3, "naziv": "A1"},
        "_links": {},
    }


@pytest.fixture
def financijer_raw():
    return {
        "id": 5,
        "amount": 75000.0,
        "currencyCode": "EUR",
        "entityId": 1,
        "entityNameHr": "Hrvatska zaklada za znanost",
        "entityNameEn": "Croatian Science Foundation",
        "tipId": 1,
        "tipNaziv": "Nacionalni financijer",
        "vrstaIzvoraFinanciranjaId": 2,
        "vrstaIzvoraFinanciranjaName": "Nacionalni",
        "pozivId": 10,
        "pozivNaziv": "IP-2019",
        "financijer": [
            {"cfLangCode": "hr", "naziv": "Hrvatska zaklada za znanost", "original": True},
            {"cfLangCode": "en", "naziv": "Croatian Science Foundation", "original": False},
        ],
        "nadleznost": [],
        "program": {"id": 1, "nazivHr": "Istraživački projekti", "nazivEn": "Research Projects"},
        "financijerPoirotId": 50,
        "_links": {},
    }


@pytest.fixture
def znanstvenik_raw():
    return {
        "id": 42,
        "ime": "Ivan",
        "prezime": "Horvat",
        "oib": "12345678901",
        "maticniBroj": "123456",
        "orcid": "0000-0001-2345-6789",
        "email": "ivan.horvat@unizg.hr",
        "web": "https://unizg.hr/~ivan",
        "datumRodjenja": "1975-03-20",
        "spol": "M",
        "maxZvanje": "Redoviti profesor",
        "aktivanZnanstvenik": True,
        "godinaPrvogZaposlenjaZnanstvenika": 2002,
        "zvanjeResources": {
            "_embedded": {
                "zvanja": [
                    {
                        "id": 1,
                        "naziv": "Redoviti profesor",
                        "kratica": "red. prof.",
                        "datumIzbora": "2015-01-01",
                        "aktivan": True,
                        "ustanova": {"id": 10, "naziv": "Sveučilište u Zagrebu"},
                    }
                ]
            }
        },
        "akademskiStupanjResources": {
            "_embedded": {
                "akademskiStupnjevi": [
                    {
                        "id": 1,
                        "naziv": "Doktor znanosti",
                        "kratica": "dr. sc.",
                        "datumStjecanja": "2005-07-01",
                    }
                ]
            }
        },
        "zaposlenjeResources": {
            "_embedded": {
                "zaposlenja": [
                    {
                        "id": 1,
                        "ustanova": {"id": 10, "naziv": "Sveučilište u Zagrebu"},
                        "datumOd": "2002-10-01",
                        "datumDo": None,
                        "radnoMjesto": "Profesor",
                        "vrstaZaposlenja": "Redovno",
                        "aktivno": True,
                    },
                    {
                        "id": 2,
                        "ustanova": {"id": 20, "naziv": "IRB"},
                        "datumOd": "1999-01-01",
                        "datumDo": "2002-09-30",
                        "radnoMjesto": "Asistent",
                        "vrstaZaposlenja": "Redovno",
                        "aktivno": False,
                    },
                ]
            }
        },
        "_links": {},
    }


@pytest.fixture
def casopis_raw():
    return {
        "id": 88,
        "naziv": "Acta Adriatica",
        "drzava": "Hrvatska",
        "drzavaKod": "HR",
        "godinaPocetka": 1932,
        "godinaZavrsetka": None,
        "issn": "0001-5113",
        "eissn": "1847-0408",
        "lissn": None,
        "coden": "AAARA",
        "udk": "551.46",
        "publikacijaResource": {
            "_embedded": {
                "publikacije": [
                    {"cfResPublId": 100, "hrJournalId": 88, "citat": "Kovač, 2022"},
                ]
            }
        },
        "_links": {},
    }


@pytest.fixture
def dogadanje_raw():
    return {
        "id": 55,
        "uri": "https://example.com/event/55",
        "datumPocetka": "2023-06-10",
        "datumZavrsetka": "2023-06-12",
        "brojSudionika": 150,
        "vrstaOrganizacije": "Međunarodna",
        "vrstaDogadanja": "Konferencija",
        "naziv": [
            {"cfLangCode": "hr", "naziv": "Testna konferencija", "original": True},
            {"cfLangCode": "en", "naziv": "Test Conference", "original": False},
        ],
        "akronim": [{"cfLangCode": "en", "naziv": "TC2023", "original": True}],
        "opis": [],
        "kljucneRijeci": [],
        "mjestoOdrzavanja": [
            {
                "venueId": 1,
                "lokacija": "Ul. Grada Vukovara 68, Zagreb",
                "mjesto": {"cfGeoBBoxId": 1, "defaultNaziv": "Zagreb"},
                "drzava": {"cfCountryCode": "HR", "cfName": "Hrvatska"},
            }
        ],
        "publikacijaResource": {"_embedded": {"publikacije": []}},
        "_links": {},
    }


@pytest.fixture
def ustanova_reg_raw():
    return {
        "id": 15,
        "naziv": "FER",
        "puniNaziv": "Fakultet elektrotehnike i računarstva",
        "puniNazivEn": "Faculty of Electrical Engineering and Computing",
        "kratkiNaziv": "FER",
        "nazivEn": "FER",
        "kratica": "FER",
        "drzavaKod": "HR",
        "mbs": "080016165",
        "mbu": "1234567",
        "sifraISVU": 100,
        "mzoId": 200,
        "oib": "11111111111",
        "aktivna": True,
        "celnik": "prof. dr. sc. Ivana Novak",
        "tipVlasnistva": "Javno",
        "zupanija": "Grad Zagreb",
        "adresa": {"mjesto": "Zagreb", "ulicaBr": "Unska 3", "postanskiBroj": "10000"},
        "kontakt": {
            "telefon": "+385 1 6129 999",
            "fax": None,
            "web": "https://www.fer.unizg.hr",
            "email": "dekanat@fer.hr",
        },
        "nadUstanova": {"id": 1, "naziv": "Sveučilište u Zagrebu", "mbu": "0000001"},
        "tipUstanova": [{"id": 1, "naziv": "Visoko učilište"}],
        "tipUstanove": [{"id": 1, "naziv": "Visoko učilište"}],
        "vrstaUstanove": {"id": 2, "naziv": "Fakultet"},
        "_links": {},
    }


@pytest.fixture
def paginated_page1():
    """Prva stranica paginiranog odgovora s next linkom."""
    return {
        "_embedded": {"projekti": [{"id": 1}, {"id": 2}]},
        "_links": {"self": {"href": "..."}, "next": {"href": "..."}},
    }


@pytest.fixture
def paginated_page2():
    """Druga i posljednja stranica (bez next linka)."""
    return {
        "_embedded": {"projekti": [{"id": 3}]},
        "_links": {"self": {"href": "..."}},
    }
