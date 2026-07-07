from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Nhập các router đã tách biệt theo từng trang
from backend.routers import router_page1
from backend.routers import router_page2

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
app.include_router(router_page1.router, tags=["Page 1"])

# Gắn router của trang 2 - Kỹ năng & Công nghệ
app.include_router(router_page2.router, tags=["Page 2"])

# Gắn router của trang 3 - Lương thị trường
from backend.routers import router_page3
app.include_router(router_page3.router, tags=["Page 3"])

# Gắn router của AI Analysis (Trang 5)
from backend.routers import router_page5
app.include_router(router_page5.router, tags=["AI Analysis"])

# Bạn có thể tiếp tục thêm page2.router, page3.router... ở đây sau này
