"""Testovi za crosbi.models.common — TranslatedText, Klasifikacija, get_text."""

import pytest

from crosbi.models.common import Klasifikacija, TranslatedText, get_text


class TestTranslatedText:
    def test_from_dict_full(self):
        raw = {
            "cfLangCode": "hr",
            "naziv": "Naslov na hrvatskom",
            "cfLangName": "hrvatski",
            "original": True,
            "mlRecordId": "abc-123",
        }
        t = TranslatedText.from_dict(raw)
        assert t.lang_code == "hr"
        assert t.naziv == "Naslov na hrvatskom"
        assert t.lang_name == "hrvatski"
        assert t.original is True
        assert t.ml_record_id == "abc-123"

    def test_from_dict_minimal(self):
        t = TranslatedText.from_dict({})
        assert t.lang_code == ""
        assert t.naziv == ""
        assert t.original is False
        assert t.lang_name is None

    def test_from_dict_missing_original_defaults_false(self):
        t = TranslatedText.from_dict({"cfLangCode": "en", "naziv": "Title"})
        assert t.original is False


class TestKlasifikacija:
    def test_from_dict(self):
        k = Klasifikacija.from_dict({"id": 3, "naziv": "Istraživački projekt"})
        assert k.id == 3
        assert k.naziv == "Istraživački projekt"

    def test_from_dict_missing_fields(self):
        k = Klasifikacija.from_dict({})
        assert k.id == 0
        assert k.naziv == ""


class TestGetText:
    @pytest.fixture
    def items(self):
        return [
            TranslatedText(lang_code="hr", naziv="Hrvatski tekst", original=True),
            TranslatedText(lang_code="en", naziv="English text", original=False),
        ]

    def test_returns_requested_language(self, items):
        assert get_text(items, "hr") == "Hrvatski tekst"
        assert get_text(items, "en") == "English text"

    def test_fallback_to_first_on_missing_lang(self, items):
        assert get_text(items, "de") == "Hrvatski tekst"

    def test_empty_list_returns_empty_string(self):
        assert get_text([], "hr") == ""

    def test_single_item_any_lang_returns_it(self):
        items = [TranslatedText(lang_code="hr", naziv="Jedini tekst")]
        assert get_text(items, "en") == "Jedini tekst"

    def test_duplicate_lang_code_returns_first(self):
        items = [
            TranslatedText(lang_code="hr", naziv="Prvi"),
            TranslatedText(lang_code="hr", naziv="Drugi"),
        ]
        assert get_text(items, "hr") == "Prvi"
