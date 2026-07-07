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

# Gắn router của trang 4 - Nhân sự trẻ
from backend.routers import router_page4
app.include_router(router_page4.router, tags=["Page 4"])

# Gắn router của AI Analysis (Trang 5)
from backend.routers import router_page5
app.include_router(router_page5.router, tags=["AI Analysis"])


# Endpoint meta: trả về số bản ghi thật của dataset (hiển thị ở badge header)
from pathlib import Path
import pandas as pd

_dataset_meta_cache = {}

@app.get("/api/meta")
def get_meta():
    csv_path = Path(__file__).parent.parent.parent / "data" / "processed" / "vietnam_it_jobs_processed.csv"
    if "total_records" not in _dataset_meta_cache:
        if csv_path.exists():
            _dataset_meta_cache["total_records"] = int(len(pd.read_csv(csv_path, usecols=[0])))
        else:
            _dataset_meta_cache["total_records"] = 0
    return {
        "dataset_name": "vietnam_it_jobs_processed.csv",
        "total_records": _dataset_meta_cache["total_records"],
    }

# Bạn có thể tiếp tục thêm page3.router... ở đây sau này
