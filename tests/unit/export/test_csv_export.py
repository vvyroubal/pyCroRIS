"""Testovi za crosbi.export.csv_export."""

import csv
import dataclasses
from pathlib import Path

import pytest

from crosbi.export.csv_export import HasToDict, to_csv


@dataclasses.dataclass
class _Stavka:
    id: int
    naziv: str
    iznos: float

    def to_dict(self) -> dict:
        return {"id": self.id, "naziv": self.naziv, "iznos": self.iznos}


class TestHasToDictProtocol:
    def test_dataclass_with_to_dict_matches(self):
        assert isinstance(_Stavka(1, "X", 0.0), HasToDict)

    def test_plain_dict_does_not_match(self):
        assert not isinstance({"a": 1}, HasToDict)

    def test_object_without_to_dict_does_not_match(self):
        assert not isinstance(object(), HasToDict)


class TestToCsv:
    def test_creates_file(self, tmp_path):
        path = tmp_path / "out.csv"
        to_csv([_Stavka(1, "A", 1.0)], path)
        assert path.exists()

    def test_empty_list_does_not_create_file(self, tmp_path):
        path = tmp_path / "empty.csv"
        to_csv([], path)
        assert not path.exists()

    def test_header_from_first_element(self, tmp_path):
        path = tmp_path / "header.csv"
        to_csv([_Stavka(1, "A", 1.0)], path)
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {"id", "naziv", "iznos"}

    def test_correct_number_of_rows(self, tmp_path):
        path = tmp_path / "rows.csv"
        items = [_Stavka(i, f"S{i}", float(i)) for i in range(5)]
        to_csv(items, path)
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 5

    def test_values_written_correctly(self, tmp_path):
        path = tmp_path / "vals.csv"
        to_csv([_Stavka(7, "Sedmica", 77.7)], path)
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["id"] == "7"
        assert rows[0]["naziv"] == "Sedmica"

    def test_unicode_preserved(self, tmp_path):
        path = tmp_path / "unicode.csv"
        to_csv([_Stavka(1, "Šibenik–Knin", 0.0)], path)
        content = path.read_text(encoding="utf-8")
        assert "Šibenik–Knin" in content

    def test_creates_parent_directories(self, tmp_path):
        path = tmp_path / "a" / "b" / "out.csv"
        to_csv([_Stavka(1, "X", 1.0)], path)
        assert path.exists()

    def test_accepts_string_path(self, tmp_path):
        path = str(tmp_path / "str.csv")
        to_csv([_Stavka(1, "X", 1.0)], path)
        assert Path(path).exists()

    def test_plain_dicts_supported(self, tmp_path):
        path = tmp_path / "dicts.csv"
        items = [{"a": 1, "b": "hello"}, {"a": 2, "b": "world"}]
        to_csv(items, path)
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]["b"] == "hello"

    def test_extra_keys_ignored(self, tmp_path):
        """DictWriter extrasaction='ignore' — extra nkeys in subsequent rows are dropped."""
        path = tmp_path / "extra.csv"
        items = [{"a": 1}, {"a": 2, "b": "extra"}]
        to_csv(items, path)
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        assert "b" not in rows[1]
