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
    from crosbi.config import CROSBI_BASE_URL
    from crosbi.endpoints.upisnik import get_sve_aktivne_ustanove
    from crosbi.endpoints.projekti import get_projekti_po_ustanovi
    from crosbi.endpoints.oprema_api import (
        fetch_oprema_by_href,
        get_oprema_hrefs,
        get_usluge_ustanove,
    )

    return (
        CROSBI_BASE_URL,
        CrorisClient,
        ThreadPoolExecutor,
        as_completed,
        fetch_oprema_by_href,
        get_oprema_hrefs,
        get_projekti_po_ustanovi,
        get_sve_aktivne_ustanove,
        get_usluge_ustanove,
        mo,
        pd,
        px,
    )


@app.cell
def _header(mo):
    mo.md("""
    # CroRIS Explorer
    >  autor: Vedran Vyroubal, vedran.vyroubal(at)vuka.hr

    Odaberi ustanovu za prikaz svih dostupnih podataka.

    ---
    """)
    return


@app.cell
def _load_ustanove(CrorisClient, get_sve_aktivne_ustanove, mo):
    _load_err = None
    ustanove_map = {}
    dropdown_options = {}
    try:
        _client = CrorisClient()
        _all = get_sve_aktivne_ustanove(client=_client)
        _sorted = sorted(_all, key=lambda u: u.puni_naziv or u.kratki_naziv or "")
        ustanove_map = {str(u.id): u for u in _sorted}
        dropdown_options = {
            f"{u.kratica or '?'} — {u.puni_naziv or u.kratki_naziv or 'Nepoznato'}": str(u.id)
            for u in _sorted
        }
    except Exception as _e:
        _load_err = str(_e)

    if _load_err:
        mo.stop(True, mo.callout(mo.md(
            f"**Greška pri učitavanju popisa ustanova.**\n\n"
            f"CroRIS API nije dostupan. Pokušaj ponovo za koji trenutak.\n\n"
            f"```\n{_load_err}\n```"
        ), kind="danger"))
    return dropdown_options, ustanove_map


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
def _pub_header(CROSBI_BASE_URL, CrorisClient, mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)

    _uid = ustanova_dropdown.value
    pub_count = 0
    pub_error = None
    try:
        _crosbi_data = CrorisClient().get(f"{CROSBI_BASE_URL}/ustanova/{_uid}")
        pub_count = len(_crosbi_data.get("_links", {}).get("publikacije", []))
    except Exception as _e:
        _status = getattr(getattr(_e, "response", None), "status_code", None)
        if _status != 404:
            pub_error = f"Greška: {_e}"

    if pub_error:
        mo.vstack([
            mo.md("---\n## Publikacije (CROSBI)"),
            mo.callout(mo.md(f"**CROSBI greška:** {pub_error}"), kind="warn"),
        ])
    elif pub_count == 0:
        mo.vstack([
            mo.md("---\n## Publikacije (CROSBI)"),
            mo.callout(mo.md("Nema CROSBI publikacija za ovu ustanovu."), kind="neutral"),
        ])
    else:
        mo.vstack([
            mo.md("---\n## Publikacije (CROSBI)"),
            mo.hstack([mo.stat(label="CROSBI publikacije", value=str(pub_count))], gap=3),
        ])
    return (pub_count,)


@app.cell
def _pub_loader(mo, pub_count):
    pub_btn = mo.ui.run_button(label=f"Učitaj publikacije ({pub_count})")
    pub_refresh = mo.ui.checkbox(label="Prisilno osvježi (zaobiđi cache)")
    mo.vstack([pub_btn, pub_refresh])
    return pub_btn, pub_refresh


