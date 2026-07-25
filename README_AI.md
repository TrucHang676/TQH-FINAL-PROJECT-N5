# 🤖 HỆ THỐNG TRỢ LÝ PHÂN TÍCH AI (HUMAN-IN-THE-LOOP AI ANALYST)

> **Tài liệu Thuyết minh Kiến trúc, Luồng Hoạt động và Quy chuẩn Tích hợp AI**  
> Tuân thủ 100% Yêu cầu Tích hợp AI theo hướng dẫn môn học (`Final/docs/ai-guide-v2.pdf`).

---

## 📑 Mục lục

- [🚀 Hướng dẫn Sử dụng Nhanh (Dành cho Người dùng)](#-hướng-dẫn-sử-dụng-nhanh-dành-cho-người-dùng)
  - [① Bắt đầu — Nhập câu hỏi/yêu cầu](#-bắt-đầu--nhập-câu-hỏiyêu-cầu)
  - [② Dùng Lệnh Nhanh (Shortcuts)](#-dùng-lệnh-nhanh-shortcuts)
  - [③ Đính kèm Ảnh để Phân tích (Vision AI)](#-đính-kèm-ảnh-để-phân-tích-vision-ai)
  - [④ Xem xét & Chỉnh sửa Code](#-xem-xét--chỉnh-sửa-code-bước-quan-trọng-nhất)
  - [⑤ Duyệt & Chạy Code](#-duyệt--chạy-code)
  - [⑥ Xem & Quản lý Lịch sử](#-xem--quản-lý-lịch-sử)
  - [💡 Câu hỏi mẫu hay dùng](#-một-số-câu-hỏi-mẫu-hay-dùng)
  - [⚠️ Lưu ý quan trọng](#️-lưu-ý-quan-trọng)
- [🗂️ Cấu trúc Cài đặt Chi tiết](#️-cấu-trúc-cài-đặt-chi-tiết)
  - [Sơ đồ thư mục](#sơ-đồ-thư-mục-liên-quan-đến-ai)
  - [Chi tiết Backend](#chi-tiết-từng-file-backend)
    - [`ai_config.py` — Cấu hình trung tâm](#backendai_configpy--cấu-hình-trung-tâm)
    - [`chart_catalog.py` — Danh mục biểu đồ](#backendchart_catalogpy--danh-mục-biểu-đồ-sẵn-có)
    - [`router_page5.py` — Router AI chính](#backendrouters-router_page5py--router-ai-chính-1019-dòng)
  - [Chi tiết Frontend](#chi-tiết-từng-file-frontend)
  - [Sơ đồ luồng dữ liệu nội bộ](#sơ-đồ-luồng-dữ-liệu-nội-bộ)
- [📌 1. Triết lý Thiết kế & Tuyên ngôn Nguyên tắc](#-1-triết-lý-thiết-kế--tuyên-ngôn-nguyên-tắc)
  - [1.1 Vai trò phân định rõ ràng](#11-vai-trò-phân-định-rõ-ràng)
  - [1.2 Nguyên tắc "Không thực thi ngầm"](#12-nguyên-tắc-không-thực-thi-ngầm-no-background-execution)
  - [1.3 Nguyên tắc Thực thi Local](#13-nguyên-tắc-thực-thi-local-local-execution-only)
- [🏗️ 2. Cấu trúc Kiến trúc Hệ thống AI](#️-2-cấu-trúc-kiến-trúc-hệ-thống-ai)
  - [2.1 Backend (Python FastAPI)](#21-backend-python-fastapi)
  - [2.2 Frontend (ReactJS + Monaco Editor)](#22-frontend-reactjs--monaco-editor)
- [🔄 3. Luồng Hoạt động Chi tiết (3 Giai đoạn)](#-3-luồng-hoạt-động-chi-tiết-3-giai-đoạn)
- [📡 4. Danh mục API Endpoints của AI](#-4-danh-mục-api-endpoints-của-ai)
  - [4.1 POST /api/ai/request/stream](#41-post-apiairequest-stream-sse-real-time-streaming)
  - [4.2 POST /api/ai/execute](#42-post-apiaiexecute-thực-thi-mã-nguồn-đã-phê-duyệt)
  - [4.3 GET, DELETE, PIN, RENAME /api/ai/history...](#43-get-delete-pin-rename-apiaihistory)
- [🛠️ 5. Hướng dẫn Thiết lập & Khởi chạy Module AI](#️-5-hướng-dẫn-thiết-lập--khởi-chạy-module-ai)
- [🌟 6. Các Tính năng Độc đáo Nổi bật](#-6-các-tính-năng-độc-đáo-nổi-bật)
- [📋 7. Quy trình Kiểm thử & Bảo vệ (Demo với Giảng viên)](#-7-quy-trình-kiểm-thử--bảo-vệ-demo-với-giảng-viên)

---

## 🚀 HƯỚNG DẪN SỬ DỤNG NHANH DÀNH CHO NGƯỜI DÙNG

> 📍 Chức năng AI nằm ở **Tab cuối cùng** của Dashboard — Tab có icon 🤖 hoặc nhãn **AI Analyst**.

---

### ① Bắt đầu — Nhập câu hỏi/yêu cầu

Ở phía dưới màn hình, trong ô nhập liệu **"Nhập yêu cầu, dán ảnh (Ctrl+V), hoặc gõ "/" để xem lệnh nâng cao..."**, bạn gõ bất kỳ câu hỏi nào bằng **tiếng Việt hoặc tiếng Anh**, rồi nhấn **Enter** hoặc bấm nút **Gửi** (icon ▶️).

Khi chưa có cuộc hội thoại nào, trang sẽ hiển thị **Màn hình chào** với 4 câu hỏi mẫu để bấm bắt đầu ngay:
- `"Top 15 kỹ năng công nghệ được săn đón nhiều nhất trong ngành IT là gì?"`
- `"So sánh mức lương giữa Senior và Junior/Fresher"`
- `"Vẽ biểu đồ số lượng tin tuyển dụng theo nhóm vị trí"`
- `"Xu hướng làm việc từ xa thay đổi thế nào theo thời gian?"`

**Ví dụ bạn có thể gõ:**
- `"Top 10 kỹ năng được tuyển dụng nhiều nhất"`
- `"So sánh mức lương theo cấp độ kinh nghiệm"`
- `"Vẽ biểu đồ phân bố vị trí công việc theo vùng miền"`
- `"Nhóm nào có mức lương trung bình cao nhất?"`
- `"Xu hướng tuyển dụng tháng nào cao nhất trong năm?"`

---

### ② Dùng Lệnh Nhanh (Shortcuts)

Gõ dấu `/` vào ô chat để hiện bảng gợi ý lệnh nâng cao. Bảng gợi ý tự lọc theo ký tự bạn đang gõ và tự ẩn sau khi bạn gõ dấu cách (chuyển sang phần nội dung câu hỏi):

| Lệnh | Chế độ gửi Backend | Tác dụng |
|---|---|---|
| `/hoi` | `mode: "ask"` | Đặt câu hỏi thống kê, AI **bắt buộc** trả lời bằng **văn bản + số liệu**, không sinh code |
| `/code` | `mode: "code"` | Yêu cầu AI **bắt buộc viết code Python** vẽ biểu đồ theo ý bạn, dù câu hỏi nghe như ý tưởng |
| `/giaithich` | `mode: "explain"` | Đề nghị AI **giải thích chi tiết** đoạn code/kết quả gần nhất trong cuộc hội thoại bằng lời |
| `/nhanxet` | `mode: "comment"` | Yêu cầu AI **nhận xét** biểu đồ đã chạy gần nhất trong cuộc hội thoại, dựa trên số liệu thật |

**Ví dụ kết hợp:**
```
/code Vẽ biểu đồ tròn thể hiện tỉ lệ hình thức làm việc (full-time, part-time, remote...)
```

---

### ③ Đính kèm Ảnh để Phân tích (Vision AI)

Bạn có thể **chụp/xuất ảnh biểu đồ** từ Dashboard rồi đính kèm vào ô chat để yêu cầu AI nhận xét:

1. Bấm nút **📎 (Đính kèm ảnh)** bên cạnh ô nhập liệu, **HOẶC** dán ảnh trực tiếp từ clipboard bằng **Ctrl+V** (tiện khi đã chụp màn hình).
2. Ảnh sẽ hiện phần **xem trước** phía trên ô nhập — bấm nút **✕** nếu muốn bỏ ảnh.
3. Gõ thêm câu hỏi, ví dụ: `"Nhận xét về xu hướng trong biểu đồ này"` rồi Gửi.

> AI sẽ đọc ảnh và đưa ra phân tích chuyên sâu, không bịa số liệu — chỉ trích dẫn con số ĐỌC ĐƯỢC trực tiếp từ ảnh.

---

### ④ Xem xét & Chỉnh sửa Code (Bước Quan trọng nhất!)

Sau khi AI sinh ra code Python, nó sẽ hiển thị trong một **khung code Monaco Editor** (giống VS Code) với badge màu vàng **"⚠️ Chờ duyệt"**. Phía trên khung code là đoạn **dẫn nhập** (preamble) giải thích hướng phân tích mà AI đề xuất.

**Lúc này bạn CÓ THỂ:**

- ✏️ **Trực tiếp gõ sửa code** trong khung đó — ví dụ:
  - Đổi `nlargest(5)` thành `nlargest(10)` để lấy Top 10 thay vì Top 5
  - Đổi màu sắc `color='#59B292'` thành màu bạn thích
  - Thêm điều kiện lọc thêm theo ý muốn
- 🔍 **Phóng to** khung code để đọc dễ hơn (bấm nút ⬜ góc phải)
- ❌ **Từ chối** và yêu cầu AI viết lại nếu không ưng

---

### ⑤ Duyệt & Chạy Code

Sau khi xem xét (và tùy chỉnh nếu muốn), bấm nút **▶️ "Duyệt & Chạy"**:

- Hệ thống thực thi code ngay trên máy tính của bạn với bộ dữ liệu thực.
- **Biểu đồ Plotly tương tác** sẽ hiển thị ngay bên dưới — bạn có thể hover, zoom, pan.
- Nút **⬇️ Tải CSV** xuất hiện — bấm để tải bảng số liệu thô định dạng `.csv`.
- Nút **📋 Xem Logs** để xem chi tiết quá trình thực thi.
- Nếu bật **Tự động nhận xét** (mặc định bật), AI sẽ tự viết nhận xét phân tích ngay dưới biểu đồ dựa trên số liệu thật vừa chạy ra — tách 2 pha để biểu đồ hiện ngay, nhận xét đến sau.

---

### ⑥ Xem & Quản lý Lịch sử

Bên **cột trái** của trang AI có panel **Lịch sử**:

- Xem lại toàn bộ các câu hỏi và kết quả trước đó trong phiên làm việc.
- Bấm vào một mục để xem lại biểu đồ/phân tích đó.
- **Đổi tên hội thoại trực tiếp (Inline Editing):** Bấm biểu tượng cây bút ✏️ bên cạnh tên phiên thoại, gõ tên mới rồi bấm lưu ✔️ hoặc hủy ❌.
- Bấm nút 📌 để **ghim** một cuộc hội thoại quan trọng lên đầu danh sách.
- Phân nhóm hiển thị: **Ghim 📌** / **Hôm nay** / **7 ngày qua** / **Cũ hơn**.
- Bấm nút 🗑️ để xóa một cuộc hội thoại không cần thiết.
- **Đồng bộ Đám mây & Dual-Write Fallback:** Toàn bộ lịch sử được lưu trên **Cloud PostgreSQL (Supabase DB)** kết hợp tự động ghi bản sao local vào `ai_history.json`. Nếu mất mạng hoặc máy chủ DB từ chối, hệ thống tự động Fallback về local file, đảm bảo 0% rủi ro mất dữ liệu hay gián đoạn dịch vụ!

---

### 💡 Một số câu hỏi mẫu hay dùng

```
Top 10 kỹ năng lập trình được yêu cầu nhiều nhất
```
```
Phân phối mức lương theo nhóm vị trí công việc (boxplot)
```
```
So sánh số lượng tuyển dụng giữa Hà Nội và TP.HCM theo từng tháng
```
```
Tỉ lệ % các nhóm kinh nghiệm (Junior, Mid, Senior, Lead) trong dataset
```
```
Nhận xét xu hướng tuyển dụng IT tại Việt Nam từ dữ liệu hiện có
```
```
Heatmap thể hiện mức lương trung bình theo kinh nghiệm và vị trí công việc
```

---

### ⚠️ Lưu ý quan trọng

| Điều cần biết | Giải thích |
|---|---|
| **AI không tự chạy code** | Code AI sinh ra luôn ở trạng thái "Chờ duyệt" — bạn phải chủ động bấm Duyệt & Chạy |
| **Dữ liệu hoàn toàn cục bộ** | Dữ liệu `vietnam_it_jobs_processed.csv` chỉ ở máy bạn, không gửi lên cloud |
| **AI có thể sai** | Hãy luôn xem lại code trước khi duyệt; bạn có thể sửa tham số tùy ý |
| **Quota Gemini** | Nếu thấy báo lỗi "Quota", hệ thống tự động chuyển sang API Key dự phòng; nếu hết tất cả key sẽ hiện thông báo thân thiện kèm nút **Thử lại** |
| **Giới hạn ngữ cảnh** | AI nhớ tối đa **8 lượt hội thoại** gần nhất trong một phiên (các lượt cũ hơn được tóm tắt thành danh sách câu đã hỏi, không mất hoàn toàn) |
| **Nút Dừng** | Khi AI đang trả lời (streaming), nút Gửi biến thành nút **⬛ Dừng** — bấm để hủy giữa chừng, tiết kiệm quota |

---


---

---

## 🗂️ CẤU TRÚC CÀI ĐẶT CHI TIẾT

### Sơ đồ thư mục liên quan đến AI

```
Final/
├── README_AI.md                          ← Tài liệu này
│
├── dashboard/
│   ├── backend/
│   │   ├── .env                          ← Chứa GEMINI_API_KEY(S) — KHÔNG commit lên git
│   │   ├── ai_config.py                  ← [CẤU HÌNH AI] Model, API keys, System/Vision/Routing/
│   │   │                                    Comment/Suggestion/Forced prompts (234 dòng)
│   │   ├── ai_history.json               ← [DỮ LIỆU] Lịch sử hội thoại lưu local (JSON)
│   │   ├── ai_prepared_questions.json    ← [DỮ LIỆU] Câu hỏi mẫu gợi ý cho người dùng
│   │   ├── chart_catalog.py              ← [CATALOG] Danh mục 19 biểu đồ sẵn có: 13 trang
│   │   │                                    dashboard (P1-01..P4-03) + 6 mở rộng (EX-1..EX-6)
│   │   │
│   │   └── routers/
│   │       └── router_page5.py           ← [ROUTER CHÍNH] Toàn bộ logic API AI (1019 dòng)
│   │
│   └── frontend/
│       └── src/
│           ├── components/
│           │   ├── Dashboard_page5.jsx   ← [VIEW CHÍNH] Trang AI — streaming, auto-comment,
│           │   │                            abort/stop, welcome screen, quota handling (724 dòng)
│           │   └── ai/
│           │       ├── AiChatMessage.jsx ← [COMPONENT] Tin nhắn AI + Monaco Editor + Nút duyệt
│           │       │                        + preamble + Plotly render + CSV download (30KB)
│           │       ├── AiHistoryPanel.jsx← [COMPONENT] Panel lịch sử bên trái + ghim/xóa
│           │       ├── AiRequestForm.jsx ← [COMPONENT] Ô nhập prompt + đính kèm ảnh + Ctrl+V
│           │       │                        paste + menu lệnh nhanh + nút Dừng (226 dòng)
│           │       └── AiService.js      ← [SERVICE] Gọi API Backend (stream, execute, history,
│           │                                pin) với SSE ReadableStream + AbortController
│           └── styles/
│               └── style.css             ← CSS cho giao diện AI (chat bubble, Monaco, badges...)
```

---

### Chi tiết từng file Backend

#### `backend/ai_config.py` — Cấu hình trung tâm

| Hằng số / Biến | Giá trị mặc định | Mô tả |
|---|---|---|
| `GEMINI_MODEL_NAME` | `gemini-pro-latest` | Model chính sinh code/phân tích (có thể override qua `.env`) |
| `TITLE_MODEL_NAME` | `gemini-flash-latest` | Model tự đặt tiêu đề cuộc hội thoại (nhanh/rẻ hơn) |
| `ROUTING_MODEL_NAME` | `gemini-flash-latest` | Model định tuyến câu hỏi vào catalog biểu đồ có sẵn |
| `GEMINI_API_KEYS` | Đọc từ `.env` | Danh sách key phân cách bởi dấu phẩy, fallback tự động khi quota 429 |
| `SYSTEM_PROMPT` | (dài ~110 dòng) | Hướng dẫn AI về dataset 18 cột, quy tắc Chế độ A (văn bản) / Chế độ B (code Plotly), cách chọn chế độ |
| `VISION_PROMPT` | (dài ~10 dòng) | System prompt riêng khi AI phân tích ảnh (Vision mode) — chỉ đọc số từ ảnh, không bịa |
| `ROUTING_PROMPT_TEMPLATE` | (template) | Prompt để AI định tuyến câu hỏi → mã catalog (VD: `P2-02`) hoặc `NONE` |
| `COMMENT_PROMPT_TEMPLATE` | (template dài) | Prompt viết nhận xét 5 khối theo Mẫu 5: luận điểm → phân tích trước → marker `[[BIEU_DO]]` → phân tích sau → lưu ý |
| `SUGGESTION_PROMPT_TEMPLATE` | (template) | **[MỚI]** Prompt gợi ý câu hỏi tiếp theo BÁM NGỮ CẢNH, theo cơ chế GOAL EXPLORER (Dibia, 2023) — chỉ CHỌN trong danh mục có sẵn, không tự bịa |
| `ASK_FORCED_PROMPT` | (prompt) | **[MỚI]** Prompt cưỡng chế Chế độ A khi người dùng gõ `/hoi` — không sinh code |
| `CODE_FORCED_SUFFIX` | (suffix) | **[MỚI]** Suffix ghép vào system prompt khi người dùng gõ `/code` — bắt buộc Chế độ B |
| `EXPLAIN_FORCED_PROMPT` | (prompt) | **[MỚI]** Prompt giải thích lại code/kết quả gần nhất khi người dùng gõ `/giaithich` |

**Cấu hình `.env`:**
```env
# Bắt buộc — ít nhất 1 key
GEMINI_API_KEY=AIzaSy...your_key

# Tùy chọn — nhiều key để fallback tự động khi hết quota
GEMINI_API_KEYS=key1,key2,key3

# Tùy chọn — ghi đè model mặc định
GEMINI_MODEL_NAME=gemini-2.5-pro
TITLE_MODEL_NAME=gemini-2.0-flash
ROUTING_MODEL_NAME=gemini-2.0-flash
```

---

#### `backend/chart_catalog.py` — Danh mục biểu đồ sẵn có

Chứa định nghĩa **19 biểu đồ** chia 2 nhóm: **13 biểu đồ hiển thị trên dashboard** (trang 1-4) và **6 biểu đồ mở rộng** (EX-1..EX-6, chuẩn bị sẵn cho buổi vấn đáp, không hiển thị trên trang dashboard nào):

**Biểu đồ trang Dashboard (P1-01 → P4-03):**

| Mã | Trang | Mô tả biểu đồ | Hàm vẽ |
|---|---|---|---|
| `P1-01` | Trang 1 | Xu hướng tuyển dụng theo thời gian | `charts_page1.create_time_trend_chart` |
| `P1-02a` | Trang 1 | Phân bố tuyển dụng theo tỉnh/thành (bản đồ) | `charts_page1.create_vietnam_map` |
| `P1-02b` | Trang 1 | Phân bố tuyển dụng theo vùng miền (Bắc/Trung/Nam) | `charts_page1.create_region_vertical_chart` |
| `P1-03` | Trang 1 | Hình thức làm việc (Full-time, Part-time, ...) | `charts_page1.create_work_type_chart` |
| `P2-01` | Trang 2 | Top 15 kỹ năng phổ biến nhất | `charts_page2.create_top_skills_chart` |
| `P2-02` | Trang 2 | Heatmap kỹ năng theo nhóm vị trí | `charts_page2.create_skills_heatmap` |
| `P2-03` | Trang 2 | Xu hướng công nghệ mới (AI/ML, Cloud, DevOps) | `charts_page2.create_tech_trend_chart` |
| `P3-01` | Trang 3 | Phân bố mức lương + tỷ lệ công khai/thỏa thuận | `charts_page3.create_salary_distribution_chart` |
| `P3-02` | Trang 3 | Heatmap lương theo vị trí × kinh nghiệm | `charts_page3.create_salary_by_position_experience_chart` |
| `P3-03` | Trang 3 | So sánh lương giữa các tỉnh/thành lớn & Remote | `charts_page3.create_salary_by_location_chart` |
| `P4-01` | Trang 4 | Phân bổ tin theo cấp độ kinh nghiệm (có ghi rõ) | `charts_page4.create_experience_distribution_chart` |
| `P4-02` | Trang 4 | Treemap cơ hội cho Intern/Fresher/Junior theo vị trí | `charts_page4.create_youth_opportunity_treemap` |
| `P4-03` | Trang 4 | Box plot lương khởi điểm Intern & Fresher | `charts_page4.create_youth_salary_boxplot` |

**Biểu đồ mở rộng (EX-1 → EX-6) — chỉ dùng cho AI:**

| Mã | Mô tả biểu đồ | Hàm vẽ |
|---|---|---|
| `EX-1` | Kỹ năng đặc trưng Senior vs Junior/Fresher | `charts_extra.create_senior_signature_skills_chart` |
| `EX-2` | Nhóm vị trí có lương cao nhất/thấp nhất | `charts_extra.create_salary_extremes_by_position_chart` |
| `EX-3` | Biết Python nên ứng tuyển nhóm vị trí nào | `charts_extra.create_python_position_recommendation_chart` |
| `EX-4` | Top 15 chức danh công việc phổ biến nhất | `charts_extra.create_top_job_titles_chart` |
| `EX-5` | Hình thức làm việc tách theo nhóm vị trí | `charts_extra.create_work_type_by_position_chart` |
| `EX-6` | Top 20 cặp kỹ năng hay xuất hiện cùng nhau | `charts_extra.create_top_skill_pairs_chart` |

Mỗi mục có trường `lien_quan` (danh sách mã liên quan) để hàm `get_suggestions()` ưu tiên gợi ý các biểu đồ cùng chủ đề.

**Các hàm trong `chart_catalog.py`:**

```python
get_catalog_prompt_listing()    # Sinh text liệt kê catalog để đưa vào routing prompt
                                # (trang=0 hiển thị "mở rộng" thay vì "trang 0")
get_catalog_item(chart_id)      # Lấy định nghĩa 1 biểu đồ theo mã (VD: "P2-02")
get_suggestions(current_id,     # Gợi ý tối đa `limit` câu hỏi tiếp theo (thuần code,
    exclude_ids, limit=2)       # không gọi AI): ưu tiên lien_quan → cùng trang → bất kỳ
```

---

#### `backend/routers/router_page5.py` — Router AI chính (1019 dòng)

**Các hằng số cấu hình:**

| Hằng số | Giá trị | Mô tả |
|---|---|---|
| `MAX_CONTEXT_TURNS` | `8` | Số lượt hội thoại gần nhất tối đa đưa vào ngữ cảnh |
| `MAX_CONTEXT_RESULT_TABLES` | `2` | Chỉ nhồi bảng số liệu của 1-2 biểu đồ gần nhất vào context |
| `MAX_CONTEXT_CSV_ROWS` | `40` | Cắt bớt bảng CSV dài, giữ dòng tiêu đề + max 40 dòng đầu |
| `_ROUTING_CACHE` | `dict` | **[MỚI]** Cache kết quả định tuyến theo câu hỏi (in-process). **Chỉ cache khi khớp được mã catalog thật** — TUYỆT ĐỐI KHÔNG cache `None` (tránh 1 lần trượt "khóa cứng" câu hỏi suốt phiên server) |
| `_DATA_GROUNDING_CACHE` | `None` | **[MỚI]** Cache đoạn mô tả dữ liệu thật (tính 1 lần, dùng suốt phiên) |

**Các hàm tiện ích nội bộ:**

```python
generate_with_key_fallback(prompt, model_name)
# Gọi Gemini API, tự fallback sang key tiếp theo khi gặp lỗi quota 429

stream_text_from_prompt(prompt_or_content, model_name)
# Generator stream từng chunk text từ Gemini theo thời gian thực (SSE),
# có cùng cơ chế fallback nhiều key. Dùng cho mọi nhánh streaming.

sse_event(data)
# Định dạng 1 sự kiện SSE: dòng JSON kết thúc bằng 2 dấu xuống dòng

route_question_to_catalog(question)
# Dùng Gemini Flash định tuyến câu hỏi → mã catalog hoặc None.
# Có ROUTING CACHE: cùng câu hỏi → cùng kết quả, tiết kiệm 1 lượt Gemini.

get_catalog_chart_data(catalog_id)
# Gọi hàm vẽ biểu đồ thật (build_fn) trên toàn bộ dữ liệu, rút CSV
# long-format, trả về {item, fig, fig_json, csv}

generate_catalog_comment(question, csv_text)
# Viết nhận xét phân tích dựa trên bảng số liệu thật (dùng model Pro)

generate_title(prompt)
# Đặt tiêu đề ngắn (<6 từ) cho cuộc hội thoại mới (dùng Flash)

build_data_grounding()                                              # [MỚI]
# RAG đơn giản: rút SỰ THẬT từ dataset thật (giá trị hợp lệ của cột
# phân loại, min/max/trung vị cột lương, top 20 kỹ năng đúng chính tả,
# vài dòng mẫu) — nhồi vào prompt sinh code để chặn model chọn nhầm
# cột / bịa giá trị. Tính 1 lần rồi cache module-level.

get_system_prompt()                                                 # [MỚI]
# Ghép SYSTEM_PROMPT + build_data_grounding() cho nhánh sinh code

build_conversation_context(history, conversation_id, max_turns)
# Dựng lại ngữ cảnh tối đa 8 lượt hội thoại trước. Bao gồm:
#   • A1a: tóm tắt gọn các lượt CŨ hơn 8 lượt (thuần code, 0 token)
#   • A1b: nhồi BẢNG SỐ LIỆU THẬT (result.csv) của 1-2 biểu đồ gần nhất
#   • A1c: đánh dấu lượt nào có kèm ẢNH

find_last_chart_result(history, conversation_id)                    # [MỚI]
# Tìm item GẦN NHẤT có kết quả biểu đồ đã chạy thành công — dùng cho
# lệnh /nhanxet và tự động nhận xét sau khi thực thi code

get_context_aware_suggestions(question, answer_text, catalog_id,    # [MỚI]
    exclude_ids, limit=2)
# Gợi ý câu hỏi tiếp theo BÁM ĐÚNG NGỮ CẢNH vừa trả lời. Dùng Gemini
# Flash để CHỌN (không SINH) trong danh sách catalog còn lại, theo cơ chế
# GOAL EXPLORER của LIDA (Dibia, 2023). Fallback về get_suggestions()
# thuần code nếu lỗi.

extract_csv_from_figure(fig)
# Trích xuất bảng số liệu long-format CSV từ Plotly Figure — xử lý riêng
# theo loại trace: pie/treemap (labels+values), box (thống kê tóm tắt),
# heatmap (ma trận 2D làm phẳng), choropleth (locations+z+hovertext),
# bar/scatter/histogram (x+y). Bỏ qua scatter trang trí khi có box/treemap.

parse_data_url_image(image_str)
# Tách data URL base64 thành (mime_type, bytes) cho Vision AI

_shrink_csv_for_context(csv_text, max_rows)                         # [MỚI]
# Rút gọn bảng CSV kết quả trước khi nhồi vào ngữ cảnh hội thoại
```

**Các API Endpoint:**

```
POST /api/ai/request           → Xử lý prompt, sinh code/văn bản (không stream — giữ lại tương thích)
POST /api/ai/request/stream    → Xử lý prompt và STREAM kết quả qua SSE theo thời gian thực
POST /api/ai/execute           → Thực thi code Python đã được người dùng duyệt
GET  /api/ai/history           → Lấy danh sách toàn bộ lịch sử hội thoại
DELETE /api/ai/history/{id}    → Xóa toàn bộ các câu hỏi thuộc 1 cuộc hội thoại
POST /api/ai/history/{id}/pin  → [MỚI] Ghim/bỏ ghim 1 cuộc hội thoại
```

---

### Chi tiết từng file Frontend

#### `frontend/src/components/ai/AiService.js` — Lớp giao tiếp API

Chứa các hàm gọi API backend:
```js
sendRequest(prompt, conversationId, image)
// POST /api/ai/request — gọi không streaming (giữ tương thích)

streamRequest({ prompt, conversationId, image, mode, catalogHint, signal },
              { onStart, onDelta, onDone, onError, onAbort })
// POST /api/ai/request/stream (SSE) — dùng fetch + ReadableStream vì axios
// không hỗ trợ đọc dần response body trên trình duyệt.
// mode: null | "ask" | "code" | "explain" | "comment"
// catalogHint: mã danh mục ĐÃ BIẾT TRƯỚC (từ chip gợi ý) — bỏ 1 bước routing
// signal: AbortSignal từ AbortController để hủy stream (nút Dừng)
// onAbort: gọi khi người dùng bấm Dừng — tách khỏi onError, không hiện lỗi

executeCode(requestId, editedCode)
// POST /api/ai/execute — gửi code đã duyệt, nhận về kết quả biểu đồ + CSV

getHistory()                 // GET /api/ai/history
deleteConversation(id)       // DELETE /api/ai/history/{id}
togglePin(conversationId)    // [MỚI] POST /api/ai/history/{id}/pin
```

#### `frontend/src/components/ai/AiChatMessage.jsx` — Component tin nhắn AI

Quản lý toàn bộ **vòng đời 1 tin nhắn AI**:
- Hiển thị **đoạn dẫn nhập (preamble)** phía trên code — giải thích hướng phân tích AI đề xuất (**Mẫu 6**)
- Hiển thị văn bản (markdown rendered) với streaming theo thời gian thực
- Render khung **Monaco Code Editor** (syntax highlighting Python)
- Badge trạng thái: `⚠️ Chờ duyệt` → `⏳ Đang chạy...` → `✅ Thành công` / `❌ Lỗi`
- Nút **▶️ Duyệt & Chạy** — gọi `executeCode()`
- Nút **⬜ Phóng to** — mở Monaco fullscreen
- Nút **⬇️ Tải CSV** — xuất file `.csv` số liệu thô
- Nút **📋 Xem Logs** — hiện log thực thi Python
- Render **Plotly Figure** tương tác sau khi thực thi thành công
- Chèn **biểu đồ nhúng** tại marker `[[BIEU_DO]]` cho câu trả lời từ catalog (**Mẫu 5**)
- Hiển thị **chip gợi ý câu hỏi tiếp theo** dưới câu trả lời (bám ngữ cảnh)
- Hiển thị thông báo **quota lỗi thân thiện** kèm nút **Thử lại** thay vì chuỗi lỗi kỹ thuật

#### `frontend/src/components/ai/AiHistoryPanel.jsx` — Panel lịch sử

- Liệt kê tất cả cuộc hội thoại theo thời gian
- Phân nhóm: **Ghim 📌** / **Hôm nay** / **7 ngày qua** / **Cũ hơn**
- Click để load lại 1 cuộc hội thoại vào khung chat chính
- Nút ghim 📌 và nút xóa 🗑️ từng cuộc hội thoại

#### `frontend/src/components/ai/AiRequestForm.jsx` — Form nhập prompt

- Ô textarea tự co giãn theo độ dài nội dung
- Hỗ trợ **đính kèm ảnh** (📎) — preview ảnh trước khi gửi
- Hỗ trợ **dán ảnh từ clipboard** (Ctrl+V) — tiện khi chụp màn hình
- **Menu lệnh nhanh**: gõ `/` hiện bảng gợi ý lệnh tự lọc theo ký tự đang gõ, bấm chọn để điền vào
- Hiển thị 3 câu hỏi mẫu gợi ý nhanh (suggestion chips) khi không gõ lệnh
- Gửi bằng `Enter` (Shift+Enter = xuống dòng)
- **Nút Dừng (⬛)**: khi đang stream, nút Gửi biến thành nút Dừng để hủy giữa chừng

#### `frontend/src/components/Dashboard_page5.jsx` — View tổng thể trang AI

- Quản lý state toàn trang: `messages[]`, `isSubmitting`, `currentConversationId`, `executingId`
- **Màn hình chào** (welcome screen) với 4 câu hỏi mẫu khi chat rỗng
- Điều phối luồng SSE streaming từ `AiService.streamRequest()` với đầy đủ 6 callback: `onStart`, `onDelta`, `onDone`, `onError`, `onAbort`
- **Mẫu 6**: mọi nhánh đều stream văn bản ngay từ đầu (kể cả code) — tạo bong bóng text, nếu cuối cùng ra code thì chuyển thành bong bóng code chờ duyệt
- **Tự động nhận xét** (`autoComment`): sau khi biểu đồ chạy thành công, tự gọi `/nhanxet` để AI viết nhận xét dựa trên số liệu thật — tách 2 pha (biểu đồ hiện ngay, nhận xét đến sau)
- **AbortController**: mỗi lượt gửi tạo 1 controller mới, nút Dừng abort fetch → backend cũng ngừng generator → không tốn thêm quota
- **Xử lý lỗi quota** thân thiện: nhận diện `429/quota/ResourceExhausted`, hiện thông báo + nút Thử lại thay vì chuỗi lỗi API thô
- **Gộp khung** (turn card): code + kết quả + nhận xét tự động cùng 1 lượt hỏi được gộp chung 1 khung `.ai-turn-card` qua `turnId`
- Tự động scroll xuống cuối khi có tin nhắn mới

---

### Sơ đồ luồng dữ liệu nội bộ

```
Người dùng nhập prompt (hoặc bấm chip gợi ý)
        │
        ▼
AiRequestForm.jsx (parseCommand: tách /hoi, /code, /giaithich, /nhanxet)
        │ gọi AiService.streamRequest({prompt, mode, catalogHint, signal})
        ▼
POST /api/ai/request/stream (SSE)
        │
        ├─► [catalogHint hợp lệ?] ──► CÓ: bỏ qua routing, dùng thẳng
        │   HOẶC
        ├─► route_question_to_catalog()  ──► khớp catalog?
        │        ├── CÓ: get_catalog_chart_data()
        │        │         ├── build_fn(df) ──► fig + CSV thật
        │        │         ├── SSE start: gửi kèm fig_json (Mẫu 5)
        │        │         └── generate_catalog_comment()  ──► nhận xét AI (stream)
        │        └── KHÔNG: get_system_prompt() (= SYSTEM_PROMPT + data grounding)
        │                     └── build_conversation_context() (A1a/A1b/A1c)
        │                           └── stream_text_from_prompt() (Mẫu 6: dẫn nhập + code)
        │
        ├─► [mode="ask"]     → ASK_FORCED_PROMPT + context → stream văn bản
        ├─► [mode="code"]    → SYSTEM_PROMPT + CODE_FORCED_SUFFIX + context → stream code
        ├─► [mode="explain"] → EXPLAIN_FORCED_PROMPT + context → stream giải thích
        ├─► [mode="comment"] → find_last_chart_result() → COMMENT_PROMPT_TEMPLATE → stream
        ├─► [có ảnh]         → VISION_PROMPT + context + ảnh → stream nhận xét ảnh
        │
        ▼ (SSE stream chunks → onDelta callback)
Dashboard_page5.jsx cập nhật AiChatMessage.jsx (streaming text/code)
        │
        ├── (onDone: tách preamble/code nếu có ```python```)
        ├── (get_context_aware_suggestions → chip gợi ý bám ngữ cảnh)
        │
        ▼ (người dùng bấm Duyệt & Chạy)
POST /api/ai/execute
        │
        ├── exec(editedCode, local_env{dff, pd})  ← thực thi tại local
        ├── extract_csv_from_figure(fig)           ← rút bảng số liệu
        └── trả về { plotly_json, csv, logs }
        │
        ▼
AiChatMessage.jsx render Plotly chart + hiện nút Tải CSV
        │
        ▼ (nếu autoComment bật & có result.csv)
triggerAutoComment() → mode="comment" → stream nhận xét tự động dưới biểu đồ
```

---

## 📌 1. Triết lý Thiết kế & Tuyên ngôn Nguyên tắc


Hệ thống AI Analyst được thiết kế theo mô hình **Human-in-the-Loop (Con người là trung tâm quyết định)**, đảm bảo nguyên tắc an toàn dữ liệu và tính minh bạch tuyệt đối:

### 1.1 Vai trò phân định rõ ràng
- **AI (Mô hình Ngôn ngữ Gemini 1.5/2.0)**:
  - Đóng vai trò trợ lý đề xuất ý tưởng phân tích.
  - Viết mã nguồn Python dựa trên yêu cầu ngôn ngữ tự nhiên của người dùng.
  - Trình bày kết quả nhận xét dựa trên số liệu THẬT (không tự bịa đặt số liệu hay hình ảnh).
- **Con người (Người dùng / Nhà phân tích)**:
  - Đóng vai trò **Người phê duyệt và Quyết định (Human Approver)**.
  - Trực tiếp xem xét, gõ sửa/thay đổi các tham số trong đoạn code AI vừa viết (ví dụ: đổi `top 5` thành `top 10`, đổi màu sắc, điều kiện lọc).
  - Quyết định bấm **Duyệt & Chạy** hoặc **Từ chối** đoạn mã.

### 1.2 Nguyên tắc "Không thực thi ngầm" (No Background Execution)
- Mã nguồn Python do AI sinh ra **KHÔNG BAO GIỜ** tự động thực thi bên dưới nền.
- Mọi đoạn code sinh ra mặc định mang trạng thái **`pending_approval` (⚠️ Chờ duyệt)**.
- Chỉ khi người dùng bấm nút **Duyệt & Chạy**, code mới được gửi xuống Backend để thực thi.

### 1.3 Nguyên tắc Thực thi Local (Local Execution Only)
- Mã nguồn Python được thực thi trực tiếp tại máy cục bộ (Local Environment) của người dùng thông qua trình thực thi của FastAPI (`exec()`), truyền CÙNG 1 dict cho cả globals và locals để tránh lỗi scope.
- Dữ liệu `dff` (Pandas DataFrame) hoàn toàn nằm tại local (`data/processed/vietnam_it_jobs_processed.csv`), không bị đẩy lên các dịch vụ đám mây bên ngoài.

---

## 🏗️ 2. Cấu trúc Kiến trúc Hệ thống AI

Hệ thống AI Analyst bao gồm 2 phần chính được kết nối qua API RESTful và Server-Sent Events (SSE):

```text
[Frontend - ReactJS]                       [Backend - FastAPI Python]
┌─────────────────────────────┐            ┌────────────────────────────────┐
│ • Chat UI & Stream Viewer   │  SSE Stream│ • Gemini API (Flash/Pro)       │
│ • Monaco Code Editor        │ ◄──────────┤ • Multiple API Keys Fallback   │
│ • Approval Action Toolbar   │            │ • Catalog Routing + Cache      │
│ • Plotly Interactive Render │  POST Exec │ • Data Grounding (RAG)         │
│ • History Sidebar & Pin     │ ──────────►│ • Local Python Executor        │
│ • Welcome Screen            │            │ • Long-format CSV Extractor    │
│ • Abort/Stop Controller     │  Abort sig │ • Context-Aware Suggestions    │
│ • Auto-Comment & Suggestions│ ──────────►│ • GOAL EXPLORER (Dibia, 2023)  │
└─────────────────────────────┘            └────────────────────────────────┘
```

### 2.1 Backend (Python FastAPI)
- **`router_page5.py`** (1019 dòng): Router trung tâm tiếp nhận request, kết nối Gemini API, quản lý SSE Stream với 6 nhánh xử lý (auto/ask/code/explain/comment/vision), thực thi code Python, lưu vết lịch sử, và gợi ý câu hỏi bám ngữ cảnh.
- **`ai_config.py`** (234 dòng): Quản lý API Key, thiết lập cơ chế **Fallback tự động nhiều API Key khi gặp lỗi Quota 429**, định nghĩa 8 loại prompt chuẩn hóa (System, Vision, Routing, Comment, Suggestion, Ask, Code, Explain).
- **`chart_catalog.py`** (243 dòng): Danh mục **19 biểu đồ** có sẵn (13 trang dashboard + 6 mở rộng) giúp đối chiếu câu hỏi để trả về ngay số liệu chuẩn 100%, kèm hàm gợi ý biểu đồ liên quan.

### 2.2 Frontend (ReactJS + Monaco Editor)
- **`Dashboard_page5.jsx`** (724 dòng): View chính quản lý luồng hội thoại streaming real-time, màn hình chào, tự động nhận xét, abort/stop, gộp khung (turn card), và xử lý lỗi quota thân thiện.
- **`AiChatMessage.jsx`** (~30KB): Component tin nhắn thông minh tích hợp **Monaco Editor (chuẩn VS Code)**, thanh Badge trạng thái, preamble (Mẫu 6), biểu đồ nhúng tại marker (Mẫu 5), chip gợi ý bám ngữ cảnh, nút Duyệt & Chạy / Phóng to / Tải CSV / Xem Logs.
- **`AiHistoryPanel.jsx`**: Quản lý lịch sử cuộc hội thoại, phân nhóm thời gian, ghim/bỏ ghim, xóa.
- **`AiRequestForm.jsx`** (226 dòng): Khung nhập prompt hỗ trợ đính kèm ảnh (click 📎 hoặc Ctrl+V paste), menu lệnh nhanh tự lọc (`/hoi`, `/code`, `/giaithich`, `/nhanxet`), suggestion chips, và nút Dừng stream.

---

## 🔄 3. Luồng Hoạt động Chi tiết (3 Giai đoạn)

```mermaid
sequenceDiagram
    autonumber
    actor User as Con người (User)
    participant FE as Frontend (React)
    participant BE as Backend (FastAPI)
    participant AI as Gemini Model API

    Note over User, AI: GIAI ĐOẠN 1: TIẾP NHẬN & SINH CODE/VĂN BẢN (GENERATION)
    User->FE: Nhập yêu cầu ("Vẽ biểu đồ Top 10 kỹ năng...")
    FE->BE: POST /api/ai/request/stream (Prompt + Mode + CatalogHint + AbortSignal)
    BE->BE: build_data_grounding() + build_conversation_context()
    BE->AI: Gửi System Prompt + Data Grounding + Context (Max 8 turns + tóm tắt cũ)
    AI-->>BE: Stream nội dung (Dẫn nhập + Hướng phân tích + Python Code)
    BE-->>FE: Stream SSE Events (phase: start → delta → done)
    FE->FE: Hiển thị dẫn nhập streaming + Code trên Monaco Editor với badge "⚠️ Chờ duyệt"

    Note over User, AI: GIAI ĐOẠN 2: PHÊ DUYỆT & CHỈNH SỬA (HUMAN REVIEW & EDIT)
    User->FE: Xem xét code, trực tiếp gõ sửa tham số (VD: đổi top 10 -> top 15)
    User->FE: Bấm nút "Duyệt & Chạy" (Play Icon)

    Note over User, AI: GIAI ĐOẠN 3: THỰC THI LOCAL & HIỂN THỊ KẾT QUẢ (LOCAL EXECUTION)
    FE->BE: POST /api/ai/execute (requestId, editedCode)
    BE->BE: Thực thi exec(editedCode, local_env) trên local DataFrame
    BE->BE: Trích xuất Plotly JSON Figure & Bảng dữ liệu Long-format CSV
    BE-->>FE: Trả về { status: "success", result: { plotly_json, csv } }
    FE->FE: Render biểu đồ Plotly tương tác & nút Tải file CSV
    FE->BE: (autoComment) POST /api/ai/request/stream mode="comment"
    BE->AI: Gửi COMMENT_PROMPT_TEMPLATE + CSV số liệu thật
    AI-->>BE: Stream nhận xét phân tích
    BE-->>FE: Stream SSE nhận xét ngay dưới biểu đồ
```

---

## 📡 4. Danh mục API Endpoints của AI

### 4.1 `POST /api/ai/request/stream` (SSE Real-time Streaming)
- **Mục đích**: Nhận prompt từ người dùng và stream kết quả (Văn bản dẫn nhập + Mã nguồn Python, hoặc nhận xét văn bản) theo thời gian thực.
- **Payload** (`AiStreamParams`):
  ```json
  {
    "prompt": "Phân tích xu hướng tuyển dụng theo cấp độ kinh nghiệm",
    "conversationId": "conv_uuid",
    "image": "data:image/png;base64,...",
    "mode": "auto | ask | code | explain | comment",
    "catalogHint": "P2-02"
  }
  ```
  - `mode`: `null`/`"auto"` = hệ thống tự quyết (routing → Chế độ A/B); `"ask"` = `/hoi`; `"code"` = `/code`; `"explain"` = `/giaithich`; `"comment"` = `/nhanxet`.
  - `catalogHint`: mã danh mục ĐÃ BIẾT TRƯỚC khi người dùng bấm chip gợi ý — bỏ hẳn lượt gọi Gemini Flash routing, giảm độ trễ.
- **Response Format**: `text/event-stream` (Server-Sent Events)
  ```
  data: {"phase":"start", "type":"text", "catalogId":"P2-02", "figure":{...}}
  data: {"phase":"delta", "text":"Dựa trên dữ liệu..."}
  data: {"phase":"delta", "text":"...thị trường tuyển dụng"}
  data: {"phase":"done", "requestId":"uuid", "conversationId":"uuid",
         "type":"text|code", "code":"...", "preamble":"...",
         "catalogId":"P2-02", "suggestions":[{"id":"P3-01","cau_hoi":"..."}]}
  ```

### 4.2 `POST /api/ai/execute` (Thực thi Mã nguồn đã Phê duyệt)
- **Mục đích**: Chạy đoạn code Python đã được con người duyệt/chỉnh sửa trên DataFrame cục bộ.
- **Payload** (`AiExecuteParams`):
  ```json
  {
    "requestId": "req_uuid_12345",
    "editedCode": "exp_counts = dff['cap_do_kinh_nghiem'].value_counts().reset_index()\nfig = px.bar(exp_counts, x='Cấp độ', y='Số lượng')"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "result": {
      "type": "plotly",
      "data": { "/* Plotly Figure JSON */" },
      "csv": "trace,nhan_x,gia_tri_y\nCấp độ,Junior,1234\n..."
    },
    "logs": "Vẽ biểu đồ Plotly thành công."
  }
  ```

### 4.3 `GET`, `DELETE`, `PIN`, `RENAME` `/api/ai/history...`
- **`GET /api/ai/history`**: Tải toàn bộ danh sách lịch sử hội thoại từ Cloud PostgreSQL (Supabase) về Frontend với chỉ 1 lần truy vấn SQL siêu tốc.
- **`DELETE /api/ai/history/{id}`**: Xóa vĩnh viễn một cuộc hội thoại khỏi Cơ sở dữ liệu và file sao lưu cục bộ.
- **`POST /api/ai/history/{id}/pin`**: Bật/tắt ghim (Toggle Pin) cho một cuộc hội thoại. Cuộc được ghim sẽ hiển thị riêng ở đầu danh sách lịch sử.
- **`PUT /api/ai/history/{id}/title`** *(Nâng cấp mới)*: Đổi tên cuộc trò chuyện theo thời gian thực. Tích hợp trực tiếp với giao diện Inline Editing trên Frontend (biểu tượng cây bút ✏️), cho phép người dùng đổi tên mượt mà.

---

## 🛠️ 5. Hướng dẫn Thiết lập & Khởi chạy Module AI

1. **Cấu hình Gemini API Key và Cloud DB**:
   Tạo hoặc chỉnh sửa file `.env` tại thư mục `dashboard/backend/.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...your_gemini_key_1
   # Bạn có thể thêm nhiều key cách nhau bởi dấu phẩy để hệ thống tự động Fallback:
   # GEMINI_API_KEYS=key1,key2,key3

   # Cấu hình Cloud PostgreSQL (Supabase) để lưu lịch sử hội thoại:
   DATABASE_URL="postgresql://postgres:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
   ```
2. **Chạy Backend**:
   ```bash
   cd dashboard
   uvicorn backend.main:app --reload --port 8000
   ```
3. **Chạy Frontend**:
   ```bash
   cd dashboard/frontend
   npm run dev
   ```
4. **Truy cập**: Mở trình duyệt tại `http://localhost:5173` và chuyển sang **Tab 5 (AI Analyst)**.

---

## 🌟 6. Các Tính năng Độc đáo Nổi bật

1. **Monaco Code Editor tích hợp**: Trải nghiệm chỉnh sửa code chuyên nghiệp như trên VS Code với syntax highlighting, line numbers và auto-wrap.
2. **Kiến trúc NoSQL Document Store trên Cloud PostgreSQL (Supabase)**: Lịch sử hội thoại được lưu trữ tập trung trên máy chủ đám mây dưới cấu trúc trường JSONB duy nhất (`ai_history_store`), mang lại tốc độ truy vấn gần như tức thì.
3. **Cơ chế Dual-Write & Offline Fallback (High Availability)**: Mỗi khi có thao tác mới, hệ thống ưu tiên đồng bộ lên Cloud PostgreSQL, đồng thời ghi âm thầm một bản sao lưu vào file `ai_history.json`. Nếu rớt mạng hoặc mất kết nối DB, Backend tự động chuyển hướng sang file local giúp hệ thống tiếp tục vận hành mượt mà 100% không bao giờ bị gián đoạn hay mất dữ liệu!
4. **Đổi tên hội thoại theo thời gian thực (Inline Editing)**: Tích hợp trực tiếp trên giao diện Lịch sử bên trái, cho phép người dùng bấm biểu tượng cây bút ✏️ để đổi tên cuộc trò chuyện, lưu ✔️ hoặc hủy ❌ tiện lợi như ChatGPT / Claude.
5. **Cơ chế API Key Fallback tự động**: Khi một Gemini API Key chạm ngưỡng giới hạn 429 (ResourceExhausted), hệ thống tự động chuyển sang API Key dự phòng mà không ngắt đoạn trải nghiệm của người dùng. Frontend nhận diện lỗi quota và hiện thông báo thân thiện kèm nút **Thử lại**.
6. **Data Grounding (RAG đơn giản)**: Nhồi SỰ THẬT rút trực tiếp từ dataset vào prompt sinh code — giá trị hợp lệ của cột phân loại, min/max/trung vị lương, top 20 kỹ năng đúng chính tả, vài dòng mẫu — chặn model chọn nhầm cột hoặc bịa giá trị ngay từ đầu.
7. **Trích xuất CSV tự động từ Biểu đồ (`extract_csv_from_figure`)**: Tự động chuyển đổi các Plotly Figures (Pie, Bar, Boxplot, Treemap, Heatmap, Choropleth) thành dạng bảng số liệu CSV chuẩn long-format cho người dùng tải về.
8. **Phân tích hình ảnh (Vision AI)**: Đọc hiểu và đưa ra nhận xét chuyên sâu từ các ảnh biểu đồ/bảng số liệu do người dùng tải lên hoặc dán từ clipboard (Ctrl+V).
9. **Catalog Matching + Routing Cache**: Tự động nhận biết các câu hỏi khớp với 19 biểu đồ sẵn có (13 trang dashboard + 6 mở rộng) để dùng ngay số liệu chuẩn 100%, chống hallucination. Kết quả routing được cache trong bộ nhớ, tiết kiệm 1 lượt gọi Gemini Flash cho câu hỏi lặp lại.
10. **Gợi ý câu hỏi bám ngữ cảnh (GOAL EXPLORER)**: Sau mỗi câu trả lời, hệ thống dùng Gemini Flash CHỌN (không SINH) các câu hỏi tiếp theo từ chính danh mục catalog, bám đúng chủ đề vừa bàn — theo cơ chế GOAL EXPLORER của LIDA (Dibia, 2023). Fallback về thuần code (0 token) nếu lỗi.
11. **Streaming thời gian thực (Mẫu 6)**: Mọi nhánh đều stream văn bản ngay từ đầu — Chế độ B luôn viết dẫn nhập + "Hướng phân tích" TRƯỚC code, frontend hiển thị dần như chat, tự nhận ra khi gặp ``` để chuyển sang xem trước code. Tách code khỏi preamble chỉ làm SAU KHI nhận đủ toàn văn.
12. **Biểu đồ nhúng giữa bài (Mẫu 5)**: Khi câu hỏi trúng catalog, backend gửi kèm figure THẬT ngay từ sự kiện `start` — AI viết nhận xét 5 khối với marker `[[BIEU_DO]]` ở giữa, frontend chèn biểu đồ thật vào đúng vị trí đó.
13. **Ngữ cảnh hội thoại nâng cao**: Tối đa 8 lượt gần nhất chi tiết, các lượt cũ hơn được tóm tắt thành danh sách câu đã hỏi (không mất hoàn toàn). Nhồi bảng số liệu thật của 1-2 biểu đồ gần nhất và đánh dấu lượt có ảnh.
14. **Dừng stream giữa chừng**: Nút Dừng (⬛) abort fetch → backend ngừng generator → không tốn thêm quota cho phần chưa sinh.
15. **Tự động nhận xét sau biểu đồ**: Khi bật (mặc định), sau khi code chạy thành công và có dữ liệu, hệ thống tự gọi `/nhanxet` để AI phân tích — tách 2 pha: biểu đồ hiện ngay, nhận xét stream dần bên dưới.
16. **4 lệnh nâng cao** (`/hoi`, `/code`, `/giaithich`, `/nhanxet`): Cho phép người dùng ép AI đi đúng hướng mong muốn, bỏ qua bước AI tự đoán chế độ.

---

## 📋 7. Quy trình Kiểm thử & Bảo vệ (Demo với Giảng viên)

Khi trình diễn chức năng AI cho môn học, thực hiện theo đúng 3 bước minh họa chuẩn **Human-in-the-Loop**:

1. **Bước 1 (Nhập prompt & Sinh code)**: Nhập câu hỏi *"Phân tích top 5 nhóm vị trí tuyển dụng nhiều nhất"*. AI sẽ viết đoạn **dẫn nhập** + **Hướng phân tích** trước, rồi sinh code Python hiển thị ở trạng thái **⚠️ Chờ duyệt**.
2. **Bước 2 (Con người can thiệp gõ sửa)**: Trực tiếp gõ sửa trong khung Monaco Editor từ `nlargest(5)` thành `nlargest(8)` và đổi màu biểu đồ.
3. **Bước 3 (Duyệt & Thực thi)**: Bấm nút **"Duyệt & Chạy"** (`Play` icon). Biểu đồ Plotly tương tác sẽ hiển thị ra ngay bên dưới kèm nút tải CSV số liệu thô. Nếu bật tự động nhận xét, AI sẽ viết thêm đoạn phân tích dựa trên số liệu thật ngay bên dưới biểu đồ.
