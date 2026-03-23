"""
CroRIS CROSBI — interaktivni Marimo notebook za pregled i vizualizaciju podataka.

Pokretanje:
    marimo run notebook.py       # read-only web app
    marimo edit notebook.py      # interaktivni editor
"""

import marimo

__generated_with = "0.8.0"
app = marimo.App(width="wide", app_title="CroRIS CROSBI Explorer")


@app.cell
def _imports():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))

    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    return mo, pd, px, go, sys, Path


@app.cell
def _header(mo):
    mo.md(
        """
        # CroRIS CROSBI Explorer

        Interaktivni pregled podataka iz [CroRIS Projekti API-ja](https://www.croris.hr/projekti-api).

        ---
        """
    )
    return


@app.cell
def _auth_ui(mo):
    mo.md("## Konfiguracija")
    return


@app.cell
def _auth_inputs(mo):
    username_input = mo.ui.text(
        placeholder="korisničko ime",
        label="Korisničko ime",
        kind="text",
    )
    password_input = mo.ui.text(
        placeholder="lozinka",
        label="Lozinka",
        kind="password",
    )
    page_size_input = mo.ui.slider(
        start=5, stop=100, step=5, value=50, label="Veličina stranice"
    )
    mo.hstack([username_input, password_input, page_size_input], gap=2)
    return username_input, password_input, page_size_input


@app.cell
def _build_client(mo, username_input, password_input, page_size_input):
    import os
    from crosbi.config import Config
    from crosbi.client import CrorisClient

    _username = username_input.value or os.getenv("CRORIS_USERNAME", "")
    _password = password_input.value or os.getenv("CRORIS_PASSWORD", "")

    cfg = Config(
        username=_username,
        password=_password,
        page_size=page_size_input.value,
    )
    client = CrorisClient(cfg)

    _auth_status = (
        mo.callout(mo.md("Autentikacija konfigurirana."), kind="success")
        if _username
        else mo.callout(
            mo.md("Nisu uneseni kredencijali. Unesite korisničko ime i lozinku ili postavite `CRORIS_USERNAME` i `CRORIS_PASSWORD` u `.env` datoteci."),
            kind="warn",
        )
    )
    _auth_status
    return cfg, client


@app.cell
def _section_divider(mo):
    mo.md("---\n## Odabir podataka")
    return


@app.cell
def _mode_selector(mo):
    mode = mo.ui.dropdown(
        options={
            "mozvag_ustanove": "MOZVAG — popis ustanova",
            "mozvag_projekti": "MOZVAG — projekti ustanove za godinu",
            "mozvag_osoba": "MOZVAG — sažetak projekata osobe",
            "projekt_id": "Detalji projekta po ID-u",
            "projekti_mbu": "Projekti ustanove po MBU kodu",
            "osobe_projekta": "Osobe na projektu",
            "publikacije_projekta": "Publikacije projekta",
            "financijeri_projekta": "Financijeri projekta",
        },
        value="mozvag_ustanove",
        label="Što želiš dohvatiti?",
        full_width=False,
    )
    mode
    return (mode,)


@app.cell
def _conditional_inputs(mo, mode):
    # Prikaži relevantne inpute ovisno o odabiru
    _inputs = []

    if mode.value in ("mozvag_projekti", "mozvag_osoba"):
        ustanova_id_input = mo.ui.number(
            start=1, stop=999999, step=1, value=1, label="ID ustanove"
        )
        _inputs.append(ustanova_id_input)
    else:
        ustanova_id_input = None

    if mode.value in ("mozvag_projekti", "mozvag_osoba"):
        godina_input = mo.ui.number(
            start=2000, stop=2030, step=1, value=2024, label="Godina"
        )
        _inputs.append(godina_input)
    else:
        godina_input = None

    if mode.value in ("projekt_id", "osobe_projekta", "publikacije_projekta", "financijeri_projekta"):
        projekt_id_input = mo.ui.number(
            start=1, stop=9999999, step=1, value=1, label="ID projekta"
        )
        _inputs.append(projekt_id_input)
    else:
        projekt_id_input = None

    if mode.value == "projekti_mbu":
        mbu_input = mo.ui.text(placeholder="npr. 0000000", label="MBU ustanove")
        _inputs.append(mbu_input)
    else:
        mbu_input = None

    if mode.value == "mozvag_osoba":
        mbz_input = mo.ui.text(placeholder="npr. 123456", label="MBZ istraživača")
        _inputs.append(mbz_input)
    else:
        mbz_input = None

    fetch_btn = mo.ui.run_button(label="Dohvati podatke")
    _inputs.append(fetch_btn)

    mo.hstack(_inputs, gap=2) if _inputs else None
    return (
        ustanova_id_input,
        godina_input,
        projekt_id_input,
        mbu_input,
        mbz_input,
        fetch_btn,
    )


