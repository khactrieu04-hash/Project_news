from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .clients import get_flood, get_gold_price_vnd, get_weather
from .config import settings

app = FastAPI(title="Vietnam Market and Weather Forecast API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/gold/current")
async def current_gold() -> dict:
    try:
        return await get_gold_price_vnd()
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Không lấy được dữ liệu giá vàng: {error}") from error


@app.get("/api/weather/forecast")
async def weather_forecast(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
) -> dict:
    try:
        return await get_weather(latitude, longitude)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Không lấy được dữ liệu thời tiết: {error}") from error


@app.get("/api/flood/forecast")
async def flood_forecast(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
) -> dict:
    try:
        return await get_flood(latitude, longitude)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Không lấy được dữ liệu lũ: {error}") from error
