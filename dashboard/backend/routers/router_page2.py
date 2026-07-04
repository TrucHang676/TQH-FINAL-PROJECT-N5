from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from pathlib import Path
import json

import backend.utils.charts_page2 as charts

router = APIRouter()

# Đường dẫn đến file dữ liệu đã xử lý
root_dir = Path(__file__).parent.parent.parent.parent.resolve()
csv_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"


class FilterRequest(BaseModel):
    sources: Optional[List[str]] = None
    position: Optional[str] = None
    experience: Optional[str] = None
    region: Optional[str] = None


@router.post("/api/dashboard/page2")
def get_page2_data(req: FilterRequest):
    """
    Endpoint xử lý logic Trang 2: Kỹ năng & Công nghệ.
    Nhận thông số lọc từ Frontend, xử lý dữ liệu kỹ năng và trả về
    KPI + 3 biểu đồ (Top Skills, Heatmap, Tech Trend).
    """
    # Đọc file CSV dữ liệu
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(columns=[
            'ten_cong_viec', 'ten_cong_ty', 'nhom_vi_tri', 'cap_do_kinh_nghiem',
            'tinh_thanh', 'vung_mien', 'luong_tb', 'hinh_thuc_lam_viec',
            'ngay_dang', 'thang_dang', 'nguon', 'ky_nang'
        ])

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

    # ---- Lấy danh sách kỹ năng kỹ thuật đã lọc (phục vụ KPI) ----
    tech_skills_series = charts._get_tech_skills(dff)

    total_jobs = int(len(dff))
    total_unique_skills = int(tech_skills_series.nunique()) if not tech_skills_series.empty else 0

    spark_color = "#FAE7CB"

    # ---- KPI 1: Tổng kỹ năng kỹ thuật unique ----
    skill_monthly_data = []
    if total_jobs > 0 and 'thang_dang' in dff.columns:
        monthly = dff.dropna(subset=['thang_dang']).groupby('thang_dang').apply(
            lambda g: g['ky_nang'].dropna().str.split(',').explode().str.strip().nunique(),
            include_groups=False
        )
        skill_monthly_data = [int(x) for x in monthly.tolist()]
    spark1_fig = charts.create_sparkline(skill_monthly_data, spark_color)

    # ---- KPI 2: Kỹ năng hot nhất ----
    top_skill_name = "N/A"
    top_skill_count = 0
    spark2_data = []
    if not tech_skills_series.empty:
        top_skill_name = str(tech_skills_series.value_counts().index[0])
        top_skill_count = int(tech_skills_series.value_counts().iloc[0])

        # Sparkline: tần suất của kỹ năng hot nhất theo tháng
        dff_time = dff.dropna(subset=['thang_dang', 'ky_nang'])
        spark2_data = []
        for month in sorted(dff_time['thang_dang'].unique()):
            month_df = dff_time[dff_time['thang_dang'] == month]
            count = month_df['ky_nang'].str.contains(
                rf'(?<![a-zA-Z]){top_skill_name}(?![a-zA-Z])', case=False, regex=True, na=False
            ).sum()
            spark2_data.append(int(count))
    spark2_fig = charts.create_sparkline(spark2_data, spark_color)

    # ---- KPI 3: Nhóm vị trí yêu cầu kỹ năng đa dạng nhất ----
    most_diverse_position = "N/A"
    avg_skills_per_job = 0.0
    spark3_data = []
    if total_jobs > 0 and 'nhom_vi_tri' in dff.columns:
        # Tính số kỹ năng trung bình mỗi tin trong từng nhóm
        dff_skills = dff.dropna(subset=['ky_nang', 'nhom_vi_tri'])
        if not dff_skills.empty:
            dff_skills = dff_skills.copy()
            dff_skills['skill_count'] = dff_skills['ky_nang'].str.split(',').apply(
                lambda x: len([s.strip() for s in x if s.strip()]) if isinstance(x, list) else 0
            )
            avg_by_pos = dff_skills.groupby('nhom_vi_tri')['skill_count'].mean()
            if not avg_by_pos.empty:
                most_diverse_position = str(avg_by_pos.idxmax())
                avg_skills_per_job = float(round(avg_by_pos.max(), 1))

                # Sparkline: số kỹ năng TB theo tháng của nhóm vị trí đa dạng nhất
                pos_dff = dff_skills[dff_skills['nhom_vi_tri'] == most_diverse_position]
                pos_dff = pos_dff.dropna(subset=['thang_dang'])
                spark3_data = [float(round(v, 1)) for v in pos_dff.groupby('thang_dang')['skill_count'].mean().tolist()]
    spark3_fig = charts.create_sparkline(spark3_data, spark_color)

    # ---- KPI 4: Công nghệ có xu hướng tăng trưởng mạnh nhất ----
    trending_tech = "N/A"
    trending_growth_pct = 0.0
    spark4_data = []
    if total_jobs > 0 and 'thang_dang' in dff.columns and 'ky_nang' in dff.columns:
        dff_time = dff.dropna(subset=['thang_dang', 'ky_nang'])
        months_sorted = sorted(dff_time['thang_dang'].unique())

        # So sánh 3 tháng đầu vs 3 tháng cuối để tính tăng trưởng
        if len(months_sorted) >= 6:
            early_months = months_sorted[:3]
            recent_months = months_sorted[-3:]

            best_growth = -999
            best_group = "N/A"
            best_spark = []

            for group_name, keywords in charts.EMERGING_TECH_GROUPS.items():
                pattern = '|'.join([rf'(?<![a-zA-Z]){kw}(?![a-zA-Z])' for kw in keywords])

                early_count = dff_time[dff_time['thang_dang'].isin(early_months)]['ky_nang'].str.contains(
                    pattern, case=False, regex=True, na=False
                ).sum()

                recent_count = dff_time[dff_time['thang_dang'].isin(recent_months)]['ky_nang'].str.contains(
                    pattern, case=False, regex=True, na=False
                ).sum()

                if early_count > 0:
                    growth = (recent_count - early_count) / early_count * 100
                elif recent_count > 0:
                    growth = 100.0
                else:
                    growth = 0.0

                if growth > best_growth:
                    best_growth = growth
                    best_group = group_name
                    # Sparkline: đếm theo tháng
                    spark_vals = []
                    for m in months_sorted:
                        cnt = dff_time[dff_time['thang_dang'] == m]['ky_nang'].str.contains(
                            pattern, case=False, regex=True, na=False
                        ).sum()
                        spark_vals.append(int(cnt))
                    best_spark = spark_vals

            trending_tech = best_group
            trending_growth_pct = float(round(best_growth, 1))
            spark4_data = best_spark

    spark4_fig = charts.create_sparkline(spark4_data, spark_color)

    # ---- Tạo 3 biểu đồ chính ----
    top_skills_fig = charts.create_top_skills_chart(dff)
    heatmap_fig = charts.create_skills_heatmap(dff)
    tech_trend_fig = charts.create_tech_trend_chart(dff)

    # ---- Xây dựng response ----
    return {
        "kpi": {
            "total_unique_skills": total_unique_skills,
            "total_jobs": total_jobs,
            "top_skill": {
                "name": top_skill_name,
                "count": top_skill_count
            },
            "most_diverse_position": {
                "name": most_diverse_position,
                "avg_skills": avg_skills_per_job
            },
            "trending_tech": {
                "name": trending_tech,
                "growth_pct": trending_growth_pct
            }
        },
        "charts": {
            "spark1": json.loads(spark1_fig.to_json()),
            "spark2": json.loads(spark2_fig.to_json()),
            "spark3": json.loads(spark3_fig.to_json()),
            "spark4": json.loads(spark4_fig.to_json()),
            "top_skills": json.loads(top_skills_fig.to_json()),
            "heatmap": json.loads(heatmap_fig.to_json()),
            "tech_trend": json.loads(tech_trend_fig.to_json()),
        }
    }
