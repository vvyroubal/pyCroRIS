"""
CroRIS Ustanova Explorer — interaktivni Marimo notebook.

Prikazuje sve dostupne podatke o odabranoj CroRIS ustanovi:
  - Javni podaci (bez autentikacije): info kartica, CROSBI publikacije, projekti
  - Autenticirani podaci (s kredencijalima): MOZVAG projekti, akreditacije

Pokretanje:
    marimo run notebook.py
    marimo edit notebook.py
"""

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="wide", app_title="CroRIS Ustanova Explorer")


# ---------------------------------------------------------------------------
# IMPORTS + KLIJENT
# ---------------------------------------------------------------------------

@app.cell
def _imports():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from crosbi.client import CrorisClient
    from crosbi.config import Config, CROSBI_BASE_URL
    from crosbi.endpoints.upisnik import get_sve_aktivne_ustanove
    from crosbi.endpoints.projekti import get_projekti_po_ustanovi
    from crosbi.endpoints.mozvag import get_projekti_ustanove as get_mozvag_projekti
    from crosbi.endpoints.znanstvenici import get_akreditacije_ustanove

    return (
        mo, pd, px, ThreadPoolExecutor, as_completed,
        CrorisClient, Config, CROSBI_BASE_URL,
        get_sve_aktivne_ustanove, get_projekti_po_ustanovi,
        get_mozvag_projekti, get_akreditacije_ustanove,
    )


# ---------------------------------------------------------------------------
# BOOT — dohvat ustanova (bez auth)
# ---------------------------------------------------------------------------

@app.cell
def _load_ustanove(CrorisClient, get_sve_aktivne_ustanove):
    _client = CrorisClient()
    _all = get_sve_aktivne_ustanove(client=_client)
    _sorted = sorted(_all, key=lambda u: u.puni_naziv or "")

    ustanove_map = {str(u.id): u for u in _sorted}
    # Marimo dropdown: {label_za_prikaz: vrijednost_value}
    dropdown_options = {
        f"{u.kratica or '?'} — {u.puni_naziv or 'Nepoznato'}": str(u.id)
        for u in _sorted
    }
    return ustanove_map, dropdown_options


# ---------------------------------------------------------------------------
# HEADER + SELEKTOR
# ---------------------------------------------------------------------------

@app.cell
def _header(mo):
    mo.md("""
    # CroRIS Ustanova Explorer

    Odaberi ustanovu za prikaz svih dostupnih podataka.

    ---
    """)
    return


@app.cell
def _selector(mo, dropdown_options):
    ustanova_dropdown = mo.ui.dropdown(
        options=dropdown_options,
        label="Odaberi ustanovu",
    )
    ustanova_dropdown
    return (ustanova_dropdown,)


# ---------------------------------------------------------------------------
# INFO KARTICA USTANOVE
# ---------------------------------------------------------------------------

@app.cell
def _ustanova_info(mo, ustanova_dropdown, ustanove_map):
    mo.stop(
        ustanova_dropdown.value is None,
        mo.md("*Odaberi ustanovu iz izbornika iznad.*"),
    )
    _u   = ustanove_map[ustanova_dropdown.value]
    _adr = _u.adresa
    _kon = _u.kontakt
    _nad = _u.nad_ustanova
    _vrst = _u.vrsta_ustanove
    _tip  = ", ".join(t.naziv or "" for t in (_u.tip_ustanova or [])) or "—"
    _adr_str = ", ".join(filter(None, [
        _adr.ulica_br if _adr else None,
        _adr.postanskI_broj if _adr else None,
        _adr.mjesto if _adr else None,
    ])) or "—"
    _web  = (_kon.web or "") if _kon else ""
    _web_md = f"[{_web}]({_web})" if _web else "—"

    mo.vstack([
        mo.md(f"## {_u.puni_naziv or '—'}"),
        mo.md(f"*{_u.puni_naziv_en}*") if _u.puni_naziv_en else mo.md(""),
        mo.hstack([
            mo.stat(label="Kratica",    value=_u.kratica or "—"),
            mo.stat(label="MBU",        value=_u.mbu or "—"),
            mo.stat(label="Županija",   value=_u.zupanija or "—"),
            mo.stat(label="Vlasništvo", value=_u.tip_vlasnistva or "—"),
        ], gap=2),
        mo.md(f"""
| Polje | Vrijednost |
|---|---|
| Vrsta | {_vrst.naziv if _vrst else "—"} |
| Tip | {_tip} |
| Adresa | {_adr_str} |
| Web | {_web_md} |
| E-mail | {(_kon.email or "—") if _kon else "—"} |
| Telefon | {(_kon.telefon or "—") if _kon else "—"} |
| Čelnik | {_u.celnik or "—"} |
| Nadređena ustanova | {_nad.naziv if _nad else "—"} |
"""),
    ])
    return


