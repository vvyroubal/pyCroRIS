# Unit Test Coverage — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pokriti unit testovima sve funkcije/modele koji trenutno nisu pokriveni (~50% pokrivenosti → ~95%).

**Architecture:** Svaki test koristi `mocker.MagicMock()` za klijent (pytest-mock), bez mrežnih poziva. Novi fixtures za raw dicts idu u `tests/conftest.py`. Pratiti obrazac iz postojećih testova: jedna klasa po funkciji, 2–3 testa po klasi (poziv URL-a, tip povratne vrijednosti, prazni odgovor).

**Tech Stack:** pytest, pytest-mock, responses (samo za `import_casopis_rad` koji koristi `session.post`)

---

## Datoteke

**Nove datoteke:**
- `tests/unit/endpoints/test_financijeri.py`
- `tests/unit/endpoints/test_osobe.py`
- `tests/unit/endpoints/test_publikacije.py`
- `tests/unit/endpoints/test_ustanove_projekti.py`
- `tests/unit/models/test_oprema.py`
- `tests/unit/models/test_publikacija_crosbi.py`

**Proširiti postojeće:**
- `tests/unit/endpoints/test_oprema.py` — dodati 11 klasa
- `tests/unit/endpoints/test_upisnik.py` — dodati 10 klasa
- `tests/unit/endpoints/test_publikacije_crosbi.py` — dodati 5 klasa
- `tests/unit/endpoints/test_casopisi.py` — dodati 2 klase
- `tests/unit/endpoints/test_dogadanja.py` — dodati 2 klase
- `tests/unit/endpoints/test_znanstvenici.py` — dodati 1 klasu
- `tests/conftest.py` — dodati fixtures za oprema, usluga_cjenik, publikacija_crosbi raw dicts

---

## Task 1: Fixtures u conftest.py

**Files:**
- Modify: `tests/conftest.py`

- [ ] **Step 1: Dodaj fixtures**

```python
@pytest.fixture
def oprema_raw():
    return {
        "id": 77,
        "model": "Model X",
        "proizvodjac": "Siemens",
        "inventarniBroj": "INV-001",
        "godinaProizvodnje": 2019,
        "datumNabave": "2019-06-01",
        "nabavnaCijena": {"iznos": 50000.0, "jedinicaMjere": "kom", "valuta": "EUR"},
        "prenosivost": False,
        "radNaDaljinu": True,
        "adresa": "Trg J.J. Strossmayera 2, Osijek",
        "naziv": {"records": [{"langCode": "hr", "naziv": "Spektrometar"}, {"langCode": "en", "naziv": "Spectrometer"}]},
        "kratkiNaziv": None,
        "opciOpis": None,
        "tehnickiOpis": None,
        "kategorija": {"id": 3, "naziv": "srednja (od 55.000 do 400.000 EUR)"},
        "stanjeOpreme": {"id": 1, "naziv": "ispravna"},
        "nacinKoristenja": {"id": 2, "naziv": "javno dostupna"},
        "ustanovaVlasnik": {"id": 10, "naziv": "IRB", "mbu": 1234567},
        "ustanovaLokacija": {"id": 10, "naziv": "IRB", "mbu": 1234567},
        "projekt": {"id": 5, "naziv": "Projekt X"},
    }


@pytest.fixture
def usluga_cjenik_raw():
    return {
        "id": 9,
        "vrstaKorisnika": {"id": 1, "naziv": "Akademska institucija"},
        "cijena": {"iznos": 200.0, "jedinicaMjere": "analiza", "valuta": "EUR"},
    }


@pytest.fixture
def publikacija_crosbi_raw():
    return {
        "crosbiId": 192111,
        "bibIrbId": 625029,
        "autori": "Horvat, Ivan; Kovač, Ana",
        "naslov": "Testna publikacija",
        "vrsta": "prilog u časopisu",
        "tip": "izvorni znanstveni rad",
        "casopis": "Test Journal",
        "volumen": "Vol. 1",
        "stranice": "1-10",
        "doi": "10.1234/test",
        "issn": "1234-5678",
        "eissn": "8765-4321",
        "isbn": None,
        "godina": "2022",
        "status": "objavljeno",
        "izdavac": "Test Publisher",
        "mjesto": "Zagreb",
        "indeksiranost": ["WoS", "Scopus"],
        "citati": [{"vrstaCitataId": 1, "vrstaCitataNaziv": "CROSBI", "citat": "Horvat, 2022"}],
        "naslovi": [{"cfLangCode": "hr", "naziv": "Testna publikacija", "original": True}],
        "sazeci": [],
        "kljucneRijeci": [],
        "poveznice": [{"urlId": 1, "urlVrstaId": 2, "urlVrstaNaziv": "DOI", "url": "https://doi.org/10.1234/test"}],
        "skup": [],
        "discipline": [{"id": 1, "naziv": "Fizika", "sifra": "1.03"}],
    }
```

