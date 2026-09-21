from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    open_meteo_base_url: str = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
    open_meteo_archive_url: str = os.getenv("OPEN_METEO_ARCHIVE_URL", "https://archive-api.open-meteo.com/v1/archive")
    open_meteo_flood_url: str = os.getenv("OPEN_METEO_FLOOD_URL", "https://flood-api.open-meteo.com/v1/flood")
    gold_prices_url: str = os.getenv("GOLD_PRICES_URL", "https://www.vang.today/api/prices")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "https://website-news.vercel.app")


settings = Settings()
