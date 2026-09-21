import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const PROVINCES = [
  ["An Giang", 10.5216, 105.1259],
  ["Bắc Ninh", 21.1861, 106.0763],
  ["Cà Mau", 9.1527, 105.1961],
  ["Cao Bằng", 22.6666, 106.2639],
  ["Cần Thơ", 10.0452, 105.7469],
  ["Đà Nẵng", 16.0471, 108.2068],
  ["Đắk Lắk", 12.71, 108.2378],
  ["Điện Biên", 21.386, 103.023],
  ["Đồng Nai", 11.0686, 107.1676],
  ["Đồng Tháp", 10.4938, 105.6882],
  ["Gia Lai", 13.9833, 108.0],
  ["Hà Nội", 21.0278, 105.8342],
  ["Hà Tĩnh", 18.3559, 105.8877],
  ["Hải Phòng", 20.8449, 106.6881],
  ["Hậu Giang", 9.7845, 105.4701],
  ["Hồ Chí Minh", 10.8231, 106.6297],
  ["Huế", 16.4637, 107.5909],
  ["Hưng Yên", 20.6464, 106.0511],
  ["Khánh Hòa", 12.2388, 109.1967],
  ["Kiên Giang", 10.0125, 105.0809],
  ["Lai Châu", 22.3864, 103.4703],
  ["Lâm Đồng", 11.5753, 108.1429],
  ["Lạng Sơn", 21.8537, 106.7615],
  ["Lào Cai", 22.3381, 104.1487],
  ["Nghệ An", 18.6796, 105.6813],
  ["Ninh Bình", 20.2506, 105.9745],
  ["Phú Thọ", 21.3227, 105.402],
  ["Quảng Ngãi", 15.1205, 108.7923],
  ["Quảng Ninh", 21.0064, 107.2925],
  ["Quảng Trị", 17.4689, 106.6223],
  ["Sơn La", 21.3256, 103.9188],
  ["Tây Ninh", 11.3352, 106.1099],
  ["Thái Nguyên", 21.5942, 105.8482],
  ["Thanh Hóa", 19.8067, 105.7852],
  ["Tuyên Quang", 21.8233, 105.214],
  ["Vĩnh Long", 10.2397, 105.9571],
].map(([name, latitude, longitude]) => ({ name, latitude, longitude }));

function weatherLabel(code) {
  if ([95, 96, 99].includes(code))
    return { icon: "⚡", label: "Giông bão", tone: "storm" };
  if ([51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82].includes(code))
    return { icon: "☂", label: "Có mưa", tone: "rain" };
  if ([1, 2, 3, 45, 48].includes(code))
    return { icon: "☁", label: "Nhiều mây", tone: "cloud" };
  return { icon: "☀", label: "Nắng", tone: "sun" };
}

function formatDay(value, index) {
  if (index === 0) return "Hôm nay";
  return new Intl.DateTimeFormat("vi-VN", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
  }).format(new Date(`${value}T12:00:00`));
}

function formatVnd(value) {
  return value == null
    ? "Chưa có dữ liệu"
    : `${Number(value).toLocaleString("vi-VN")} đ`;
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json();
}