@app.cell
def _pub_fetch(
    CROSBI_BASE_URL,
    CrorisClient,
    ThreadPoolExecutor,
    as_completed,
    mo,
    pub_btn,
    pub_count,
    pub_refresh,
    ustanova_dropdown,
):
    import datetime as _dt_pub
    import json as _json_pub
    import os as _os_pub
    import tempfile as _tempfile_pub
    import time as _time_pub

    def _atomic_write_pub(path, data):
        _dir = _os_pub.path.dirname(path)
        with _tempfile_pub.NamedTemporaryFile("w", dir=_dir, delete=False, suffix=".tmp") as _tf:
            _json_pub.dump(data, _tf, ensure_ascii=False)
            _tf.flush()
            _os_pub.fsync(_tf.fileno())
        _os_pub.replace(_tf.name, path)

    mo.stop(ustanova_dropdown.value is None)

    _uid_pub = ustanova_dropdown.value
    _CACHE_DIR_PUB = _os_pub.path.join(_os_pub.path.dirname(__file__), ".cache")
    _os_pub.makedirs(_CACHE_DIR_PUB, exist_ok=True)
    _cache_file_pub = _os_pub.path.join(_CACHE_DIR_PUB, f"pub_{_uid_pub}.json")
    _MAX_AGE_H_PUB = 24

    def _pub_cache_fresh():
        if not _os_pub.path.exists(_cache_file_pub):
            return False
        return (_time_pub.time() - _os_pub.path.getmtime(_cache_file_pub)) < _MAX_AGE_H_PUB * 3600

    _use_cache_pub = _pub_cache_fresh() and not pub_refresh.value
    if not _use_cache_pub:
        mo.stop(not pub_btn.value,
            mo.callout(mo.md("Pritisni **Učitaj publikacije**."), kind="neutral"))

    pub_rows = []
    _pub_err = None
    _from_cache_pub = False

    try:
        if _use_cache_pub:
            with open(_cache_file_pub) as _f:
                pub_rows = _json_pub.load(_f)
            _from_cache_pub = True
        else:
            _client_pub = CrorisClient()
            with mo.status.spinner(title="Dohvaćam popis publikacija..."):
                _crosbi_data = _client_pub.get(f"{CROSBI_BASE_URL}/ustanova/{_uid_pub}")
                _urls = [
                    lnk["href"]
                    for lnk in _crosbi_data.get("_links", {}).get("publikacije", [])
                ]

            def _fetch_pub(url):
                try:
                    return CrorisClient().get(url)
                except Exception:
                    return None

            _total_pub = len(_urls)
            with ThreadPoolExecutor(max_workers=10) as _pool_pub:
                _futures_pub = {_pool_pub.submit(_fetch_pub, u): u for u in _urls}
                _done_pub = 0
                with mo.status.progress_bar(
                    total=_total_pub,
                    title=f"Dohvaćam publikacije ({_total_pub})...",
                    subtitle=f"0 / {_total_pub}",
                    show_rate=True,
                    show_eta=True,
                ) as _bar_pub:
                    for _fut_pub in as_completed(_futures_pub):
                        _d = _fut_pub.result()
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
                        _done_pub += 1
                        _bar_pub.update(increment=1, subtitle=f"{_done_pub} / {_total_pub}")

            _atomic_write_pub(_cache_file_pub, pub_rows)
    except Exception as _e:
        _pub_err = str(_e)

    if _pub_err:
        mo.callout(mo.md(f"**Greška:** {_pub_err}"), kind="danger")
    elif _from_cache_pub:
        _mtime_pub = _dt_pub.datetime.fromtimestamp(_os_pub.path.getmtime(_cache_file_pub)).strftime("%d.%m.%Y %H:%M")
        mo.callout(mo.md(
            f"Učitano iz cachea ({_mtime_pub}) — **{len(pub_rows)}** publikacija. "
            f"Za svježe podatke označi *Prisilno osvježi*."
        ), kind="info")
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
def _proj_section_header(mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)
    mo.md("""
    ---
    ## Projekti (CroRIS)
    """)
    return


