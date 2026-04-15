# notebook.py Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ispraviti bugove u `notebook.py`, dodati nedostajuće endpointe u dropdown, te dodati vizualizacije za module koji ih nemaju.

**Architecture:** Sve izmjene su unutar jedne datoteke — `notebook.py`. Svaka Marimo ćelija je izolirani Python scope; ovisnosti se prenose kroz povratne vrijednosti i parametre funkcija. Plan prati Marimo konvenciju: ćelija vraća ono što expose drugim ćelijama.

**Tech Stack:** Python 3.11+, Marimo 0.20.4, Pandas, Plotly Express, crosbi (interni paket)

---

## Datoteke koje se mijenjaju

- Modify: `notebook.py` — jedina datoteka; sve izmjene su u njoj

---

## FAZA 1: Bugfixevi

### Task 1: Popravi ćelije koje ne returnaju output (`_header`, `_mode_selector`, `_build_client`)

**Files:**
- Modify: `notebook.py:39-47`, `notebook.py:79-85`, `notebook.py:59-76`

**Kontekst:** Marimo prikazuje output ćelije samo ako je zadnji izraz returnana vrijednost. Ćelije `_header`, `_mode_selector` i `_build_client` pozivaju `mo.md()` / postavljaju `_status` ali ne returnaju — output se gubi.

- [ ] **Step 1: Popravi `_header` ćeliju**

Pronađi u `notebook.py` (oko linije 39):
```python
@app.cell
def _header(mo):
    mo.md("""
    # CroRIS Explorer
    ...
    """)
    return
```

Zamijeni s:
```python
@app.cell
def _header(mo):
    return mo.md("""
    # CroRIS Explorer

    Interaktivni pregled podataka iz svih [CroRIS REST API](https://wiki.srce.hr/spaces/CRORIS/pages/49283931/Programska+su%C4%8Delja+CroRIS-a) modula.

    ---
    """)
```

- [ ] **Step 2: Popravi `_mode_selector` ćeliju**

Pronađi (oko linije 79):
```python
@app.cell
def _mode_selector(mo):
    mo.md("""
    ---
    ## Odabir podataka
    """)
    return
```

Zamijeni s:
```python
@app.cell
def _mode_selector(mo):
    return mo.md("""
    ---
    ## Odabir podataka
    """)
```

- [ ] **Step 3: Popravi `_build_client` ćeliju — `_status` nije returnana**

Pronađi (oko linije 70-76):
```python
    _status = (
        mo.callout(mo.md("Autentikacija konfigurirana."), kind="success")
        if _u
        else mo.callout(mo.md("Nisu uneseni kredencijali — postavi u `.env` ili unesi iznad."), kind="warn")
    )
    _status
    return (client,)
```

Zamijeni s:
```python
    _status = (
        mo.callout(mo.md("Autentikacija konfigurirana."), kind="success")
        if _u
        else mo.callout(mo.md("Nisu uneseni kredencijali — postavi u `.env` ili unesi iznad."), kind="warn")
    )
    mo.output.replace(_status)
    return (client,)
```

> **Napomena:** `mo.output.replace()` eksplicitno prikazuje output čak i kad ćelija mora returnati `client`. Alternativa je `mo.vstack([_status])` kao zadnji izraz, ali tada `client` mora biti u `return` iskazu koji nije zadnji izraz — što je isti problem. `mo.output.replace()` je idiomatski Marimo obrazac za ovo.

- [ ] **Step 4: Ručno provjeri u `marimo edit notebook.py`**

Pokreni: `marimo edit notebook.py`

Očekivano: header, "Odabir podataka" naslov i status poruka su vidljivi u UI.

- [ ] **Step 5: Commit**

```bash
git add notebook.py
git commit -m "fix: popravi Marimo ćelije koje nisu returnale output"
```

---

### Task 2: Ukloni nekorištene importe iz `_fetch`

**Files:**
- Modify: `notebook.py:202-206`

**Kontekst:** `ustanove` i `publikacije` se importiraju ali nigdje ne koriste u `_fetch`. To nije crash, ali je zbunjujuće i može uzrokovati linter greške.

- [ ] **Step 1: Ukloni `ustanove` i `publikacije` iz importa**

Pronađi (oko linije 202):
```python
    from crosbi.endpoints import (
        mozvag, projekti, osobe, ustanove, financijeri,
        upisnik, publikacije_crosbi, oprema_api, casopisi,
        dogadanja, znanstvenici,
    )
```

