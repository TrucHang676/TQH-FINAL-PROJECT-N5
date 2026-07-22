# TQHDL - Vietnam IT Recruitment Market Analytics & AI Analyst Dashboard

> **Hệ thống Phân tích dữ liệu & Dashboard Trực quan hóa Thị trường Tuyển dụng IT Việt Nam tích hợp Trợ lý AI Phê duyệt Mã nguồn (Human-in-the-Loop)**

Dự án môn học **Phân tích Quản lý Dữ liệu lớn (TQHDL)** — Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM.

---

## 📌 Tổng quan dự án

Dự án được xây dựng theo kiến trúc **Monorepo**, bao gồm toàn bộ vòng đời phân tích dữ liệu:
1. **Crawl & Thu thập Dữ liệu**: Thu thập dữ liệu việc làm IT tự động từ các nền tảng tuyển dụng lớn tại Việt Nam (ITviec, TopCV, TopDev, VietJobs, Vieclam24h, JobsGO).
2. **Tiền xử lý Dữ liệu (Data Cleaning & Normalization)**: Làm sạch, chuẩn hóa kỹ năng, mức lương, cấp bậc kinh nghiệm, hình thức làm việc và vị trí địa lý.
3. **Web Dashboard Trực quan hóa (FastAPI + ReactJS + Plotly)**: Hệ thống 5 trang phân tích chuyên sâu với giao diện hiện đại, tương tác mượt mà và trực quan.
4. **Hệ thống Trợ lý AI Phê duyệt Mã nguồn (Human-in-the-Loop AI Analyst)**: Tích hợp AI (Gemini 1.5/2.0) giúp đề xuất ý tưởng, tự động sinh code Python phân tích và thực thi an toàn tại máy cục bộ dưới sự phê duyệt của con người.

---

## 📂 Cấu trúc dự án

```text
Final/
├── docs/                           # Tài liệu hướng dẫn & Báo cáo đồ án
│   ├── ai-guide-v2.pdf             # Yêu cầu & Hướng dẫn tích hợp AI của môn học
│   └── Report_Final.docx           # Báo cáo tổng kết đồ án
├── data/                           # Dữ liệu tập trung
│   ├── raw/                        # Dữ liệu cào thô
│   └── processed/                  # Dữ liệu sạch (vietnam_it_jobs_processed.csv)
├── crawler/                        # Scripts cào dữ liệu tự động
├── notebooks/                      # Jupyter Notebooks phục vụ EDA & xử lý dữ liệu
├── README_AI.md                    # 📘 TÀI LIỆU CHI TIẾT VỀ HỆ THỐNG AI ANALYST
└── dashboard/                      # Hệ thống Web Dashboard hoàn chỉnh
    ├── backend/                    # Backend REST API & Executer (FastAPI)
    │   ├── routers/                # API Endpoints (Page 1 -> Page 5 AI)
    │   │   ├── router_page1.py     # API Trang 1: Xu hướng & Địa lý
    │   │   ├── router_page2.py     # API Trang 2: Kỹ năng công nghệ
    │   │   ├── router_page3.py     # API Trang 3: Mức lương & Phúc lợi
    │   │   ├── router_page4.py     # API Trang 4: Cấp bậc kinh nghiệm
    │   │   └── router_page5.py     # API Trang 5: Trợ lý AI Analyst (SSE Streaming, Exec, History)
    │   ├── utils/                  # Logic tính toán & khởi tạo biểu đồ Plotly
    │   ├── ai_config.py            # Cấu hình Gemini API Keys, Fallback & System Prompts
    │   ├── chart_catalog.py        # Danh mục biểu đồ có sẵn cho AI Catalog Routing
    │   ├── main.py                 # Endpoint chính FastAPI & Cache Warm-up
    │   └── requirements.txt
    └── frontend/                   # Frontend Giao diện Tương tác (ReactJS + Vite)
        ├── src/
        │   ├── components/         # Các Dashboard Components (Page 1 -> 5)
        │   │   └── ai/             # Components giao diện Chat AI, Monaco Editor, History
        │   ├── styles/             # Design System & Custom CSS Styling
        │   └── App.jsx             # Root Layout, Tab Navigation & Header
        ├── package.json
        └── vite.config.js
```

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