- [ ] **Step 2: Pokreni testove da provjeriš da fixtures ne ruše ništa**

```bash
pytest tests/unit/ -q
```

Očekivano: sve prolazi, isti broj testova kao prije.

---

## Task 2: test_financijeri.py

**Files:**
- Create: `tests/unit/endpoints/test_financijeri.py`

- [ ] **Step 1: Napiši testove**

```python
"""Testovi za crosbi.endpoints.financijeri."""
import pytest
from crosbi.endpoints.financijeri import get_financijer, get_financijeri_projekta
from crosbi.models.financijer import Financijer


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetFinancijer:
    def test_poziva_ispravan_url(self, mock_client, financijer_raw):
        mock_client.get.return_value = financijer_raw
        get_financijer(5, client=mock_client)
        mock_client.get.assert_called_once_with("/financijer/5")

    def test_vraca_financijer_instancu(self, mock_client, financijer_raw):
        mock_client.get.return_value = financijer_raw
        result = get_financijer(5, client=mock_client)
        assert isinstance(result, Financijer)

    def test_id_se_mapira_ispravno(self, mock_client, financijer_raw):
        mock_client.get.return_value = financijer_raw
        result = get_financijer(5, client=mock_client)
        assert result.id == 5


class TestGetFinancijeриProjekta:
    def test_poziva_ispravan_url(self, mock_client, financijer_raw):
        mock_client.get_embedded.return_value = [financijer_raw]
        get_financijeri_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            "/financijer/projekt/1", "financijeri"
        )

    def test_vraca_listu_financijera(self, mock_client, financijer_raw):
        mock_client.get_embedded.return_value = [financijer_raw]
        result = get_financijeri_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Financijer)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_financijeri_projekta(1, client=mock_client) == []
```

- [ ] **Step 2: Pokreni i provjeri da prolaze**

```bash
pytest tests/unit/endpoints/test_financijeri.py -v
```

