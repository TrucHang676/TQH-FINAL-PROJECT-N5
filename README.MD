# 📊 TQHDL - Vietnam IT Recruitment Market Analytics & AI Analyst Dashboard

> **Hệ thống Phân tích dữ liệu & Dashboard Trực quan hóa Thị trường Tuyển dụng IT Việt Nam tích hợp Trợ lý AI Phê duyệt Mã nguồn (Human-in-the-Loop)**

Đồ án môn học **Phân tích Quản lý Dữ liệu lớn (TQHDL)** — Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM.

---

## 📑 Mục lục

- [1. Tổng quan Dự án](#-1-tổng-quan-dự-án)
- [2. Cấu trúc Dự án](#-2-cấu-trúc-dự-án)
- [3. Hướng dẫn Cài đặt & Khởi chạy](#-3-hướng-dẫn-cài-đặt--khởi-chạy)
  - [Cách 1: Khởi chạy nhanh bằng file `.exe`](#-cách-1-khởi-chạy-nhanh-bằng-file-exe-khuyên-dùng-trên-windows)
  - [Cách 2: Khởi chạy thủ công (Dev / macOS / Linux)](#️-cách-2-khởi-chạy-thủ-công-dành-cho-dev--macos--linux)
- [4. Cấu trúc 5 Trang Phân tích của Dashboard](#-4-cấu-trúc-5-trang-phân-tích-của-dashboard)
- [5. Hệ thống AI Analyst (Human-in-the-Loop)](#-5-hệ-thống-ai-analyst-human-in-the-loop)
- [6. Thành viên thực hiện & Phân công nhiệm vụ](#-6-thành-viên-thực-hiện--phân-công-nhiệm-vụ)

---

## 📌 1. Tổng quan Dự án
Dự án được xây dựng theo kiến trúc **Monorepo**, bao gồm toàn bộ chuỗi cung ứng dữ liệu:
1. **Crawl & Thu thập Dữ liệu**: Thu thập dữ liệu việc làm IT tự động từ các nền tảng tuyển dụng lớn tại Việt Nam (ITviec, TopCV, TopDev, VietJobs, Vieclam24h, JobsGO).
2. **Tiền xử lý Dữ liệu (Data Processing & Cleaning)**: Làm sạch, chuẩn hóa kỹ năng, mức lương, cấp bậc kinh nghiệm, hình thức làm việc và vị trí địa lý.
3. **Web Dashboard Trực quan hóa (FastAPI + ReactJS + Plotly)**: Hệ thống 5 trang phân tích chuyên sâu với giao diện hiện đại, tương tác mượt mà (Drill-down & Cross-filtering).
4. **Trợ lý AI Phê duyệt Mã nguồn (Human-in-the-Loop AI Analyst)**: Tích hợp AI (Gemini 1.5/2.0) giúp đề xuất ý tưởng, tự động sinh code Python phân tích và thực thi an toàn tại máy cục bộ dưới sự kiểm tra, phê duyệt của con người.

---

## 📂 2. Cấu trúc Dự án

```text
Final/
├── RunDashboard.exe                # File thực thi khởi chạy nhanh Dashboard trên Windows
├── requirements.txt                # Các thư viện Python tổng quát
├── README.md                       # 📘 Tài liệu giới thiệu & Hướng dẫn khởi chạy dự án
├── README_AI.md                    # 🤖 Thuyết minh chi tiết Hệ thống AI Analyst (Human-in-the-Loop)
├── docs/                           # Tài liệu hướng dẫn & Báo cáo đồ án
│   ├── ai-guide-v2.pdf             # Yêu cầu & Hướng dẫn tích hợp AI của môn học
│   └── Report_Final.docx           # Báo cáo tổng kết đồ án
├── data/                           # Kho dữ liệu tập trung
│   ├── raw/                        # Dữ liệu cào thô chưa qua xử lý
│   └── processed/                  # Dữ liệu sạch (vietnam_it_jobs_processed.csv)
├── crawler/                        # Scripts cào dữ liệu tự động từ các trang web
├── notebooks/                      # Jupyter Notebooks phục vụ EDA & Data Cleaning
└── dashboard/                      # Hệ thống Web Dashboard (Frontend & Backend)
    ├── backend/                    # Backend REST API & Executer (FastAPI)
    │   ├── routers/                # Các Endpoints API theo trang (router_page1 -> router_page5)
    │   ├── utils/                  # Logic tính toán & khởi tạo biểu đồ Plotly
    │   ├── ai_config.py            # Cấu hình Gemini API Keys, Fallback & System Prompts
    │   ├── chart_catalog.py        # Danh mục biểu đồ có sẵn cho Catalog Routing
    │   ├── main.py                 # Endpoint chính FastAPI & Cache Warm-up
    │   └── requirements.txt        # Thư viện Python dành riêng cho Backend
    └── frontend/                   # Frontend Giao diện Tương tác (ReactJS + Vite)
        ├── src/
        │   ├── components/         # Các Component giao diện (Page 1 -> Page 5)
        │   │   └── ai/             # Components Chat AI, Monaco Editor, History Sidebar
        │   ├── styles/             # Design System & Custom CSS Styling
        │   └── App.jsx             # Root Layout & Tab Navigation
        ├── package.json
        └── vite.config.js
```

---

## 🚀 3. Hướng dẫn Cài đặt & Khởi chạy

### 📋 Yêu cầu hệ thống tối thiểu:
- **Python**: 3.10 trở lên
- **Node.js**: 18.x hoặc 20.x LTS trở lên

---

### ⚡ CÁCH 1: KHỞI CHẠY NHANH BẰNG FILE `.EXE` (Khuyên dùng trên Windows)

1. Mở thư mục dự án `Final/`.
2. Click đúp chuột vào file **`RunDashboard.exe`**.
3. Ứng dụng sẽ tự động bật các tiến trình Backend và Frontend.
4. Mở trình duyệt truy cập: **`http://localhost:5173`**

---

### 🛠️ CÁCH 2: KHỞI CHẠY THỦ CÔNG (Dành cho Dev / macOS / Linux)

#### 🔹 Bước 1: Khởi chạy Backend (FastAPI)

1. Mở Terminal tại thư mục `dashboard/`:
   ```bash
   cd dashboard
   ```
2. Cài đặt các thư viện Python:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Cấu hình Gemini API Key cho AI (Tùy chọn):
   Tạo file `.env` trong thư mục `dashboard/backend/.env` với nội dung:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. Khởi chạy FastAPI Server tại cổng `8000`:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *(Backend API sẽ hoạt động tại: `http://localhost:8000`)*

#### 🔹 Bước 2: Khởi chạy Frontend (React + Vite)

1. Mở một cửa sổ Terminal mới và di chuyển vào thư mục `dashboard/frontend/`:
   ```bash
   cd dashboard/frontend
   ```
2. Cài đặt các gói thư viện Node.js:
   ```bash
   npm install
   ```
3. Khởi chạy Dev Server:
   ```bash
   npm run dev
   ```
   *(Giao diện Web Dashboard sẽ hoạt động tại: `http://localhost:5173`)*

---

## 📊 4. Cấu trúc 5 Trang Phân tích của Dashboard

- **Trang 1 — Xu hướng & Địa lý**: Tổng quan số lượng tin tuyển dụng, xu hướng theo thời gian, bản đồ địa lý các tỉnh/thành Việt Nam (hỗ trợ **Drill-down theo Vùng miền** và **Cross-filter Brushing & Linking** từ Hình thức làm việc ➔ Line Chart xu hướng).
- **Trang 2 — Kỹ năng Công nghệ**: Top 15 kỹ năng công nghệ được săn đón nhất, Heatmap ma trận Kỹ năng x Nhóm vị trí, và xu hướng công nghệ mới (AI/ML, Cloud, DevOps, Data).
- **Trang 3 — Mức lương & Phúc lợi**: Phân bố mức lương toàn ngành (Median vs Mean), chênh lệch lương giữa các địa phương/Remote, Heatmap lương theo Vị trí & Kinh nghiệm.
- **Trang 4 — Cấp bậc Kinh nghiệm**: Treemap phân tích độ cởi mở của các nhóm vị trí đối với nhân sự trẻ (Intern/Fresher/Junior) và biểu đồ phân bố cấp bậc kinh nghiệm.
- **Trang 5 — Trợ lý Phân tích AI (AI Analyst)**: Khung tương tác AI hỗ trợ hỏi đáp, tự động sinh mã nguồn Python phân tích, cho phép người dùng **xem, gõ sửa code trực tiếp trên Monaco Editor** và **Duyệt & Thực thi an toàn tại máy local**.

---

## 🤖 5. Hệ thống AI Analyst (Human-in-the-Loop)

Dự án đáp ứng 100% các tiêu chuẩn trong hướng dẫn tích hợp AI của môn học (`Final/docs/ai-guide-v2.pdf`):
- **Phê duyệt mã nguồn (Human-in-the-Loop)**: Code do AI sinh ra ở trạng thái **⚠️ Chờ duyệt** ➔ Người dùng gõ sửa tham số ➔ Bấm **Duyệt & Chạy** mới thực thi.
- **Thực thi Local**: Code Python chạy trực tiếp trên Pandas DataFrame local qua `exec()`, không thực thi ngầm.
- **Tích hợp SSE Streaming & Vision AI**: AI trả lời theo thời gian thực và đọc hiểu phân tích ảnh biểu đồ/bảng số liệu.
- **Lưu trữ nhật ký lịch sử**: Truy xuất toàn bộ prompt, code, kết quả Plotly và cho phép **tải file CSV số liệu thô**.

📖 **Xem tài liệu chi tiết về Hệ thống AI tại file: [`README_AI.md`](file:///d:/BaiTapKi2Nam3/TQHDL/Final/README_AI.md)**

---

## 👥 6. Thành viên thực hiện & Phân công nhiệm vụ

Đồ án thuộc môn **Trực quan hóa dữ liệu (CQ2023/24)** — **Nhóm 5**:

| STT | MSSV | Họ và tên | Nhiệm vụ phân công | Đóng góp |
|:---:|:---:|:---|:---|:---:|
| 1 | **23120192** | **Nguyễn Nhật Vy** | • Phân tích chung về bộ dữ liệu<br>• Phân tích mục tiêu cá nhân<br>• Thiết kế dashboard<br>• Viết báo cáo<br>• Kiểm thử AI | **25%** |
| 2 | **23120193** | **Trần Kim Yến** | • Phân tích chung về bộ dữ liệu<br>• Phân tích mục tiêu cá nhân<br>• Thiết kế dashboard<br>• Viết báo cáo<br>• Kiểm thử AI | **25%** |
| 3 | **23120201** | **Nguyễn Thị Trúc Hằng** | • Phân công nhiệm vụ<br>• Thu thập dữ liệu<br>• Phân tích mục tiêu cá nhân<br>• Thiết kế dashboard<br>• Tích hợp AI<br>• Viết báo cáo | **25%** |
| 4 | **23120206** | **Ngô Thuận An** | • Thu thập dữ liệu<br>• Phân tích mục tiêu cá nhân<br>• Thiết kế dashboard<br>• Tích hợp AI<br>• Viết báo cáo | **25%** |