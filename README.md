# CroRIS CROSBI Explorer

Python klijent i interaktivni notebook za dohvat i vizualizaciju podataka iz [CroRIS Projekti API-ja](https://www.croris.hr/projekti-api).

## Sadržaj

- [Instalacija](#instalacija)
- [Konfiguracija](#konfiguracija)
- [Struktura projekta](#struktura-projekta)
- [CLI korištenje](#cli-korištenje)
- [Marimo notebook](#marimo-notebook)
- [Programsko korištenje](#programsko-korištenje)
- [Export podataka](#export-podataka)

---

## Instalacija

Zahtijeva Python 3.11+.

```bash
# Kloniraj ili preuzmi projekt
cd /path/to/CROSBI

# Instaliraj u editable modu (preporučeno za razvoj)
pip install -e .

# Ili samo dependencije
pip install requests urllib3 python-dotenv marimo plotly pandas
```

---

## Konfiguracija

Kopiraj `.env.example` u `.env` i unesi kredencijale:

```bash
cp .env.example .env
```

```dotenv
CRORIS_USERNAME=your_username
CRORIS_PASSWORD=your_password

# Opcionalno
CRORIS_PAGE_SIZE=50    # broj rezultata po stranici (5–100)
CRORIS_TIMEOUT=30      # timeout HTTP zahtjeva u sekundama
```

Alternativno, kredencijale možeš proslijediti direktno kroz CLI (`--username`, `--password`) ili programski kroz `Config` objekt.

---

## Struktura projekta

```
CROSBI/
├── crosbi/                      # Python paket
│   ├── config.py                # Konfiguracija (Config dataclass, .env)
│   ├── client.py                # HTTP klijent (session, retry, paginacija, HAL+JSON)
│   ├── models/                  # Typed dataclass modeli
│   │   ├── common.py            # TranslatedText, Klasifikacija
│   │   ├── projekt.py           # Projekt
│   │   ├── osoba.py             # Osoba
│   │   ├── ustanova.py          # Ustanova
│   │   ├── publikacija.py       # Publikacija
│   │   ├── financijer.py        # Financijer, FinancijerProgram
│   │   └── mozvag.py            # MOZVAG modeli (agregirani podaci)
│   ├── endpoints/               # Funkcije po API resursu
│   │   ├── projekti.py
│   │   ├── osobe.py
│   │   ├── ustanove.py
│   │   ├── publikacije.py
│   │   ├── financijeri.py
│   │   └── mozvag.py
│   └── export/                  # Export u JSON i CSV
│       ├── json_export.py
│       └── csv_export.py
├── notebook.py                  # Marimo interaktivni notebook
├── main.py                      # CLI entry point
├── pyproject.toml
└── .env.example
```

---

## CLI korištenje

```bash
# Opći oblik
python main.py [--username U] [--password P] [--output datoteka] [--format json|csv] <resurs> [opcije]
```

### Projekti

```bash
# Dohvati sve projekte (paginacija automatska) — spremi u JSON
python main.py projekt --output projekti.json

# Dohvati sve projekte i spremi u CSV
python main.py projekt --output projekti.csv --format csv

# Dohvati jedan projekt po ID-u
python main.py projekt --id 12345

# Dohvati sve projekte ustanove po MBU kodu
python main.py projekt --mbu 0000000
```

### Osobe

```bash
# Dohvati osobu po internom ID-u
python main.py osoba --id 9876

# Dohvati osobu po OIB-u
python main.py osoba --oib 12345678901

# Dohvati sve osobe na projektu
python main.py osoba --projekt-id 12345 --output osobe.csv --format csv
```

### Ustanove

```bash
# Dohvati ustanovu po ID-u
python main.py ustanova --id 42

# Dohvati sve ustanove na projektu
python main.py ustanova --projekt-id 12345
```

### MOZVAG (agregirani podaci)

```bash
# Popis svih ustanova
python main.py mozvag ustanove --output ustanove.csv --format csv

# Popis svih financijera
python main.py mozvag financijeri

# Projekti ustanove za godinu
python main.py mozvag projekti --ustanova-id 123 --godina 2024 --output projekti_2024.csv --format csv

# Sažetak projekata istraživača po MBZ-u
python main.py mozvag osoba --mbz 123456 --godina 2024

# Sažetak projekata istraživača po OIB-u
python main.py mozvag osoba --oib 12345678901 --ustanova-id 123 --godina 2024
```

---

## Marimo notebook

Interaktivni notebook za vizualizaciju podataka u web pregledniku.

```bash
# Pokretanje kao web aplikacija (read-only)
marimo run notebook.py

# Pokretanje u interaktivnom editor modu
marimo edit notebook.py
```

Notebook se otvara na `http://localhost:2718`.

### Funkcionalnosti notebooka

| Sekcija | Opis |
|---|---|
| **Konfiguracija** | Unos korisničkog imena, lozinke i veličine stranice |
| **Odabir podataka** | Dropdown s 8 tipova upita |
| **Dinamički inputi** | Pojavljuju se ovisno o odabiru (ID, MBU, godina, MBZ...) |
| **Tablica rezultata** | Interaktivna tablica s filterima i sortiranjem |
| **Vizualizacije** | Plotly grafovi prilagođeni odabranom tipu podataka |
| **Download** | Preuzimanje rezultata kao CSV ili JSON |

#### Dostupni upiti i vizualizacije

| Upit | Vizualizacija |
|---|---|
| MOZVAG — popis ustanova | Bar chart ustanova po gradu |
| MOZVAG — projekti ustanove za godinu | Pie po vrsti projekta · Top 15 financijera · Gantt timeline |
| MOZVAG — sažetak projekata osobe | Tablica (broj zn. i ostalih projekata) |
| Detalji projekta po ID-u | Tablica |
| Projekti ustanove po MBU | Tablica |
| Osobe na projektu | Pie raspodjele uloga |
| Publikacije projekta | Bar po vrsti · Trend po godini |
| Financijeri projekta | Bar chart iznosa po financijeru |

---

## Programsko korištenje

```python
from crosbi.config import Config
from crosbi.client import CrorisClient
from crosbi.endpoints import projekti, osobe, mozvag
from crosbi.export import to_json, to_csv

# Inicijalizacija klijenta
cfg = Config(username="user", password="pass", page_size=100)
client = CrorisClient(cfg)

# Dohvat projekata ustanove (MOZVAG)
projekti_2024 = mozvag.get_projekti_ustanove(ustanova_id=123, godina=2024, client=client)
for p in projekti_2024:
    print(p.naziv, p.projekt_iznos, p.projekt_valuta)

# Dohvat svih projekata (automatska paginacija)
for projekt in projekti.list_projekti(client=client):
    print(projekt.get_title("hr"), projekt.pocetak, projekt.kraj)

# Dohvat osoba na projektu
osobe_lista = osobe.get_osobe_projekta(projekt_id=12345, client=client)
for o in osobe_lista:
    print(o.puno_ime, o.klasifikacija.naziv if o.klasifikacija else "—")

# Export
to_csv(projekti_2024, "projekti_2024.csv")
to_json(projekti_2024, "projekti_2024.json")
```

### Višejezični tekst

Polja kao `title`, `summary` i `keywords` dolaze u više jezika. Koristite helper metode:

```python
projekt = projekti.get_projekt(12345, client=client)
print(projekt.get_title("hr"))   # naziv na hrvatskom
print(projekt.get_title("en"))   # naziv na engleskom
```

---

## Export podataka

Svi modeli implementiraju `to_dict()` metodu pogodnu za export.

```python
from crosbi.export import to_json, to_csv

# Spremanje u JSON
to_json(lista_objekata, "output/rezultati.json")

# Spremanje u CSV
to_csv(lista_objekata, "output/rezultati.csv")
```

Export funkcije automatski kreiraju direktorij ako ne postoji.

---

## API referenca

- **Swagger UI:** https://www.croris.hr/projekti-api/swagger-ui/index.html
- **OpenAPI spec:** https://www.croris.hr/projekti-api/v3/api-docs
- **Wiki dokumentacija:** https://wiki.srce.hr/spaces/CRORIS/pages/97878205/Projekti+API