Očekivano: 6 testova PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/endpoints/test_financijeri.py tests/conftest.py
git commit -m "test: dodaj unit testove za endpoints financijeri i conftest fixtures"
```

---

## Task 3: test_osobe.py

**Files:**
- Create: `tests/unit/endpoints/test_osobe.py`

- [ ] **Step 1: Napiši testove**

```python
"""Testovi za crosbi.endpoints.osobe."""
import pytest
from crosbi.endpoints.osobe import (
    get_osoba,
    get_osoba_by_oib,
    get_voditelj_by_oib,
    get_osobe_projekta,
)
from crosbi.models.osoba import Osoba


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetOsoba:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        get_osoba(7, client=mock_client)
        mock_client.get.assert_called_once_with("/osoba/7")

    def test_vraca_osoba_instancu(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        result = get_osoba(7, client=mock_client)
        assert isinstance(result, Osoba)


class TestGetOsobaByOib:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        get_osoba_by_oib("98765432109", client=mock_client)
        mock_client.get.assert_called_once_with("/osoba/oib/98765432109")

    def test_vraca_osoba_instancu(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        result = get_osoba_by_oib("98765432109", client=mock_client)
        assert isinstance(result, Osoba)


class TestGetVoditeljByOib:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        get_voditelj_by_oib("98765432109", client=mock_client)
        mock_client.get.assert_called_once_with("/osoba/voditelj/oib/98765432109")

    def test_vraca_osoba_instancu(self, mock_client, osoba_raw):
        mock_client.get.return_value = osoba_raw
        result = get_voditelj_by_oib("98765432109", client=mock_client)
        assert isinstance(result, Osoba)


class TestGetOsobeProjekta:
    def test_poziva_ispravan_url(self, mock_client, osoba_raw):
        mock_client.get_embedded.return_value = [osoba_raw]
        get_osobe_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with("/osoba/projekt/1", "osobe")

    def test_vraca_listu_osoba(self, mock_client, osoba_raw):
        mock_client.get_embedded.return_value = [osoba_raw]
        result = get_osobe_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Osoba)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_osobe_projekta(1, client=mock_client) == []
```

- [ ] **Step 2: Pokreni i provjeri**

```bash
pytest tests/unit/endpoints/test_osobe.py -v
```

Očekivano: 8 testova PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/endpoints/test_osobe.py
git commit -m "test: dodaj unit testove za endpoints osobe"
```

---

## Task 4: test_publikacije.py i test_ustanove_projekti.py

**Files:**
- Create: `tests/unit/endpoints/test_publikacije.py`
- Create: `tests/unit/endpoints/test_ustanove_projekti.py`

- [ ] **Step 1: Napiši test_publikacije.py**

```python
"""Testovi za crosbi.endpoints.publikacije (projekti-api)."""
import pytest
from crosbi.endpoints.publikacije import get_publikacija, get_publikacije_projekta
from crosbi.models.publikacija import Publikacija


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetPublikacija:
    def test_poziva_ispravan_url(self, mock_client, publikacija_raw):
        mock_client.get.return_value = publikacija_raw
        get_publikacija(42, client=mock_client)
        mock_client.get.assert_called_once_with("/publikacija/42")

    def test_vraca_publikacija_instancu(self, mock_client, publikacija_raw):
        mock_client.get.return_value = publikacija_raw
        result = get_publikacija(42, client=mock_client)
        assert isinstance(result, Publikacija)

    def test_id_se_mapira_ispravno(self, mock_client, publikacija_raw):
        mock_client.get.return_value = publikacija_raw
        result = get_publikacija(42, client=mock_client)
        assert result.id == 42


class TestGetPublikacijeProjekta:
    def test_poziva_ispravan_url(self, mock_client, publikacija_raw):
        mock_client.get_embedded.return_value = [publikacija_raw]
        get_publikacije_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            "/publikacija/projekt/1", "publikacije"
        )

    def test_vraca_listu_publikacija(self, mock_client, publikacija_raw):
        mock_client.get_embedded.return_value = [publikacija_raw]
        result = get_publikacije_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Publikacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_publikacije_projekta(1, client=mock_client) == []
```

- [ ] **Step 2: Napiši test_ustanove_projekti.py**

```python
"""Testovi za crosbi.endpoints.ustanove (projekti-api)."""
import pytest
from crosbi.endpoints.ustanove import get_ustanova, get_ustanove_projekta
from crosbi.models.ustanova import Ustanova


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


class TestGetUstanova:
    def test_poziva_ispravan_url(self, mock_client, ustanova_raw):
        mock_client.get.return_value = ustanova_raw
        get_ustanova(10, client=mock_client)
        mock_client.get.assert_called_once_with("/ustanova/10")

    def test_vraca_ustanova_instancu(self, mock_client, ustanova_raw):
        mock_client.get.return_value = ustanova_raw
        result = get_ustanova(10, client=mock_client)
        assert isinstance(result, Ustanova)

    def test_id_se_mapira_ispravno(self, mock_client, ustanova_raw):
        mock_client.get.return_value = ustanova_raw
        result = get_ustanova(10, client=mock_client)
        assert result.id == 10


class TestGetUstanoveProjekta:
    def test_poziva_ispravan_url(self, mock_client, ustanova_raw):
        mock_client.get_embedded.return_value = [ustanova_raw]
        get_ustanove_projekta(1, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            "/ustanova/projekt/1", "ustanove"
        )

    def test_vraca_listu_ustanova(self, mock_client, ustanova_raw):
        mock_client.get_embedded.return_value = [ustanova_raw]
        result = get_ustanove_projekta(1, client=mock_client)
        assert isinstance(result, list)
        assert isinstance(result[0], Ustanova)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_ustanove_projekta(1, client=mock_client) == []
```

- [ ] **Step 3: Pokreni i provjeri**

```bash
pytest tests/unit/endpoints/test_publikacije.py tests/unit/endpoints/test_ustanove_projekti.py -v
```

Očekivano: 12 testova PASSED.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/endpoints/test_publikacije.py tests/unit/endpoints/test_ustanove_projekti.py
git commit -m "test: dodaj unit testove za endpoints publikacije i ustanove (projekti-api)"
```

---

## Task 5: Proširiti test_oprema.py

**Files:**
- Modify: `tests/unit/endpoints/test_oprema.py`

- [ ] **Step 1: Dodaj importove i klase na kraj datoteke**

Dopisati na kraj `tests/unit/endpoints/test_oprema.py`:

```python
from crosbi.endpoints.oprema_api import (
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
from crosbi.models.oprema import UslugaCjenik, OpremaOsoba


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


class TestGetOpremaByhref:
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
        mocker.patch("crosbi.endpoints.oprema_api.CrorisClient", return_value=mocker.MagicMock(**{"get.return_value": oprema_raw}))
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
```

- [ ] **Step 2: Ažuriraj import blok na vrhu datoteke**

Zamijeni postojeći import blok s:

```python
import pytest
import responses as resp_lib

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
```

- [ ] **Step 3: Pokreni i provjeri**

```bash
pytest tests/unit/endpoints/test_oprema.py -v
```

Očekivano: sve klase PASSED (stare + nove).

- [ ] **Step 4: Commit**

```bash
git add tests/unit/endpoints/test_oprema.py
git commit -m "test: proširi test_oprema s pokrivanjem svih preostalih funkcija"
```

---

## Task 6: Proširiti test_upisnik.py

**Files:**
- Modify: `tests/unit/endpoints/test_upisnik.py`

- [ ] **Step 1: Dodaj importove**

Na vrh datoteke (existing imports proširiti):

```python
from crosbi.endpoints.upisnik import (
    get_ustanova_by_id,
    get_ustanova_by_mbu,
    get_sve_aktivne_ustanove,
    get_croris_ustanove,
    get_sva_podrucja,
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
```

- [ ] **Step 2: Dodaj klase na kraj datoteke**

```python
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
        mock_client.get.return_value = {"id": 1, "naziv": "Prirodne znanosti", "sifra": "1"}
        get_podrucje(1, client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/evidencija-ppg/podrucje/1"
        )

    def test_vraca_podrucje_instancu(self, mock_client):
        mock_client.get.return_value = {"id": 1, "naziv": "Prirodne znanosti", "sifra": "1"}
        result = get_podrucje(1, client=mock_client)
        assert isinstance(result, Podrucje)


class TestGetPoljeSGranama:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"id": 2, "naziv": "Fizika", "sifra": "1.02", "grane": []}
        get_polje_s_granama(1, 2, client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{USTANOVE_BASE_URL}/evidencija-ppg/podrucje/1/polje/2"
        )

    def test_vraca_polje_instancu(self, mock_client):
        mock_client.get.return_value = {"id": 2, "naziv": "Fizika", "sifra": "1.02", "grane": []}
        result = get_polje_s_granama(1, 2, client=mock_client)
        assert isinstance(result, Polje)
```

- [ ] **Step 3: Pokreni i provjeri**

```bash
pytest tests/unit/endpoints/test_upisnik.py -v
```

Očekivano: sve klase PASSED (stare + nove).

- [ ] **Step 4: Commit**

```bash
git add tests/unit/endpoints/test_upisnik.py
git commit -m "test: proširi test_upisnik s pokrivanjem svih preostalih funkcija"
```

---

## Task 7: Proširiti test_publikacije_crosbi.py

**Files:**
- Modify: `tests/unit/endpoints/test_publikacije_crosbi.py`

- [ ] **Step 1: Dodaj importove i klase**

Dopisati na kraj `tests/unit/endpoints/test_publikacije_crosbi.py`:

```python
import responses as resp_lib
from crosbi.endpoints.publikacije_crosbi import (
    get_projekti_publikacije,
    get_publikacije_osobe,
    get_publikacije_osobe_by_mbz,
    get_osobe_publikacije,
    import_casopis_rad,
)
from crosbi.models.publikacija_crosbi import ProjektPublikacija, OsobaPublikacija
from crosbi.config import CROSBI_BASE_URL


class TestGetProjektiPublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get_embedded.return_value = []
        get_projekti_publikacije(100, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CROSBI_BASE_URL}/projekt/publikacija/100", "projekti"
        )

    def test_vraca_listu_projekt_publikacija(self, mock_client):
        mock_client.get_embedded.return_value = [{"crorisId": 5, "naziv": "Proj"}]
        result = get_projekti_publikacije(100, client=mock_client)
        assert isinstance(result[0], ProjektPublikacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_projekti_publikacije(100, client=mock_client) == []


class TestGetPublikacijeOsobe:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9}
        get_publikacije_osobe(9, client=mock_client)
        mock_client.get.assert_called_once_with(f"{CROSBI_BASE_URL}/osoba/9")

    def test_vraca_osoba_publikacija_instancu(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9, "ime": "Ana"}
        result = get_publikacije_osobe(9, client=mock_client)
        assert isinstance(result, OsobaPublikacija)


class TestGetPublikacijeOsobeByMbz:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9}
        get_publikacije_osobe_by_mbz("123456", client=mock_client)
        mock_client.get.assert_called_once_with(
            f"{CROSBI_BASE_URL}/osoba/maticni-broj/123456"
        )

    def test_vraca_osoba_publikacija_instancu(self, mock_client):
        mock_client.get.return_value = {"crorisId": 9, "ime": "Ana"}
        result = get_publikacije_osobe_by_mbz("123456", client=mock_client)
        assert isinstance(result, OsobaPublikacija)


class TestGetOsobePublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get_embedded.return_value = []
        get_osobe_publikacije(192111, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CROSBI_BASE_URL}/osoba/publikacija/192111", "osobe"
        )

    def test_vraca_listu_osoba(self, mock_client):
        mock_client.get_embedded.return_value = [{"crorisId": 9, "ime": "Ana"}]
        result = get_osobe_publikacije(192111, client=mock_client)
        assert isinstance(result[0], OsobaPublikacija)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_osobe_publikacije(192111, client=mock_client) == []


class TestImportCasopisRad:
    @resp_lib.activate
    def test_salje_post_zahtjev(self, test_config):
        from crosbi.client import CrorisClient
        url = f"{CROSBI_BASE_URL}/publikacija/import/casopisi-rad"
        resp_lib.add(resp_lib.POST, url, json={"saved": 1, "skipped": 0}, status=200)
        client = CrorisClient(test_config)
        result = import_casopis_rad([{"tip": 760, "godina": "2024"}], client=client)
        assert result == {"saved": 1, "skipped": 0}

    def test_baca_error_za_vise_od_100_zapisa(self, mock_client):
        import pytest
        with pytest.raises(ValueError, match="100"):
            import_casopis_rad([{}] * 101, client=mock_client)
```

- [ ] **Step 2: Pokreni i provjeri**

```bash
pytest tests/unit/endpoints/test_publikacije_crosbi.py -v
```

Očekivano: sve klase PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/endpoints/test_publikacije_crosbi.py
git commit -m "test: proširi test_publikacije_crosbi s preostalim funkcijama i import_casopis_rad"
```

