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

### CÁCH 1: KHỞI CHẠY NHANH (Khuyên dùng)
Dự án đã được tích hợp sẵn script chạy tự động cho hệ điều hành Windows.
1. Mở thư mục dự án `TQHDL/Final/` trong File Explorer.
2. Click đúp chuột vào file `run.bat`.
3. Script sẽ tự động bật 2 cửa sổ Terminal (1 cho Backend, 1 cho Frontend). Đợi vài giây, mở trình duyệt truy cập `http://localhost:5173`.

---

### CÁCH 2: KHỞI CHẠY THỦ CÔNG (Dành cho Dev / Fix bug)
Nếu chạy bằng file `.bat` gặp lỗi, hoặc bạn đang dùng macOS/Linux, hãy chạy thủ công theo 2 bước sau:

#### Bước 1: Khởi chạy Backend (FastAPI)

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

#### Bước 2: Khởi chạy Frontend (React)

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

## 3. Kiến trúc luồng dữ liệu (Data Flow)

Để làm tiếp các trang Dashboard tiếp theo, các thành viên cần hiểu rõ chu trình luồng dữ liệu 3 bước (Mô hình Client - Server):

### 3.1. Frontend (React)
- **Quản lý trạng thái (State):** Người dùng tương tác với các nút bấm, bộ lọc (Vị trí, Cấp bậc, Vùng miền...) trên giao diện. Trạng thái này được lưu tập trung bằng `useState` bên trong Component (ví dụ `Dashboard_page1.jsx`).
- **Gửi API Request:** Mỗi khi bộ lọc thay đổi, React sử dụng hàm `useEffect` để kích hoạt việc gọi API bằng thư viện `axios`.
- **Payload:** Thông tin bộ lọc được đóng gói thành một HTTP POST Request (định dạng JSON) và gửi xuống đường dẫn API tương ứng (VD: `http://localhost:8000/api/page1/data`).

### 3.2. Backend (FastAPI)
- **Tiếp nhận Request:** Endpoint tại `routers/router_page1.py` sẽ hứng request, giải mã JSON payload để lấy ra các tham số lọc (`position`, `experience`, `region`).
- **Xử lý Dữ liệu (Data Processing):**
  - Đọc file tổng `data/processed/vietnam_it_jobs_processed.csv` thành một `Pandas DataFrame`.
  - Dùng Pandas query/mask để lọc bỏ các dòng không thỏa mãn điều kiện filter.
- **Tạo biểu đồ (Visualization Logic):**
  - Truyền DataFrame đã lọc xuống các hàm tạo biểu đồ cụ thể nằm trong `utils/charts_page1.py`.
  - Các hàm này tính toán tần suất, nhóm dữ liệu (groupby) và sử dụng Plotly Express/Graph Objects để vẽ hình (`fig`).
  - Hàm `apply_layout_styles` từ `utils/charts_common.py` được gọi để đồng bộ giao diện cho `fig`.
- **Trả về (Response):** Hàm `json.loads(fig.to_json())` chuyển đổi cấu trúc `fig` của Plotly Python thành một JSON Object thuần túy và trả về cho Frontend kèm theo các số liệu KPI tính toán được.

### 3.3. Frontend Render
- **Tiếp nhận Response:** Frontend nhận cục dữ liệu JSON từ Backend (chứa KPI và danh sách các charts).
- **Cập nhật Giao diện:** Gắn dữ liệu số vào các Component thẻ như `<KpiCard />`.
- **Render Biểu đồ Tương tác:** Chuyển phần tử chart JSON vào thư viện `react-plotly.js` thông qua wrapper Component `<PlotlyChart figure={data.charts.xxx} />`. Lúc này thư viện Plotly.js phía Frontend sẽ tiếp quản và hiển thị biểu đồ, đồng thời lắng nghe các sự kiện (Click, Hover) để tạo trải nghiệm tương tác trực quan.