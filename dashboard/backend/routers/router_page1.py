from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from pathlib import Path
import json
import backend.utils.charts_page1 as charts

from backend.utils.data_loader import get_df, make_cache_key, get_cached_response, set_cached_response

router = APIRouter()

# Model dữ liệu nhận vào (Request Body)
class FilterRequest(BaseModel):
    sources: Optional[List[str]] = None
    position: Optional[str] = None
    experience: Optional[str] = None
    region: Optional[str] = None
    work_type: Optional[str] = None
    map_toggle: Optional[str] = 'map'

@router.post("/api/dashboard/page1")
def get_dashboard_data(req: FilterRequest):
    """
    Hàm xử lý logic của Trang 1: Xu hướng & Địa lý.
    Nhận các thông số lọc từ Frontend, xử lý Data và trả về KPI + Biểu đồ.
    """
    cache_key = make_cache_key("page1", req)
    cached_val = get_cached_response(cache_key)
    if cached_val is not None:
        return cached_val

    # Đọc dữ liệu CSV từ cache
    df = get_df()
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

    if req.work_type:
        dff = dff[dff['hinh_thuc_lam_viec'] == req.work_type]

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

    trend_dff = dff

    # Vẽ tất cả biểu đồ song song để tăng tốc độ
    from concurrent.futures import ThreadPoolExecutor

    _dff = dff  # capture cho closure
    with ThreadPoolExecutor(max_workers=4) as pool:
        f_trend       = pool.submit(charts.create_time_trend_chart, trend_dff)
        f_work        = pool.submit(charts.create_work_type_chart, _dff, selected_work_type=req.work_type)
        f_map         = pool.submit(charts.create_vietnam_map, _dff)
        f_region      = pool.submit(charts.create_region_vertical_chart, _dff)

    trend_fig        = f_trend.result()
    work_fig         = f_work.result()
    map_fig          = f_map.result()
    region_chart_fig = f_region.result()

    region_counts = dff['vung_mien'].value_counts().to_dict()
    regions_data = {
        "Bắc": int(region_counts.get('Bắc', 0)),
        "Trung": int(region_counts.get('Trung', 0)),
        "Nam": int(region_counts.get('Nam', 0)),
        "Từ xa / Remote": int(region_counts.get('Từ xa / Remote', 0)),
        "Khác": int(region_counts.get('Khác', 0))
    }

    # Drill-down data: top 15 tỉnh/thành cho mỗi vùng miền
    city_breakdown = {}
    for vung in ['Bắc', 'Trung', 'Nam']:
        vung_df = dff[dff['vung_mien'] == vung]
        if not vung_df.empty:
            city_counts = vung_df['tinh_thanh'].value_counts().head(15)
            city_breakdown[vung] = [
                {"city": str(k), "count": int(v)}
                for k, v in city_counts.items()
            ]
        else:
            city_breakdown[vung] = []

    res = {
        "kpi": {
            "total_jobs": total_jobs,
            "peak_month": {"month": peak_month, "count": peak_count},
            "top_city": {"city": top_city, "pct": top_city_pct},
            "top_work": {"work": top_work, "pct": top_work_pct},
        },
        "regions": regions_data,
        "city_breakdown": city_breakdown,
        "caption": "Không hiển thị nhóm Khác và Từ xa/Remote trên bản đồ do không có tọa độ địa lý cụ thể.",
        "charts": {
            "spark1": json.loads(spark1_fig.to_json()),
            "spark2": json.loads(spark2_fig.to_json()),
            "spark3": json.loads(spark3_fig.to_json()),
            "spark4": json.loads(spark4_fig.to_json()),
            "trend": json.loads(trend_fig.to_json()),
            "work": json.loads(work_fig.to_json()),
            "map": json.loads(map_fig.to_json()),
            "region_chart": json.loads(region_chart_fig.to_json())
        }
    }
    set_cached_response(cache_key, res)
    return res
