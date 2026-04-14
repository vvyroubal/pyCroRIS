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

__generated_with = "0.23.1"
app = marimo.App(width="wide", app_title="CroRIS Ustanova Explorer")


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
    from crosbi.endpoints.znanstvenici import (
        get_akreditacije_ustanove,
        get_znanstvenik_by_oib,
        get_znanstvenik_by_mbz,
    )
    from crosbi.endpoints.casopisi import list_casopisi
    from crosbi.endpoints.dogadanja import list_dogadanja
    from crosbi.endpoints.oprema_api import list_oprema, list_usluge

    return (
        CROSBI_BASE_URL,
        Config,
        CrorisClient,
        ThreadPoolExecutor,
        get_akreditacije_ustanove,
        get_mozvag_projekti,
        get_projekti_po_ustanovi,
        get_sve_aktivne_ustanove,
        get_znanstvenik_by_mbz,
        get_znanstvenik_by_oib,
        list_casopisi,
        list_dogadanja,
        list_oprema,
        list_usluge,
        mo,
        pd,
        px,
    )


@app.cell
def _load_ustanove(CrorisClient, get_sve_aktivne_ustanove):
    _client = CrorisClient()
    _all = get_sve_aktivne_ustanove(client=_client)
    _sorted = sorted(_all, key=lambda u: u.puni_naziv or u.kratki_naziv or "")

    ustanove_map = {str(u.id): u for u in _sorted}
    # Marimo dropdown: {label_za_prikaz: vrijednost_value}
    dropdown_options = {
        f"{u.kratica or '?'} — {u.puni_naziv or u.kratki_naziv or 'Nepoznato'}": str(u.id)
        for u in _sorted
    }
    return dropdown_options, ustanove_map


@app.cell
def _header(mo):
    mo.md("""
    # CroRIS Explorer

    Odaberi ustanovu za prikaz svih dostupnih podataka.

    ---
    """)
    return


