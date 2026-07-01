from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from typing import List, Optional

# Nhập các hàm vẽ biểu đồ từ thư mục utils
from utils import charts

app = FastAPI(title="IT Recruitment Dashboard API")

# Cấu hình CORS để cho phép Frontend React gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Có thể giới hạn domain trong thực tế
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đường dẫn file dữ liệu
root_dir = Path(__file__).parent.parent.resolve()
csv_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"

# Tải dữ liệu toàn cục
try:
    df = pd.read_csv(csv_path)
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()


class FilterRequest(BaseModel):
    sources: List[str] = ["TopCV", "VietnamWorks", "ITviec"]
    position: str = "All"
    experience: str = "All"
    region: str = "All"
    map_toggle: str = "map"  # 'map' hoặc 'region_chart'


@app.post("/api/dashboard/page1")
def get_dashboard_data(req: FilterRequest):
    if df.empty:
        return {"error": "Data not available"}

    dff = df.copy()

    # Lọc dữ liệu theo nguồn
    if req.sources:
        dff = dff[dff['nguon'].isin(req.sources)]
    else:
        dff = dff.iloc[0:0]

    # Lọc theo nhóm vị trí
    if req.position and req.position != 'All':
        dff = dff[dff['nhom_vi_tri'] == req.position]

    # Lọc theo cấp độ kinh nghiệm
    if req.experience and req.experience != 'All':
        dff = dff[dff['cap_do_kinh_nghiem'] == req.experience]

    # Lọc theo vùng miền
    if req.region and req.region != 'All':
        dff = dff[dff['vung_mien'] == req.region]

    total_jobs = len(dff)

    # 1. Tính KPI 1 & Sparkline
    spark1_data = []
    if total_jobs > 0 and 'thang_dang' in dff.columns:
        monthly = dff.dropna(subset=['thang_dang']).groupby('thang_dang').size()
        spark1_data = monthly.tolist()

    spark_color = "#FAE7CB"
    spark1_fig = charts.create_sparkline(spark1_data, spark_color)
    spark2_fig = charts.create_sparkline(spark1_data, spark_color)

    # 2. KPI 2: Tháng cao điểm
    peak_month = "N/A"
    peak_count = 0
    if total_jobs > 0:
        trend_dff = dff.dropna(subset=['thang_dang'])
        if not trend_dff.empty:
            month_counts = trend_dff.groupby('thang_dang').size()
            if not month_counts.empty:
                peak_month = month_counts.idxmax()
                peak_count = month_counts.max()

    # 3. KPI 3: Địa bàn lớn nhất
    top_city = "N/A"
    top_city_pct = 0
    spark3_fig = charts.create_sparkline([], spark_color)
    if total_jobs > 0:
        top_city_series = dff['tinh_thanh'].value_counts()
        if not top_city_series.empty:
            top_city = top_city_series.index[0]
            top_city_count = top_city_series.iloc[0]
            top_city_pct = (top_city_count / total_jobs) * 100
            
            loc_dff = dff[dff['tinh_thanh'] == top_city].dropna(subset=['thang_dang'])
            spark3_data = loc_dff.groupby('thang_dang').size().tolist()
            spark3_fig = charts.create_sparkline(spark3_data, spark_color)

    # 4. KPI 4: Hình thức làm việc phổ biến nhất
    top_work = "N/A"
    top_work_pct = 0
    spark4_fig = charts.create_sparkline([], spark_color)
    if total_jobs > 0:
        top_work_series = dff['hinh_thuc_lam_viec'].value_counts()
        if not top_work_series.empty:
            top_work = top_work_series.index[0]
            top_work_count = top_work_series.iloc[0]
            top_work_pct = (top_work_count / total_jobs) * 100
            
            work_dff = dff[dff['hinh_thuc_lam_viec'] == top_work].dropna(subset=['thang_dang'])
            spark4_data = work_dff.groupby('thang_dang').size().tolist()
            spark4_fig = charts.create_sparkline(spark4_data, spark_color)

    # Biểu đồ xu hướng và hình thức
    trend_fig = charts.create_time_trend_chart(dff)
    work_fig = charts.create_work_type_chart(dff)

    # Bản đồ
    if req.map_toggle == 'region_chart':
        map_fig = charts.create_region_vertical_chart(dff)
        caption = "Biểu đồ cột thể hiện nhu cầu tuyển dụng theo từng vùng miền."
    else:
        map_fig = charts.create_vietnam_map(dff)
        caption = "Không hiển thị nhóm Khác và Từ xa/Remote trên bản đồ do không có tọa độ địa lý cụ thể."

    # Xây dựng kết quả trả về: KPIs + Dữ liệu biểu đồ định dạng dictionary
    return {
        "kpi": {
            "total_jobs": total_jobs,
            "peak_month": {"month": peak_month, "count": peak_count},
            "top_city": {"city": top_city, "pct": top_city_pct},
            "top_work": {"work": top_work, "pct": top_work_pct},
        },
        "caption": caption,
        "charts": {
            "spark1": spark1_fig.to_dict(),
            "spark2": spark2_fig.to_dict(),
            "spark3": spark3_fig.to_dict(),
            "spark4": spark4_fig.to_dict(),
            "trend": trend_fig.to_dict(),
            "work": work_fig.to_dict(),
            "map": map_fig.to_dict()
        }
    }
