import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "CRORIS_BASE_URL", "https://www.croris.hr/projekti-api"
        )
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
