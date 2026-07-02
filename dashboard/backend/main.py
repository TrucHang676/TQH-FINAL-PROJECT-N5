from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Nhập các router đã tách biệt theo từng trang
from backend.routers import page1

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="IT Recruitment Dashboard API")

# Cấu hình CORS để cho phép Frontend React gọi API
# Lưu ý: allow_credentials=False để không xung đột với allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế nên giới hạn domain cụ thể
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn (include) router của trang 1 vào ứng dụng chính
app.include_router(page1.router, tags=["Page 1"])

# Gắn router của AI Analysis (Trang 5)
from backend.routers import ai_analysis
app.include_router(ai_analysis.router, tags=["AI Analysis"])

# Bạn có thể tiếp tục thêm page2.router, page3.router... ở đây sau này