function Metric({ label, value, detail }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function GoldProductTable({ products = [] }) {
  return (
    <div className="gold-products">
      <div className="product-row product-header">
        <span>SẢN PHẨM</span>
        <span>MUA VÀO</span>
        <span>BÁN RA</span>
      </div>
      {products.map((product) => (
        <div className="product-row" key={product.code}>
          <strong>{product.name}</strong>
          <span>{formatVnd(product.buy_vnd)}</span>
          <span>{formatVnd(product.sell_vnd)}</span>
        </div>
      ))}
    </div>
  );
}

function App() {
  const [province, setProvince] = useState(
    PROVINCES.find((item) => item.name === "Đà Nẵng"),
  );
  const [gold, setGold] = useState(null);
  const [weather, setWeather] = useState(null);
  const [flood, setFlood] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchJson(`${API_URL}/api/gold/current`)
      .then(setGold)
      .catch(() => setError("Chưa lấy được dữ liệu giá vàng."));
  }, []);

  useEffect(() => {
    setWeather(null);
    setFlood(null);
    Promise.allSettled([
      fetchJson(
        `${API_URL}/api/weather/forecast?latitude=${province.latitude}&longitude=${province.longitude}`,
      ),
      fetchJson(
        `${API_URL}/api/flood/forecast?latitude=${province.latitude}&longitude=${province.longitude}`,
      ),
    ]).then(([weatherResult, floodResult]) => {
      if (weatherResult.status === "fulfilled") setWeather(weatherResult.value);
      if (floodResult.status === "fulfilled") setFlood(floodResult.value);
      if (
        weatherResult.status === "rejected" ||
        floodResult.status === "rejected"
      ) {
        setError("Một nguồn thời tiết chưa phản hồi. Hãy thử lại sau.");
      } else {
        setError("");
      }
    });
  }, [province]);

  const weatherRows =
    weather?.hourly?.time?.slice(0, 24).map((time, index) => ({
      time: time.slice(11, 16),
      wind: weather.hourly.wind_gusts_10m[index],
      rain: weather.hourly.precipitation[index],
    })) || [];

  const dailyForecast =
    weather?.daily?.time?.map((date, index) => ({
      date,
      status: weatherLabel(weather.daily.weather_code[index]),
      max: weather.daily.temperature_2m_max[index],
      min: weather.daily.temperature_2m_min[index],
      rainChance: weather.daily.precipitation_probability_max[index],
      rain: weather.daily.precipitation_sum[index],
      wind: weather.daily.wind_speed_10m_max[index],
      gust: weather.daily.wind_gusts_10m_max[index],
      index,
    })) || [];

  return (
    <main>
      <header className="topbar">
        <div>
          <p className="eyebrow">VIETNAM FORECAST LAB</p>
          <h1>Market & weather signals</h1>
        </div>
        <span className="status">
          <i /> Live API
        </span>
      </header>
      {error && <div className="alert">{error}</div>}
      <section className="hero-grid">
        <div className="hero-copy">
          <p className="eyebrow">BẢNG ĐIỀU KHIỂN</p>
          <h2>
            Dữ liệu hôm nay,
            <br />
            <em>quyết định sáng hơn.</em>
          </h2>
          <p className="muted">
            Theo dõi giá vàng và dự báo thời tiết 7 ngày theo từng tỉnh, thành
            phố.
          </p>
        </div>
        <div className="hero-note">
          <label htmlFor="province">TỈNH / THÀNH PHỐ</label>
          <select
            id="province"
            value={province.name}
            onChange={(event) =>
              setProvince(
                PROVINCES.find((item) => item.name === event.target.value),
              )
            }
          >
            {PROVINCES.map((item) => (
              <option key={item.name} value={item.name}>
                {item.name}
              </option>
            ))}
          </select>
          <strong>{province.latitude.toFixed(4)}° N</strong>
          <strong>{province.longitude.toFixed(4)}° E</strong>
          <small>Dự báo theo giờ tại {province.name}</small>
        </div>
      </section>
      <div className="metrics">
        <Metric
          label="SJC MUA VÀO"
          value={formatVnd(
            gold?.products?.find((product) => product.code === "SJL1L10")
              ?.buy_vnd,
          )}
          detail="VND / lượng"
        />
        <Metric
          label="SJC BÁN RA"
          value={formatVnd(
            gold?.products?.find((product) => product.code === "SJL1L10")
              ?.sell_vnd,
          )}
          detail="VND / lượng"
        />
        <Metric
          label="GIÓ GIẬT CAO NHẤT"
          value={
            weather?.hourly
              ? `${Math.max(...weather.hourly.wind_gusts_10m.slice(0, 24)).toFixed(1)}`
              : "--"
          }
          detail="km/h trong 24 giờ"
        />
        <Metric
          label="DÒNG CHẢY"
          value={flood?.daily?.river_discharge?.[0] ?? "--"}
          detail="m³/s dự báo hôm nay"
        />
      </div>
      <section className="forecast-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">DỰ BÁO 7 NGÀY</p>
            <h3>{province.name}: nắng, mưa, gió và giông bão</h3>
          </div>
          <span className="badge">THEO NGÀY</span>
        </div>
        <div className="forecast-grid">
          {dailyForecast.map((day) => (
            <article
              className={`forecast-card ${day.status.tone}`}
              key={day.date}
            >
              <span className="forecast-date">
                {formatDay(day.date, day.index)}
              </span>
              <strong className="forecast-icon" aria-label={day.status.label}>
                {day.status.icon}
              </strong>
              <strong className="forecast-label">{day.status.label}</strong>
              <div className="temperature">
                <b>{Math.round(day.max)}°</b>
                <span>{Math.round(day.min)}°</span>
              </div>
              <div className="forecast-detail">
                <span>Khả năng mưa</span>
                <b>{day.rainChance ?? 0}%</b>
              </div>
              <div className="forecast-detail">
                <span>Lượng mưa</span>
                <b>{day.rain?.toFixed(1) ?? "0.0"} mm</b>
              </div>
              <div className="forecast-detail">
                <span>Gió / giật</span>
                <b>
                  {day.wind?.toFixed(0) ?? "--"} /{" "}
                  {day.gust?.toFixed(0) ?? "--"}
                </b>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section className="panel-grid">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">MÔ-ĐUN BÃO</p>
              <h3>Tín hiệu gió và mưa theo giờ</h3>
            </div>
            <span className="badge">7 NGÀY</span>
          </div>
          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weatherRows}>
                <defs>
                  <linearGradient id="wind" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#e66d4d" stopOpacity=".4" />
                    <stop offset="100%" stopColor="#e66d4d" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#dedbd4"
                />
                <XAxis dataKey="time" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="wind"
                  name="Gió giật"
                  stroke="#e66d4d"
                  fill="url(#wind)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </article>
        <article className="panel gold-panel">
          <p className="eyebrow">MÔ-ĐUN GIÁ VÀNG</p>
          <h3>Giá theo từng loại</h3>
          <GoldProductTable products={gold?.products} />
          <div className="gold-display">
            <span>VÀNG THẾ GIỚI</span>
            <strong>
              {gold?.gold_usd != null ? `$${gold.gold_usd.toFixed(2)}` : "--"}
            </strong>
            <small>
              Cập nhật: {gold?.updated_at || "--"} · {gold?.date || "--"}
            </small>
          </div>
          <div className="divider" />
          <p className="muted">
            Dữ liệu mua vào và bán ra lấy trực tiếp từ vang.today, đơn vị
            VND/lượng.
          </p>
        </article>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
