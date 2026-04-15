# Ustanova Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `ustanova_explorer.py` — a Marimo notebook that lets users browse CroRIS institution data (publications, projects) without authentication.

**Architecture:** Single Marimo notebook file using the existing `crosbi` package models. Public endpoints are called directly via `requests` — no auth. CROSBI publications fetched in batches of 10 via `ThreadPoolExecutor`. Projects fetched with an 8-second timeout and graceful error handling.

**Tech Stack:** Python 3.11, Marimo, Plotly Express, Pandas, requests, concurrent.futures

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `ustanova_explorer.py` | **Create** | Complete notebook — all cells |

No existing files are modified. The notebook imports from the existing `crosbi` package (models + config constants) but calls HTTP directly — no client auth needed.

---

### Task 1: Notebook skeleton + imports

**Files:**
- Create: `ustanova_explorer.py`

- [ ] **Step 1: Create the file with header and imports cell**

```python
"""
Ustanova Explorer — pregled javno dostupnih CroRIS podataka po ustanovi.

Dohvaća podatke bez autentikacije:
  - Upisnik ustanova (MZO)
  - CROSBI publikacije po ustanovi
  - Projekti po MBU (uz timeout)

Pokretanje:
    marimo run ustanova_explorer.py
    marimo edit ustanova_explorer.py
"""

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="wide", app_title="CroRIS Ustanova Explorer")


@app.cell
def _imports():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))

    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed

    HEADERS = {"Accept": "application/hal+json"}
    USTANOVE_BASE = "https://www.croris.hr/ustanove-api"
    CROSBI_BASE = "https://www.croris.hr/crosbi-api"
    PROJEKTI_BASE = "https://www.croris.hr/projekti-api"

    return mo, pd, px, requests, ThreadPoolExecutor, as_completed, HEADERS, USTANOVE_BASE, CROSBI_BASE, PROJEKTI_BASE


if __name__ == "__main__":
    app.run()
```

- [ ] **Step 2: Verify the file runs**

```bash
cd /Users/vedran/Projects/VUKA/pyCroRIS
conda run -n marimo python -c "import ast; ast.parse(open('ustanova_explorer.py').read()); print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add ustanova_explorer.py
git commit -m "feat: dodaj ustanova_explorer notebook skeleton"
```

---

### Task 2: Učitavanje ustanova pri boot-u i dropdown

**Files:**
- Modify: `ustanova_explorer.py`

- [ ] **Step 1: Dodaj ćeliju za dohvat svih ustanova**

Dodaj nakon `_imports` ćelije:

```python
@app.cell
def _load_ustanove(mo, requests, HEADERS, USTANOVE_BASE):
    """Dohvati sve aktivne ustanove iz upisnika pri pokretanju (bez auth)."""
    _r = requests.get(
        f"{USTANOVE_BASE}/upisnik-ustanova/ustanova",
        headers=HEADERS,
        timeout=20,
    )
    _r.raise_for_status()
    _raw = _r.json().get("_embedded", {}).get("ustanove", [])

    # Sortiraj po punom nazivu, izgradi options dict za dropdown
    _sorted = sorted(_raw, key=lambda u: u.get("puniNaziv", ""))
    ustanove_map = {
        u["id"]: u for u in _sorted
    }
    dropdown_options = {
        u["id"]: f"{u.get('kratica', '?')} — {u.get('puniNaziv', 'Nepoznato')}"
        for u in _sorted
    }
    return ustanove_map, dropdown_options
```

- [ ] **Step 2: Dodaj header i dropdown ćeliju**

```python
@app.cell
def _header(mo):
    return mo.md("""
    # CroRIS Ustanova Explorer

    Pregled javno dostupnih podataka o CroRIS ustanovama — bez prijave.

    ---
    """)


@app.cell
def _selector(mo, dropdown_options):
    ustanova_dropdown = mo.ui.dropdown(
        options=dropdown_options,
        label="Odaberi ustanovu",
    )
    ustanova_dropdown
    return (ustanova_dropdown,)
```

- [ ] **Step 3: Verify syntax**

```bash
conda run -n marimo python -c "import ast; ast.parse(open('ustanova_explorer.py').read()); print('OK')"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add ustanova_explorer.py
git commit -m "feat: dodaj ucitavanje ustanova i dropdown selector"
```

---

### Task 3: Info kartica ustanove

**Files:**
- Modify: `ustanova_explorer.py`

- [ ] **Step 1: Dodaj ćeliju za info karticu**

Dodaj nakon `_selector`:

```python
@app.cell
def _ustanova_info(mo, ustanova_dropdown, ustanove_map):
    mo.stop(ustanova_dropdown.value is None, mo.md("*Odaberi ustanovu iz izbornika iznad.*"))

    u = ustanove_map[ustanova_dropdown.value]

    adresa = u.get("adresa", {}) or {}
    kontakt = u.get("kontakt", {}) or {}
    nad = u.get("nadUstanova")
    tip_list = u.get("tipUstanove", [])
    vrsta = u.get("vrstaUstanove", {}) or {}

    _tip_str = ", ".join(t.get("naziv", "") for t in tip_list) if tip_list else "—"
    _nad_str = nad["naziv"] if nad else "—"
    _adr_str = f"{adresa.get('ulicaBr', '')}, {adresa.get('postanskiBroj', '')} {adresa.get('mjesto', '')}".strip(", ")
    _web = kontakt.get("web", "")
    _web_link = f"[{_web}](https://{_web})" if _web else "—"

    mo.vstack([
        mo.md(f"## {u.get('puniNaziv', '—')}"),
        mo.md(f"*{u.get('puniNazivEn', '')}*") if u.get("puniNazivEn") else mo.md(""),
        mo.hstack([
            mo.stat(label="Kratica", value=u.get("kratica", "—")),
            mo.stat(label="MBU", value=u.get("mbu", "—")),
            mo.stat(label="Županija", value=u.get("zupanija", "—")),
            mo.stat(label="Vlasništvo", value=u.get("tipVlasnistva", "—")),
        ], gap=2),
        mo.md(f"""
| Polje | Vrijednost |
|---|---|
| Vrsta | {vrsta.get("naziv", "—")} |
| Tip | {_tip_str} |
| Adresa | {_adr_str} |
| Web | {_web_link} |
| E-mail | {kontakt.get("email", "—")} |
| Telefon | {kontakt.get("telefon", "—")} |
| Čelnik | {u.get("celnik", "—")} |
| Nadređena ustanova | {_nad_str} |
"""),
    ])
```

- [ ] **Step 2: Verify syntax**

```bash
conda run -n marimo python -c "import ast; ast.parse(open('ustanova_explorer.py').read()); print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add ustanova_explorer.py
git commit -m "feat: dodaj info karticu ustanove"
```

---

### Task 4: CROSBI count + projekti count

**Files:**
- Modify: `ustanova_explorer.py`

- [ ] **Step 1: Dodaj ćeliju za dohvat countova**

Dodaj nakon `_ustanova_info`:

```python
@app.cell
def _counts(mo, ustanova_dropdown, requests, HEADERS, CROSBI_BASE, PROJEKTI_BASE, ustanove_map):
    mo.stop(ustanova_dropdown.value is None)

    croris_id = ustanova_dropdown.value
    u = ustanove_map[croris_id]
    mbu = u.get("mbu", "")

    # CROSBI count — dohvati listu linkova (brzo, bez fetch sadržaja)
    pub_count = 0
    pub_error = None
    try:
        _r = requests.get(
            f"{CROSBI_BASE}/ustanova/{croris_id}",
            headers=HEADERS,
            timeout=15,
        )
        if _r.status_code == 200:
            pub_count = len(_r.json().get("_links", {}).get("publikacije", []))
        elif _r.status_code == 404:
            pub_count = 0
        else:
            pub_error = f"CROSBI API greška: HTTP {_r.status_code}"
    except Exception as _e:
        pub_error = f"CROSBI timeout: {_e}"

    # Projekti count — pokušaj s timeoutom 8s
    proj_count = None
    proj_error = None
    proj_raw = []
    try:
        _r2 = requests.get(
            f"{PROJEKTI_BASE}/projekt/ustanova/{mbu}",
            headers=HEADERS,
            timeout=8,
        )
        if _r2.status_code == 200:
            proj_raw = _r2.json().get("_embedded", {}).get("projekti", [])
            proj_count = len(proj_raw)
        else:
            proj_error = f"Projekti API greška: HTTP {_r2.status_code}"
    except Exception as _e:
        proj_error = "Endpoint projekata nije odgovorio u 8s."

    _pub_stat = (
        mo.stat(label="CROSBI publikacije", value=str(pub_count))
        if pub_error is None
        else mo.callout(mo.md(f"**CROSBI:** {pub_error}"), kind="warn")
    )
    _proj_stat = (
        mo.stat(label="Projekti", value=str(proj_count))
        if proj_error is None
        else mo.callout(mo.md(f"**Projekti:** {proj_error}"), kind="warn")
    )

    mo.vstack([
        mo.md("---\n### Pregled dostupnih podataka"),
        mo.hstack([_pub_stat, _proj_stat], gap=3),
    ])

    return pub_count, pub_error, proj_raw, proj_error
```

- [ ] **Step 2: Verify syntax**

```bash
conda run -n marimo python -c "import ast; ast.parse(open('ustanova_explorer.py').read()); print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add ustanova_explorer.py
git commit -m "feat: dodaj CROSBI i projekti count prikaz"
```

---