@app.cell
def _selector(dropdown_options, mo):
    ustanova_dropdown = mo.ui.dropdown(
        options=dropdown_options,
        label="Odaberi ustanovu",
    )
    ustanova_dropdown
    return (ustanova_dropdown,)


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
    _tip  = ", ".join(t.naziv or "" for t in (_u.tip_ustanove or [])) or "—"
    _adr_str = ", ".join(filter(None, [
        _adr.ulica_br if _adr else None,
        _adr.postanskI_broj if _adr else None,
        _adr.mjesto if _adr else None,
    ])) or "—"
    _web  = (_kon.web or "") if _kon else ""
    _web_md = f"[{_web}]({_web})" if _web else "—"

    mo.vstack([
        mo.md(f"## {_u.puni_naziv or _u.kratki_naziv or '—'}"),
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


@app.cell
def _counts(CROSBI_BASE_URL, CrorisClient, mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)

    _uid = ustanova_dropdown.value
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

    mo.vstack([
        mo.md("---\n### Javni podaci"),
        mo.hstack([
            mo.stat(label="CROSBI publikacije", value=str(pub_count))
                if pub_error is None
                else mo.callout(mo.md(f"**CROSBI greška:** {pub_error}"), kind="warn"),
        ], gap=3),
    ])
    return pub_count, pub_error


@app.cell
def _pub_header(mo, pub_count, pub_error):
    mo.stop(pub_error is not None or pub_count == 0,
        mo.callout(mo.md("Nema CROSBI publikacija za ovu ustanovu."), kind="neutral"))
    mo.md("---\n## Publikacije (CROSBI)")
    return


@app.cell
def _pub_loader(mo, pub_count):
    pub_btn = mo.ui.run_button(label=f"Učitaj publikacije ({pub_count})")
    pub_btn
    return (pub_btn,)


@app.cell
def _pub_fetch(
    CROSBI_BASE_URL,
    CrorisClient,
    ThreadPoolExecutor,
    mo,
    pub_btn,
    pub_count,
    ustanova_dropdown,
):
    mo.stop(not pub_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj publikacije**."), kind="neutral"))
    mo.stop(ustanova_dropdown.value is None)

    _uid    = ustanova_dropdown.value
    _client = CrorisClient()
    pub_rows = []
    _pub_err = None

    def _fetch_safe(_url):
        try:
            return _client.get(_url)
        except Exception:
            return None

    try:
        with mo.status.spinner(title="Dohvaćam popis publikacija..."):
            _crosbi_data = _client.get(f"{CROSBI_BASE_URL}/ustanova/{_uid}")
            _urls = [
                lnk["href"]
                for lnk in _crosbi_data.get("_links", {}).get("publikacije", [])
            ]

        with ThreadPoolExecutor(max_workers=10) as _pool:
            for _d in mo.status.progress_bar(
                _pool.map(_fetch_safe, _urls),
                total=len(_urls),
                title=f"Dohvaćam publikacije ({len(_urls)})...",
            ):
                if _d is not None:
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
    except Exception as _e:
        _pub_err = str(_e)

    if _pub_err:
        mo.callout(mo.md(f"**Greška:** {_pub_err}"), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(pub_rows)}** / {pub_count} publikacija."), kind="success")
    return (pub_rows,)


@app.cell
def _pub_df(mo, pd, pub_rows):
    mo.stop(not pub_rows)
    pub_df = pd.DataFrame(pub_rows)
    pub_df["godina"] = pd.to_numeric(pub_df["godina"], errors="coerce")
    return (pub_df,)


@app.cell
def _pub_year_slider(mo, pub_df):
    _years = pub_df["godina"].dropna().astype(int)
    _min = int(_years.min())
    _max = int(_years.max())
    pub_year_slider = mo.ui.range_slider(
        start=_min,
        stop=_max,
        step=1,
        value=[_min, _max],
        label=f"Raspon godina ({_min}–{_max})",
        show_value=False,
    )
    pub_year_slider
    return (pub_year_slider,)


@app.cell
def _pub_filtered(pub_df, pub_year_slider):
    _lo, _hi = pub_year_slider.value
    pub_df_filtered = pub_df[
        pub_df["godina"].between(_lo, _hi, inclusive="both")
    ].copy()
    return (pub_df_filtered,)


@app.cell
def _pub_viz(mo, pub_df_filtered, px):
    mo.stop(pub_df_filtered is None or pub_df_filtered.empty)

    _v = pub_df_filtered["vrsta"].replace("", "Nepoznato").value_counts().reset_index()
    _v.columns = ["vrsta", "broj"]
    _pie = px.pie(_v, names="vrsta", values="broj", title="Publikacije po vrsti", hole=0.4)

    _g = (pub_df_filtered.dropna(subset=["godina"])
          .groupby("godina").size().reset_index(name="broj")
          .sort_values("godina"))
    _bar = px.bar(_g, x="godina", y="broj", title="Publikacije po godini",
                  color="broj", color_continuous_scale="Blues")
    _bar.update_layout(showlegend=False)

    mo.vstack([mo.as_html(_pie), mo.as_html(_bar)])
    return


@app.cell
def _pub_table(mo, pub_df_filtered):
    mo.stop(pub_df_filtered is None or pub_df_filtered.empty)
    mo.md(f"### Tablica publikacija ({len(pub_df_filtered)} zapisa)")
    mo.ui.dataframe(pub_df_filtered[["naslov", "autori", "vrsta", "godina", "casopis", "doi", "status"]])
    return


@app.cell
def _proj_section_header(mo):
    mo.md("""
    ---
    ## Projekti (CroRIS)
    """)
    return


@app.cell
def _proj_loader(mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)
    proj_btn = mo.ui.run_button(label="Učitaj projekte")
    proj_btn
    return (proj_btn,)


@app.cell
def _proj_fetch(
    CrorisClient,
    get_projekti_po_ustanovi,
    mo,
    proj_btn,
    ustanova_dropdown,
    ustanove_map,
):
    mo.stop(not proj_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj projekte**."), kind="neutral"))
    mo.stop(ustanova_dropdown.value is None)

    _uid  = ustanova_dropdown.value
    _mbu  = ustanove_map[_uid].mbu or ""
    proj_list  = []
    proj_error = None
    try:
        with mo.status.spinner(title="Dohvaćam projekte..."):
            proj_list = get_projekti_po_ustanovi(_mbu, client=CrorisClient())
    except Exception as _e:
        proj_error = str(_e)

    if proj_error:
        mo.callout(mo.md(f"**Greška:** {proj_error}"), kind="danger")
    elif not proj_list:
        mo.callout(mo.md("Nema projekata za ovu ustanovu."), kind="neutral")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(proj_list)}** projekata."), kind="success")
    return (proj_list,)


@app.cell
def _proj_df(mo, pd, proj_list):
    mo.stop(not proj_list)
    _rows = [p.to_dict() for p in proj_list]
    proj_df = pd.DataFrame(_rows)
    proj_df = proj_df.rename(columns={
        "hr_sifra_projekta": "sifra",
        "acro": "akronim",
        "title_hr": "naziv_hr",
        "title_en": "naziv_en",
        "tip_projekta": "tip",
        "total_cost": "total_cost",
        "currency_code": "currency",
    })
    proj_df["pocetak"] = pd.to_datetime(proj_df["pocetak"], dayfirst=True, errors="coerce")
    proj_df["kraj"]    = pd.to_datetime(proj_df["kraj"],    dayfirst=True, errors="coerce")
    return (proj_df,)


@app.cell
def _proj_year_slider(mo, proj_df):
    _years = proj_df["pocetak"].dropna().dt.year
    _min = int(_years.min())
    _max = int(_years.max())
    proj_year_slider = mo.ui.range_slider(
        start=_min, stop=_max, step=1, value=[_min, _max],
        label=f"Raspon godina početka projekta ({_min}–{_max})", show_value=False,
    )
    proj_year_slider
    return (proj_year_slider,)


@app.cell
def _proj_filtered(proj_df, proj_year_slider):
    _lo, _hi = proj_year_slider.value
    proj_df_filtered = proj_df[
        proj_df["pocetak"].dt.year.between(_lo, _hi)
    ].copy()
    return (proj_df_filtered,)


@app.cell
def _proj_viz(mo, pd, proj_df_filtered, px):
    mo.stop(proj_df_filtered is None or proj_df_filtered.empty)

    _t = proj_df_filtered["tip"].replace("", "Nepoznato").fillna("Nepoznato").value_counts().reset_index()
    _t.columns = ["tip", "broj"]
    _bar = px.bar(_t, x="tip", y="broj", title="Projekti po tipu",
                  color="broj", color_continuous_scale="Teal")
    _bar.update_layout(xaxis_tickangle=-30, showlegend=False)

    _tl = proj_df_filtered.dropna(subset=["pocetak"]).copy()
    _danas = pd.Timestamp.today().normalize()
    _tl["kraj_viz"] = _tl["kraj"].fillna(_danas)

    _charts = [mo.as_html(_bar)]
    if not _tl.empty:
        _gantt = px.timeline(
            _tl,
            x_start="pocetak", x_end="kraj_viz",
            y="sifra",
            color="tip",
            hover_data={"naziv_hr": True, "akronim": True, "tip": True,
                        "pocetak": True, "kraj": True, "sifra": False},
            title=f"Timeline projekata ({len(_tl)})",
        )
        _gantt.update_yaxes(autorange="reversed")
        _gantt.update_layout(height=max(350, len(_tl) * 22))
        _charts.append(mo.as_html(_gantt))

    mo.vstack(_charts)
    return


@app.cell
def _proj_table(mo, proj_df_filtered):
    mo.stop(proj_df_filtered is None or proj_df_filtered.empty)
    mo.md("### Tablica projekata")
    mo.ui.dataframe(proj_df_filtered[["sifra", "akronim", "naziv_hr", "tip", "pocetak", "kraj", "total_cost", "currency"]])
    return


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
    godina_input   = mo.ui.dropdown(
        options={str(g): g for g in range(2000, 2031)},
        value="2024",
        label="Godina (MOZVAG)",
    )
    mo.hstack([username_input, password_input, godina_input], gap=2)
    return godina_input, password_input, username_input


@app.cell
def _auth_status(Config, CrorisClient, mo, password_input, username_input):
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
    return auth_client, auth_ok


@app.cell
def _mozvag_header(auth_ok, mo):
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
def _mozvag_fetch(
    auth_client,
    get_mozvag_projekti,
    godina_input,
    mo,
    mozvag_btn,
    ustanova_dropdown,
):
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
    mozvag_df["start_date"] = pd.to_datetime(mozvag_df["start_date"], dayfirst=True, errors="coerce")
    mozvag_df["end_date"]   = pd.to_datetime(mozvag_df["end_date"],   dayfirst=True, errors="coerce")
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
    _tl = mozvag_df.dropna(subset=["start_date"]).copy()
    _tl["end_date_viz"] = _tl["end_date"].fillna(pd.Timestamp.today().normalize())
    if not _tl.empty:
        _gantt = px.timeline(_tl, x_start="start_date", x_end="end_date_viz",
                             y="naziv", color="vrsta",
                             title=f"Timeline MOZVAG projekata ({len(_tl)})")
        _gantt.update_yaxes(autorange="reversed")
        _gantt.update_layout(height=max(350, len(_tl) * 25))
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


@app.cell
def _akred_header(auth_ok, mo):
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
def _akred_fetch(
    akred_btn,
    auth_client,
    get_akreditacije_ustanove,
    mo,
    ustanova_dropdown,
):
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
def _akred_df(akred_rows, mo, pd):
    mo.stop(not akred_rows)
    akred_df = pd.DataFrame(akred_rows)
    return (akred_df,)


@app.cell
def _akred_viz(akred_df, mo, px):
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
def _akred_table(akred_df, mo):
    mo.stop(akred_df is None or akred_df.empty)
    mo.md("### Tablica akreditacija")
    mo.ui.dataframe(akred_df[["prezime", "ime", "vrsta_zaposlenja", "vrsta_rad_odnosa", "podrucje", "polje"]])
    return


@app.cell
def _oprema_header(mo):
    mo.md("---\n## Oprema (CroRIS)")
    return


@app.cell
def _oprema_loader(mo):
    oprema_btn = mo.ui.run_button(label="Učitaj opremu i usluge")
    oprema_btn
    return (oprema_btn,)


@app.cell
def _oprema_fetch(CrorisClient, ThreadPoolExecutor, list_oprema, list_usluge, mo, oprema_btn):
    mo.stop(not oprema_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj opremu i usluge**."), kind="neutral"))

    oprema_rows = []
    usluge_rows = []
    _err = None
    try:
        _client = CrorisClient()
        with ThreadPoolExecutor(max_workers=2) as _pool:
            _fut_oprema = _pool.submit(lambda: list(list_oprema(client=_client)))
            _fut_usluge = _pool.submit(lambda: list(list_usluge(client=_client)))
            with mo.status.spinner(title="Dohvaćam opremu i usluge..."):
                _oprema_list = _fut_oprema.result()
                _usluge_list = _fut_usluge.result()

        for o in _oprema_list:
            oprema_rows.append({
                "id":            o.id,
                "model":         o.model or "",
                "proizvodjac":   o.proizvodjac or "",
                "inventarni_br": o.inventarni_broj or "",
                "godina_proiz":  o.godina_proizvodnje,
                "kategorija":    o.kategorija.naziv if o.kategorija else "",
                "stanje":        o.stanje.naziv if o.stanje else "",
                "ustanova":      o.ustanova_vlasnik.naziv if o.ustanova_vlasnik else "",
                "lokacija":      o.ustanova_lokacija.naziv if o.ustanova_lokacija else "",
                "naziv_hr":      o.naziv.get("hr") if o.naziv else "",
            })
        for u in _usluge_list:
            usluge_rows.append({
                "id":        u.id,
                "naziv_hr":  u.naziv.get("hr") if u.naziv else "",
                "ustanova":  u.ustanova_naziv or "",
                "aktivnost": u.aktivnost,
            })
    except Exception as _e:
        _err = str(_e)

    if _err:
        mo.callout(mo.md(f"**Greška:** {_err}"), kind="danger")
    else:
        mo.callout(mo.md(
            f"Dohvaćeno **{len(oprema_rows)}** opreme i **{len(usluge_rows)}** usluga."
        ), kind="success")
    return oprema_rows, usluge_rows


@app.cell
def _oprema_df(mo, oprema_rows, pd, usluge_rows):
    mo.stop(not oprema_rows and not usluge_rows)
    oprema_df  = pd.DataFrame(oprema_rows)  if oprema_rows  else pd.DataFrame()
    usluge_df  = pd.DataFrame(usluge_rows)  if usluge_rows  else pd.DataFrame()
    return oprema_df, usluge_df


@app.cell
def _oprema_viz(mo, oprema_df, px, usluge_df):
    mo.stop(oprema_df.empty and usluge_df.empty)
    _charts = []
    if not oprema_df.empty:
        _k = oprema_df["kategorija"].replace("", "Nepoznato").fillna("Nepoznato").value_counts().reset_index()
        _k.columns = ["kategorija", "broj"]
        _bar = px.bar(_k, x="kategorija", y="broj", title=f"Oprema po kategoriji ({len(oprema_df)})",
                      color="broj", color_continuous_scale="Teal")
        _bar.update_layout(xaxis_tickangle=-30, showlegend=False)
        _charts.append(mo.as_html(_bar))
    if not usluge_df.empty:
        _u = usluge_df["ustanova"].replace("", "Nepoznato").fillna("Nepoznato").value_counts().nlargest(15).reset_index()
        _u.columns = ["ustanova", "broj"]
        _bar2 = px.bar(_u, x="broj", y="ustanova", orientation="h",
                       title=f"Top ustanove po uslugama ({len(usluge_df)})",
                       color="broj", color_continuous_scale="Blues")
        _bar2.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
        _charts.append(mo.as_html(_bar2))
    mo.vstack(_charts)
    return


@app.cell
def _oprema_table(mo, oprema_df, usluge_df):
    mo.stop(oprema_df.empty and usluge_df.empty)
    _tabs = {}
    if not oprema_df.empty:
        _tabs["Oprema"] = mo.ui.dataframe(
            oprema_df[["naziv_hr", "model", "proizvodjac", "kategorija", "stanje", "ustanova", "lokacija"]]
        )
    if not usluge_df.empty:
        _tabs["Usluge"] = mo.ui.dataframe(
            usluge_df[["naziv_hr", "ustanova", "aktivnost"]]
        )
    mo.ui.tabs(_tabs)
    return


@app.cell
def _casopisi_header(mo):
    mo.md("---\n## Časopisi (CroRIS)")
    return


@app.cell
def _casopisi_loader(mo):
    casopisi_btn = mo.ui.run_button(label="Učitaj časopise")
    casopisi_btn
    return (casopisi_btn,)


@app.cell
def _casopisi_fetch(CrorisClient, list_casopisi, mo, casopisi_btn):
    mo.stop(not casopisi_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj časopise**."), kind="neutral"))

    casopisi_rows = []
    _err_c = None
    try:
        _client_c = CrorisClient()
        for _c in mo.status.progress_bar(
            list_casopisi(client=_client_c),
            title="Dohvaćam časopise...",
        ):
            casopisi_rows.append({
                "id":             _c.id,
                "naziv":          _c.naziv or "",
                "drzava":         _c.drzava or "",
                "drzava_kod":     _c.drzava_kod or "",
                "issn":           _c.issn or "",
                "eissn":          _c.eissn or "",
                "godina_pocetka": _c.godina_pocetka,
                "godina_zavrsetka": _c.godina_zavrsetka,
            })
    except Exception as _e:
        _err_c = str(_e)

    if _err_c:
        mo.callout(mo.md(f"**Greška:** {_err_c}"), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(casopisi_rows)}** časopisa."), kind="success")
    return (casopisi_rows,)


@app.cell
def _casopisi_df(casopisi_rows, mo, pd):
    mo.stop(not casopisi_rows)
    casopisi_df = pd.DataFrame(casopisi_rows)
    return (casopisi_df,)


@app.cell
def _casopisi_viz(casopisi_df, mo, px):
    mo.stop(casopisi_df is None or casopisi_df.empty)
    _d = casopisi_df["drzava"].replace("", "Nepoznato").fillna("Nepoznato").value_counts().nlargest(20).reset_index()
    _d.columns = ["drzava", "broj"]
    _bar = px.bar(_d, x="broj", y="drzava", orientation="h",
                  title=f"Časopisi po zemlji izdavanja (top 20 od {len(casopisi_df)})",
                  color="broj", color_continuous_scale="Teal")
    _bar.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
    mo.as_html(_bar)
    return


@app.cell
def _casopisi_table(casopisi_df, mo):
    mo.stop(casopisi_df is None or casopisi_df.empty)
    mo.md(f"### Tablica časopisa ({len(casopisi_df)} zapisa)")
    mo.ui.dataframe(casopisi_df[["naziv", "drzava", "issn", "eissn", "godina_pocetka", "godina_zavrsetka"]])
    return


@app.cell
def _dogadanja_header(mo):
    mo.md("---\n## Događanja (CroRIS)")
    return


@app.cell
def _dogadanja_loader(mo):
    dogadanja_btn = mo.ui.run_button(label="Učitaj događanja")
    dogadanja_btn
    return (dogadanja_btn,)


@app.cell
def _dogadanja_fetch(CrorisClient, dogadanja_btn, list_dogadanja, mo):
    mo.stop(not dogadanja_btn.value,
        mo.callout(mo.md("Pritisni **Učitaj događanja**."), kind="neutral"))

    dogadanja_rows = []
    _err_d = None
    try:
        _client_d = CrorisClient()
        for _d in mo.status.progress_bar(
            list_dogadanja(client=_client_d),
            title="Dohvaćam događanja...",
        ):
            _prvo_mjesto = _d.mjesto_odrzavanja[0] if _d.mjesto_odrzavanja else None
            _mjesto = _prvo_mjesto.mjesto_naziv if _prvo_mjesto else ""
            _drzava = (_prvo_mjesto.drzava.naziv
                       if _prvo_mjesto and _prvo_mjesto.drzava else "")
            dogadanja_rows.append({
                "id":             _d.id,
                "naziv":          _d.get_naziv("hr"),
                "akronim":        _d.get_akronim("hr"),
                "vrsta":          _d.vrsta_dogadanja or "",
                "datum_pocetka":  _d.datum_pocetka or "",
                "datum_zavrsetka": _d.datum_zavrsetka or "",
                "broj_sudionika": _d.broj_sudionika,
                "mjesto":         _mjesto,
                "drzava":         _drzava,
            })
    except Exception as _e:
        _err_d = str(_e)

    if _err_d:
        mo.callout(mo.md(f"**Greška:** {_err_d}"), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(dogadanja_rows)}** događanja."), kind="success")
    return (dogadanja_rows,)


@app.cell
def _dogadanja_df(dogadanja_rows, mo, pd):
    mo.stop(not dogadanja_rows)
    dogadanja_df = pd.DataFrame(dogadanja_rows)
    dogadanja_df["godina"] = pd.to_datetime(
        dogadanja_df["datum_pocetka"], errors="coerce"
    ).dt.year
    return (dogadanja_df,)


@app.cell
def _dogadanja_viz(dogadanja_df, mo, px):
    mo.stop(dogadanja_df is None or dogadanja_df.empty)
    _charts = []
    _g = dogadanja_df["godina"].dropna().astype(int).value_counts().sort_index().reset_index()
    _g.columns = ["godina", "broj"]
    _bar1 = px.bar(_g, x="godina", y="broj",
                   title=f"Događanja po godini ({len(dogadanja_df)})",
                   color="broj", color_continuous_scale="Teal")
    _charts.append(mo.as_html(_bar1))

    _v = dogadanja_df["vrsta"].replace("", "Nepoznato").fillna("Nepoznato").value_counts().reset_index()
    _v.columns = ["vrsta", "broj"]
    _bar2 = px.pie(_v, names="vrsta", values="broj", title="Događanja po vrsti")
    _charts.append(mo.as_html(_bar2))
    mo.vstack(_charts)
    return


@app.cell
def _dogadanja_table(dogadanja_df, mo):
    mo.stop(dogadanja_df is None or dogadanja_df.empty)
    mo.md(f"### Tablica događanja ({len(dogadanja_df)} zapisa)")
    mo.ui.dataframe(dogadanja_df[["naziv", "akronim", "vrsta", "datum_pocetka", "datum_zavrsetka", "mjesto", "drzava"]])
    return


@app.cell
def _znan_header(mo):
    mo.md("""
    ---
    ## Znanstvenici (pretraga)

    Pretraži profil znanstvenika po OIB-u ili matičnom broju znanstvenika (MBZ).
    Zahtijeva odobrenje MZO-a za pristup.
    """)
    return


@app.cell
def _znan_inputs(mo):
    znan_oib_input = mo.ui.text(placeholder="npr. 12345678901", label="OIB")
    znan_mbz_input = mo.ui.text(placeholder="npr. 123456", label="MBZ")
    znan_search_btn = mo.ui.run_button(label="Pretraži")
    mo.hstack([znan_oib_input, znan_mbz_input, znan_search_btn], gap=2)
    return znan_mbz_input, znan_oib_input, znan_search_btn


@app.cell
def _znan_fetch(
    CrorisClient,
    get_znanstvenik_by_mbz,
    get_znanstvenik_by_oib,
    mo,
    znan_mbz_input,
    znan_oib_input,
    znan_search_btn,
):
    mo.stop(not znan_search_btn.value,
        mo.callout(mo.md("Unesi OIB ili MBZ i pritisni **Pretraži**."), kind="neutral"))
    mo.stop(not znan_oib_input.value and not znan_mbz_input.value,
        mo.callout(mo.md("Unesi OIB ili MBZ za pretragu."), kind="warn"))

    znanstvenik = None
    _err_z = None
    try:
        _client_z = CrorisClient()
        with mo.status.spinner(title="Dohvaćam podatke o znanstveniku..."):
            if znan_oib_input.value:
                znanstvenik = get_znanstvenik_by_oib(znan_oib_input.value.strip(), client=_client_z)
            else:
                znanstvenik = get_znanstvenik_by_mbz(znan_mbz_input.value.strip(), client=_client_z)
    except Exception as _e:
        _err_z = str(_e)

    if _err_z:
        mo.callout(mo.md(f"**Greška:** {_err_z}"), kind="danger")
    return (znanstvenik,)


@app.cell
def _znan_profile(mo, znanstvenik):
    mo.stop(znanstvenik is None)
    _z = znanstvenik
    mo.vstack([
        mo.md(f"### {_z.ime or ''} {_z.prezime or ''}"),
        mo.md(f"""
| Polje | Vrijednost |
|---|---|
| ID | {_z.id} |
| OIB | {_z.oib or '—'} |
| MBZ | {_z.maticni_broj or '—'} |
| ORCID | {_z.orcid or '—'} |
| E-mail | {_z.email or '—'} |
| Najviše zvanje | {_z.max_zvanje or '—'} |
| Aktivan | {'Da' if _z.aktivan else 'Ne'} |
| Godina prvog zaposlenja | {_z.godina_prvog_zaposlenja or '—'} |
"""),
    ])
    return


@app.cell
def _znan_tables(mo, pd, znanstvenik):
    mo.stop(znanstvenik is None)
    _z = znanstvenik
    _tabs = {}

    if _z.zaposlenja:
        _zap_df = pd.DataFrame([{
            "ustanova":  z.ustanova.naziv if z.ustanova else "",
            "radno_mjesto": z.radno_mjesto or "",
            "vrsta_zaposlenja": z.vrsta_zaposlenja or "",
            "datum_od":  z.datum_od or "",
            "datum_do":  z.datum_do or "",
            "aktivno":   z.aktivno,
        } for z in _z.zaposlenja])
        _tabs["Zaposlenja"] = mo.ui.dataframe(_zap_df)

    if _z.zvanja:
        _zv_df = pd.DataFrame([{
            "zvanje":   z.naziv or "",
            "kratica":  z.kratica or "",
            "ustanova": z.ustanova.naziv if z.ustanova else "",
            "datum_izbora": z.datum_izbora or "",
            "aktivan":  z.aktivan,
        } for z in _z.zvanja])
        _tabs["Zvanja"] = mo.ui.dataframe(_zv_df)

    if _z.akademski_stupnjevi:
        _as_df = pd.DataFrame([{
            "stupanj":  s.naziv or "",
            "kratica":  s.kratica or "",
            "datum_stjecanja": s.datum_stjecanja or "",
        } for s in _z.akademski_stupnjevi])
        _tabs["Akademski stupnjevi"] = mo.ui.dataframe(_as_df)

    mo.ui.tabs(_tabs) if _tabs else mo.md("_Nema podataka o zaposlenjima i zvanjima._")
    return


if __name__ == "__main__":
    app.run()