# ---------------------------------------------------------------------------
# COUNTS — CROSBI i projekti (bez auth)
# ---------------------------------------------------------------------------

@app.cell
def _counts(mo, ustanova_dropdown, ustanove_map, CrorisClient, CROSBI_BASE_URL, get_projekti_po_ustanovi):
    mo.stop(ustanova_dropdown.value is None)

    _uid = ustanova_dropdown.value
    _u   = ustanove_map[_uid]
    _mbu = _u.mbu or ""

    _client = CrorisClient()

    # CROSBI count — dohvati raw HAL+JSON za listu linkova publikacija
    pub_count = 0
    pub_error = None
    try:
        _crosbi_data = _client.get(f"{CROSBI_BASE_URL}/ustanova/{_uid}")
        pub_count = len(_crosbi_data.get("_links", {}).get("publikacije", []))
    except Exception as _e:
        _status = getattr(getattr(_e, "response", None), "status_code", None)
        if _status == 404:
            pub_count = 0
        else:
            pub_error = f"Greška: {_e}"

    # Projekti count
    proj_list  = []
    proj_count = None
    proj_error = None
    try:
        proj_list  = get_projekti_po_ustanovi(_mbu, client=_client)
        proj_count = len(proj_list)
    except Exception:
        proj_error = f"Endpoint nije odgovorio na vrijeme."

    mo.vstack([
        mo.md("---\n### Javni podaci"),
        mo.hstack([
            mo.stat(label="CROSBI publikacije", value=str(pub_count))
                if pub_error is None
                else mo.callout(mo.md(f"**CROSBI greška:** {pub_error}"), kind="warn"),
            mo.stat(label="Projekti (CroRIS)", value=str(proj_count) if proj_count is not None else "—")
                if proj_error is None
                else mo.callout(mo.md(f"**Projekti greška:** {proj_error}"), kind="warn"),
        ], gap=3),
    ])
    return pub_count, pub_error, proj_list, proj_error


# ---------------------------------------------------------------------------
# SEKCIJA: PUBLIKACIJE (CROSBI)
# ---------------------------------------------------------------------------

@app.cell
def _pub_header(mo, pub_count, pub_error):
    mo.stop(pub_error is not None or pub_count == 0,
        mo.callout(mo.md("Nema CROSBI publikacija za ovu ustanovu."), kind="neutral"))
    mo.md("---\n## Publikacije (CROSBI)")
    return


@app.cell
def _pub_loader(mo, pub_count):
    pub_btn = mo.ui.run_button(label=f"Učitaj publikacije (max 200 od {pub_count})")
    pub_btn
    return (pub_btn,)