---

## Task 8: Proširiti test_casopisi.py, test_dogadanja.py, test_znanstvenici.py

**Files:**
- Modify: `tests/unit/endpoints/test_casopisi.py`
- Modify: `tests/unit/endpoints/test_dogadanja.py`
- Modify: `tests/unit/endpoints/test_znanstvenici.py`

- [ ] **Step 1: Dodaj u test_casopisi.py**

Pročitaj `tests/unit/endpoints/test_casopisi.py` da vidiš postojeće importove, pa dopisati na kraj:

```python
from crosbi.endpoints.casopisi import get_casopisi_ustanove, get_casopis_publikacije
from crosbi.config import CASOPISI_BASE_URL


class TestGetCasopisiUstanove:
    def test_poziva_ispravan_url(self, mock_client, casopis_raw):
        mock_client.get_embedded.return_value = [casopis_raw]
        get_casopisi_ustanove(10, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CASOPISI_BASE_URL}/casopis/ustanova/10", "casopisi"
        )

    def test_vraca_listu_casopisa(self, mock_client, casopis_raw):
        from crosbi.models.casopis import Casopis
        mock_client.get_embedded.return_value = [casopis_raw]
        result = get_casopisi_ustanove(10, client=mock_client)
        assert isinstance(result[0], Casopis)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_casopisi_ustanove(10, client=mock_client) == []


class TestGetCasopisPublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get_embedded.return_value = []
        get_casopis_publikacije(100, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{CASOPISI_BASE_URL}/publikacija/casopis/100", "publikacije"
        )

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_casopis_publikacije(100, client=mock_client) == []
```

- [ ] **Step 2: Dodaj u test_dogadanja.py**

Dopisati na kraj:

