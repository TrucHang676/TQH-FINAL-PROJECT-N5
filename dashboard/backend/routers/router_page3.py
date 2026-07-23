"""
Router cho Trang 3: Phân tích mức lương thị trường IT Việt Nam.
Endpoint: POST /api/dashboard/page3
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from pathlib import Path
import json
import numpy as np

import backend.utils.charts_page3 as charts

from backend.utils.data_loader import get_df, make_cache_key, get_cached_response, set_cached_response

router = APIRouter()

class FilterRequest(BaseModel):
    sources: Optional[List[str]] = None
    position: Optional[str] = None
    experience: Optional[str] = None
    region: Optional[str] = None


@router.post("/api/dashboard/page3")
def get_page3_data(req: FilterRequest):
    """
    Endpoint xử lý logic Trang 3: Lương thị trường.
    Nhận thông số lọc từ Frontend, xử lý dữ liệu lương và trả về
    KPI + 3 biểu đồ phân tích lương.
    """
    cache_key = make_cache_key("page3", req)
    cached_val = get_cached_response(cache_key)
    if cached_val is not None:
        return cached_val

    # Đọc dữ liệu CSV từ cache
    df = get_df()
    dff = df.copy()

    # ---- Áp dụng bộ lọc ----
    if req.sources:
        dff = dff[dff['nguon'].isin(req.sources)]
    else:
        dff = dff.iloc[0:0]  # Không chọn nguồn nào thì trả về rỗng

    if req.position and req.position != 'All':
        dff = dff[dff['nhom_vi_tri'] == req.position]

    if req.experience and req.experience != 'All':
        dff = dff[dff['cap_do_kinh_nghiem'] == req.experience]

    if req.region and req.region != 'All':
        dff = dff[dff['vung_mien'] == req.region]

    total_jobs = int(len(dff))

    # ---- DataFrame chỉ chứa tin có dữ liệu lương ----
    salary_df = dff.dropna(subset=['luong_tb'])
    total_with_salary = int(len(salary_df))

    spark_color = "#c7d2fe"  # Indigo nhạt, phù hợp theme lương

    # =========================================================================
    # KPI 1: Lương trung bình ngành IT
    # =========================================================================
    avg_salary = 0.0
    spark1_data = []
    if total_with_salary > 0:
        avg_salary = float(round(salary_df['luong_tb'].mean(), 1))

        # Sparkline: lương TB theo tháng
        if 'thang_dang' in salary_df.columns:
            monthly_salary = (
                salary_df.dropna(subset=['thang_dang'])
                .groupby('thang_dang')['luong_tb']
                .mean()
                .round(1)
            )
            spark1_data = [float(x) for x in monthly_salary.tolist()]

    spark1_fig = charts.create_sparkline(spark1_data, spark_color)

    # =========================================================================
    # KPI 2: Tỷ lệ công khai lương
    # =========================================================================
    salary_disclosure_pct = 0.0
    spark2_data = []
    if total_jobs > 0:
        salary_disclosure_pct = float(round((total_with_salary / total_jobs) * 100, 1))

        # Sparkline: tỷ lệ công khai theo tháng
        if 'thang_dang' in dff.columns:
            monthly_total = dff.dropna(subset=['thang_dang']).groupby('thang_dang').size()
            monthly_has_salary = salary_df.dropna(subset=['thang_dang']).groupby('thang_dang').size()
            monthly_pct = (monthly_has_salary / monthly_total * 100).fillna(0).round(1)
            spark2_data = [float(x) for x in monthly_pct.tolist()]

    spark2_fig = charts.create_sparkline(spark2_data, spark_color)

    # =========================================================================
    # KPI 3: Nhóm vị trí có lương cao nhất
    # =========================================================================
    top_salary_position = "N/A"
    top_salary_value = 0.0
    spark3_data = []
    if total_with_salary > 0 and 'nhom_vi_tri' in salary_df.columns:
        pos_salary = salary_df.groupby('nhom_vi_tri')['luong_tb'].mean()
        if not pos_salary.empty:
            top_salary_position = str(pos_salary.idxmax())
            top_salary_value = float(round(pos_salary.max(), 1))

            # Sparkline: lương TB của vị trí cao nhất theo tháng
            top_pos_df = salary_df[salary_df['nhom_vi_tri'] == top_salary_position]
            top_pos_df = top_pos_df.dropna(subset=['thang_dang'])
            if not top_pos_df.empty:
                spark3_data = [
                    float(round(v, 1))
                    for v in top_pos_df.groupby('thang_dang')['luong_tb'].mean().tolist()
                ]

    spark3_fig = charts.create_sparkline(spark3_data, spark_color)

    # =========================================================================
    # KPI 4: Khoảng cách lương giữa cấp độ kinh nghiệm (Max / Min)
    # =========================================================================
    salary_gap_ratio = 0.0
    gap_description = "N/A"
    spark4_data = []
    if total_with_salary > 0 and 'cap_do_kinh_nghiem' in salary_df.columns:
        exp_salary = salary_df.groupby('cap_do_kinh_nghiem')['luong_tb'].mean()
        # Loại bỏ "Không rõ" khi tính gap
        exp_salary_clean = exp_salary.drop('Không rõ', errors='ignore')

        if len(exp_salary_clean) >= 2:
            max_exp = str(exp_salary_clean.idxmax())
            min_exp = str(exp_salary_clean.idxmin())
            max_val = float(exp_salary_clean.max())
            min_val = float(exp_salary_clean.min())

            if min_val > 0:
                salary_gap_ratio = float(round(max_val / min_val, 1))
                gap_description = f"{max_exp} vs {min_exp}"

            # Sparkline: lương TB các cấp kinh nghiệm (sắp xếp tăng dần)
            exp_order_vals = []
            for exp in charts.EXPERIENCE_ORDER:
                if exp in exp_salary.index and exp != 'Không rõ':
                    exp_order_vals.append(float(round(exp_salary[exp], 1)))
            spark4_data = exp_order_vals

    spark4_fig = charts.create_sparkline(spark4_data, spark_color)

    # =========================================================================
    # Tạo 3 biểu đồ chính
    # =========================================================================
    salary_dist_fig = charts.create_salary_distribution_chart(dff)
    salary_pos_exp_fig = charts.create_salary_by_position_experience_chart(dff)
    salary_location_fig = charts.create_salary_by_location_chart(dff)

    # =========================================================================
    # Xây dựng response
    # =========================================================================
    res = {
        "kpi": {
            "avg_salary": avg_salary,
            "total_with_salary": total_with_salary,
            "total_jobs": total_jobs,
            "salary_disclosure_pct": salary_disclosure_pct,
            "top_salary_position": {
                "name": top_salary_position,
                "value": top_salary_value,
            },
            "salary_gap": {
                "ratio": salary_gap_ratio,
                "description": gap_description,
            },
        },
        "charts": {
            "spark1": json.loads(spark1_fig.to_json()),
            "spark2": json.loads(spark2_fig.to_json()),
            "spark3": json.loads(spark3_fig.to_json()),
            "spark4": json.loads(spark4_fig.to_json()),
            "salary_distribution": json.loads(salary_dist_fig.to_json()),
            "salary_by_position_experience": json.loads(salary_pos_exp_fig.to_json()),
            "salary_by_location": json.loads(salary_location_fig.to_json()),
        }
    }
    set_cached_response(cache_key, res)
    return res