### Task 5: Sekcija publikacija — fetch + vizualizacije + tablica

**Files:**
- Modify: `ustanova_explorer.py`

- [ ] **Step 1: Dodaj ćeliju za dohvat publikacija (batch)**

Dodaj nakon `_counts`:

```python
@app.cell
def _pub_section(mo, pub_count, pub_error):
    mo.stop(pub_error is not None or pub_count == 0,
            mo.callout(mo.md("Nema CROSBI publikacija za ovu ustanovu."), kind="neutral"))
    mo.md("---\n## Publikacije (CROSBI)")
    return


@app.cell
def _pub_loader(mo):
    pub_btn = mo.ui.run_button(label=f"Učitaj publikacije (max 200)")
    pub_btn
    return (pub_btn,)


@app.cell
def _pub_fetch(
    mo, pub_btn, ustanova_dropdown, pub_count,
    requests, HEADERS, CROSBI_BASE,
    ThreadPoolExecutor, as_completed,
):
    mo.stop(not pub_btn.value,
            mo.callout(mo.md("Pritisni **Učitaj publikacije** za dohvat podataka."), kind="neutral"))
    mo.stop(ustanova_dropdown.value is None)

    croris_id = ustanova_dropdown.value
    pub_rows = []
    _fetch_error = None

    def _fetch_one(url):
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()

    try:
        with mo.status.spinner(title="Dohvaćam popis publikacija..."):
            _r = requests.get(
                f"{CROSBI_BASE}/ustanova/{croris_id}",
                headers=HEADERS,
                timeout=15,
            )
            _r.raise_for_status()
            _links = _r.json().get("_links", {}).get("publikacije", [])
            _urls = [lnk["href"] for lnk in _links[:200]]

        with mo.status.spinner(title=f"Dohvaćam {len(_urls)} publikacija..."):
            with ThreadPoolExecutor(max_workers=10) as _pool:
                _futures = {_pool.submit(_fetch_one, u): u for u in _urls}
                for _fut in as_completed(_futures):
                    try:
                        _data = _fut.result()
                        pub_rows.append({
                            "crosbi_id": _data.get("crosbiId"),
                            "naslov": _data.get("naslov", ""),
                            "autori": _data.get("autori", ""),
                            "vrsta": _data.get("vrsta", ""),
                            "tip": _data.get("tip", ""),
                            "godina": _data.get("godina"),
                            "casopis": _data.get("casopis", ""),
                            "doi": _data.get("doi", ""),
                            "status": _data.get("status", ""),
                            "izdavac": _data.get("izdavac", ""),
                        })
                    except Exception:
                        pass
    except Exception as _e:
        _fetch_error = str(_e)

    if _fetch_error:
        mo.callout(mo.md(f"**Greška:** {_fetch_error}"), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(pub_rows)}** publikacija (od {pub_count} ukupno)."), kind="success")

    return (pub_rows,)
```

- [ ] **Step 2: Dodaj vizualizacije i tablicu publikacija**

```python
@app.cell
def _pub_to_df(mo, pub_rows, pd):
    mo.stop(not pub_rows)
    pub_df = pd.DataFrame(pub_rows)
    return (pub_df,)


@app.cell
def _pub_viz(mo, pub_df, px):
    mo.stop(pub_df is None or pub_df.empty)

    # Pie: po vrsti
    _v = pub_df["vrsta"].value_counts().reset_index()
    _v.columns = ["vrsta", "broj"]
    _pie = px.pie(_v, names="vrsta", values="broj",
                  title="Publikacije po vrsti", hole=0.4)

    # Bar: po godini
    _g = (
        pub_df.dropna(subset=["godina"])
        .assign(godina=lambda df: pd.to_numeric(df["godina"], errors="coerce"))
        .dropna(subset=["godina"])
        .groupby("godina")
        .size()
        .reset_index(name="broj")
        .sort_values("godina")
    )
    _bar = px.bar(_g, x="godina", y="broj",
                  title="Publikacije po godini",
                  color="broj", color_continuous_scale="Blues")
    _bar.update_layout(showlegend=False)

    mo.vstack([mo.plotly(_pie), mo.plotly(_bar)])


@app.cell
def _pub_table(mo, pub_df):
    mo.stop(pub_df is None or pub_df.empty)
    mo.md("### Tablica publikacija")
    mo.ui.dataframe(pub_df[["naslov", "autori", "vrsta", "godina", "casopis", "doi", "status"]])
```

- [ ] **Step 3: Verify syntax**

```bash
conda run -n marimo python -c "import ast; ast.parse(open('ustanova_explorer.py').read()); print('OK')"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add ustanova_explorer.py
git commit -m "feat: dodaj sekciju publikacija s fetch, vizualizacijama i tablicom"
```

---

### Task 6: Sekcija projekata — vizualizacije + tablica

**Files:**
- Modify: `ustanova_explorer.py`

