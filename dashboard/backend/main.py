from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading

# Nhập các router đã tách biệt theo từng trang
from backend.routers import router_page1, router_page2, router_page4, router_page3, router_page5

def _warmup_cache():
    """
    Chạy trong background thread khi server khởi động.
    Pre-compute cache cho bộ lọc mặc định (tất cả nguồn, All position/experience/region)
    để người dùng đầu tiên nhận kết quả ngay lập tức.
    """
    try:
        from backend.utils.data_loader import get_df
        get_df()  # nạp CSV vào RAM trước

        all_sources = ['ITviec', 'TopDev', 'VietJobs', 'Vieclam24h', 'TopCV', 'JobsGO']

        # Warm up Page 1
        from backend.routers.router_page1 import get_dashboard_data, FilterRequest as FR1
        get_dashboard_data(FR1(sources=all_sources, position='All', experience='All', region='All'))

        # Warm up Page 2
        from backend.routers.router_page2 import get_page2_data, FilterRequest as FR2
        get_page2_data(FR2(sources=all_sources, position='All', experience='All', region='All'))

        # Warm up Page 3
        from backend.routers.router_page3 import get_page3_data, FilterRequest as FR3
        get_page3_data(FR3(sources=all_sources, position='All', experience='All', region='All'))

        # Warm up Page 4
        from backend.routers.router_page4 import get_page4_data, FilterRequest as FR4
        get_page4_data(FR4(sources=all_sources, region='All', position='All', work_type='All'))

        print("✅ [Warm-up] Cache đã sẵn sàng cho tất cả 4 trang!")
    except Exception as e:
        print(f"⚠️ [Warm-up] Lỗi khi khởi tạo cache: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chạy warm-up trong background để không block server startup
    thread = threading.Thread(target=_warmup_cache, daemon=True)
    thread.start()
    yield

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="IT Recruitment Dashboard API", lifespan=lifespan)

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
app.include_router(router_page4.router, tags=["Page 4"])
# Gắn router của trang 3 - Lương thị trường
app.include_router(router_page3.router, tags=["Page 3"])

# Gắn router của AI Analysis (Trang 5)
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
