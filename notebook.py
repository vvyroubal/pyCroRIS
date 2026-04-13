"""
CroRIS Explorer — interaktivni Marimo notebook za pregled i vizualizaciju podataka.

Pokriva sve CroRIS API module:
  - Projekti API, MOZVAG
  - Ustanove API (MZO upisnik, PPG, CroRIS ustanove)
  - CROSBI API (bibliografske publikacije)
  - Oprema API
  - Časopisi API
  - Događanja API
  - Znanstvenici API

Pokretanje:
    marimo run notebook.py       # read-only web app
    marimo edit notebook.py      # interaktivni editor
"""

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="wide", app_title="CroRIS Explorer")


@app.cell
def _imports():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))

    import marimo as mo
    import pandas as pd
    import plotly.express as px

    return mo, pd, px


@app.cell
def _header(mo):
    return mo.md("""
    # CroRIS Explorer

    Interaktivni pregled podataka iz svih [CroRIS REST API](https://wiki.srce.hr/spaces/CRORIS/pages/49283931/Programska+su%C4%8Delja+CroRIS-a) modula.

    ---
    """)


@app.cell
def _auth_inputs(mo):
    username_input = mo.ui.text(placeholder="korisničko ime", label="Korisničko ime")
    password_input = mo.ui.text(placeholder="lozinka", label="Lozinka", kind="password")
    page_size_input = mo.ui.slider(start=5, stop=100, step=5, value=50, label="Veličina stranice")
    mo.hstack([username_input, password_input, page_size_input], gap=2)
    return page_size_input, password_input, username_input


@app.cell
def _build_client(mo, page_size_input, password_input, username_input):
    import os
    from crosbi.config import Config
    from crosbi.client import CrorisClient

    _u = username_input.value or os.getenv("CRORIS_USERNAME", "")
    _p = password_input.value or os.getenv("CRORIS_PASSWORD", "")
    cfg = Config(username=_u, password=_p, page_size=page_size_input.value)
    client = CrorisClient(cfg)

    _status = (
        mo.callout(mo.md("Autentikacija konfigurirana."), kind="success")
        if _u
        else mo.callout(mo.md("Nisu uneseni kredencijali — postavi u `.env` ili unesi iznad."), kind="warn")
    )
    # Koristi mo.output.replace() jer ćelija mora i vratiti client (za dalje ćelije) i prikazati status
    mo.output.replace(_status)
    return (client,)


@app.cell
def _mode_selector(mo):
    return mo.md("""
    ---
    ## Odabir podataka
    """)


@app.cell
def _mode(mo):
    mode = mo.ui.dropdown(
        options={
            # Projekti API
            "Projekti — MOZVAG ustanove":           "mozvag_ustanove",
            "Projekti — MOZVAG projekti ustanove":  "mozvag_projekti",
            "Projekti — MOZVAG financijeri":        "mozvag_financijeri",
            "Projekti — MOZVAG osoba po MBZ-u":     "mozvag_osoba_mbz",
            "Projekti — po MBU ustanove":           "projekti_mbu",
            "Projekti — detalji projekta":          "projekt_id",
            "Projekti — osobe na projektu":         "osobe_projekta",
            "Projekti — financijeri projekta":      "financijeri_proj",
            "Projekti — publikacije projekta":      "publikacije_proj",
            "Projekti — ustanove na projektu":      "ustanove_projekta",
            # Ustanove API
            "Ustanove — sve aktivne (MZO)":         "upisnik_sve",
            "Ustanove — znanstvene":                "upisnik_znan",
            "Ustanove — visoka učilišta":           "upisnik_vu",
            "Ustanove — javni znan. instituti":     "upisnik_jzi",
            "Ustanove — PPG područja":              "ppg_podrucja",
            # CROSBI API
            "CROSBI — publikacije osobe (MBZ)":     "crosbi_osoba_mbz",
            "CROSBI — publikacija po ID-u":         "crosbi_pub_id",
            # Oprema API
            "Oprema — popis":                       "oprema_list",
            "Oprema — popis usluga":                "oprema_usluge",
            # Časopisi API
            "Časopisi — popis":                     "casopisi_list",
            "Časopisi — detalji časopisa":          "casopis_detalj",
            "Časopisi — publikacije časopisa":      "publikacije_casopisa",
            # Događanja API
            "Događanja — popis":                    "dogadanja_list",
            "Događanja — detalji događanja":        "dogadanje_detalj",
            # Znanstvenici API
            "Znanstvenici — pretraga po OIB-u":     "znan_oib",
            "Znanstvenici — pretraga po MBZ-u":     "znan_mbz",
            "Znanstvenici — akreditacije org. jedinice": "znan_akred",
            "Znanstvenici — svi (cached)":          "svi_znanstvenici",
        },
        value="Projekti — MOZVAG ustanove",
        label="Što želiš dohvatiti?",
    )
    mode
    return (mode,)


