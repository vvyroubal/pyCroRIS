"""Pomoćne funkcije za izvoz podataka u CSV format."""
import csv
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HasToDict(Protocol):
    """Protokol za objekte koji implementiraju metodu to_dict()."""

    def to_dict(self) -> dict: ...


def to_csv(items: list[Any], path: str | Path) -> None:
    """
    Spremi listu objekata (koji imaju to_dict()) ili dictionarya u CSV datoteku.
    Stupci se određuju iz prvog elementa.
    """
    if not items:
        return

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = [item.to_dict() if isinstance(item, HasToDict) else item for item in items]
    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