@app.cell
def _pub_fetch(mo, pub_btn, ustanova_dropdown, pub_count, CrorisClient, CROSBI_BASE_URL, ThreadPoolExecutor, as_completed):
    mo.stop(not pub_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj publikacije**."), kind="neutral"))
    mo.stop(ustanova_dropdown.value is None)

    _uid    = ustanova_dropdown.value
    _client = CrorisClient()
    pub_rows = []
    _pub_err = None

    def _fetch_one(_url):
        return _client.get(_url)

    try:
        with mo.status.spinner(title="Dohvaćam popis publikacija..."):
            _crosbi_data = _client.get(f"{CROSBI_BASE_URL}/ustanova/{_uid}")
            _urls = [
                lnk["href"]
                for lnk in _crosbi_data.get("_links", {}).get("publikacije", [])[:200]
            ]

        with mo.status.spinner(title=f"Dohvaćam {len(_urls)} publikacija..."):
            with ThreadPoolExecutor(max_workers=10) as _pool:
                for _fut in as_completed({_pool.submit(_fetch_one, u): u for u in _urls}):
                    try:
                        _d = _fut.result()
                        pub_rows.append({
                            "crosbi_id": _d.get("crosbiId"),
                            "naslov":    _d.get("naslov", ""),
                            "autori":    _d.get("autori", ""),
                            "vrsta":     _d.get("vrsta", ""),
                            "tip":       _d.get("tip", ""),
                            "godina":    _d.get("godina"),
                            "casopis":   _d.get("casopis", ""),
                            "doi":       _d.get("doi", ""),
                            "status":    _d.get("status", ""),
                            "izdavac":   _d.get("izdavac", ""),
                        })
                    except Exception:
                        pass
    except Exception as _e:
        _pub_err = str(_e)

    if _pub_err:
        mo.callout(mo.md(f"**Greška:** {_pub_err}"), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(pub_rows)}** / {pub_count} publikacija."), kind="success")
    return (pub_rows,)


@app.cell
def _pub_df(mo, pub_rows, pd):
    mo.stop(not pub_rows)
    pub_df = pd.DataFrame(pub_rows)
    return (pub_df,)


@app.cell
def _pub_viz(mo, pub_df, pd, px):
    mo.stop(pub_df is None or pub_df.empty)

    _v = pub_df["vrsta"].replace("", "Nepoznato").value_counts().reset_index()
    _v.columns = ["vrsta", "broj"]
    _pie = px.pie(_v, names="vrsta", values="broj", title="Publikacije po vrsti", hole=0.4)

    _g = (pub_df.dropna(subset=["godina"])
          .assign(godina=lambda _df: pd.to_numeric(_df["godina"], errors="coerce"))
          .dropna(subset=["godina"])
          .groupby("godina").size().reset_index(name="broj")
          .sort_values("godina"))
    _bar = px.bar(_g, x="godina", y="broj", title="Publikacije po godini",
                  color="broj", color_continuous_scale="Blues")
    _bar.update_layout(showlegend=False)

    mo.vstack([mo.as_html(_pie), mo.as_html(_bar)])
    return


@app.cell
def _pub_table(mo, pub_df):
    mo.stop(pub_df is None or pub_df.empty)
    mo.md("### Tablica publikacija")
    mo.ui.dataframe(pub_df[["naslov", "autori", "vrsta", "godina", "casopis", "doi", "status"]])
    return


# ---------------------------------------------------------------------------
# SEKCIJA: PROJEKTI (CroRIS, bez auth)
# ---------------------------------------------------------------------------

@app.cell
def _proj_header(mo, proj_error, proj_list):
    _empty = proj_error is not None or not proj_list
    mo.vstack([
        mo.md("---\n## Projekti (CroRIS)"),
        mo.callout(mo.md(proj_error or "Nema projekata za ovu ustanovu."),
                   kind="warn" if proj_error else "neutral"),
    ]) if _empty else mo.md("---\n## Projekti (CroRIS)")
    mo.stop(_empty)
    return


@app.cell
def _proj_df(mo, proj_list, pd):
    mo.stop(not proj_list)
    _rows = [p.to_dict() for p in proj_list]
    proj_df = pd.DataFrame(_rows)
    # Preimenuj stupce za konzistentnost s vizualizacijama
    proj_df = proj_df.rename(columns={
        "hr_sifra_projekta": "sifra",
        "acro": "akronim",
        "title_hr": "naziv_hr",
        "title_en": "naziv_en",
        "tip_projekta": "tip",
        "total_cost": "total_cost",
        "currency_code": "currency",
    })
    return (proj_df,)


@app.cell
def _proj_viz(mo, proj_df, pd, px):
    mo.stop(proj_df is None or proj_df.empty)

    _t = proj_df["tip"].replace("", "Nepoznato").fillna("Nepoznato").value_counts().reset_index()
    _t.columns = ["tip", "broj"]
    _bar = px.bar(_t, x="tip", y="broj", title="Projekti po tipu",
                  color="broj", color_continuous_scale="Teal")
    _bar.update_layout(xaxis_tickangle=-30, showlegend=False)

    _tl = proj_df.dropna(subset=["pocetak", "kraj"]).copy()
    _tl["pocetak"] = pd.to_datetime(_tl["pocetak"], errors="coerce")
    _tl["kraj"]    = pd.to_datetime(_tl["kraj"],    errors="coerce")
    _tl = _tl.dropna(subset=["pocetak", "kraj"]).head(30)

    _charts = [mo.as_html(_bar)]
    if not _tl.empty:
        _tl["label"] = _tl["akronim"].where(_tl["akronim"] != "", _tl["sifra"])
        _gantt = px.timeline(_tl, x_start="pocetak", x_end="kraj", y="label",
                             color="tip", title=f"Timeline projekata (prvih {len(_tl)})")
        _gantt.update_yaxes(autorange="reversed")
        _gantt.update_layout(height=max(350, len(_tl) * 22))
        _charts.append(mo.as_html(_gantt))

    mo.vstack(_charts)
    return


@app.cell
def _proj_table(mo, proj_df):
    mo.stop(proj_df is None or proj_df.empty)
    mo.md("### Tablica projekata")
    mo.ui.dataframe(proj_df[["sifra", "akronim", "naziv_hr", "tip", "pocetak", "kraj", "total_cost", "currency"]])
    return


# ---------------------------------------------------------------------------
# AUTENTIKACIJA (opcionalna)
# ---------------------------------------------------------------------------

@app.cell
def _auth_header(mo):
    mo.md("""
    ---
    ## Autenticirani podaci

    Unesi CroRIS kredencijale za pristup MOZVAG podacima i akreditacijama.
    Ostavi prazno ako nemaš pristup.
    """)
    return


@app.cell
def _auth_inputs(mo):
    username_input = mo.ui.text(placeholder="korisničko ime", label="Korisničko ime")
    password_input = mo.ui.text(placeholder="lozinka", label="Lozinka", kind="password")
    godina_input   = mo.ui.number(start=2000, stop=2030, step=1, value=2024, label="Godina (MOZVAG)")
    mo.hstack([username_input, password_input, godina_input], gap=2)
    return username_input, password_input, godina_input


@app.cell
def _auth_status(mo, username_input, password_input, CrorisClient, Config):
    import os as _os
    _u = username_input.value or _os.getenv("CRORIS_USERNAME", "")
    _p = password_input.value or _os.getenv("CRORIS_PASSWORD", "")
    auth_ok = bool(_u and _p)

    if auth_ok:
        auth_client = CrorisClient(Config(username=_u, password=_p))
        mo.callout(mo.md("Kredencijali uneseni. Pritisni gumbe ispod za dohvat podataka."), kind="success")
    else:
        auth_client = None
        mo.callout(mo.md("Unesi kredencijale za dohvat MOZVAG i akreditacija."), kind="neutral")
    return auth_ok, auth_client


# ---------------------------------------------------------------------------
# SEKCIJA: MOZVAG PROJEKTI (auth)
# ---------------------------------------------------------------------------

@app.cell
def _mozvag_header(mo, auth_ok):
    mo.md("---\n## MOZVAG projekti")
    mo.stop(not auth_ok,
        mo.callout(mo.md("Unesi kredencijale iznad za dohvat MOZVAG podataka."), kind="neutral"))
    return


@app.cell
def _mozvag_loader(mo):
    mozvag_btn = mo.ui.run_button(label="Učitaj MOZVAG projekte")
    mozvag_btn
    return (mozvag_btn,)


@app.cell
def _mozvag_fetch(mo, mozvag_btn, ustanova_dropdown, auth_client, godina_input, get_mozvag_projekti):
    mo.stop(not mozvag_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj MOZVAG projekte**."), kind="neutral"))
    mo.stop(ustanova_dropdown.value is None)
    mo.stop(auth_client is None)

    _uid    = int(ustanova_dropdown.value)
    _godina = int(godina_input.value)
    mozvag_rows = []
    _mozvag_err = None

    try:
        with mo.status.spinner(title=f"Dohvaćam MOZVAG projekte za godinu {_godina}..."):
            _projekti = get_mozvag_projekti(_uid, _godina, client=auth_client)
            mozvag_rows = [p.to_dict() for p in _projekti]
    except Exception as _e:
        _status = getattr(getattr(_e, "response", None), "status_code", None)
        if _status == 401:
            _mozvag_err = "Autentikacija nije uspjela — provjeri kredencijale."
        elif _status == 404:
            mozvag_rows = []
        else:
            _mozvag_err = str(_e)

    if _mozvag_err:
        mo.callout(mo.md(f"**Greška:** {_mozvag_err}"), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(mozvag_rows)}** MOZVAG projekata za {_godina}."), kind="success")
    return (mozvag_rows,)


@app.cell
def _mozvag_df(mo, mozvag_rows, pd):
    mo.stop(not mozvag_rows)
    mozvag_df = pd.DataFrame(mozvag_rows)
    return (mozvag_df,)


@app.cell
def _mozvag_viz(mo, mozvag_df, pd, px):
    mo.stop(mozvag_df is None or mozvag_df.empty)

    _charts = []

    # Pie po vrsti projekta
    _v = mozvag_df["vrsta"].replace("", "Nepoznato").fillna("Nepoznato").value_counts().reset_index()
    _v.columns = ["vrsta", "broj"]
    _charts.append(mo.as_html(
        px.pie(_v, names="vrsta", values="broj", title="MOZVAG projekti po vrsti", hole=0.4)
    ))

    # Bar iznosi ustanove po projektu (top 20)
    _iznos = mozvag_df.dropna(subset=["ustanova_iznos"]).copy()
    if not _iznos.empty:
        _iznos = _iznos.sort_values("ustanova_iznos", ascending=False).head(20)
        _charts.append(mo.as_html(
            px.bar(_iznos, x="naziv", y="ustanova_iznos",
                   title="Top 20 projekata po iznosu ustanove",
                   color="ustanova_iznos", color_continuous_scale="Blues",
                   labels={"naziv": "Projekt", "ustanova_iznos": "Iznos"})
        ))

    # Gantt timeline
    _tl = mozvag_df.dropna(subset=["start_date", "end_date"]).copy()
    _tl["start_date"] = pd.to_datetime(_tl["start_date"], errors="coerce")
    _tl["end_date"]   = pd.to_datetime(_tl["end_date"],   errors="coerce")
    _tl = _tl.dropna(subset=["start_date", "end_date"]).head(30)
    if not _tl.empty:
        _gantt = px.timeline(_tl, x_start="start_date", x_end="end_date",
                             y="naziv", color="vrsta",
                             title=f"Timeline MOZVAG projekata (prvih {len(_tl)})")
        _gantt.update_yaxes(autorange="reversed")
        _gantt.update_layout(height=max(350, len(_tl) * 22))
        _charts.append(mo.as_html(_gantt))

    mo.vstack(_charts)
    return


@app.cell
def _mozvag_table(mo, mozvag_df):
    mo.stop(mozvag_df is None or mozvag_df.empty)
    mo.md("### Tablica MOZVAG projekata")
    mo.ui.dataframe(mozvag_df[["naziv", "vrsta", "uloga", "start_date", "end_date",
                                "ustanova_iznos", "ustanova_valuta", "financijeri"]])
    return


# ---------------------------------------------------------------------------
# SEKCIJA: AKREDITACIJE / ZNANSTVENICI (auth)
# ---------------------------------------------------------------------------

@app.cell
def _akred_header(mo, auth_ok):
    mo.md("---\n## Akreditacije (nastavnici i istraživači)")
    mo.stop(not auth_ok,
        mo.callout(mo.md("Unesi kredencijale iznad za dohvat akreditacija."), kind="neutral"))
    return


@app.cell
def _akred_loader(mo):
    akred_btn = mo.ui.run_button(label="Učitaj akreditacije")
    akred_btn
    return (akred_btn,)


@app.cell
def _akred_fetch(mo, akred_btn, ustanova_dropdown, auth_client, get_akreditacije_ustanove):
    mo.stop(not akred_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj akreditacije**."), kind="neutral"))
    mo.stop(ustanova_dropdown.value is None)
    mo.stop(auth_client is None)

    _uid = int(ustanova_dropdown.value)
    akred_rows = []
    _akred_err = None

    try:
        with mo.status.spinner(title="Dohvaćam akreditacije..."):
            _akreditacije = get_akreditacije_ustanove(_uid, client=auth_client)
            akred_rows = [
                {
                    "ime":              a.ime or "",
                    "prezime":          a.prezime or "",
                    "vrsta_zaposlenja": a.vrsta_zaposlenja_hr or "",
                    "vrsta_rad_odnosa": a.vrsta_radnog_odnosa_hr or "",
                    "podrucje":         a.podrucje_hr or "",
                    "polje":            a.polje_hr or "",
                }
                for a in _akreditacije
            ]
    except Exception as _e:
        _status = getattr(getattr(_e, "response", None), "status_code", None)
        if _status == 401:
            _akred_err = "Autentikacija nije uspjela — provjeri kredencijale."
        else:
            _akred_err = str(_e)

    if _akred_err:
        mo.callout(mo.md(f"**Greška:** {_akred_err}"), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(akred_rows)}** akreditacija."), kind="success")
    return (akred_rows,)


@app.cell
def _akred_df(mo, akred_rows, pd):
    mo.stop(not akred_rows)
    akred_df = pd.DataFrame(akred_rows)
    return (akred_df,)


@app.cell
def _akred_viz(mo, akred_df, px):
    mo.stop(akred_df is None or akred_df.empty)

    _charts = []

    if "vrsta_zaposlenja" in akred_df.columns:
        _v = akred_df["vrsta_zaposlenja"].replace("", "Nepoznato").value_counts().reset_index()
        _v.columns = ["vrsta", "broj"]
        _charts.append(mo.as_html(
            px.pie(_v, names="vrsta", values="broj",
                   title="Akreditacije po vrsti zaposlenja", hole=0.4)
        ))

    if "podrucje" in akred_df.columns:
        _p = akred_df["podrucje"].dropna().replace("", "Nepoznato").value_counts().reset_index()
        _p.columns = ["podrucje", "broj"]
        _charts.append(mo.as_html(
            px.bar(_p, x="podrucje", y="broj",
                   title="Akreditacije po znanstvenom području",
                   color="broj", color_continuous_scale="Teal")
        ))

    if "vrsta_rad_odnosa" in akred_df.columns:
        _z = akred_df["vrsta_rad_odnosa"].dropna().replace("", "Nepoznato").value_counts().reset_index()
        _z.columns = ["vrsta", "broj"]
        _charts.append(mo.as_html(
            px.bar(_z, x="vrsta", y="broj",
                   title="Akreditacije po vrsti radnog odnosa",
                   color="broj", color_continuous_scale="Purples")
        ))

    mo.vstack(_charts) if _charts else mo.callout(mo.md("Nema podataka za vizualizaciju."), kind="neutral")
    return


@app.cell
def _akred_table(mo, akred_df):
    mo.stop(akred_df is None or akred_df.empty)
    mo.md("### Tablica akreditacija")
    mo.ui.dataframe(akred_df[["prezime", "ime", "vrsta_zaposlenja", "vrsta_rad_odnosa", "podrucje", "polje"]])
    return


if __name__ == "__main__":
    app.run()
