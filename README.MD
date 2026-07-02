# TQHDL - IT Recruitment Analysis Dashboard

Dự án Phân tích dữ liệu và Xây dựng Dashboard trực quan hóa thị trường tuyển dụng ngành Công nghệ Thông tin tại Việt Nam. 

Dự án này được tổ chức theo cấu trúc Monorepo, bao gồm phần Crawl dữ liệu, Tiền xử lý (Data Processing) và Hệ thống Dashboard hoàn chỉnh (Frontend & Backend).

## 1. Cấu trúc dự án

Dự án được phân rã thành các module cụ thể như sau:

```text
TQHDL/Final/
├── crawler/                # Module thu thập dữ liệu tự động
│   ├── output/             # File kết quả cào dữ liệu (JSON, CSV gốc)
│   └── scripts/            # Các script crawler (VD: Selenium, BeautifulSoup)
├── data/                   # Kho dữ liệu tập trung
│   ├── raw/                # Dữ liệu thô chưa qua xử lý
│   └── processed/          # Dữ liệu sạch đã chuẩn hóa (sẵn sàng cho dashboard)
├── notebooks/              # Jupyter Notebooks phục vụ EDA và Data Cleaning
└── dashboard/              # Hệ thống Web Dashboard
    ├── backend/            # REST API (Python FastAPI)
    │   ├── routers/        # Các endpoints xử lý API (router_page1.py, router_page5.py,...)
    │   ├── utils/          # Logic vẽ biểu đồ Plotly và xử lý data (charts_common.py, charts_page1.py)
    │   ├── main.py         # File khởi chạy server FastAPI
    │   └── requirements.txt
    └── frontend/           # Giao diện người dùng (ReactJS + Vite)
        ├── src/
        │   ├── components/ # Các component giao diện (Dashboard1, KpiCard, PlotlyChart...)
        │   ├── styles/     # File CSS định dạng UI/UX (style.css)
        │   └── App.jsx     # Root component, quản lý Layout & Routing
        ├── package.json
        └── vite.config.js
```

## 2. Hướng dẫn cài đặt và khởi chạy

Để cài đặt và chạy hệ thống ở môi trường Local, vui lòng thực hiện theo các bước sau.

### Yêu cầu hệ thống:
- Python 3.9 trở lên
- Node.js (phiên bản LTS 18.x hoặc 20.x)

### Bước 2.1. Khởi chạy Backend (FastAPI)

1. Mở Terminal và di chuyển vào thư mục backend:
   ```bash
   cd dashboard/backend
   ```
2. Cài đặt các thư viện Python:
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy server (tại `http://localhost:8000`):
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Bước 2.2. Khởi chạy Frontend (React)

1. Mở một Terminal mới và di chuyển vào thư mục frontend:
   ```bash
   cd dashboard/frontend
   ```
2. Cài đặt thư viện NodeJS:
   ```bash
   npm install
   ```
3. Khởi chạy Dev Server (tại `http://localhost:5173`):
   ```bash
   npm run dev
   ```

## 3. Kiến trúc luồng dữ liệu

1. **Frontend (React):** 
   - Quản lý trạng thái (State) tập trung (Vị trí, Cấp bậc, Vùng miền...).
   - Gửi yêu cầu phân tích (HTTP POST request) mang theo tham số bộ lọc xuống Backend.
2. **Backend (FastAPI):**
   - Nhận Filter Request (tại `routers/router_page1.py`).
   - Đọc dữ liệu từ file `data/processed/vietnam_it_jobs_processed.csv` qua thư viện Pandas.
   - Trích xuất dữ liệu, tổng hợp và gọi các hàm tạo biểu đồ Plotly trong `utils/charts_page1.py`. (Lưu ý: Mọi config màu sắc/style chuẩn được viết trong `charts_common.py`).
   - Trả về cấu trúc biểu đồ (Figure) dưới định dạng JSON.
3. **Frontend Render:**
   - Sử dụng thư viện `react-plotly.js` (Component `<PlotlyChart />`) để parse JSON và hiển thị biểu đồ tương tác lên giao diện.