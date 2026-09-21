# Vietnam Forecast Lab

Ứng dụng gồm hai mô-đun độc lập trong cùng một dashboard React:

- Giá vàng quốc tế được quy đổi sang VND.
- Dự báo thời tiết theo giờ, tín hiệu rủi ro bão từ gió/mưa, và dòng chảy phục vụ mô-đun lũ.

## Chạy backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
copy .env.example .env
py -m uvicorn app.main:app --reload --port 8000
```

## Chạy dashboard

```powershell
cd frontend
npm install
npm run dev
```

Dashboard mặc định gọi backend tại `http://localhost:8000`. Có thể đổi địa chỉ bằng biến `VITE_API_URL` khi chạy Vite.

Trong dashboard, chọn tỉnh/thành phố ở khu vực điểm quan sát. Hệ thống sẽ gọi lại Open-Meteo theo tọa độ tỉnh đó và hiển thị 7 ngày gồm trạng thái nắng/mây/mưa/giông bão, nhiệt độ cao thấp, xác suất mưa, lượng mưa, tốc độ gió và gió giật.

## Deploy công khai miễn phí

Phương án không cần mua tên miền: deploy backend lên Render để nhận subdomain `onrender.com`, sau đó deploy thư mục `frontend` lên Vercel để nhận subdomain `vercel.app`.

1. Đẩy project lên GitHub.
2. Trên Render, tạo Web Service từ thư mục `backend`, dùng Dockerfile và đặt biến `FRONTEND_ORIGIN` tạm thời là URL Vercel dự kiến.
3. Trên Vercel, import project, đặt Root Directory là `frontend`, thêm biến `VITE_API_URL` bằng URL Render thật, rồi deploy.
4. Quay lại Render, cập nhật `FRONTEND_ORIGIN` bằng URL Vercel thật để bật CORS.

Tên frontend mục tiêu là `https://website-news.vercel.app`. Tên này chỉ hoạt động nếu tài khoản Vercel của bạn tạo được project với tên `website-news`; nếu tên đã bị dùng, Vercel sẽ cấp tên khác. Tên miền riêng như `website-news.com` không được cấp miễn phí ổn định; cần mua tên miền và trỏ DNS về Vercel.

## Chạy bằng Docker

Cài Docker Desktop, mở PowerShell tại thư mục project và chạy:

```powershell
docker compose up --build
```

Mở dashboard bằng Chrome tại `http://localhost:8080`. Backend API và tài liệu Swagger chạy tại `http://localhost:8000/docs`.

Dừng hệ thống:

```powershell
docker compose down
```

## Train/test

Pipeline `backend/scripts/train.py` tự tải dữ liệu lịch sử thời tiết, chia tuần tự 80% cho train và 20% cho test, tạo đặc trưng độ trễ 1/3/6/12/24 giờ, trung bình trượt và chu kỳ thời gian, sau đó huấn luyện riêng nhiệt độ, lượng mưa, gió giật và giông bão. Model được lưu vào `backend/models/`, metrics lưu ở `backend/models/weather_metrics.json`.

Lần train đã hoàn tất với 2 năm dữ liệu, 6 khu vực và 105.114 mẫu sau khi tạo tập supervised. Kết quả test: nhiệt độ MAE `0.426°C`, lượng mưa MAE `0.364 mm`, gió giật MAE `2.122 km/h`. Nhãn giông trong tập test không có mẫu dương nên F1 `0.0`; cần bổ sung các giai đoạn có giông/bão hoặc dữ liệu cảnh báo bão để đánh giá và cải thiện riêng mô hình này. Dashboard hiện vẫn dùng dự báo trực tiếp từ Open-Meteo; các model train là nền tảng cho bước tích hợp dự báo ML tiếp theo.

Mô hình giá vàng và mô hình lũ cần được bổ sung dữ liệu lịch sử tương ứng trước khi train riêng. API `vang.today` được dùng cho giá vàng nội địa: `SJL1L10` là SJC, `SJ9999` là nhẫn SJC, `DOHNL` là DOJI Hà Nội và `PQHN24NTT` là vàng 24K. API hiện không trả mã vàng 18K nên mục này hiển thị không có dữ liệu, không tự suy ra giá. Không nên coi tín hiệu bão hiện tại là đường đi tâm bão; nó là mức rủi ro khí tượng được suy ra từ dữ liệu theo giờ.

## Nguồn dữ liệu

Các adapter backend dùng API công khai miễn phí và có thể thay qua `.env`: vang.today, Open-Meteo Forecast, Open-Meteo Archive và Open-Meteo Flood. Cần kiểm tra giới hạn truy cập và điều khoản sử dụng trước khi triển khai thực tế.