@app.cell
def _proj_loader(mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)
    proj_btn = mo.ui.run_button(label="Učitaj projekte")
    proj_refresh = mo.ui.checkbox(label="Prisilno osvježi (zaobiđi cache)")
    mo.vstack([proj_btn, proj_refresh])
    return proj_btn, proj_refresh


@app.cell
def _proj_fetch(
    ThreadPoolExecutor,
    get_projekti_po_ustanovi,
    mo,
    proj_btn,
    proj_refresh,
    ustanova_dropdown,
    ustanove_map,
):
    import datetime as _dt_p
    import json as _json_p
    import os as _os_p
    import tempfile as _tempfile_p
    import time as _time_p

    def _atomic_write_p(path, data):
        _dir = _os_p.path.dirname(path)
        with _tempfile_p.NamedTemporaryFile("w", dir=_dir, delete=False, suffix=".tmp") as _tf:
            _json_p.dump(data, _tf, ensure_ascii=False)
            _tf.flush()
            _os_p.fsync(_tf.fileno())
        _os_p.replace(_tf.name, path)

    mo.stop(ustanova_dropdown.value is None)

    _uid_p = ustanova_dropdown.value
    _mbu   = ustanove_map[_uid_p].mbu or ""
    _CACHE_DIR_P = _os_p.path.join(_os_p.path.dirname(__file__), ".cache")
    _os_p.makedirs(_CACHE_DIR_P, exist_ok=True)
    _cache_file_p = _os_p.path.join(_CACHE_DIR_P, f"projekti_{_uid_p}.json")
    _MAX_AGE_H_P = 24

    proj_rows  = []
    proj_error = None
    _from_cache_p = False

    def _proj_cache_fresh():
        if not _os_p.path.exists(_cache_file_p):
            return False
        return (_time_p.time() - _os_p.path.getmtime(_cache_file_p)) < _MAX_AGE_H_P * 3600

    def _to_row(p):
        return {
            "id":         p.id,
            "sifra":      p.hr_sifra_projekta,
            "akronim":    p.acro,
            "naziv_hr":   p.get_title("hr"),
            "naziv_en":   p.get_title("en"),
            "tip":        p.tip_projekta.naziv if p.tip_projekta else None,
            "pocetak":    p.pocetak,
            "kraj":       p.kraj,
            "total_cost": p.total_cost,
            "currency":   p.currency_code,
            "uri":        p.uri,
            "verified":   p.verified,
        }

    _use_cache_p = _proj_cache_fresh() and not proj_refresh.value
    if not _use_cache_p:
        mo.stop(not proj_btn.value,
            mo.callout(mo.md("Pritisni **Učitaj projekte**."), kind="neutral"))

    try:
        if _use_cache_p:
            with open(_cache_file_p) as _f:
                proj_rows = _json_p.load(_f)
            _from_cache_p = True
        else:
            _ESTIMATED_S = 40.0
            with ThreadPoolExecutor(max_workers=1) as _pool_p:
                _fut_p = _pool_p.submit(get_projekti_po_ustanovi, _mbu)
                _t0_p = _time_p.time()
                _last_pct = 0
                with mo.status.progress_bar(
                    total=100,
                    title="Dohvaćam projekte... ",
                    subtitle="0%  ·  0s",
                    show_rate=False,
                    show_eta=False,
                ) as _bar_p:
                    while not _fut_p.done():
                        _elapsed = _time_p.time() - _t0_p
                        _pct = min(95, int(_elapsed / _ESTIMATED_S * 100))
                        if _pct > _last_pct:
                            _bar_p.update(
                                increment=_pct - _last_pct,
                                subtitle=f"{_pct}%  ·  {_elapsed:.0f}s",
                            )
                            _last_pct = _pct
                        _time_p.sleep(0.3)
                    _fetched = _fut_p.result()
                    _bar_p.update(
                        increment=100 - _last_pct,
                        subtitle=f"100%  ·  {_time_p.time() - _t0_p:.0f}s",
                    )
            proj_rows = [_to_row(p) for p in _fetched]
            _atomic_write_p(_cache_file_p, proj_rows)
    except Exception as _e:
        proj_error = str(_e)

    if proj_error:
        mo.callout(mo.md(f"**Greška:** {proj_error}"), kind="danger")
    elif _from_cache_p:
        _mtime_p = _dt_p.datetime.fromtimestamp(_os_p.path.getmtime(_cache_file_p)).strftime("%d.%m.%Y %H:%M")
        mo.callout(mo.md(
            f"Učitano iz cachea ({_mtime_p}) — **{len(proj_rows)}** projekata. "
            f"Za svježe podatke označi *Prisilno osvježi*."
        ), kind="info")
    elif not proj_rows:
        mo.callout(mo.md("Nema projekata za ovu ustanovu."), kind="neutral")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(proj_rows)}** projekata."), kind="success")
    return (proj_rows,)