@app.cell
def _conditional_inputs(mo, mode):
    show = mode.value

    ustanova_id_input = (
        mo.ui.number(start=1, stop=999999, step=1, value=1, label="ID ustanove")
        if show in ("mozvag_projekti", "znan_akred")
        else None
    )
    godina_input = (
        mo.ui.number(start=2000, stop=2030, step=1, value=2024, label="Godina")
        if show in ("mozvag_projekti", "mozvag_osoba_mbz")
        else None
    )
    projekt_id_input = (
        mo.ui.number(start=1, stop=9999999, step=1, value=1, label="ID projekta")
        if show in ("projekt_id", "osobe_projekta", "financijeri_proj", "publikacije_proj", "ustanove_projekta")
        else None
    )
    mbu_input = (
        mo.ui.text(placeholder="npr. 0000000", label="MBU ustanove")
        if show == "projekti_mbu"
        else None
    )
    mbz_input = (
        mo.ui.text(placeholder="npr. 123456", label="MBZ")
        if show in ("crosbi_osoba_mbz", "znan_mbz", "mozvag_osoba_mbz")
        else None
    )
    oib_input = (
        mo.ui.text(placeholder="11-znamenkasti OIB", label="OIB")
        if show == "znan_oib"
        else None
    )
    pub_id_input = (
        mo.ui.number(start=1, stop=9999999, step=1, value=1, label="ID publikacije")
        if show == "crosbi_pub_id"
        else None
    )
    casopis_id_input = (
        mo.ui.number(start=1, stop=9999999, step=1, value=1, label="ID časopisa")
        if show in ("casopis_detalj", "publikacije_casopisa")
        else None
    )
    dogadanje_id_input = (
        mo.ui.number(start=1, stop=9999999, step=1, value=1, label="ID događanja")
        if show == "dogadanje_detalj"
        else None
    )

    fetch_btn = mo.ui.run_button(label="Dohvati podatke")

    _inputs = [x for x in [
        ustanova_id_input, godina_input, projekt_id_input,
        mbu_input, mbz_input, oib_input, pub_id_input, casopis_id_input, dogadanje_id_input, fetch_btn,
    ] if x is not None]

    mo.hstack(_inputs, gap=2)
    return (
        casopis_id_input,
        dogadanje_id_input,
        fetch_btn,
        godina_input,
        mbu_input,
        mbz_input,
        oib_input,
        projekt_id_input,
        pub_id_input,
        ustanova_id_input,
    )


