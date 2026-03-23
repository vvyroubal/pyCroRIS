# CroRIS Explorer

Python klijent i interaktivni notebook za dohvat i vizualizaciju podataka iz svih [CroRIS REST API](https://wiki.srce.hr/spaces/CRORIS/pages/49283931/Programska+su%C4%8Delja+CroRIS-a) modula.

## Pokriveni API moduli

| Modul | Base URL | Pristup |
|---|---|---|
| **Projekti API** | `https://www.croris.hr/projekti-api` | Javno (s auth) |
| **Ustanove API** | `https://www.croris.hr/ustanove-api` | Javno |
| **CROSBI API** | `https://www.croris.hr/crosbi-api` | Javno |
| **Oprema API** | `https://www.croris.hr/oprema-api` | Javno (s auth) |
| **Časopisi API** | `https://www.croris.hr/casopisi-api` | Javno |
| **Događanja API** | `https://www.croris.hr/dogadanja-api` | Javno |
| **Znanstvenici API** | `https://www.croris.hr/znanstvenici-api` | Zahtijeva odobrenje MZO-a |

## Sadržaj

- [Instalacija](#instalacija)
- [Konfiguracija](#konfiguracija)
- [Struktura projekta](#struktura-projekta)
- [CLI korištenje](#cli-korištenje)
- [Marimo notebook](#marimo-notebook)
- [Programsko korištenje](#programsko-korištenje)
- [Export podataka](#export-podataka)
- [API referenca](#api-referenca)

---

## Instalacija

Zahtijeva Python 3.11+.

```bash
pip install -e .
```

---

## Konfiguracija

```bash
cp .env.example .env
```

```dotenv
CRORIS_USERNAME=your_username
CRORIS_PASSWORD=your_password

# Opcionalno
CRORIS_PAGE_SIZE=50
CRORIS_TIMEOUT=30
```

Kredencijale možeš proslijediti i direktno kroz CLI (`--username`, `--password`) ili programski kroz `Config` objekt.

---

## Struktura projekta

```
CROSBI/
├── crosbi/
│   ├── config.py                  # Config + base URL konstante za sve module
│   ├── client.py                  # HTTP klijent (session, retry, paginacija, HAL+JSON)
│   ├── models/
│   │   ├── common.py              # TranslatedText, Klasifikacija
│   │   ├── projekt.py             # Projekt (projekti-api)
│   │   ├── osoba.py               # Osoba (projekti-api)
│   │   ├── ustanova.py            # Ustanova (projekti-api)
│   │   ├── publikacija.py         # Publikacija (projekti-api)
│   │   ├── financijer.py          # Financijer (projekti-api)
│   │   ├── mozvag.py              # MOZVAG modeli (projekti-api)
│   │   ├── ustanova_reg.py        # UstanovaReg, Podrucje, Polje, Grana (ustanove-api)
│   │   ├── publikacija_crosbi.py  # PublikacijaCrosbi + srodni (crosbi-api)
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
│   │   ├── publikacije_crosbi.py  # crosbi-api: CROSBI publikacije (+ import)
│   │   ├── oprema_api.py          # oprema-api: oprema, usluge, cjenik, datoteke
│   │   ├── casopisi.py            # casopisi-api: časopisi
│   │   ├── dogadanja.py           # dogadanja-api: događanja
│   │   └── znanstvenici.py        # znanstvenici-api: znanstvenici, akreditacije
│   └── export/
│       ├── json_export.py
│       └── csv_export.py
├── notebook.py                    # Marimo interaktivni notebook
├── main.py                        # CLI entry point
├── pyproject.toml
└── .env.example
```

---

## CLI korištenje

```bash
python main.py [--username U] [--password P] [-o datoteka] [-f json|csv] <modul> [opcije]
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
python main.py upisnik sve -o ustanove.csv -f csv        # sve aktivne
python main.py upisnik znanstvene                         # znanstvene ustanove
python main.py upisnik visoka-ucilista                    # visoka učilišta
python main.py upisnik jzi                                # javni znan. instituti
python main.py upisnik ppg                                # PPG područja
python main.py upisnik id 42                              # po internom ID-u
python main.py upisnik mbu 0000000                        # po MBU kodu
```

### CROSBI API

```bash
python main.py crosbi --id 123456                         # publikacija po ID-u
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

## Marimo notebook

```bash
marimo run notebook.py    # web app (http://localhost:2718)
marimo edit notebook.py   # interaktivni editor
```

### Dostupni upiti u notebooku

| Kategorija | Upiti | Vizualizacije |
|---|---|---|
| **Projekti** | MOZVAG ustanove, MOZVAG projekti, projekti po MBU, detalji projekta, osobe/financijeri/publikacije projekta | Bar po gradu, pie po vrsti, top financijeri, Gantt timeline, pie uloga |
| **Ustanove** | Sve aktivne, znanstvene, visoka učilišta, JZI, PPG područja | Bar po gradu, bar PPG područja |
| **CROSBI** | Publikacije osobe (MBZ), publikacija po ID-u | Pie po vrsti |
| **Oprema** | Popis opreme, popis usluga | Bar po kategoriji |
| **Časopisi** | Popis časopisa | Bar po zemlji izdavanja |
| **Događanja** | Popis događanja | Bar po godini |
| **Znanstvenici** | Pretraga po OIB-u, MBZ-u, akreditacije org. jedinice | Tablica |

Sve kombinacije podržavaju **download CSV/JSON** gumbima.

---

## Programsko korištenje

```python
from crosbi.config import Config
from crosbi.client import CrorisClient
from crosbi.endpoints import projekti, upisnik, publikacije_crosbi, znanstvenici
from crosbi.export import to_json, to_csv

client = CrorisClient(Config(username="u", password="p"))

# Projekti po MBU
ps = projekti.get_projekti_po_ustanovi("0000000", client=client)

# Sve znanstvene ustanove (MZO upisnik)
zust = upisnik.get_znanstvene_ustanove(client=client)

# CROSBI publikacije osobe po MBZ-u
pub = publikacije_crosbi.get_publikacije_osobe_by_mbz("123456", client=client)

# Znanstvenik po OIB-u
z = znanstvenici.get_znanstvenik_by_oib("12345678901", client=client)
print(z.puno_ime, z.orcid, z.max_zvanje)

# PPG klasifikacija
podrucja = upisnik.get_sva_podrucja(client=client)

# Export
to_csv(ps, "projekti.csv")
to_json(zust, "ustanove.json")
```

### Import publikacija (CROSBI API)

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

## Export podataka

```python
from crosbi.export import to_json, to_csv

to_json(lista_objekata, "output/rezultati.json")
to_csv(lista_objekata, "output/rezultati.csv")
```

Export automatski kreira direktorij ako ne postoji.

---

## API referenca

| Modul | Swagger UI | OpenAPI spec |
|---|---|---|
| Projekti | `/projekti-api/swagger-ui/index.html` | `/projekti-api/v3/api-docs` |
| Ustanove | `/ustanove-api/api-docs.html` | `/ustanove-api/v3/api-docs` |
| CROSBI | `/crosbi-api/swagger-ui/index.html` | `/crosbi-api/v3/api-docs` |
| Oprema | `/oprema-api/swagger-ui/index.html` | `/oprema-api/v3/api-docs` |
| Časopisi | `/casopisi-api/swagger-ui/index.html` | `/casopisi-api/v3/api-docs` |
| Događanja | `/dogadanja-api/swagger-ui/index.html` | `/dogadanja-api/v3/api-docs` |
| Znanstvenici | `/znanstvenici-api/api-docs.html` | `/znanstvenici-api/v3/api-docs` |

Base za sve URL-ove: `https://www.croris.hr`

**Wiki dokumentacija:** https://wiki.srce.hr/spaces/CRORIS/pages/49283931/Programska+su%C4%8Delja+CroRIS-a
