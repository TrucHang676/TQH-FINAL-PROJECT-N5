from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from pathlib import Path
import json
from backend.utils import charts

router = APIRouter()

# Lấy thư mục gốc chứa dữ liệu
root_dir = Path(__file__).parent.parent.parent.resolve()
csv_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"

# Model dữ liệu nhận vào (Request Body)
class FilterRequest(BaseModel):
    sources: Optional[List[str]] = None
    position: Optional[str] = None
    experience: Optional[str] = None
    region: Optional[str] = None
    map_toggle: Optional[str] = 'map'

@router.post("/api/dashboard/page1")
def get_dashboard_data(req: FilterRequest):
    """
    Hàm xử lý logic của Trang 1: Xu hướng & Địa lý.
    Nhận các thông số lọc từ Frontend, xử lý Data và trả về KPI + Biểu đồ.
    """
    # Đọc dữ liệu CSV
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        # Trả về lỗi hoặc dataframe rỗng nếu không có dữ liệu
        df = pd.DataFrame(columns=[
            'ten_cong_viec', 'ten_cong_ty', 'nhom_vi_tri', 'cap_do_kinh_nghiem', 
            'tinh_thanh', 'vung_mien', 'luong_tb', 'hinh_thuc_lam_viec', 'ngay_dang', 
            'thang_dang', 'nguon'
        ])

    dff = df.copy()

    # Áp dụng bộ lọc
    if req.sources:
        dff = dff[dff['nguon'].isin(req.sources)]
    else:
        dff = dff.iloc[0:0]

    if req.position and req.position != 'All':
        dff = dff[dff['nhom_vi_tri'] == req.position]

    if req.experience and req.experience != 'All':
        dff = dff[dff['cap_do_kinh_nghiem'] == req.experience]

    if req.region and req.region != 'All':
        dff = dff[dff['vung_mien'] == req.region]

    # Tính toán tổng tin
    total_jobs = int(len(dff))

    # 1. Tính KPI 1 & Sparkline (Dữ liệu line nhỏ bên dưới KPI)
    spark1_data = []
    if total_jobs > 0 and 'thang_dang' in dff.columns:
        monthly = dff.dropna(subset=['thang_dang']).groupby('thang_dang').size()
        spark1_data = [int(x) for x in monthly.tolist()]

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
                peak_month = str(month_counts.idxmax())
                peak_count = int(month_counts.max())

    # 3. KPI 3: Địa bàn lớn nhất
    top_city = "N/A"
    top_city_pct = 0.0
    spark3_fig = charts.create_sparkline([], spark_color)
    if total_jobs > 0:
        top_city_series = dff['tinh_thanh'].value_counts()
        if not top_city_series.empty:
            top_city = str(top_city_series.index[0])
            top_city_count = int(top_city_series.iloc[0])
            top_city_pct = float((top_city_count / total_jobs) * 100)
            
            loc_dff = dff[dff['tinh_thanh'] == top_city].dropna(subset=['thang_dang'])
            spark3_data = [int(x) for x in loc_dff.groupby('thang_dang').size().tolist()]
            spark3_fig = charts.create_sparkline(spark3_data, spark_color)

    # 4. KPI 4: Hình thức làm việc phổ biến nhất
    top_work = "N/A"
    top_work_pct = 0.0
    spark4_fig = charts.create_sparkline([], spark_color)
    if total_jobs > 0:
        top_work_series = dff['hinh_thuc_lam_viec'].value_counts()
        if not top_work_series.empty:
            top_work = str(top_work_series.index[0])
            top_work_count = int(top_work_series.iloc[0])
            top_work_pct = float((top_work_count / total_jobs) * 100)
            
            work_dff = dff[dff['hinh_thuc_lam_viec'] == top_work].dropna(subset=['thang_dang'])
            spark4_data = [int(x) for x in work_dff.groupby('thang_dang').size().tolist()]
            spark4_fig = charts.create_sparkline(spark4_data, spark_color)

    # Tạo biểu đồ xu hướng và hình thức
    trend_fig = charts.create_time_trend_chart(dff)
    work_fig = charts.create_work_type_chart(dff)

    caption = ""
    if req.map_toggle == 'region_chart':
        map_fig = charts.create_region_vertical_chart(dff)
    else:
        map_fig = charts.create_vietnam_map(dff)
        caption = "Không hiển thị nhóm Khác và Từ xa/Remote trên bản đồ do không có tọa độ địa lý cụ thể."

    # Xây dựng kết quả trả về, lưu ý phải ép kiểu dữ liệu Numpy về Python chuẩn (int, float, str)
    return {
        "kpi": {
            "total_jobs": total_jobs,
            "peak_month": {"month": peak_month, "count": peak_count},
            "top_city": {"city": top_city, "pct": top_city_pct},
            "top_work": {"work": top_work, "pct": top_work_pct},
        },
        "caption": caption,
        "charts": {
            "spark1": json.loads(spark1_fig.to_json()),
            "spark2": json.loads(spark2_fig.to_json()),
            "spark3": json.loads(spark3_fig.to_json()),
            "spark4": json.loads(spark4_fig.to_json()),
            "trend": json.loads(trend_fig.to_json()),
            "work": json.loads(work_fig.to_json()),
            "map": json.loads(map_fig.to_json())
        }
    }
