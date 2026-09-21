import asyncio
from datetime import date, timedelta

import httpx

from .config import settings


async def get_gold_price_vnd() -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(settings.gold_prices_url)
        response.raise_for_status()
        payload = response.json()

    if not payload.get("success"):
        raise ValueError("vang.today trả về phản hồi không thành công")

    prices = payload["prices"]
    world_gold = prices.get("XAUUSD", {})
    products = [
        {"code": "SJL1L10", "name": "Vàng miếng SJC", "price": prices.get("SJL1L10")},
        {"code": "SJ9999", "name": "Vàng nhẫn SJC 99.99%", "price": prices.get("SJ9999")},
        {"code": "DOHNL", "name": "Vàng DOJI", "price": prices.get("DOHNL")},
        {"code": "GOLD18", "name": "Vàng 18", "price": None},
        {"code": "PQHN24NTT", "name": "Vàng 24", "price": prices.get("PQHN24NTT")},
    ]

    return {
        "source": "vang.today",
        "updated_at": payload.get("time"),
        "date": payload.get("date"),
        "gold_usd": world_gold.get("buy"),
        "products": [
            {
                "code": product["code"],
                "name": product["name"],
                "buy_vnd": product["price"].get("buy") if product["price"] else None,
                "sell_vnd": product["price"].get("sell") if product["price"] else None,
                "change_buy": product["price"].get("change_buy") if product["price"] else None,
                "change_sell": product["price"].get("change_sell") if product["price"] else None,
                "available": product["price"] is not None,
            }
            for product in products
        ],
    }


async def get_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,pressure_msl,wind_speed_10m,wind_gusts_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max",
        "forecast_days": 7,
        "timezone": "Asia/Ho_Chi_Minh",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(settings.open_meteo_base_url, params=params)
        response.raise_for_status()
        return response.json()


async def get_flood(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "river_discharge",
        "forecast_days": 7,
        "timezone": "Asia/Ho_Chi_Minh",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(settings.open_meteo_flood_url, params=params)
        response.raise_for_status()
        return response.json()


async def get_weather_history(latitude: float, longitude: float, days: int = 365) -> dict:
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=days)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,pressure_msl,wind_speed_10m,wind_gusts_10m,weather_code",
        "timezone": "Asia/Ho_Chi_Minh",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(3):
            response = await client.get(settings.open_meteo_archive_url, params=params)
            if response.status_code != 429:
                response.raise_for_status()
                return response.json()
            if attempt < 2:
                retry_after = int(response.headers.get("Retry-After", "3"))
                await asyncio.sleep(min(retry_after, 10))
        response.raise_for_status()
        return response.json()