- [ ] **Step 1: Dodaj sekciju projekata**

Dodaj na kraj (prije `if __name__ == "__main__"`):

```python
@app.cell
def _proj_section(mo, proj_error, proj_raw):
    _no_data = proj_error is not None or not proj_raw
    mo.stop(
        _no_data,
        mo.vstack([
            mo.md("---\n## Projekti"),
            mo.callout(
                mo.md(proj_error or "Nema projekata za ovu ustanovu."),
                kind="warn" if proj_error else "neutral",
            ),
        ]) if _no_data else None,
    )
    mo.md("---\n## Projekti")
    return


@app.cell
def _proj_to_df(mo, proj_raw, pd):
    mo.stop(not proj_raw)

    _rows = []
    for _p in proj_raw:
        _tip = _p.get("tipProjekta", {}) or {}
        _titles = _p.get("title", [])
        _naziv_hr = next((t["text"] for t in _titles if t.get("language") == "hr"), "")
        _naziv_en = next((t["text"] for t in _titles if t.get("language") == "en"), "")
        _rows.append({
            "id": _p.get("id"),
            "sifra": _p.get("hrSifraProjekta", ""),
            "akronim": _p.get("acro", ""),
            "naziv_hr": _naziv_hr,
            "naziv_en": _naziv_en,
            "tip": _tip.get("naziv", ""),
            "pocetak": _p.get("pocetak"),
            "kraj": _p.get("kraj"),
            "total_cost": _p.get("totalCost"),
            "currency": _p.get("currencyCode", ""),
        })
    proj_df = pd.DataFrame(_rows)
    return (proj_df,)


@app.cell
def _proj_viz(mo, proj_df, pd, px):
    mo.stop(proj_df is None or proj_df.empty)

    # Bar: po tipu projekta
    _t = proj_df["tip"].replace("", "Nepoznato").value_counts().reset_index()
    _t.columns = ["tip", "broj"]
    _bar = px.bar(_t, x="tip", y="broj",
                  title="Projekti po tipu",
                  color="broj", color_continuous_scale="Teal")
    _bar.update_layout(xaxis_tickangle=-30, showlegend=False)

    # Gantt timeline — prvih 30 s datumima
    _tl = proj_df.dropna(subset=["pocetak", "kraj"]).copy()
    _tl["pocetak"] = pd.to_datetime(_tl["pocetak"], errors="coerce")
    _tl["kraj"] = pd.to_datetime(_tl["kraj"], errors="coerce")
    _tl = _tl.dropna(subset=["pocetak", "kraj"]).head(30)

    charts = [mo.plotly(_bar)]
    if not _tl.empty:
        _tl["label"] = _tl["akronim"].where(_tl["akronim"] != "", _tl["sifra"])
        _gantt = px.timeline(
            _tl, x_start="pocetak", x_end="kraj", y="label",
            color="tip", title=f"Timeline projekata (prvih {len(_tl)})",
        )
        _gantt.update_yaxes(autorange="reversed")
        _gantt.update_layout(height=max(350, len(_tl) * 22))
        charts.append(mo.plotly(_gantt))

    mo.vstack(charts)


@app.cell
def _proj_table(mo, proj_df):
    mo.stop(proj_df is None or proj_df.empty)
    mo.md("### Tablica projekata")
    mo.ui.dataframe(
        proj_df[["sifra", "akronim", "naziv_hr", "tip", "pocetak", "kraj", "total_cost", "currency"]]
    )
```

- [ ] **Step 2: Verify syntax**

```bash
conda run -n marimo python -c "import ast; ast.parse(open('ustanova_explorer.py').read()); print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add ustanova_explorer.py
git commit -m "feat: dodaj sekciju projekata s vizualizacijama i tablicom"
```

---

### Task 7: Provjera - pokreni notebook i provjeri funkcionalnost

**Files:**
- No changes

- [ ] **Step 1: Pokreni marimo notebook**

```bash
cd /Users/vedran/Projects/VUKA/pyCroRIS
conda run -n marimo marimo run ustanova_explorer.py
```

Provjeri u browseru:
1. Dropdown se popunjava s ustanovama
2. Odaberi "IOR — INSTITUT ZA OCEANOGRAFIJU I RIBARSTVO"
3. Info kartica prikazuje podatke (kratica, MBU, adresa, kontakt)
4. CROSBI count prikazuje broj publikacija (~4171)
5. Projekti count prikazuje broj ili poruku o timeoutu
6. Klikni "Učitaj publikacije" → spinner → pie + bar chart + tablica
7. Sekcija projekata prikazuje bar chart + gantt (ako su projekti dohvaćeni)

- [ ] **Step 2: Final commit**

```bash
git add ustanova_explorer.py
git commit -m "feat: ustanova_explorer notebook kompletiran"
```
