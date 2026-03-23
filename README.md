# CroRIS Explorer

Python klijent i interaktivna bilježnica za dohvat i vizualizaciju podataka iz svih [CroRIS REST API](https://wiki.srce.hr/spaces/CRORIS/pages/49283931/Programska+su%C4%8Delja+CroRIS-a) modula.

## Pokriveni API moduli

| Modul | Osnovna adresa | Pristup |
|---|---|---|
| **Projekti API** | `https://www.croris.hr/projekti-api` | Javno (s autentikacijom) |
| **Ustanove API** | `https://www.croris.hr/ustanove-api` | Javno |
| **CROSBI API** | `https://www.croris.hr/crosbi-api` | Javno |
| **Oprema API** | `https://www.croris.hr/oprema-api` | Javno (s autentikacijom) |
| **Časopisi API** | `https://www.croris.hr/casopisi-api` | Javno |
| **Događanja API** | `https://www.croris.hr/dogadanja-api` | Javno |
| **Znanstvenici API** | `https://www.croris.hr/znanstvenici-api` | Zahtijeva odobrenje MZO-a |

## Sadržaj

- [Preduvjeti](#preduvjeti)
- [Postavljanje virtualnog okruženja](#postavljanje-virtualnog-okruženja)
- [Konfiguracija](#konfiguracija)
- [Struktura projekta](#struktura-projekta)
- [Korištenje sučelja naredbenog retka](#korištenje-sučelja-naredbenog-retka)
- [Marimo bilježnica](#marimo-bilježnica)
- [Programsko korištenje](#programsko-korištenje)
- [Izvoz podataka](#izvoz-podataka)
- [Testiranje](#testiranje)
- [Referenca API-ja](#referenca-api-ja)

---

## Preduvjeti

- Python 3.11 ili noviji

---

## Postavljanje virtualnog okruženja

Preporučuje se pokretanje projekta unutar Python virtualnog okruženja kako bi se izbjeglo zagađivanje globalnog okruženja i osigurao ponovljiv rad.

### Stvaranje virtualnog okruženja

```bash
python3 -m venv .venv
```

### Aktivacija virtualnog okruženja

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

Nakon uspješne aktivacije naziv virtualnog okruženja (`.venv`) pojavljuje se na početku redka naredbenog retka.

### Instalacija ovisnosti

```bash
# Preporučeno — instalacija iz requirements.txt
pip install -r requirements.txt

# Alternativno — instalacija paketa u razvojnom načinu rada
pip install -e .
```

### Deaktivacija virtualnog okruženja

```bash
deactivate
```

---

## Konfiguracija

Kopirati primjer datoteke s okolišnim varijablama i popuniti vjerodajnice:

```bash
cp .env.example .env
```

```dotenv
CRORIS_USERNAME=korisnicko_ime
CRORIS_PASSWORD=lozinka

# Neobavezno
CRORIS_PAGE_SIZE=50   # broj zapisa po stranici (5–100)
CRORIS_TIMEOUT=30     # istek HTTP zahtjeva u sekundama
```

Vjerodajnice je moguće proslijediti i izravno putem sučelja naredbenog retka (`--username`, `--password`) ili programski putem objekta `Config`.

---

## Struktura projekta

```
CROSBI/
├── crosbi/
│   ├── config.py                  # Config + konstante osnovnih adresa za sve module
│   ├── client.py                  # HTTP klijent (sjednica, ponovni pokušaji, straničenje, HAL+JSON)
│   ├── models/
│   │   ├── common.py              # TranslatedText, Klasifikacija
│   │   ├── projekt.py             # Projekt (projekti-api)
│   │   ├── osoba.py               # Osoba (projekti-api)
│   │   ├── ustanova.py            # Ustanova (projekti-api)
│   │   ├── publikacija.py         # Publikacija (projekti-api)
│   │   ├── financijer.py          # Financijer (projekti-api)
│   │   ├── mozvag.py              # MOZVAG modeli (projekti-api)
│   │   ├── ustanova_reg.py        # UstanovaReg, Podrucje, Polje, Grana (ustanove-api)
│   │   ├── publikacija_crosbi.py  # PublikacijaCrosbi i srodni modeli (crosbi-api)
│   │   ├── oprema.py              # Oprema, Usluga, UslugaCjenik (oprema-api)
│   │   ├── casopis.py             # Casopis, PublikacijaCasopis (casopisi-api)
│   │   ├── dogadanje.py           # Dogadanje, MjestoOdrzavanja (dogadanja-api)
│   │   └── znanstvenik.py         # Znanstvenik, Zvanje, RadniOdnos... (znanstvenici-api)
│   ├── endpoints/
│   │   ├── projekti.py            # projekti-api: projekti
│   │   ├── osobe.py               # projekti-api: osobe
│   │   ├── ustanove.py            # projekti-api: ustanove
│   │   ├── publikacije.py         # projekti-api: publikacije
│   │   ├── financijeri.py         # projekti-api: financijeri
│   │   ├── mozvag.py              # projekti-api: MOZVAG
│   │   ├── upisnik.py             # ustanove-api: MZO upisnik, PPG, CroRIS ustanove
│   │   ├── publikacije_crosbi.py  # crosbi-api: CROSBI publikacije (+ uvoz)
│   │   ├── oprema_api.py          # oprema-api: oprema, usluge, cjenik, datoteke
│   │   ├── casopisi.py            # casopisi-api: časopisi
│   │   ├── dogadanja.py           # dogadanja-api: događanja
│   │   └── znanstvenici.py        # znanstvenici-api: znanstvenici, akreditacije
│   └── export/
│       ├── json_export.py
│       └── csv_export.py
├── tests/
│   ├── conftest.py                # Zajednički učici
│   └── unit/                      # Jedinični testovi
├── notebook.py                    # Marimo interaktivna bilježnica
├── main.py                        # Ulazna točka sučelja naredbenog retka
├── requirements.txt               # Popis ovisnosti (pokretanje)
├── requirements-dev.txt           # Popis ovisnosti (razvoj i testiranje)
├── pyproject.toml
└── .env.example
```

---

## Korištenje sučelja naredbenog retka

```bash
python main.py [--username K] [--password L] [-o datoteka] [-f json|csv] <modul> [mogućnosti]
```

### Projekti API

```bash
python main.py projekt --output projekti.csv -f csv     # svi projekti
python main.py projekt --id 12345                        # jedan projekt
python main.py projekt --mbu 0000000                     # projekti ustanove
python main.py osoba --projekt-id 12345                  # osobe na projektu
python main.py ustanova --projekt-id 12345               # ustanove na projektu
```

### MOZVAG (agregirani podaci)

```bash
python main.py mozvag ustanove -o ustanove.csv -f csv
python main.py mozvag projekti --ustanova-id 123 --godina 2024
python main.py mozvag osoba --mbz 123456 --godina 2024
```

### Ustanove API

```bash
python main.py upisnik sve -o ustanove.csv -f csv        # sve aktivne ustanove
python main.py upisnik znanstvene                         # znanstvene ustanove
python main.py upisnik visoka-ucilista                    # visoka učilišta
python main.py upisnik jzi                                # javni znanstveni instituti
python main.py upisnik ppg                                # PPG područja
python main.py upisnik id 42                              # ustanova po internom identifikatoru
python main.py upisnik mbu 0000000                        # ustanova po MBU kodu
```

### CROSBI API

```bash
python main.py crosbi --id 123456                         # publikacija po identifikatoru
python main.py crosbi --mbz 123456                        # publikacije osobe (MBZ)
python main.py crosbi --osoba-id 9876                     # publikacije osobe (ID)
python main.py crosbi --projekt-id 12345                  # publikacije projekta
```

### Oprema API

```bash
python main.py oprema -o oprema.csv -f csv                # sva oprema
python main.py oprema --id 456                            # jedna oprema
python main.py oprema --usluge -o usluge.csv -f csv       # sve usluge
```

### Časopisi API

```bash
python main.py casopisi -o casopisi.csv -f csv
python main.py casopisi --id 789
```

### Događanja API

```bash
python main.py dogadanja -o dogadanja.csv -f csv
python main.py dogadanja --id 101
```

### Znanstvenici API

```bash
python main.py znanstvenici --oib 12345678901
python main.py znanstvenici --mbz 123456
python main.py znanstvenici --akreditacije-org-id 21 -o akred.csv -f csv
```

---

## Marimo bilježnica

```bash
marimo run notebook.py    # mrežna aplikacija (http://localhost:2718)
marimo edit notebook.py   # interaktivni uredničku način rada
```

### Dostupni upiti u bilježnici

| Kategorija | Upiti | Vizualizacije |
|---|---|---|
| **Projekti** | MOZVAG ustanove, MOZVAG projekti, projekti po MBU, detalji projekta, osobe/financijeri/publikacije projekta | Stupčasti po gradu, kružni po vrsti, top 15 financijera, vremenski prikaz (Gantt), kružni raspored uloga |
| **Ustanove** | Sve aktivne, znanstvene, visoka učilišta, JZI, PPG područja | Stupčasti po gradu, stupčasti PPG područja |
| **CROSBI** | Publikacije osobe (MBZ), publikacija po identifikatoru | Kružni po vrsti |
| **Oprema** | Popis opreme, popis usluga | Stupčasti po kategoriji |
| **Časopisi** | Popis časopisa | Stupčasti po zemlji izdavanja |
| **Događanja** | Popis događanja | Stupčasti po godini |
| **Znanstvenici** | Pretraga po OIB-u, MBZ-u, akreditacije organizacijske jedinice | Tablica |

Sve kombinacije podržavaju preuzimanje rezultata u obliku CSV-a ili JSON-a.

---

## Programsko korištenje

```python
from crosbi.config import Config
from crosbi.client import CrorisClient
from crosbi.endpoints import projekti, upisnik, publikacije_crosbi, znanstvenici
from crosbi.export import to_json, to_csv

client = CrorisClient(Config(username="korisnik", password="lozinka"))

# Projekti po MBU kodu ustanove
ps = projekti.get_projekti_po_ustanovi("0000000", client=client)

# Sve znanstvene ustanove (MZO upisnik)
zust = upisnik.get_znanstvene_ustanove(client=client)

# CROSBI publikacije osobe po matičnom broju znanstvenika
pub = publikacije_crosbi.get_publikacije_osobe_by_mbz("123456", client=client)

# Profil znanstvenika po OIB-u
z = znanstvenici.get_znanstvenik_by_oib("12345678901", client=client)
print(z.puno_ime, z.orcid, z.max_zvanje)

# PPG klasifikacija
podrucja = upisnik.get_sva_podrucja(client=client)

# Izvoz
to_csv(ps, "projekti.csv")
to_json(zust, "ustanove.json")
```

### Višejezična polja

Polja poput `title`, `summary` i `keywords` dostupna su na više jezika. Za dohvat teksta koristiti pomoćne metode:

```python
projekt = projekti.get_projekt(12345, client=client)
print(projekt.get_title("hr"))   # naslov na hrvatskom jeziku
print(projekt.get_title("en"))   # naslov na engleskom jeziku
```

### Uvoz publikacija (CROSBI API)

```python
from crosbi.endpoints.publikacije_crosbi import import_casopis_rad

status = import_casopis_rad([
    {
        "tip": 760,
        "godina": "2024",
        "status": 965,
        "suradnja_medjunarodna": "DA",
        "autor_string": "Horvat, Ivan; Kovač, Ana",
        "doi": "10.1234/example.2024",
        "ml": [{"jezik": "en", "trans": "O", "naslov": "Example title"}],
    }
], client=client)
```

---

## Izvoz podataka

Svi modeli implementiraju metodu `to_dict()` koja je prilagođena izvozu.

```python
from crosbi.export import to_json, to_csv

to_json(lista_objekata, "izlaz/rezultati.json")
to_csv(lista_objekata, "izlaz/rezultati.csv")
```

Izvozne funkcije automatski stvaraju odredišni direktorij ako ne postoji.

---

## Testiranje

Projekt sadrži jediničnu testnu zbirku koja pokriva HTTP klijent, konfiguracijske postavke, modele podataka i izvozne module.

### Instalacija razvojnih ovisnosti

```bash
pip install -r requirements-dev.txt
```

### Pokretanje testova

```bash
# Sve jedinične provjere
pytest tests/unit/

# S prikazom pokrivenosti izvornog koda
pytest tests/unit/ --cov=crosbi --cov-report=term-missing

# HTML izvješće o pokrivenosti (otvara se u pregledniku)
pytest tests/unit/ --cov=crosbi --cov-report=html
# → htmlcov/index.html

# Samo određeni modul
pytest tests/unit/models/ -v
pytest tests/unit/test_client.py -v
```

### Preskakanje integracijskih testova

Integracijski testovi zahtijevaju mrežni pristup CroRIS poslužitelju. Tijekom razvoja moguće ih je preskočiti:

```bash
pytest -m "not integration"
```

### Struktura testne zbirke

```
tests/
├── conftest.py                  # Zajednički učici (fixtures) za sve testove
└── unit/
    ├── models/
    │   ├── test_common.py       # TranslatedText, Klasifikacija, get_text()
    │   ├── test_projekt.py      # Model Projekt
    │   ├── test_znanstvenik.py  # Model Znanstvenik i srodni modeli
    │   └── test_ostali_modeli.py # Osoba, Ustanova, Financijer, Casopis, Dogadanje...
    ├── endpoints/
    │   └── test_projekti.py     # Endpointovi projekata
    ├── export/
    │   ├── test_json_export.py  # DataclassEncoder, to_json(), from_json()
    │   └── test_csv_export.py   # to_csv(), HasToDict protokol
    ├── test_client.py           # CrorisClient: sjednica, get(), paginate()...
    └── test_config.py           # Config: zadane vrijednosti, okolišne varijable
```

---

## Referenca API-ja

| Modul | Swagger UI | OpenAPI specifikacija |
|---|---|---|
| Projekti | `/projekti-api/swagger-ui/index.html` | `/projekti-api/v3/api-docs` |
| Ustanove | `/ustanove-api/api-docs.html` | `/ustanove-api/v3/api-docs` |
| CROSBI | `/crosbi-api/swagger-ui/index.html` | `/crosbi-api/v3/api-docs` |
| Oprema | `/oprema-api/swagger-ui/index.html` | `/oprema-api/v3/api-docs` |
| Časopisi | `/casopisi-api/swagger-ui/index.html` | `/casopisi-api/v3/api-docs` |
| Događanja | `/dogadanja-api/swagger-ui/index.html` | `/dogadanja-api/v3/api-docs` |
| Znanstvenici | `/znanstvenici-api/api-docs.html` | `/znanstvenici-api/v3/api-docs` |

Osnovna adresa za sve URL-ove: `https://www.croris.hr`

**Wiki dokumentacija:** https://wiki.srce.hr/spaces/CRORIS/pages/49283931/Programska+su%C4%8Delja+CroRIS-a

---

## Licenca

Ovaj projekt objavljen je pod [MIT licencom](LICENSE).
Uvjeti korištenja CroRIS API-ja (SRCE / Ministarstvo znanosti i obrazovanja) primjenjuju se neovisno.