@app.cell
def _proj_df(mo, pd, proj_rows):
    mo.stop(not proj_rows)
    proj_df = pd.DataFrame(proj_rows)
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
def _oprema_header(mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)
    mo.md("""
    ---
    ## Oprema (CroRIS)
    """)
    return


@app.cell
def _oprema_loader(mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)
    oprema_btn = mo.ui.run_button(label="Učitaj opremu i usluge")
    oprema_refresh = mo.ui.checkbox(label="Prisilno osvježi (zaobiđi cache)")
    mo.vstack([oprema_btn, oprema_refresh])
    return oprema_btn, oprema_refresh


@app.cell
def _oprema_fetch(
    ThreadPoolExecutor,
    as_completed,
    fetch_oprema_by_href,
    get_oprema_hrefs,
    get_usluge_ustanove,
    mo,
    oprema_btn,
    oprema_refresh,
    ustanova_dropdown,
):
    import datetime as _dt
    import json as _json
    import os as _os
    import tempfile as _tempfile
    import time as _time

    def _atomic_write(path, data):
        _dir = _os.path.dirname(path)
        with _tempfile.NamedTemporaryFile("w", dir=_dir, delete=False, suffix=".tmp") as _tf:
            _json.dump(data, _tf, ensure_ascii=False)
            _tf.flush()
            _os.fsync(_tf.fileno())
        _os.replace(_tf.name, path)

    mo.stop(ustanova_dropdown.value is None)

    _CACHE_DIR = _os.path.join(_os.path.dirname(__file__), ".cache")
    _os.makedirs(_CACHE_DIR, exist_ok=True)
    _uid = int(ustanova_dropdown.value)
    _cache_file = _os.path.join(_CACHE_DIR, f"oprema_{_uid}.json")
    _MAX_AGE_H = 24

    oprema_rows = []
    usluge_rows = []
    _err = None
    _from_cache = False
    _fetch_errors = []

    def _cache_fresh():
        if not _os.path.exists(_cache_file):
            return False
        return (_time.time() - _os.path.getmtime(_cache_file)) < _MAX_AGE_H * 3600

    _use_cache = _cache_fresh() and not oprema_refresh.value
    if not _use_cache:
        mo.stop(not oprema_btn.value,
            mo.callout(mo.md("Pritisni **Učitaj opremu i usluge**."), kind="neutral"))

    try:
        if _use_cache:
            with open(_cache_file) as _f:
                _cached = _json.load(_f)
            oprema_rows = _cached["oprema"]
            usluge_rows = _cached["usluge"]
            _from_cache = True
        else:
            with mo.status.spinner(title="Dohvaćam usluge..."):
                _usluge_list = list(get_usluge_ustanove(_uid))

            _hrefs = get_oprema_hrefs(_uid)
            _total = len(_hrefs)
            _oprema_list = []
            with mo.status.progress_bar(
                total=_total,
                title=f"Dohvaćam opremu ({_total} stavki)...",
                subtitle=f"0 / {_total}",
                show_rate=True,
                show_eta=True,
            ) as _bar:
                with ThreadPoolExecutor(max_workers=10) as _pool:
                    _futures = {_pool.submit(fetch_oprema_by_href, h): h for h in _hrefs}
                    _done = 0
                    for _fut in as_completed(_futures):
                        _href = _futures[_fut]
                        try:
                            _oprema_list.append(_fut.result())
                        except Exception as _exc:
                            _fetch_errors.append(_href)
                        _done += 1
                        _bar.update(increment=1, subtitle=f"{_done} / {_total}")

            for o in _oprema_list:
                oprema_rows.append({
                    "id":            o.id,
                    "model":         o.model or "",
                    "proizvodjac":   o.proizvodjac or "",
                    "inventarni_br": o.inventarni_broj or "",
                    "godina_proiz":  o.godina_proizvodnje,
                    "datum_nabave":  o.datum_nabave or "",
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
            _atomic_write(_cache_file, {"oprema": oprema_rows, "usluge": usluge_rows})
    except Exception as _e:
        _err = str(_e)

    if _err:
        mo.callout(mo.md(f"**Greška:** {_err}"), kind="danger")
    elif _from_cache:
        _mtime = _dt.datetime.fromtimestamp(_os.path.getmtime(_cache_file)).strftime("%d.%m.%Y %H:%M")
        mo.callout(mo.md(
            f"Učitano iz cachea ({_mtime}) — **{len(oprema_rows)}** opreme, **{len(usluge_rows)}** usluga. "
            f"Za svježe podatke označi *Prisilno osvježi*."
        ), kind="info")
    else:
        _warn_part = f" (**{len(_fetch_errors)}** neuspješnih dohvata)" if _fetch_errors else ""
        mo.callout(mo.md(
            f"Dohvaćeno **{len(oprema_rows)}** opreme i **{len(usluge_rows)}** usluga{_warn_part}."
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
        _k = _k.sort_values("broj")
        _bar = px.bar(_k, x="broj", y="kategorija", orientation="h",
                      title=f"Oprema po kategoriji ({len(oprema_df)})",
                      color="broj", color_continuous_scale="Teal",
                      text="broj")
        _bar.update_layout(yaxis_title=None, xaxis_title="broj", showlegend=False,
                           height=max(250, len(_k) * 40))
        _bar.update_traces(textposition="outside")
        _charts.append(mo.as_html(_bar))
    mo.vstack(_charts)
    return


@app.cell
def _oprema_table(mo, oprema_df, usluge_df):
    mo.stop(oprema_df.empty and usluge_df.empty)
    _tabs = {}
    if not oprema_df.empty:
        _tabs["Oprema"] = mo.ui.dataframe(
            oprema_df[["naziv_hr", "model", "proizvodjac", "godina_proiz", "datum_nabave", "kategorija", "stanje", "ustanova", "lokacija"]]
        )
    if not usluge_df.empty:
        _tabs["Usluge"] = mo.ui.dataframe(
            usluge_df[["naziv_hr", "ustanova", "aktivnost"]]
        )
    mo.ui.tabs(_tabs)
    return


@app.cell
def _znan_header(mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)
    mo.md("""
    ---
    ## Znanstvenici (CROSBI pretraga)

    Pretraži CROSBI profil znanstvenika po matičnom broju znanstvenika (MBZ).
    """)
    return


@app.cell
def _znan_inputs(mo, ustanova_dropdown):
    mo.stop(ustanova_dropdown.value is None)
    znan_mbz_input = mo.ui.text(placeholder="npr. 123456", label="Matični broj znanstvenika (MBZ)")
    znan_search_btn = mo.ui.run_button(label="Pretraži")
    mo.hstack([znan_mbz_input, znan_search_btn], gap=2)
    return znan_mbz_input, znan_search_btn


@app.cell
def _znan_fetch(
    CROSBI_BASE_URL,
    CrorisClient,
    ThreadPoolExecutor,
    as_completed,
    mo,
    znan_mbz_input,
    znan_search_btn,
):
    mo.stop(not znan_search_btn.value,
        mo.callout(mo.md("Unesi MBZ i pritisni **Pretraži**."), kind="neutral"))
    mo.stop(not znan_mbz_input.value,
        mo.callout(mo.md("Unesi matični broj znanstvenika (MBZ)."), kind="warn"))

    znan_data = None
    znan_pubs = []
    _err_z = None
    try:
        with mo.status.spinner(title="Dohvaćam podatke o znanstveniku..."):
            znan_data = CrorisClient().get(
                f"{CROSBI_BASE_URL}/osoba/maticni-broj/{znan_mbz_input.value.strip()}"
            )

        _pub_list = znan_data.get("publikacijaList") or []
        _hrefs = [p["link"]["href"] for p in _pub_list if p.get("link", {}).get("href")]
        if _hrefs:
            def _fetch_pub(href):
                return CrorisClient().get(href)

            with ThreadPoolExecutor(max_workers=10) as _pool_z:
                _futs = {_pool_z.submit(_fetch_pub, h): h for h in _hrefs}
                with mo.status.progress_bar(
                    total=len(_hrefs),
                    title=f"Dohvaćam detalje publikacija ({len(_hrefs)})...",
                    subtitle=f"0 / {len(_hrefs)}",
                    show_rate=True,
                    show_eta=True,
                ) as _bar_z:
                    _done_z = 0
                    for _fut_z in as_completed(_futs):
                        try:
                            znan_pubs.append(_fut_z.result())
                        except Exception:
                            pass
                        _done_z += 1
                        _bar_z.update(increment=1, subtitle=f"{_done_z} / {len(_hrefs)}")
    except Exception as _e:
        _err_z = str(_e)

    if _err_z:
        mo.stop(True, mo.callout(mo.md(f"**Greška:** {_err_z}"), kind="danger"))
    return znan_data, znan_pubs


@app.cell
def _znan_profile(mo, znan_data, znan_pubs):
    mo.stop(znan_data is None)
    _titula = znan_data.get("titulaIspredImena") or ""
    _ime    = znan_data.get("ime") or ""
    _prezime = znan_data.get("prezime") or ""
    _funkcija = (znan_data.get("funkcija") or {}).get("naziv") or "—"
    _pubs = znan_pubs
    mo.vstack([
        mo.md(f"### {_titula} {_ime} {_prezime}".strip()),
        mo.md(f"""
    | Polje | Vrijednost |
    |---|---|
    | CROSBI ID | {znan_data.get("crorisId") or "—"} |
    | Funkcija | {_funkcija} |
    | Broj publikacija (CROSBI) | {len(_pubs)} |
    """),
    ])
    return


@app.cell
def _znan_pubs(mo, pd, znan_data, znan_pubs):
    mo.stop(znan_data is None)
    mo.stop(not znan_pubs, mo.md("_Nema CROSBI publikacija za ovog znanstvenika._"))
    _rows = []
    for _p in znan_pubs:
        _rows.append({
            "naslov":  _p.get("naslov") or "",
            "godina":  _p.get("godina"),
            "vrsta":   _p.get("vrsta") or "",
            "tip":     _p.get("tip") or "",
            "casopis": _p.get("casopis") or "",
            "doi":     _p.get("doi") or "",
            "autori":  _p.get("autori") or "",
        })
    _pubs_df = pd.DataFrame(_rows).sort_values("godina", ascending=False, na_position="last")
    mo.vstack([
        mo.md(f"### Publikacije ({len(_rows)})"),
        mo.ui.dataframe(_pubs_df[["naslov", "godina", "vrsta", "tip", "casopis", "doi", "autori"]]),
    ])
    return


if __name__ == "__main__":
    app.run()