@app.cell
def _fetch_data(
    mo,
    mode,
    client,
    fetch_btn,
    ustanova_id_input,
    godina_input,
    projekt_id_input,
    mbu_input,
    mbz_input,
):
    from crosbi.endpoints import mozvag, projekti, osobe, ustanove, publikacije, financijeri
    import traceback

    result = None
    error_msg = None

    mo.stop(not fetch_btn.value, mo.callout(mo.md("Pritisni **Dohvati podatke** za učitavanje."), kind="neutral"))

    try:
        with mo.status.spinner(title="Dohvaćam podatke..."):
            if mode.value == "mozvag_ustanove":
                result = mozvag.get_ustanove(client=client)

            elif mode.value == "mozvag_projekti":
                result = mozvag.get_projekti_ustanove(
                    ustanova_id=int(ustanova_id_input.value),
                    godina=int(godina_input.value),
                    client=client,
                )

            elif mode.value == "mozvag_osoba":
                osoba = mozvag.get_osoba_po_mbz(
                    mbz=mbz_input.value,
                    godina=int(godina_input.value),
                    client=client,
                )
                result = [osoba]

            elif mode.value == "projekt_id":
                p = projekti.get_projekt(int(projekt_id_input.value), client=client)
                result = [p]

            elif mode.value == "projekti_mbu":
                result = projekti.get_projekti_po_ustanovi(mbu_input.value, client=client)

            elif mode.value == "osobe_projekta":
                result = osobe.get_osobe_projekta(int(projekt_id_input.value), client=client)

            elif mode.value == "publikacije_projekta":
                result = publikacije.get_publikacije_projekta(int(projekt_id_input.value), client=client)

            elif mode.value == "financijeri_projekta":
                result = financijeri.get_financijeri_projekta(int(projekt_id_input.value), client=client)

    except Exception as e:
        error_msg = f"**Greška pri dohvatu:** {e}\n\n```\n{traceback.format_exc()}\n```"

    if error_msg:
        mo.callout(mo.md(error_msg), kind="danger")
    else:
        mo.callout(mo.md(f"Dohvaćeno **{len(result)}** zapisa."), kind="success")

    return result, error_msg


@app.cell
def _show_table(mo, pd, result, error_msg):
    mo.stop(error_msg is not None or result is None)

    rows = [
        item.to_dict() if hasattr(item, "to_dict") else vars(item)
        for item in result
    ]

    if not rows:
        mo.callout(mo.md("Nema podataka."), kind="warn")
    else:
        df = pd.DataFrame(rows)
        mo.md("---\n## Tablica rezultata")
    return (df,)


@app.cell
def _data_table(mo, df):
    mo.stop(df is None)
    mo.ui.dataframe(df)
    return


@app.cell
def _viz_section(mo, df, mode, pd):
    mo.stop(df is None or df.empty)

    mo.md("---\n## Vizualizacije")
    return


@app.cell
def _chart_mozvag_ustanove(mo, px, df, mode):
    mo.stop(mode.value != "mozvag_ustanove")

    _fig = px.bar(
        df.dropna(subset=["grad"]).groupby("grad").size().reset_index(name="broj_ustanova"),
        x="grad",
        y="broj_ustanova",
        title="Broj ustanova po gradu",
        labels={"grad": "Grad", "broj_ustanova": "Broj ustanova"},
        color="broj_ustanova",
        color_continuous_scale="Blues",
    )
    _fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    mo.plotly(_fig)
    return


@app.cell
def _chart_mozvag_projekti(mo, px, df, mode):
    mo.stop(mode.value != "mozvag_projekti")

    mo.vstack([
        _chart_vrsta_projekata(px, df),
        _chart_financijeri(px, df),
        _chart_projekti_timeline(px, df),
    ])
    return


def _chart_vrsta_projekata(px, df):
    import marimo as mo
    _vrsta = df["vrsta"].value_counts().reset_index()
    _vrsta.columns = ["vrsta", "broj"]
    _fig = px.pie(
        _vrsta,
        names="vrsta",
        values="broj",
        title="Projekti po vrsti",
        hole=0.4,
    )
    return mo.plotly(_fig)


def _chart_financijeri(px, df):
    import marimo as mo
    import pandas as pd
    _f = (
        df["financijeri"]
        .str.split(", ")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(15)
        .reset_index()
    )
    _f.columns = ["financijer", "broj_projekata"]
    _fig = px.bar(
        _f,
        x="broj_projekata",
        y="financijer",
        orientation="h",
        title="Top 15 financijera",
        labels={"financijer": "Financijer", "broj_projekata": "Broj projekata"},
        color="broj_projekata",
        color_continuous_scale="Teal",
    )
    _fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
    return mo.plotly(_fig)


