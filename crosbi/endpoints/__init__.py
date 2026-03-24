"""Svi endpoint moduli CroRIS API klijenta — javno sučelje paketa crosbi.endpoints."""
from . import (
    casopisi,
    dogadanja,
    financijeri,
    mozvag,
    oprema_api,
    osobe,
    projekti,
    publikacije,
    publikacije_crosbi,
    ustanove,
    upisnik,
    znanstvenici,
)

__all__ = [
    # projekti-api
    "projekti",
    "osobe",
    "ustanove",
    "publikacije",
    "financijeri",
    "mozvag",
    # ustanove-api
    "upisnik",
    # crosbi-api
    "publikacije_crosbi",
    # oprema-api
    "oprema_api",
    # casopisi-api
    "casopisi",
    # dogadanja-api
    "dogadanja",
    # znanstvenici-api
    "znanstvenici",
]