Zamijeni s:
```python
    from crosbi.endpoints import (
        mozvag, projekti, osobe, financijeri,
        upisnik, publikacije_crosbi, oprema_api, casopisi,
        dogadanja, znanstvenici,
    )
```

- [ ] **Step 2: Commit**

```bash
git add notebook.py
git commit -m "fix: ukloni nekorištene importe ustanove i publikacije iz _fetch"
```

---

### Task 3: Popravi `_viz_ppg` — guard za stupac `sifra`

**Files:**
- Modify: `notebook.py` — ćelija `_viz_ppg` (oko linije 431)

**Kontekst:** `df.sort_values("sifra")` pada s `KeyError` ako `sifra` stupac ne postoji u DataFrame-u.

- [ ] **Step 1: Dodaj provjeru stupca**

Pronađi:
```python
@app.cell
def _viz_ppg(df, mo, mode, px):
    mo.stop(mode.value != "ppg_podrucja")
    if not df.empty:
        _fig = px.bar(df.sort_values("sifra"), x="sifra", y="naziv",
```

Zamijeni s:
```python
@app.cell
def _viz_ppg(df, mo, mode, px):
    mo.stop(mode.value != "ppg_podrucja")
    if not df.empty and "sifra" in df.columns and "naziv" in df.columns:
        _fig = px.bar(df.sort_values("sifra"), x="sifra", y="naziv",
```

- [ ] **Step 2: Commit**

```bash
git add notebook.py
git commit -m "fix: dodaj column guard u _viz_ppg za sifra i naziv"
```

---

### Task 4: Ispravi label `page_size_input`

**Files:**
- Modify: `notebook.py:54`

- [ ] **Step 1: Promijeni label**

Pronađi:
```python
    page_size_input = mo.ui.slider(start=5, stop=100, step=5, value=50, label="Stranica")
```

Zamijeni s:
```python
    page_size_input = mo.ui.slider(start=5, stop=100, step=5, value=50, label="Veličina stranice")
```

- [ ] **Step 2: Commit**

```bash
git add notebook.py
git commit -m "fix: ispravi label slidera za veličinu stranice"
```

---

## FAZA 2: Novi endpointi

### Task 5: Dodaj `mozvag_financijeri` i `mozvag_osoba_mbz` u dropdown i `_fetch`

**Files:**
- Modify: `notebook.py` — ćelije `_mode`, `_conditional_inputs`, `_fetch`

**Kontekst:**
- `mozvag.get_financijere()` vraća `list[FinancijerMozvag]` (polja: `financijer_id`, `naziv_hr`, `nadleznost`, `programi`)
- `mozvag.get_osoba_po_mbz(mbz, godina)` vraća jedan `OsobaMozvag` objekt (polja: `osoba_id`, `ime`, `prezime`, `maticni_broj`, `znanstveni_projekti`, `ostali_projekti`); nema `to_dict` pa treba koristiti `vars()`

- [ ] **Step 1: Dodaj opcije u dropdown (`_mode` ćelija)**

U `_mode` ćeliji, unutar `options` rječnika, dodaj na kraj sekcije `# Projekti API`:
```python
            "mozvag_financijeri": "Projekti — MOZVAG financijeri",
            "mozvag_osoba_mbz":   "Projekti — MOZVAG osoba po MBZ-u",
```

- [ ] **Step 2: Dodaj input za MBZ i godinu u `_conditional_inputs`**

`mbz_input` već postoji za `crosbi_osoba_mbz` i `znan_mbz`. Proširi uvjet:
```python
    mbz_input = (
        mo.ui.text(placeholder="npr. 123456", label="MBZ")
        if show in ("crosbi_osoba_mbz", "znan_mbz", "mozvag_osoba_mbz")
        else None
    )
```

`godina_input` već postoji za `mozvag_projekti`. Proširi uvjet:
```python
    godina_input = (
        mo.ui.number(start=2000, stop=2030, step=1, value=2024, label="Godina")
        if show in ("mozvag_projekti", "mozvag_osoba_mbz")
        else None
    )
```

- [ ] **Step 3: Dodaj grane u `_fetch`**

U `_fetch` ćeliji, unutar `try` bloka, dodaj nakon `elif s == "ppg_podrucja":` grane:
```python
            elif s == "mozvag_financijeri":
                result = mozvag.get_financijere(client=client)
            elif s == "mozvag_osoba_mbz":
                result = [mozvag.get_osoba_po_mbz(mbz_input.value, int(godina_input.value), client=client)]
```

- [ ] **Step 4: Provjeri u UI da novi modovi rade**

Pokreni: `marimo edit notebook.py`