@app.cell
def _fetch(
    casopis_id_input,
    client,
    dogadanje_id_input,
    fetch_btn,
    godina_input,
    mbu_input,
    mbz_input,
    mo,
    mode,
    oib_input,
    projekt_id_input,
    pub_id_input,
    ustanova_id_input,
):
    from crosbi.endpoints import (
        mozvag, projekti, osobe, financijeri,
        upisnik, publikacije_crosbi, oprema_api, casopisi,
        dogadanja, znanstvenici,
    )
    import traceback

    result = None
    error_msg = None

    mo.stop(
        not fetch_btn.value,
        mo.callout(mo.md("Pritisni **Dohvati podatke**."), kind="neutral"),
    )

    try:
        with mo.status.spinner(title="Dohvaćam podatke..."):
            s = mode.value
            if s == "mozvag_ustanove":
                result = mozvag.get_ustanove(client=client)
            elif s == "mozvag_projekti":
                result = mozvag.get_projekti_ustanove(
                    int(ustanova_id_input.value), int(godina_input.value), client=client
                )
            elif s == "projekti_mbu":
                result = projekti.get_projekti_po_ustanovi(mbu_input.value, client=client)
            elif s == "projekt_id":
                result = [projekti.get_projekt(int(projekt_id_input.value), client=client)]
            elif s == "osobe_projekta":
                result = osobe.get_osobe_projekta(int(projekt_id_input.value), client=client)
            elif s == "financijeri_proj":
                result = financijeri.get_financijeri_projekta(int(projekt_id_input.value), client=client)
            elif s == "publikacije_proj":
                result = [publikacije_crosbi.get_publikacije_projekta(int(projekt_id_input.value), client=client)]  # noqa: E501
            elif s == "upisnik_sve":
                result = upisnik.get_sve_aktivne_ustanove(client=client)
            elif s == "upisnik_znan":
                result = upisnik.get_znanstvene_ustanove(client=client)
            elif s == "upisnik_vu":
                result = upisnik.get_visoka_ucilista(client=client)
            elif s == "upisnik_jzi":
                result = upisnik.get_javni_znanstveni_instituti(client=client)
            elif s == "ppg_podrucja":
                result = upisnik.get_sva_podrucja(client=client)
            elif s == "mozvag_financijeri":
                result = mozvag.get_financijere(client=client)
            elif s == "mozvag_osoba_mbz":
                result = [mozvag.get_osoba_po_mbz(mbz_input.value, int(godina_input.value), client=client)]
            elif s == "crosbi_osoba_mbz":
                result = [publikacije_crosbi.get_publikacije_osobe_by_mbz(mbz_input.value, client=client)]
            elif s == "crosbi_pub_id":
                result = [publikacije_crosbi.get_publikacija(int(pub_id_input.value), client=client)]
            elif s == "oprema_list":
                result = list(oprema_api.list_oprema(client=client))
            elif s == "oprema_usluge":
                result = list(oprema_api.list_usluge(client=client))
            elif s == "casopisi_list":
                result = list(casopisi.list_casopisi(client=client))
            elif s == "casopis_detalj":
                result = [casopisi.get_casopis(int(casopis_id_input.value), client=client)]
            elif s == "publikacije_casopisa":
                result = casopisi.get_publikacije_casopisa(int(casopis_id_input.value), client=client)
            elif s == "dogadanja_list":
                result = list(dogadanja.list_dogadanja(client=client))
            elif s == "ustanove_projekta":
                from crosbi.endpoints import ustanove as ustanove_ep
                result = ustanove_ep.get_ustanove_projekta(int(projekt_id_input.value), client=client)
            elif s == "dogadanje_detalj":
                result = [dogadanja.get_dogadanje(int(dogadanje_id_input.value), client=client)]
            elif s == "znan_oib":
                result = [znanstvenici.get_znanstvenik_by_oib(oib_input.value, client=client)]
            elif s == "znan_mbz":
                result = [znanstvenici.get_znanstvenik_by_mbz(mbz_input.value, client=client)]
            elif s == "znan_akred":
                result = znanstvenici.get_akreditacije_ustanove(int(ustanova_id_input.value), client=client)
            elif s == "svi_znanstvenici":
                result = znanstvenici.get_svi_znanstvenici(client=client)
    except Exception as e:
        error_msg = f"**Greška:** {e}\n\n```\n{traceback.format_exc()}\n```"

    if error_msg:
        mo.callout(mo.md(error_msg), kind="danger")
    elif result is not None:
        mo.callout(mo.md(f"Dohvaćeno **{len(result)}** zapisa."), kind="success")
    result = result if result is not None else []
    return error_msg, result


@app.cell
def _to_df(error_msg, mo, pd, result):
    mo.stop(error_msg is not None or not result)
    rows = [
        item.to_dict() if hasattr(item, "to_dict") else vars(item)
        for item in result
        if item is not None
    ]
    df = pd.DataFrame(rows) if rows else pd.DataFrame()
    mo.md("---\n## Tablica rezultata")
    return (df,)