### Yêu cầu hệ thống:
- **Python**: 3.10 trở lên
- **Node.js**: 18.x hoặc 20.x LTS trở lên

---

### ⚡ CÁCH 1: KHỞI CHẠY NHANH (Khuyên dùng cho Windows)

1. Mở thư mục `Final/` trong trình quản lý file.
2. Click đúp chuột vào file **`run.bat`**.
3. File `.bat` sẽ tự động khởi chạy 2 cửa sổ Terminal độc lập (Backend Port `8000` & Frontend Port `5173`).
4. Truy cập giao diện Web tại: **`http://localhost:5173`**

---

### 🛠️ CÁCH 2: KHỞI CHẠY THỦ CÔNG (Dành cho Dev / macOS / Linux)

#### 1. Khởi chạy Backend (FastAPI):
```bash
cd dashboard/backend

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Cấu hình file .env (Tùy chọn cho tính năng AI)
# Tạo file .env trong dashboard/backend với nội dung:
# GEMINI_API_KEY=your_gemini_api_key_here

# Khởi chạy FastAPI Server
uvicorn main:app --reload --port 8000
```
*Backend Server sẽ chạy tại: `http://localhost:8000`*

#### 2. Khởi chạy Frontend (React + Vite):
```bash
cd dashboard/frontend

# Cài đặt gói thư viện Node
npm install

# Khởi chạy Dev Server
npm run dev
```
*Frontend App sẽ chạy tại: `http://localhost:5173`*

---

## 📊 Cấu trúc 5 Trang Phân tích của Dashboard

1. **Trang 1 — Xu hướng & Địa lý**: Phân tích tổng quan số lượng tin tuyển dụng, xu hướng theo thời gian, bản đồ phân bố tuyển dụng các tỉnh/thành phố Việt Nam (hỗ trợ **Drill-down theo Vùng miền** và **Cross-filtering**).
2. **Trang 2 — Kỹ năng Công nghệ**: Top 15 kỹ năng công nghệ được săn đón nhất, Heatmap ma trận kỹ năng x nhóm vị trí, và xu hướng công nghệ emerging (AI/ML, Cloud, DevOps, Data).
3. **Trang 3 — Mức lương & Phúc lợi**: Phân bố mức lương toàn ngành (Median vs Mean), chênh lệch lương giữa các địa phương/Remote, Heatmap lương theo Vị trí & Cấp bậc.
4. **Trang 4 — Cấp bậc Kinh nghiệm**: Treemap phân tích độ cởi mở của các nhóm vị trí đối với nhân sự trẻ (Intern/Fresher/Junior) và biểu đồ phân bố cấp bậc.
5. **Trang 5 — Trợ lý Phân tích AI (AI Analyst)**: Khung tương tác AI hỗ trợ hỏi đáp, tự động sinh mã nguồn Python phân tích, cho phép người dùng **xem, gõ sửa code trực tiếp trên Monaco Editor** và **Duyệt & Thực thi an toàn tại máy local**.

---

## 🤖 Hệ thống AI Analyst (Human-in-the-Loop)

Dự án tích hợp đầy đủ các tiêu chuẩn theo hướng dẫn môn học (`ai-guide-v2.pdf`):
- **Phê duyệt mã nguồn (Human-in-the-Loop)**: AI sinh code ➔ Trạng thái **Chờ duyệt** ➔ Người dùng gõ sửa tham số ➔ Bấm **Duyệt & Chạy** mới thực thi.
- **Thực thi Local**: Mã nguồn Python chạy trực tiếp trên Pandas DataFrame ở máy cục bộ thông qua môi trường cách ly `exec()`.
- **Tích hợp SSE Streaming & Vision AI**: AI sinh câu trả lời theo thời gian thực và hỗ trợ phân tích hình ảnh biểu đồ/bảng số liệu.
- **Lưu trữ nhật ký lịch sử**: Truy xuất đầy đủ tất cả câu hỏi, code, kết quả Plotly và file CSV số liệu thô.

📖 **Xem hướng dẫn chi tiết về Kiến trúc AI tại file: [`README_AI.md`](file:///d:/BaiTapKi2Nam3/TQHDL/Final/README_AI.md)**

---

## 👥 Thành viên thực hiện
Đồ án thuộc môn **Phân tích Quản lý Dữ liệu lớn (TQHDL)** - Nhóm 5.