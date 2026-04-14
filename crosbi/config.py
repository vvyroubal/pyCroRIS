"""Konfiguracija CroRIS klijenta — URL-ovi modula i konfiguracijska klasa."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

# Base URL konstante za sve CroRIS API module
PROJEKTI_BASE_URL = "https://www.croris.hr/projekti-api"
USTANOVE_BASE_URL = "https://www.croris.hr/ustanove-api"
CROSBI_BASE_URL = "https://www.croris.hr/crosbi-api"
OPREMA_BASE_URL = "https://www.croris.hr/oprema-api"
CASOPISI_BASE_URL = "https://www.croris.hr/casopisi-api"
DOGADANJA_BASE_URL = "https://www.croris.hr/dogadanja-api"
ZNANSTVENICI_BASE_URL = "https://www.croris.hr/znanstvenici-api"


@dataclass
class Config:
    """Konfiguracijske postavke HTTP klijenta.

    Vrijednosti se čitaju iz okružnih varijabli (.env) ako nisu proslijeđene
    izravno. Sve varijable su neobavezne — postavljene su razumne zadane
    vrijednosti.

    Atributi:
        base_url: Osnovna adresa API-ja (zadano: Projekti API).
        username: Korisničko ime za HTTP Basic autentikaciju.
        password: Lozinka za HTTP Basic autentikaciju.
        page_size: Broj zapisa po stranici pri paginaciji (5–100).
        timeout: Istek HTTP zahtjeva u sekundama.
        max_retries: Broj automatskih ponovnih pokušaja za 5xx odgovore.
    """

    base_url: str = field(
        default_factory=lambda: os.getenv("CRORIS_BASE_URL", PROJEKTI_BASE_URL)
    )
    username: str = field(default_factory=lambda: os.getenv("CRORIS_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("CRORIS_PASSWORD", ""))
    page_size: int = field(
        default_factory=lambda: int(os.getenv("CRORIS_PAGE_SIZE", "50"))
    )
    timeout: int = field(
        default_factory=lambda: int(os.getenv("CRORIS_TIMEOUT", "60"))
    )
    max_retries: int = 3


config = Config()