@app.cell
def _table(df, mo):
    mo.stop(df is None or df.empty)
    mo.ui.dataframe(df)
    return


@app.cell
def _viz_header(df, mo):
    mo.stop(df is None or df.empty)
    mo.md("---\n## Vizualizacije")
    return


@app.cell
def _viz_mozvag_ustanove(df, mo, mode, px):
    mo.stop(mode.value != "mozvag_ustanove")
    _fig = px.bar(
        df.dropna(subset=["grad"]).groupby("grad").size().reset_index(name="broj"),
        x="grad", y="broj",
        title="Broj ustanova po gradu",
        color="broj", color_continuous_scale="Blues",
    )
    _fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    mo.as_html(_fig)
    return


@app.cell
def _viz_mozvag_projekti(df, mo, mode, pd, px):
    mo.stop(mode.value != "mozvag_projekti")

    _v = df["vrsta"].value_counts().reset_index()
    _v.columns = ["vrsta", "broj"]
    _pie = px.pie(_v, names="vrsta", values="broj", title="Projekti po vrsti", hole=0.4)

    _f = (
        df["financijeri"].str.split(", ").explode().str.strip()
        .replace("", pd.NA).dropna().value_counts().head(15).reset_index()
    )
    _f.columns = ["financijer", "broj"]
    _bar = px.bar(_f, x="broj", y="financijer", orientation="h",
                  title="Top 15 financijera", color="broj",
                  color_continuous_scale="Teal")
    _bar.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)

    _tl = df.dropna(subset=["start_date", "end_date"]).copy()
    _tl["start_date"] = pd.to_datetime(_tl["start_date"], errors="coerce")
    _tl["end_date"] = pd.to_datetime(_tl["end_date"], errors="coerce")
    _tl = _tl.dropna(subset=["start_date", "end_date"]).head(40)
    _gantt = (
        px.timeline(_tl, x_start="start_date", x_end="end_date", y="naziv",
                    color="vrsta", title="Timeline projekata (prvih 40)")
        if not _tl.empty
        else None
    )
    if _gantt:
        _gantt.update_yaxes(autorange="reversed")
        _gantt.update_layout(height=max(400, len(_tl) * 25))

    mo.vstack([mo.as_html(_pie), mo.as_html(_bar)] + ([mo.as_html(_gantt)] if _gantt else []))
    return


@app.cell
def _viz_upisnik(df, mo, mode, px):
    mo.stop(mode.value not in ("upisnik_sve", "upisnik_znan", "upisnik_vu", "upisnik_jzi"))
    if "grad" in df.columns:
        _fig = px.bar(
            df.dropna(subset=["grad"]).groupby("grad").size().reset_index(name="broj"),
            x="grad", y="broj", title="Ustanove po gradu",
            color="broj", color_continuous_scale="Greens",
        )
        _fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        mo.as_html(_fig)
    return


@app.cell
def _viz_osobe(df, mo, mode, px):
    mo.stop(mode.value != "osobe_projekta")
    if "uloga" in df.columns:
        _v = df["uloga"].value_counts().reset_index()
        _v.columns = ["uloga", "broj"]
        _fig = px.pie(_v, names="uloga", values="broj", title="Uloge na projektu", hole=0.3)
        mo.as_html(_fig)
    return


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
            mo.as_html(_fig)
    return


@app.cell
def _viz_akreditacije(df, mo, mode, px):
    mo.stop(mode.value != "znan_akred")
    charts = []
    if "vrsta_zaposlenja" in df.columns and not df.empty:
        _v = df["vrsta_zaposlenja"].value_counts().reset_index()
        _v.columns = ["vrsta", "broj"]
        charts.append(mo.as_html(
            px.pie(_v, names="vrsta", values="broj",
                   title="Akreditacije po vrsti zaposlenja", hole=0.4)
        ))
    if "podrucje" in df.columns and not df.empty:
        _p = df["podrucje"].dropna().value_counts().reset_index()
        _p.columns = ["podrucje", "broj"]
        charts.append(mo.as_html(
            px.bar(_p, x="podrucje", y="broj",
                   title="Akreditacije po znanstvenom području",
                   color="broj", color_continuous_scale="Teal")
        ))
    if charts:
        mo.vstack(charts)
    return


