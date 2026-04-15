# CroRIS Explorer

Python klijent i interaktivna bilježnica za dohvat i vizualizaciju podataka iz [CroRIS REST API](https://wiki.srce.hr/spaces/CRORIS/pages/49283931/Programska+su%C4%8Delja+CroRIS-a) modula.

## Pokriveni API moduli

| Modul | Osnovna adresa | Pristup |
|---|---|---|
| **Projekti API** | `https://www.croris.hr/projekti-api` | Javno |
| **Ustanove API** | `https://www.croris.hr/ustanove-api` | Javno |
| **CROSBI API** | `https://www.croris.hr/crosbi-api` | Javno |
| **Oprema API** | `https://www.croris.hr/oprema-api` | Javno |
| **Časopisi API** | `https://www.croris.hr/casopisi-api` | Javno |
| **Događanja API** | `https://www.croris.hr/dogadanja-api` | Javno |
| **Znanstvenici API** | `https://www.croris.hr/znanstvenici-api` | Zahtijeva odobrenje MZO-a |

## Sadržaj

- [Preduvjeti](#preduvjeti)
- [Postavljanje okruženja](#postavljanje-okruženja)
- [Konfiguracija](#konfiguracija)
- [Struktura projekta](#struktura-projekta)
- [Marimo bilježnica](#marimo-bilježnica)
- [Docker](#docker)
- [Docker Compose — višekorisnički deployment s AD autentifikacijom](#docker-compose--višekorisnički-deployment-s-ad-autentifikacijom)
- [Programsko korištenje](#programsko-korištenje)
- [Korištenje sučelja naredbenog retka](#korištenje-sučelja-naredbenog-retka)
- [Testiranje](#testiranje)
- [Referenca API-ja](#referenca-api-ja)

---

## Preduvjeti

- Python 3.11 ili noviji

---

## Postavljanje okruženja

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate.bat     # Windows (Command Prompt)
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)

pip install -r requirements.txt
```

---

## Konfiguracija

Kopirati primjer i po potrebi popuniti vjerodajnice:

```bash
cp .env.example .env
```

```dotenv
CRORIS_USERNAME=          # opcionalno — bez vjerodajnica rade svi javni endpointi
CRORIS_PASSWORD=

# Neobavezno
CRORIS_PAGE_SIZE=50       # broj zapisa po stranici (5–100)
CRORIS_TIMEOUT=30         # istek HTTP zahtjeva u sekundama
```

Bilježnica radi bez vjerodajnica — svi korišteni endpointi su javni.

---

## Struktura projekta

```
pyCroRIS/
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
│   ├── conftest.py
│   ├── unit/                      # Jedinični testovi (pokrivenost: 98%)
│   └── integration/               # Integracijski testovi (zahtijevaju mrežni pristup)
├── notebook.py                    # Marimo interaktivna bilježnica
├── main.py                        # Ulazna točka sučelja naredbenog retka
├── Dockerfile                     # Kontejner za pokretanje bilježnice (jednokorisnički)
├── docker-compose.yml             # Višekorisnički deployment (Nginx + Authelia + Marimo)
├── docker/
│   ├── nginx/
│   │   └── nginx.conf             # Nginx reverse proxy + WebSocket + auth_request
│   └── authelia/
│       └── configuration.yml      # Authelia konfiguracija (LDAP/AD, sesije, pristup)
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .env.example                   # Predložak za CroRIS vjerodajnice
└── .env.docker.example            # Predložak za Authelia tajne ključeve
```

---

## Marimo bilježnica

Interaktivna bilježnica za prikaz podataka odabrane CroRIS ustanove. Radi bez vjerodajnica.

```bash
marimo run notebook.py    # web aplikacija (http://localhost:2718)
marimo edit notebook.py   # urednički način rada
```

### Sekcije bilježnice

| Sekcija | Izvor podataka | Sadržaj |
|---|---|---|
| **Info kartica** | Ustanove API | Naziv, adresa, OIB, kontakt, čelnik, nadređena ustanova |
| **Publikacije (CROSBI)** | CROSBI API | Broj publikacija, tablica s filtrom po godini, vizualizacije po vrsti i godini |
| **Projekti (CroRIS)** | Projekti API | Tablica s filtrom po godini početka, stupčasti grafikon po tipu, Gantt timeline |
| **Oprema (CroRIS)** | Oprema API | Popis opreme i usluga, horizontalni grafikon po kategoriji |
| **Znanstvenici** | CROSBI API | Pretraga profila po matičnom broju znanstvenika (MBZ), popis publikacija s detaljima |

### Predmemoriranje (cache)

Publikacije, projekti i oprema predmemoriraju se lokalno u direktorij `.cache/` (TTL: 24 h). Pri ponovnom pokretanju bilježnice podaci se učitavaju iz predmemorije bez čekanja. Svaka sekcija ima checkbox **Prisilno osvježi** za ručno osvježavanje.

### Napomena o brzini dohvata

Dohvat opreme zahtijeva zasebni HTTP zahtjev za svaku stavku (N×1 zahtjevi); npr. za ~78 stavki to traje oko 90 s. Projekti se dohvaćaju jednim sporim zahtjevom (~35 s). Oba dohvata prikazuju traku napretka i automatski se predmemoriraju — svaki sljedeći prikaz je trenutan.

---

## Docker

Bilježnica se može pokrenuti unutar Docker kontejnera bez lokalnog postavljanja okruženja.

### Izgradnja kontejnera

```bash
docker build -t crosbi-notebook .
```

### Pokretanje

**Run mode** — web aplikacija samo za čitanje (zadano):

```bash
docker run -p 2718:2718 crosbi-notebook
```

**Edit mode** — urednički način rada s mogućnošću izmjene koda:

```bash
docker run -p 2718:2718 -e MODE=edit crosbi-notebook
```

Bilježnica je dostupna na `http://localhost:2718`.

### Opcije montiranja

**S `.env` datotekom** (za opcionalne vjerodajnice):

```bash
docker run -p 2718:2718 --env-file .env crosbi-notebook
```

**S trajnim cacheom** (podaci ostaju i nakon zaustavljanja kontejnera):

```bash
docker run -p 2718:2718 -v $(pwd)/.cache:/app/.cache crosbi-notebook
```

## Docker Compose — višekorisnički deployment s AD autentifikacijom

Za produkcijski deployment koji omogućava višekorisničko korištenje bilježnice s autentifikacijom putem institucijskog Active Directory-ja. Arhitektura uključuje tri servisa: Nginx (reverse proxy + TLS), Authelia (autentifikacija prema AD/LDAP) i Marimo (bilježnica).

```
Internet → Nginx (443) → Authelia (provjera sesije) → Marimo (2718, interno)
```

#### Preduvjeti

- Docker Engine i Docker Compose
- TLS certifikat za domenu (`.pem` format)
- Service account u Active Directory-ju s pravima čitanja korisnika

#### Postavljanje

**1. Tajni ključevi za Authelia**

Kreirati `.env.docker` prema predlošku:

```bash
cp .env.docker.example .env.docker
```

Generirati nasumične vrijednosti za svaki ključ:

```bash
openssl rand -hex 32   # pokrenuti 3× — za SESSION_SECRET, STORAGE_ENCRYPTION_KEY i JWT_SECRET
```

Popuniti `.env.docker`:

```dotenv
AUTHELIA_SESSION_SECRET=<32+ znaka>
AUTHELIA_STORAGE_ENCRYPTION_KEY=<32+ znaka>
AUTHELIA_JWT_SECRET=<32+ znaka>
AUTHELIA_LDAP_PASSWORD=<lozinka service accounta>
```

**2. TLS certifikat**

Kopirati certifikat i privatni ključ u `docker/nginx/certs/`:

```bash
mkdir -p docker/nginx/certs
cp /putanja/do/cert.pem docker/nginx/certs/cert.pem
cp /putanja/do/key.pem  docker/nginx/certs/key.pem
```

Direktorij `docker/nginx/certs/` isključen je iz git repozitorija (`.gitignore`).

**3. Konfiguracija Nginx**

Urediti `docker/nginx/nginx.conf` — zamijeniti domenu na svim mjestima označenima s `# <-- zamijeniti`:

```nginx
server_name notebook.ustanova.hr;   # stvarna domena
```

**4. Konfiguracija Authelia**

Urediti `docker/authelia/configuration.yml` — prilagoditi svim mjestima označenima s `# <-- zamijeniti`:

| Parametar | Opis | Primjer |
|---|---|---|
| `address` | Adresa AD servera (LDAPS port 636) | `ldaps://ad.ustanova.hr:636` |
| `base_dn` | Root Distinguished Name domene | `DC=ustanova,DC=hr` |
| `additional_users_dn` | OU s korisnicima | `CN=Users` |
| `additional_groups_dn` | OU s grupama | `CN=Users` |
| `user` | DN service accounta | `CN=svc-croris,CN=Users,DC=ustanova,DC=hr` |
| `domain` (session) | Domena kolačića | `notebook.ustanova.hr` |
| `authelia_url` | Javna URL Authelia portala | `https://notebook.ustanova.hr/auth/` |

Ako AD koristi self-signed certifikat (npr. testno okruženje), postaviti `tls.skip_verify: true` — ali ne u produkciji.

**5. Pokretanje**

```bash
docker compose up -d
```

Bilježnica je dostupna na `https://notebook.ustanova.hr`. Korisnici se prijavljuju korisničkim imenom i lozinkom iz Active Directory-ja.

#### Upravljanje

```bash
docker compose logs -f authelia   # praćenje logova autentifikacije
docker compose logs -f marimo     # praćenje logova bilježnice
docker compose restart marimo     # restart bilježnice (bez prekida sesija)
docker compose down               # zaustavljanje svih servisa
```

#### Struktura konfiguracijskih datoteka

```
docker/
├── nginx/
│   ├── nginx.conf              # Nginx konfiguracija (reverse proxy + auth_request)
│   └── certs/                  # TLS certifikati (nije u gitu)
│       ├── cert.pem
│       └── key.pem
└── authelia/
    ├── configuration.yml       # Authelia konfiguracija (LDAP, sesije, pristup)
    └── db.sqlite3              # Authelia baza sesija (kreira se automatski)
docker-compose.yml
.env.docker                     # Tajni ključevi (nije u gitu)
.env.docker.example             # Predložak
```

---

## Programsko korištenje

```python
from crosbi.client import CrorisClient
from crosbi.endpoints import projekti, upisnik, publikacije_crosbi
from crosbi.export import to_json, to_csv

client = CrorisClient()   # čita .env; vjerodajnice nisu potrebne za javne endpointe

# Projekti po MBU kodu ustanove
ps = projekti.get_projekti_po_ustanovi("248", client=client)

# Sve aktivne ustanove (MZO upisnik)
sve = upisnik.get_sve_aktivne_ustanove(client=client)

# CROSBI publikacije osobe po matičnom broju znanstvenika
pub = publikacije_crosbi.get_publikacije_osobe_by_mbz("123456", client=client)

# Izvoz
to_csv(ps, "projekti.csv")
to_json(sve, "ustanove.json")
```

### Oprema po ustanovi (paralelni dohvat)

```python
from crosbi.endpoints.oprema_api import get_oprema_hrefs, fetch_oprema_by_href
from concurrent.futures import ThreadPoolExecutor, as_completed

hrefs = get_oprema_hrefs(ustanova_id=176)   # dohvati listu hrefs (brzo)

with ThreadPoolExecutor(max_workers=10) as pool:
    futures = {pool.submit(fetch_oprema_by_href, h): h for h in hrefs}
    oprema = [f.result() for f in as_completed(futures)]
```

### Višejezična polja

```python
projekt = projekti.get_projekt(12345, client=client)
print(projekt.get_title("hr"))   # naslov na hrvatskom
print(projekt.get_title("en"))   # naslov na engleskom
```

---

## Korištenje sučelja naredbenog retka

```bash
python main.py [--username K] [--password L] [-o datoteka] [-f json|csv] <modul> [mogućnosti]
```

### Projekti API

```bash
python main.py projekt -o projekti.csv -f csv        # svi projekti
python main.py projekt --id 12345                     # jedan projekt
python main.py projekt --mbu 248                      # projekti ustanove po MBU
```

### Ustanove API

```bash
python main.py upisnik sve -o ustanove.csv -f csv    # sve aktivne ustanove
python main.py upisnik znanstvene                     # znanstvene ustanove
python main.py upisnik visoka-ucilista                # visoka učilišta
python main.py upisnik jzi                            # javni znanstveni instituti
python main.py upisnik ppg                            # PPG područja
python main.py upisnik id 42                          # ustanova po ID-u
python main.py upisnik mbu 248                        # ustanova po MBU kodu
```

### CROSBI API

```bash
python main.py crosbi --id 123456                     # publikacija po ID-u
python main.py crosbi --mbz 123456                    # publikacije osobe (MBZ)
python main.py crosbi --osoba-id 9876                 # publikacije osobe (ID)
python main.py crosbi --projekt-id 12345              # publikacije projekta
```

### Oprema API

```bash
python main.py oprema -o oprema.csv -f csv            # sva oprema
python main.py oprema --id 456                        # jedna oprema
python main.py oprema --usluge -o usluge.csv -f csv   # sve usluge
```

### Časopisi i događanja

```bash
python main.py casopisi -o casopisi.csv -f csv
python main.py dogadanja -o dogadanja.csv -f csv
```

### MOZVAG

```bash
python main.py mozvag ustanove -o ustanove.csv -f csv
python main.py mozvag projekti --ustanova-id 123 --godina 2024
python main.py mozvag osoba --mbz 123456 --godina 2024
```

---

## Testiranje

```bash
pip install -r requirements-dev.txt

pytest tests/unit/                                         # sve jedinične provjere
pytest tests/unit/ --cov=crosbi --cov-report=term-missing  # s pokrivenošću (98%)
pytest -m "not integration"                                # preskoči integracijske
```

### Struktura testne zbirke

```
tests/
├── conftest.py
├── unit/
│   ├── models/
│   │   ├── test_common.py
│   │   ├── test_projekt.py
│   │   ├── test_znanstvenik.py
│   │   ├── test_ostali_modeli.py
│   │   ├── test_oprema.py
│   │   └── test_publikacija_crosbi.py
│   ├── endpoints/
│   │   ├── test_projekti.py
│   │   ├── test_casopisi.py
│   │   ├── test_dogadanja.py
│   │   ├── test_mozvag.py
│   │   ├── test_oprema.py
│   │   ├── test_publikacije_crosbi.py
│   │   ├── test_upisnik.py
│   │   ├── test_znanstvenici.py
│   │   ├── test_financijeri.py
│   │   ├── test_osobe.py
│   │   ├── test_publikacije.py
│   │   └── test_ustanove_projekti.py
│   ├── export/
│   │   ├── test_json_export.py
│   │   └── test_csv_export.py
│   ├── test_client.py
│   └── test_config.py
└── integration/
    └── test_client.py
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
## Autor
Vedran Vyroubal

## Licenca

Ovaj projekt objavljen je pod [MIT licencom](LICENSE).
Uvjeti korištenja CroRIS API-ja (SRCE / Ministarstvo znanosti i obrazovanja) primjenjuju se neovisno.
