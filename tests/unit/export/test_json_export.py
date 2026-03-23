"""Testovi za crosbi.export.json_export."""

import dataclasses
import json
from pathlib import Path

import pytest

from crosbi.export.json_export import DataclassEncoder, from_json, to_json


@dataclasses.dataclass
class _Tocka:
    x: float
    y: float


@dataclasses.dataclass
class _Linija:
    naziv: str
    tocke: list[_Tocka]


class TestDataclassEncoder:
    def test_encodes_simple_dataclass(self):
        t = _Tocka(1.0, 2.0)
        result = json.loads(json.dumps(t, cls=DataclassEncoder))
        assert result == {"x": 1.0, "y": 2.0}

    def test_encodes_nested_dataclass(self):
        l = _Linija("AB", [_Tocka(0.0, 0.0), _Tocka(1.0, 1.0)])
        result = json.loads(json.dumps(l, cls=DataclassEncoder))
        assert result["naziv"] == "AB"
        assert len(result["tocke"]) == 2

    def test_encodes_list_of_dataclasses(self):
        items = [_Tocka(1.0, 2.0), _Tocka(3.0, 4.0)]
        result = json.loads(json.dumps(items, cls=DataclassEncoder))
        assert len(result) == 2
        assert result[1]["x"] == 3.0

    def test_falls_back_for_non_dataclass(self):
        encoder = DataclassEncoder()
        with pytest.raises(TypeError):
            encoder.default(object())

    def test_plain_dict_unchanged(self):
        d = {"a": 1, "b": [1, 2, 3]}
        result = json.loads(json.dumps(d, cls=DataclassEncoder))
        assert result == d


class TestToJson:
    def test_writes_file(self, tmp_path):
        path = tmp_path / "output.json"
        to_json({"key": "value"}, path)
        assert path.exists()

    def test_file_is_valid_json(self, tmp_path):
        path = tmp_path / "output.json"
        to_json([1, 2, 3], path)
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        assert data == [1, 2, 3]

    def test_creates_parent_directories(self, tmp_path):
        path = tmp_path / "a" / "b" / "c" / "output.json"
        to_json({"x": 1}, path)
        assert path.exists()

    def test_preserves_unicode(self, tmp_path):
        path = tmp_path / "unicode.json"
        to_json({"naziv": "Šibenik–Knin"}, path)
        content = path.read_text(encoding="utf-8")
        assert "Šibenik–Knin" in content
        assert "\\u" not in content  # ensure_ascii=False

    def test_writes_dataclass(self, tmp_path):
        path = tmp_path / "tocka.json"
        to_json(_Tocka(3.0, 4.0), path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data == {"x": 3.0, "y": 4.0}

    def test_indent_applied(self, tmp_path):
        path = tmp_path / "indented.json"
        to_json({"a": 1}, path, indent=4)
        content = path.read_text(encoding="utf-8")
        assert "    " in content  # 4-space indent present

    def test_accepts_string_path(self, tmp_path):
        path = str(tmp_path / "str_path.json")
        to_json({"ok": True}, path)
        assert Path(path).exists()


class TestFromJson:
    def test_reads_dict(self, tmp_path):
        path = tmp_path / "data.json"
        path.write_text('{"id": 42}', encoding="utf-8")
        result = from_json(path)
        assert result == {"id": 42}

    def test_reads_list(self, tmp_path):
        path = tmp_path / "list.json"
        path.write_text('[1, 2, 3]', encoding="utf-8")
        assert from_json(path) == [1, 2, 3]

    def test_reads_unicode(self, tmp_path):
        path = tmp_path / "unicode.json"
        path.write_text('{"naziv": "Čakovec"}', encoding="utf-8")
        assert from_json(path)["naziv"] == "Čakovec"

    def test_accepts_string_path(self, tmp_path):
        path = tmp_path / "str.json"
        path.write_text('{"x": 1}', encoding="utf-8")
        assert from_json(str(path)) == {"x": 1}


class TestRoundTrip:
    def test_dict_round_trip(self, tmp_path):
        original = {"id": 1, "naziv": "Projekt Alfa", "iznos": 12345.67}
        path = tmp_path / "rt.json"
        to_json(original, path)
        assert from_json(path) == original

    def test_list_of_dicts_round_trip(self, tmp_path):
        original = [{"id": i, "x": float(i)} for i in range(5)]
        path = tmp_path / "rt_list.json"
        to_json(original, path)
        assert from_json(path) == original
