# Ustanova Explorer Notebook — Design Spec

**Date:** 2026-04-13  
**File:** `ustanova_explorer.py` (Marimo notebook)

---

## Cilj

Novi Marimo notebook koji prikazuje sve javno dostupne podatke o odabranoj CroRIS ustanovi bez potrebe za autentikacijom. Korisnik odabere ustanovu s dropdown izbornika, a notebook automatski prikazuje informacijsku karticu i nudi gumbe za učitavanje CROSBI publikacija i projekata.

---

## Dostupnost endpointa (bez autentikacije)

| Endpoint | Status | Napomena |
|---|---|---|
| `ustanove-api/upisnik-ustanova/ustanova` | ✓ | 225 ustanova |
| `crosbi-api/ustanova/{id}` | ✓ | Vraća listu linkova na publikacije |
| `crosbi-api/publikacija/{id}` | ✓ | Pojedinih. publikacija |
| `projekti-api/projekt/ustanova/{mbu}` | ⚠️ | Nestabilan timeout za neke MBU-e |
| `ustanove-api/evidencija-ppg/podrucje` | ✓ | Referentni podaci |
| `mozvag/*` | ✗ | 401 — potrebna auth |
| `znanstvenici-api/*` | ✗ | 401 — potrebna auth |

---

## Arhitektura

### Faza 1 — Boot (bez interakcije korisnika)

- Pri pokretanju notebooka dohvati sve ustanove iz upisnika bez auth
- Napuni dropdown opcijama formata `"KRATICA — Puni naziv"`, sortirano abecedno
- Notebook je odmah funkcionalan bez auth ekrana

### Faza 2 — Odabir ustanove

- Korisnik odabere ustanovu iz dropdowna
- Automatski prikaže **info karticu** s:
  - Puni naziv (HR i EN)
  - Kratica, MBU
  - Adresa, kontakt (web, email, telefon)
  - Tip ustanove, vrsta, vlasništvo, županija
  - Nadređena ustanova (ako postoji)
- Odmah prikaže count: `"X CROSBI publikacija dostupno"` (broj linkova iz `crosbi-api/ustanova/{id}`, bez fetch sadržaja)
- Pokušaj fetch projekata po MBU (timeout=8s): prikaži count ili graceful poruku o grešci

### Faza 3 — Učitavanje po sekcijama

Dvije neovisne sekcije s `mo.ui.run_button`:

#### Sekcija: Publikacije
- Gumb "Učitaj publikacije (max 200)"
- Fetch prvih 200 linkova iz `_links.publikacije` u batchevima od 50 paralelnih poziva
- Progress: `mo.status.spinner`
- Vizualizacije:
  - Pie chart: distribucija po `vrsta` (autorska knjiga, rad u časopisu, poglavlje, itd.)
  - Bar chart: broj publikacija po `godina`
  - Pretraživiva tablica: naslov, vrsta, godina, autori, status

#### Sekcija: Projekti
- Gumb "Učitaj projekte"
- Fetch `projekti-api/projekt/ustanova/{mbu}`, timeout=8s
- Graceful error ako endpoint timeoutuje
- Vizualizacije (ako podaci dostupni):
  - Bar chart: projekti po `tipProjekta`
  - Gantt timeline: prvih 30 projekata po datumu početka/kraja
  - Tablica: naziv, šifra, tip, pocetak, kraj, total_cost

---

## Struktura Marimo ćelija

```
_imports
_load_ustanove          → dohvat upisnika pri boot-u
_ustanova_selector      → dropdown UI
_ustanova_info          → info kartica + CROSBI count + projekti count
_pub_section_header
_pub_loader             → run_button
_pub_data               → fetch logika (batch, max 200)
_pub_viz                → pie + bar chart
_pub_table              → mo.ui.dataframe
_proj_section_header
_proj_loader            → run_button
_proj_data              → fetch logika (timeout=8s)
_proj_viz               → bar + gantt
_proj_table             → mo.ui.dataframe
```

---

## Ograničenja i rubni slučajevi

- **Ustanova bez publikacija**: prikaži callout "Nema CROSBI publikacija za ovu ustanovu"
- **Projekti timeout**: prikaži callout "Endpoint projekata nije odgovorio u 8s. Pokušajte ponovo."
- **Prazna ustanova**: dropdown ne smije biti prazan (upisnik uvijek vraća podatke)
- **Batch fetch publikacija**: koristiti `concurrent.futures.ThreadPoolExecutor` s max 10 workera
- **CROSBI id**: ustanova u CROSBI koristi isti `id` kao u upisniku

---

## Što se NE uključuje

- MOZVAG, Wissenschenici (zahtijevaju auth)
- Casopisi, dogadanja, oprema (nisu po ustanovi)
- Download gumbi (CSV/JSON) — out of scope za ovu verziju
- Auth unos — namjerno izostavljen, notebook je čisto javni preglednik