def _chart_projekti_timeline(px, df):
    import marimo as mo
    import pandas as pd
    _timeline = df.dropna(subset=["start_date", "end_date"]).copy()
    if _timeline.empty:
        return mo.md("*Nema podataka za vremensku liniju.*")
    _timeline["start_date"] = pd.to_datetime(_timeline["start_date"], errors="coerce")
    _timeline["end_date"] = pd.to_datetime(_timeline["end_date"], errors="coerce")
    _timeline = _timeline.dropna(subset=["start_date", "end_date"])
    if _timeline.empty:
        return mo.md("*Nema valjanih datuma za prikaz.*")
    _fig = px.timeline(
        _timeline.head(40),
        x_start="start_date",
        x_end="end_date",
        y="naziv",
        color="vrsta",
        title="Vremenska linija projekata (prvih 40)",
        labels={"naziv": "Projekt", "vrsta": "Vrsta"},
    )
    _fig.update_yaxes(autorange="reversed")
    _fig.update_layout(height=max(400, len(_timeline.head(40)) * 25))
    return mo.plotly(_fig)


@app.cell
def _chart_osobe_projekta(mo, px, df, mode):
    mo.stop(mode.value != "osobe_projekta")

    _uloge = df["uloga"].value_counts().reset_index()
    _uloge.columns = ["uloga", "broj"]
    _fig = px.pie(
        _uloge,
        names="uloga",
        values="broj",
        title="Raspodjela uloga na projektu",
        hole=0.3,
    )
    mo.plotly(_fig)
    return


@app.cell
def _chart_publikacije(mo, px, df, mode):
    mo.stop(mode.value != "publikacije_projekta")

    mo.vstack([
        _chart_vrsta_pub(px, df),
        _chart_pub_timeline(px, df),
    ])
    return


def _chart_vrsta_pub(px, df):
    import marimo as mo
    _v = df["vrsta"].value_counts().reset_index()
    _v.columns = ["vrsta", "broj"]
    _fig = px.bar(
        _v, x="vrsta", y="broj",
        title="Publikacije po vrsti",
        labels={"vrsta": "Vrsta", "broj": "Broj"},
        color="vrsta",
    )
    _fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    return mo.plotly(_fig)


def _chart_pub_timeline(px, df):
    import marimo as mo
    import pandas as pd
    _df = df.dropna(subset=["datum"]).copy()
    if _df.empty:
        return mo.md("*Nema datuma za prikaz.*")
    _df["godina"] = pd.to_datetime(_df["datum"], errors="coerce").dt.year
    _yearly = _df.dropna(subset=["godina"]).groupby("godina").size().reset_index(name="broj")
    _fig = px.bar(
        _yearly, x="godina", y="broj",
        title="Publikacije po godini",
        labels={"godina": "Godina", "broj": "Broj"},
        color="broj",
        color_continuous_scale="Purples",
    )
    _fig.update_layout(showlegend=False)
    return mo.plotly(_fig)


@app.cell
def _chart_financijeri_projekta(mo, px, df, mode):
    mo.stop(mode.value != "financijeri_projekta")

    _f = df.dropna(subset=["amount"])
    if _f.empty:
        mo.callout(mo.md("Nema podataka o iznosima."), kind="warn")
    else:
        _fig = px.bar(
            _f,
            x="naziv",
            y="amount",
            color="tip",
            title="Financiranje projekta po financijeru",
            labels={"naziv": "Financijer", "amount": "Iznos", "tip": "Tip"},
            text_auto=True,
        )
        _fig.update_layout(xaxis_tickangle=-30)
        mo.plotly(_fig)
    return


@app.cell
def _export_section(mo, df):
    mo.stop(df is None or df.empty)

    mo.md("---\n## Preuzimanje podataka")
    return


@app.cell
def _download_buttons(mo, df):
    mo.stop(df is None or df.empty)

    _csv_data = df.to_csv(index=False).encode("utf-8")
    _json_data = df.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8")

    mo.hstack([
        mo.download(
            data=_csv_data,
            filename="crosbi_export.csv",
            mimetype="text/csv",
            label="Preuzmi CSV",
        ),
        mo.download(
            data=_json_data,
            filename="crosbi_export.json",
            mimetype="application/json",
            label="Preuzmi JSON",
        ),
    ], gap=2)
    return


if __name__ == "__main__":
    app.run()