@app.cell
def _viz_crosbi(df, mo, mode, px):
    mo.stop(mode.value != "crosbi_osoba_mbz")
    if "vrsta" in df.columns and not df.empty:
        _v = df["vrsta"].value_counts().reset_index()
        _v.columns = ["vrsta", "broj"]
        _pie = px.pie(_v, names="vrsta", values="broj",
                      title="Publikacije po vrsti", hole=0.4)
        mo.as_html(_pie)
    return


@app.cell
def _viz_casopisi(df, mo, mode, px):
    mo.stop(mode.value != "casopisi_list")
    if "drzava" in df.columns:
        _d = df["drzava"].value_counts().head(20).reset_index()
        _d.columns = ["drzava", "broj"]
        _fig = px.bar(_d, x="drzava", y="broj",
                      title="Časopisi po zemlji izdavanja (top 20)",
                      color="broj", color_continuous_scale="Oranges")
        _fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        mo.as_html(_fig)
    return


@app.cell
def _viz_dogadanja(df, mo, mode, pd, px):
    mo.stop(mode.value != "dogadanja_list")
    if "datum_pocetka" in df.columns:
        _df = df.dropna(subset=["datum_pocetka"]).copy()
        _df["godina"] = pd.to_datetime(_df["datum_pocetka"], errors="coerce").dt.year
        _y = _df.dropna(subset=["godina"]).groupby("godina").size().reset_index(name="broj")
        _fig = px.bar(_y, x="godina", y="broj",
                      title="Događanja po godini", color="broj",
                      color_continuous_scale="Purples")
        mo.as_html(_fig)
    return


@app.cell
def _viz_oprema(df, mo, mode, px):
    mo.stop(mode.value != "oprema_list")
    if "kategorija" in df.columns:
        _k = df["kategorija"].value_counts().reset_index()
        _k.columns = ["kategorija", "broj"]
        _fig = px.bar(_k, x="kategorija", y="broj",
                      title="Oprema po kategoriji",
                      color="broj", color_continuous_scale="Reds")
        _fig.update_layout(xaxis_tickangle=-30, showlegend=False)
        mo.as_html(_fig)
    return


@app.cell
def _viz_ppg(df, mo, mode, px):
    mo.stop(mode.value != "ppg_podrucja")
    if not df.empty and "sifra" in df.columns and "naziv" in df.columns:
        _fig = px.bar(df.sort_values("sifra"), x="sifra", y="naziv",
                      orientation="h", title="PPG Područja",
                      color_discrete_sequence=["#4e79a7"])
        _fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
        mo.as_html(_fig)
    return


@app.cell
def _viz_mozvag_financijeri(df, mo, mode, px):
    mo.stop(mode.value != "mozvag_financijeri")
    if "nadleznost" in df.columns and not df.empty:
        _n = df["nadleznost"].dropna().value_counts().reset_index()
        _n.columns = ["nadleznost", "broj"]
        if not _n.empty:
            _fig = px.bar(
                _n, x="broj", y="nadleznost", orientation="h",
                title="Financijeri po nadležnosti",
                color="broj", color_continuous_scale="Blues",
            )
            _fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
            mo.as_html(_fig)
    return


@app.cell
def _export_section(df, mo):
    mo.stop(df is None or df.empty)
    mo.md("---\n## Preuzimanje podataka")
    return


@app.cell
def _download(df, mo):
    mo.stop(df is None or df.empty)
    mo.hstack([
        mo.download(
            data=df.to_csv(index=False).encode("utf-8"),
            filename="crosbi_export.csv",
            mimetype="text/csv",
            label="Preuzmi CSV",
        ),
        mo.download(
            data=df.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"),
            filename="crosbi_export.json",
            mimetype="application/json",
            label="Preuzmi JSON",
        ),
    ], gap=2)
    return


if __name__ == "__main__":
    app.run()