Odaberi "Projekti — MOZVAG financijeri", klikni Dohvati podatke.
Očekivano: popis financijera s brojem zapisa > 0.

- [ ] **Step 5: Commit**

```bash
git add notebook.py
git commit -m "feat: dodaj mozvag_financijeri i mozvag_osoba_mbz endpointe"
```

---

### Task 6: Dodaj `casopis_detalj` i `publikacije_casopisa`

**Files:**
- Modify: `notebook.py` — ćelije `_mode`, `_conditional_inputs`, `_fetch`

**Kontekst:**
- `casopisi.get_casopis(casopis_id)` vraća jedan `Casopis` s `to_dict()` (polja: `id`, `naziv`, `drzava`, `issn`, `eissn`, `godina_pocetka`, `godina_zavrsetka`, `coden`, `udk`)
- `casopisi.get_publikacije_casopisa(casopis_id)` vraća `list[PublikacijaCasopis]` s `to_dict()` (polja: `cf_res_publ_id`, `hr_journal_id`, `citat`)

- [ ] **Step 1: Dodaj opcije u dropdown**

U sekciji `# Časopisi API`:
```python
            "casopis_detalj":      "Časopisi — detalji časopisa",
            "publikacije_casopisa":"Časopisi — publikacije časopisa",
```

- [ ] **Step 2: Dodaj `casopis_id_input` u `_conditional_inputs`**

Dodaj novu varijablu ispred `fetch_btn`:
```python
    casopis_id_input = (
        mo.ui.number(start=1, stop=9999999, step=1, value=1, label="ID časopisa")
        if show in ("casopis_detalj", "publikacije_casopisa")
        else None
    )
```

Dodaj `casopis_id_input` u `_inputs` listu i `return` iskaz:
```python
    _inputs = [x for x in [
        ustanova_id_input, godina_input, projekt_id_input,
        mbu_input, mbz_input, oib_input, pub_id_input,
        casopis_id_input, fetch_btn,
    ] if x is not None]
```

Return:
```python
    return (
        fetch_btn,
        casopis_id_input,
        godina_input,
        mbu_input,
        mbz_input,
        oib_input,
        projekt_id_input,
        pub_id_input,
        ustanova_id_input,
    )
```

- [ ] **Step 3: Dodaj `casopis_id_input` u parametre `_fetch` ćelije**

Dodaj `casopis_id_input` u listu parametara funkcije `_fetch`:
```python
def _fetch(
    casopis_id_input,
    client,
    fetch_btn,
    ...
):
```

- [ ] **Step 4: Dodaj grane u `_fetch`**

```python
            elif s == "casopis_detalj":
                result = [casopisi.get_casopis(int(casopis_id_input.value), client=client)]
            elif s == "publikacije_casopisa":
                result = casopisi.get_publikacije_casopisa(int(casopis_id_input.value), client=client)
```

- [ ] **Step 5: Commit**

```bash
git add notebook.py
git commit -m "feat: dodaj casopis_detalj i publikacije_casopisa endpointe"
```

---

### Task 7: Dodaj `dogadanje_detalj` i `ustanove_projekta`

**Files:**
- Modify: `notebook.py` — ćelije `_mode`, `_conditional_inputs`, `_fetch`

**Kontekst:**
- `dogadanja.get_dogadanje(dogadanje_id)` vraća jedan `Dogadanje` s `to_dict()`
- `ustanove.get_ustanove_projekta(projekt_id)` vraća `list[Ustanova]` s `to_dict()`; modul `ustanove` treba dodati natrag u import (ali samo u `_fetch`, ne globalno)

- [ ] **Step 1: Dodaj opcije u dropdown**

U sekciji `# Događanja API`:
```python
            "dogadanje_detalj": "Događanja — detalji događanja",
```

U sekciji `# Projekti API`:
```python
            "ustanove_projekta": "Projekti — ustanove na projektu",
```

- [ ] **Step 2: Dodaj `dogadanje_id_input` u `_conditional_inputs`**

```python
    dogadanje_id_input = (
        mo.ui.number(start=1, stop=9999999, step=1, value=1, label="ID događanja")
        if show == "dogadanje_detalj"
        else None
    )
```

Dodaj u `_inputs` listu i `return`.

- [ ] **Step 3: Dodaj `dogadanje_id_input` u parametre i grane `_fetch`**

Dodaj `dogadanje_id_input` u parametre `_fetch`.

Grane:
```python
            elif s == "dogadanje_detalj":
                result = [dogadanja.get_dogadanje(int(dogadanje_id_input.value), client=client)]
            elif s == "ustanove_projekta":
                from crosbi.endpoints import ustanove as ustanove_ep
                result = ustanove_ep.get_ustanove_projekta(int(projekt_id_input.value), client=client)
```

