"""Testovi za crosbi.config — Config i konstante."""

import pytest

from crosbi.config import (
    CASOPISI_BASE_URL,
    CROSBI_BASE_URL,
    DOGADANJA_BASE_URL,
    OPREMA_BASE_URL,
    PROJEKTI_BASE_URL,
    USTANOVE_BASE_URL,
    ZNANSTVENICI_BASE_URL,
    Config,
)


class TestConfigDefaults:
    def test_default_base_url(self, monkeypatch):
        monkeypatch.delenv("CRORIS_BASE_URL", raising=False)
        cfg = Config()
        assert cfg.base_url == PROJEKTI_BASE_URL

    def test_default_page_size(self, monkeypatch):
        monkeypatch.delenv("CRORIS_PAGE_SIZE", raising=False)
        cfg = Config()
        assert cfg.page_size == 50

    def test_default_timeout(self, monkeypatch):
        monkeypatch.delenv("CRORIS_TIMEOUT", raising=False)
        cfg = Config()
        assert cfg.timeout == 60

    def test_default_credentials_empty(self, monkeypatch):
        monkeypatch.delenv("CRORIS_USERNAME", raising=False)
        monkeypatch.delenv("CRORIS_PASSWORD", raising=False)
        cfg = Config()
        assert cfg.username == ""
        assert cfg.password == ""

    def test_max_retries_default(self):
        assert Config().max_retries == 3


class TestConfigFromEnv:
    def test_username_from_env(self, monkeypatch):
        monkeypatch.setenv("CRORIS_USERNAME", "testuser")
        assert Config().username == "testuser"

    def test_password_from_env(self, monkeypatch):
        monkeypatch.setenv("CRORIS_PASSWORD", "tajnalozinka")
        assert Config().password == "tajnalozinka"

    def test_page_size_from_env(self, monkeypatch):
        monkeypatch.setenv("CRORIS_PAGE_SIZE", "25")
        assert Config().page_size == 25

    def test_timeout_from_env(self, monkeypatch):
        monkeypatch.setenv("CRORIS_TIMEOUT", "60")
        assert Config().timeout == 60

    def test_base_url_from_env(self, monkeypatch):
        monkeypatch.setenv("CRORIS_BASE_URL", "https://custom.example.com/api")
        assert Config().base_url == "https://custom.example.com/api"


class TestConfigDirect:
    def test_direct_assignment_overrides_env(self, monkeypatch):
        monkeypatch.setenv("CRORIS_USERNAME", "from_env")
        cfg = Config(username="direct_user")
        assert cfg.username == "direct_user"


class TestBaseUrlConstants:
    def test_all_constants_defined(self):
        assert PROJEKTI_BASE_URL.endswith("/projekti-api")
        assert USTANOVE_BASE_URL.endswith("/ustanove-api")
        assert CROSBI_BASE_URL.endswith("/crosbi-api")
        assert OPREMA_BASE_URL.endswith("/oprema-api")
        assert CASOPISI_BASE_URL.endswith("/casopisi-api")
        assert DOGADANJA_BASE_URL.endswith("/dogadanja-api")
        assert ZNANSTVENICI_BASE_URL.endswith("/znanstvenici-api")

    def test_all_constants_same_domain(self):
        constants = [
            PROJEKTI_BASE_URL, USTANOVE_BASE_URL, CROSBI_BASE_URL,
            OPREMA_BASE_URL, CASOPISI_BASE_URL, DOGADANJA_BASE_URL,
            ZNANSTVENICI_BASE_URL,
        ]
        for url in constants:
            assert "croris.hr" in url
