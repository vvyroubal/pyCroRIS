import dataclasses
import json
from pathlib import Path
from typing import Any


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return dataclasses.asdict(obj)
        return super().default(obj)


def to_json(data: Any, path: str | Path, indent: int = 2) -> None:
    """Spremi podatke (dataclass, lista, dict) u JSON datoteku."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, cls=DataclassEncoder, ensure_ascii=False, indent=indent)


def from_json(path: str | Path) -> Any:
    """Učitaj JSON datoteku."""
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)