> **Napomena:** `projekt_id_input` već postoji za `projekt_id`, `osobe_projekta`, itd. — samo proširi uvjet u `_conditional_inputs`:
> ```python
>     projekt_id_input = (
>         mo.ui.number(start=1, stop=9999999, step=1, value=1, label="ID projekta")
>         if show in ("projekt_id", "osobe_projekta", "financijeri_proj", "publikacije_proj", "ustanove_projekta")
>         else None
>     )
> ```

- [ ] **Step 4: Commit**

```bash
git add notebook.py
git commit -m "feat: dodaj dogadanje_detalj i ustanove_projekta endpointe"
```

---

### Task 8: Dodaj `svi_znanstvenici`

**Files:**
- Modify: `notebook.py` — ćelije `_mode`, `_fetch`

**Kontekst:** `znanstvenici.get_svi_znanstvenici()` vraća `list[Znanstvenik]` s `to_dict()`. Endpoint je cachiran — može biti spor ali ne zahtijeva input parametre. Upozori korisnika u UI opisom.

- [ ] **Step 1: Dodaj opciju u dropdown**

U sekciji `# Znanstvenici API`:
```python
            "svi_znanstvenici": "Znanstvenici — svi (cached)",
```

- [ ] **Step 2: Dodaj granu u `_fetch`**

```python
            elif s == "svi_znanstvenici":
                result = wissenschenici.get_svi_znanstvenici(client=client)
```

> **Ispravak tipfeja:** koristi `znanstvenici`, ne `wissenschenici`.

```python
            elif s == "svi_znanstvenici":
                result = znanstvenici.get_svi_znanstvenici(client=client)
```

- [ ] **Step 3: Commit**

```bash
git add notebook.py
git commit -m "feat: dodaj svi_znanstvenici endpoint (cached)"
```

---

## FAZA 3: Vizualizacije

### Task 9: Vizualizacija za `financijeri_proj` — iznosi po financijeru

**Files:**
- Modify: `notebook.py` — dodaj novu `@app.cell` ćeliju `_viz_financijeri` nakon `_viz_osobe`

**Kontekst:** `Financijer.to_dict()` vraća: `naziv`, `tip`, `vrsta_izvora`, `poziv`, `amount`, `currency_code`, `program`. Vizualizacija: horizontalni bar chart iznosa po financijeru.

- [ ] **Step 1: Dodaj ćeliju `_viz_financijeri`**

Dodaj novu ćeliju nakon `_viz_osobe` ćelije:

```python
@app.cell
def _viz_financijeri(df, mo, mode, px):
    mo.stop(mode.value != "financijeri_proj")
    if "naziv" in df.columns and "amount" in df.columns:
        _df = df.dropna(subset=["amount"]).copy()
        if not _df.empty:
            _fig = px.bar(
                _df.sort_values("amount", ascending=True),
                x="amount", y="naziv", orientation="h",
                color="vrsta_izvora" if "vrsta_izvora" in _df.columns else None,
                title="Iznosi financiranja po financijeru",
                labels={"amount": "Iznos", "naziv": "Financijer"},
            )
            _fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=True)
            mo.plotly(_fig)
    return
```

- [ ] **Step 2: Commit**

```bash
git add notebook.py
git commit -m "feat: dodaj vizualizaciju iznosa za financijeri_proj"
```

---

### Task 10: Vizualizacija za `znan_akred` — distribucija po području i vrsti zaposlenja

**Files:**
- Modify: `notebook.py` — dodaj novu ćeliju `_viz_akreditacije` nakon `_viz_financijeri`

**Kontekst:** `OsobaAkreditacija.to_dict()` vraća: `id`, `puno_ime`, `oib`, `vrsta_zaposlenja`, `vrsta_radnog_odnosa`, `podrucje`, `polje`. Vizualizacije: pie chart po `vrsta_zaposlenja`, bar chart po `podrucje`.

- [ ] **Step 1: Dodaj ćeliju `_viz_akreditacije`**

```python
@app.cell
def _viz_akreditacije(df, mo, mode, px):
    mo.stop(mode.value != "znan_akred")
    charts = []
    if "vrsta_zaposlenja" in df.columns and not df.empty:
        _v = df["vrsta_zaposlenja"].value_counts().reset_index()
        _v.columns = ["vrsta", "broj"]
        charts.append(mo.plotly(
            px.pie(_v, names="vrsta", values="broj",
                   title="Akreditacije po vrsti zaposlenja", hole=0.4)
        ))
    if "podrucje" in df.columns and not df.empty:
        _p = df["podrucje"].dropna().value_counts().reset_index()
        _p.columns = ["podrucje", "broj"]
        charts.append(mo.plotly(
            px.bar(_p, x="podrucje", y="broj",
                   title="Akreditacije po znanstvenom području",
                   color="broj", color_continuous_scale="Teal")
        ))
    if charts:
        mo.vstack(charts)
    return
```

