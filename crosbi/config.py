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
    base_url: str = field(
        default_factory=lambda: os.getenv("CRORIS_BASE_URL", PROJEKTI_BASE_URL)
    )
    username: str = field(default_factory=lambda: os.getenv("CRORIS_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("CRORIS_PASSWORD", ""))
    page_size: int = field(
        default_factory=lambda: int(os.getenv("CRORIS_PAGE_SIZE", "50"))
    )
    timeout: int = field(
        default_factory=lambda: int(os.getenv("CRORIS_TIMEOUT", "30"))
    )
    max_retries: int = 3


config = Config()