```python
from crosbi.endpoints.dogadanja import get_dogadanja_ustanove, get_dogadanje_publikacije
from crosbi.config import DOGADANJA_BASE_URL


class TestGetDogadanjaUstanove:
    def test_poziva_ispravan_url(self, mock_client, dogadanje_raw):
        mock_client.get_embedded.return_value = [dogadanje_raw]
        get_dogadanja_ustanove(10, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{DOGADANJA_BASE_URL}/dogadanje/ustanova/10", "dogadanja"
        )

    def test_vraca_listu_dogadanja(self, mock_client, dogadanje_raw):
        from crosbi.models.dogadanje import Dogadanje
        mock_client.get_embedded.return_value = [dogadanje_raw]
        result = get_dogadanja_ustanove(10, client=mock_client)
        assert isinstance(result[0], Dogadanje)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_dogadanja_ustanove(10, client=mock_client) == []


class TestGetDogadanjePublikacije:
    def test_poziva_ispravan_url(self, mock_client):
        mock_client.get_embedded.return_value = []
        get_dogadanje_publikacije(100, client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{DOGADANJA_BASE_URL}/publikacija/dogadanje/100", "publikacije"
        )

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_dogadanje_publikacije(100, client=mock_client) == []
```

- [ ] **Step 3: Dodaj u test_znanstvenici.py**

Dopisati na kraj:

```python
from crosbi.endpoints.znanstvenici import get_svi_znanstvenici
from crosbi.config import ZNANSTVENICI_BASE_URL


class TestGetSviZnanstvenici:
    def test_poziva_ispravan_url(self, mock_client, znanstvenik_raw):
        mock_client.get_embedded.return_value = [znanstvenik_raw]
        get_svi_znanstvenici(client=mock_client)
        mock_client.get_embedded.assert_called_once_with(
            f"{ZNANSTVENICI_BASE_URL}/znanstvenik/collect", "znanstvenici"
        )

    def test_vraca_listu_znanstvenika(self, mock_client, znanstvenik_raw):
        from crosbi.models.znanstvenik import Znanstvenik
        mock_client.get_embedded.return_value = [znanstvenik_raw]
        result = get_svi_znanstvenici(client=mock_client)
        assert all(isinstance(z, Znanstvenik) for z in result)

    def test_prazan_odgovor(self, mock_client):
        mock_client.get_embedded.return_value = []
        assert get_svi_znanstvenici(client=mock_client) == []
```

- [ ] **Step 4: Provjeri koje konstante postoje u config.py**

```bash
grep -n "BASE_URL" crosbi/config.py
```

Ako `CASOPISI_BASE_URL`, `DOGADANJA_BASE_URL`, `ZNANSTVENICI_BASE_URL` ne postoje u `config.py`, pronađi ih u endpoint datotekama i dodaj u config.

- [ ] **Step 5: Pokreni i provjeri**

```bash
pytest tests/unit/endpoints/test_casopisi.py tests/unit/endpoints/test_dogadanja.py tests/unit/endpoints/test_znanstvenici.py -v
```

Očekivano: sve klase PASSED.

- [ ] **Step 6: Commit**

```bash
git add tests/unit/endpoints/test_casopisi.py tests/unit/endpoints/test_dogadanja.py tests/unit/endpoints/test_znanstvenici.py
git commit -m "test: proširi test_casopisi, test_dogadanja, test_znanstvenici s preostalim funkcijama"
```

---

## Task 9: test_oprema.py (modeli)

**Files:**
- Create: `tests/unit/models/test_oprema.py`

- [ ] **Step 1: Napiši testove**

```python
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
```

- [ ] **Step 2: Pokreni i provjeri**

```bash
pytest tests/unit/models/test_oprema.py -v
```

Očekivano: sve klase PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/models/test_oprema.py
git commit -m "test: dodaj unit testove za models/oprema"
```

---

## Task 10: test_publikacija_crosbi.py (modeli)

**Files:**
- Create: `tests/unit/models/test_publikacija_crosbi.py`

- [ ] **Step 1: Napiši testove**

```python
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
        assert len(p.povezave) == 1
        assert isinstance(p.povezave[0], Poveznica)
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
```

- [ ] **Step 2: Pokreni i provjeri**

```bash
pytest tests/unit/models/test_publikacija_crosbi.py -v
```

Očekivano: sve klase PASSED.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/models/test_publikacija_crosbi.py
git commit -m "test: dodaj unit testove za models/publikacija_crosbi"
```

---

## Task 11: Finalna provjera i push

- [ ] **Step 1: Pokreni sve testove**

```bash
pytest tests/unit/ -v --tb=short 2>&1 | tail -30
```

Očekivano: 0 grešaka, sve klase PASSED.

- [ ] **Step 2: Provjeri pokrivenost**

```bash
pytest tests/unit/ --cov=crosbi --cov-report=term-missing 2>&1 | grep -E "TOTAL|endpoints|models"
```

Očekivano: TOTAL pokrivenost > 90%.

- [ ] **Step 3: Push na GitHub**

```bash
git push origin master
```