- [ ] **Step 2: Commit**

```bash
git add notebook.py
git commit -m "feat: dodaj vizualizaciju za znan_akred (zaposlenja i područja)"
```

---

### Task 11: Vizualizacija za `mozvag_financijeri` — financijeri po nadležnosti

**Files:**
- Modify: `notebook.py` — dodaj novu ćeliju `_viz_mozvag_financijeri` nakon `_viz_akreditacije`

**Kontekst:** `FinancijerMozvag` nema `to_dict()` — `_to_df` će koristiti `vars()`. Dostupna polja: `financijer_id`, `naziv_hr`, `naziv_en`, `nadleznost`, `programi` (lista objekata, ne string). Bar chart po `nadleznost`.

- [ ] **Step 1: Dodaj ćeliju `_viz_mozvag_financijeri`**

```python
@app.cell
def _viz_mozvag_financijeri(df, mo, mode, px):
    mo.stop(mode.value != "mozvag_financijeri")
    if "nadleznost" in df.columns and not df.empty:
        _n = df["nadleznost"].dropna().value_counts().reset_index()
        _n.columns = ["nadleznost", "broj"]
        _fig = px.bar(
            _n, x="broj", y="nadleznost", orientation="h",
            title="Financijeri po nadležnosti",
            color="broj", color_continuous_scale="Blues",
        )
        _fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
        mo.plotly(_fig)
    return
```

- [ ] **Step 2: Commit**

```bash
git add notebook.py
git commit -m "feat: dodaj vizualizaciju za mozvag_financijeri po nadleznosti"
```

---

## Self-Review

**Spec coverage:**
- Bugfix 1 — `_header`, `_mode_selector`, `_build_client` return ✓ (Task 1)
- Bugfix 2 — nekorišteni importi ✓ (Task 2)
- Bugfix 3 — `_viz_ppg` column guard ✓ (Task 3)
- Bugfix 4 — label slidera ✓ (Task 4)
- `mozvag_financijeri` ✓ (Task 5)
- `mozvag_osoba_mbz` ✓ (Task 5)
- `casopis_detalj` ✓ (Task 6)
- `publikacije_casopisa` ✓ (Task 6)
- `dogadanje_detalj` ✓ (Task 7)
- `ustanove_projekta` ✓ (Task 7)
- `svi_znanstvenici` ✓ (Task 8)
- Viz `financijeri_proj` ✓ (Task 9)
- Viz `znan_akred` ✓ (Task 10)
- Viz `mozvag_financijeri` ✓ (Task 11)

**Placeholder scan:** Nema TBD, nema "implement later". Sav kod je konkretan.

**Type consistency:**
- `mozvag.get_financijere()` → `list[FinancijerMozvag]` → `vars()` u `_to_df` (nema `to_dict`) ✓
- `mozvag.get_osoba_po_mbz()` → jedan `OsobaMozvag` → wrapped u `[...]` → `vars()` ✓
- `casopisi.get_casopis()` → `Casopis` s `to_dict()` ✓
- `casopisi.get_publikacije_casopisa()` → `list[PublikacijaCasopis]` s `to_dict()` ✓
- `dogadanja.get_dogadanje()` → `Dogadanje` s `to_dict()` ✓
- `ustanove.get_ustanove_projekta()` → `list[Ustanova]` s `to_dict()` ✓
- `znanstvenici.get_svi_znanstvenici()` → `list[Znanstvenik]` s `to_dict()` ✓

**Rubni slučaj — `_fetch` parametri:** Svaki novi `*_input` koji se doda u `_conditional_inputs` mora biti dodan i u parametre `_fetch` funkcije — plan to eksplicitno navodi u svakom Tasku.

**Rubni slučaj — `casopis_id_input` je `None` za ostale modove:** U `_fetch` granama za `casopis_detalj` i `publikacije_casopisa` koristi se `casopis_id_input.value` — ovo je sigurno jer Marimo garantira da je ta grana aktivna samo kad je `mode.value` odgovarajući string, a input je non-None samo za te iste modove. Kombinacija `mo.stop` logike i `_conditional_inputs` uvjeta to osigurava.
