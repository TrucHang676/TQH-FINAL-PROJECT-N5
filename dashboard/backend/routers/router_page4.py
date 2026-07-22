from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from pathlib import Path
import json

import backend.utils.charts_page4 as charts

from backend.utils.data_loader import get_df, make_cache_key, get_cached_response, set_cached_response

router = APIRouter()

class FilterRequest(BaseModel):
    sources: Optional[List[str]] = None
    region: Optional[str] = None
    position: Optional[str] = None
    work_type: Optional[str] = None


@router.post("/api/dashboard/page4")
def get_page4_data(req: FilterRequest):
    """
    Endpoint xử lý logic Trang 4: Nhân sự trẻ.
    Nhận thông số lọc từ Frontend, xử lý dữ liệu và trả về KPI + biểu đồ
    trả lời câu hỏi: "Những nhóm vị trí công việc nào cởi mở nhất và có nhu cầu
    tuyển dụng đối tượng Fresher/Intern cao nhất?"
    """
    cache_key = make_cache_key("page4", req)
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

    if req.region and req.region != 'All':
        dff = dff[dff['vung_mien'] == req.region]

    if req.position and req.position != 'All':
        dff = dff[dff['nhom_vi_tri'] == req.position]

    if req.work_type and req.work_type != 'All':
        dff = dff[dff['hinh_thuc_lam_viec'] == req.work_type]

    # ---- KPI: Tỷ lệ tin dành cho nhân sự trẻ (trên số tin có ghi rõ cấp bậc) ----
    known_df = dff[dff['cap_do_kinh_nghiem'] != charts.UNKNOWN_LEVEL]
    young_df = known_df[known_df['cap_do_kinh_nghiem'].isin(charts.YOUNG_LEVELS)]

    total_jobs = int(len(dff))
    total_known = int(len(known_df))
    total_young = int(len(young_df))
    young_pct = float(round(total_young / total_known * 100, 1)) if total_known > 0 else 0.0

    # ---- KPI: Nhóm vị trí cởi mở nhất với nhân sự trẻ (đủ mẫu tối thiểu) ----
    most_open_group = "N/A"
    most_open_pct = 0.0
    work_df = known_df[known_df['nhom_vi_tri'] != charts.EXCLUDED_POSITION]
    if not work_df.empty:
        group_known = work_df.groupby('nhom_vi_tri').size()
        group_young = work_df[work_df['cap_do_kinh_nghiem'].isin(charts.YOUNG_LEVELS)].groupby('nhom_vi_tri').size()
        group_ratio = (group_young / group_known * 100).fillna(0)
        group_ratio = group_ratio[group_known >= charts.MIN_SAMPLE_SIZE]
        if not group_ratio.empty:
            most_open_group = str(group_ratio.idxmax())
            most_open_pct = float(round(group_ratio.max(), 1))

    # ---- KPI: Lương khởi điểm trung vị của Fresher và Intern (gắn với câu 3) ----
    fresher_median_salary = 0.0
    fresher_df = dff[(dff['cap_do_kinh_nghiem'] == 'Fresher')].dropna(subset=['luong_tb'])
    if not fresher_df.empty:
        fresher_median_salary = float(round(fresher_df['luong_tb'].median(), 1))

    intern_median_salary = 0.0
    intern_df = dff[(dff['cap_do_kinh_nghiem'] == 'Intern')].dropna(subset=['luong_tb'])
    if not intern_df.empty:
        intern_median_salary = float(round(intern_df['luong_tb'].median(), 1))

    # ---- Tạo các biểu đồ ----
    treemap_fig = charts.create_youth_opportunity_treemap(dff)
    exp_dist_fig = charts.create_experience_distribution_chart(dff)
    salary_box_fig = charts.create_youth_salary_boxplot(dff)

    res = {
        "kpi": {
            "total_jobs": total_jobs,
            "total_young_jobs": total_young,
            "young_pct": young_pct,
            "most_open_group": {
                "name": most_open_group,
                "pct": most_open_pct
            },
            "fresher_median_salary": fresher_median_salary,
            "intern_median_salary": intern_median_salary
        },
        "charts": {
            "experience_distribution": json.loads(exp_dist_fig.to_json()),
            "youth_opportunity_treemap": json.loads(treemap_fig.to_json()),
            "youth_salary_boxplot": json.loads(salary_box_fig.to_json()),
        }
    }
    set_cached_response(cache_key, res)
    return res
