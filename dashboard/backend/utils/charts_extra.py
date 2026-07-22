# Biểu đồ cho các câu hỏi "mở rộng" (EX-1..EX-6) — nằm NGOÀI 5 mục tiêu phân tích
# chính, không hiển thị ở trang dashboard 1-4 nào, CHỈ dùng cho tính năng "Nhận xét
# dựa trên biểu đồ có sẵn" của AI trang 5 (đăng ký trong chart_catalog.py).
#
# Được chuẩn bị trước cho buổi vấn đáp: logic tính toán đã được kiểm chứng chạy
# đúng trên dữ liệu thật (xem dashboard/backend/ai_prepared_questions.json, các
# mục EX-1..EX-6), viết lại thành hàm build_fn(df) chuẩn để route như 1 biểu đồ
# thật — tránh rủi ro AI sinh code lỗi khi demo trực tiếp.

import itertools
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from backend.utils.charts_common import apply_layout_styles
from backend.utils.charts_page2 import _get_tech_skills, NON_TECH_SKILLS

BRAND_GREEN = '#59B292'
NEUTRAL_GRAY = '#9ca3af'
MIN_SENIOR_SHARE = 3.0  # % tối thiểu ở nhóm Senior để 1 kỹ năng được xét (lọc nhiễu)


def _empty_fig(message):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=12, color="#9ca3af"))
    apply_layout_styles(fig)
    return fig


# ===================================================
# EX-1: Kỹ năng nào đặc trưng cho cấp Senior nhưng ít xuất hiện ở Junior/Fresher?
# ===================================================
def create_senior_signature_skills_chart(df):
    needed = {'ky_nang', 'cap_do_kinh_nghiem'}
    if df.empty or not needed.issubset(df.columns):
        return _empty_fig("Không có dữ liệu")

    valid_levels = ['Senior', 'Junior', 'Fresher']
    base = df.dropna(subset=['ky_nang', 'cap_do_kinh_nghiem'])
    base = base[base['cap_do_kinh_nghiem'].isin(valid_levels)]

    def skill_pct(sub_df):
        total = len(sub_df)
        if total == 0:
            return pd.Series(dtype=float)
        skills = _get_tech_skills(sub_df)
        return skills.value_counts() / total * 100

    senior_pct = skill_pct(base[base['cap_do_kinh_nghiem'] == 'Senior'])
    jf_pct = skill_pct(base[base['cap_do_kinh_nghiem'].isin(['Junior', 'Fresher'])])

    compare = pd.DataFrame({'Senior': senior_pct, 'Junior/Fresher': jf_pct}).fillna(0)
    compare = compare[compare['Senior'] >= MIN_SENIOR_SHARE]
    if compare.empty:
        return _empty_fig("Không đủ dữ liệu kỹ năng theo cấp bậc")

    compare['chenh_lech'] = compare['Senior'] - compare['Junior/Fresher']
    top = compare.sort_values('chenh_lech', ascending=False).head(15)
    top.index.name = 'ky_nang'
    order = top.index.tolist()[::-1]

    # Làm tròn NGAY trên dữ liệu (không chỉ format hiển thị) — CSV rút từ figure
    # để AI nhận xét phải đọc được số đã làm tròn, tránh số thập phân dài vô nghĩa.
    top[['Senior', 'Junior/Fresher']] = top[['Senior', 'Junior/Fresher']].round(1)
    plot_df = top.reset_index().melt(
        id_vars='ky_nang', value_vars=['Senior', 'Junior/Fresher'],
        var_name='Nhóm', value_name='ty_le'
    )

    fig = px.bar(
        plot_df, x='ty_le', y='ky_nang', color='Nhóm', barmode='group', orientation='h',
        text_auto='.1f',
        color_discrete_map={'Senior': BRAND_GREEN, 'Junior/Fresher': NEUTRAL_GRAY},
        labels={'ty_le': 'Tỷ lệ % tin tuyển dụng yêu cầu', 'ky_nang': 'Kỹ năng'},
    )
    fig.update_traces(textposition='outside', cliponaxis=False)
    fig.update_yaxes(categoryorder='array', categoryarray=order)
    apply_layout_styles(fig)
    fig.update_layout(
        margin=dict(l=140, r=20, t=10, b=10), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1)
    )
    return fig


# ===================================================
# EX-2: Nhóm vị trí nào có mức lương trung bình cao nhất và thấp nhất?
# ===================================================
def create_salary_extremes_by_position_chart(df):
    needed = {'nhom_vi_tri', 'luong_tb'}
    if df.empty or not needed.issubset(df.columns):
        return _empty_fig("Không có dữ liệu lương")

    valid = df.dropna(subset=['luong_tb'])
    grouped = valid.groupby('nhom_vi_tri', as_index=False)['luong_tb'].mean()
    if grouped.empty:
        return _empty_fig("Không đủ dữ liệu lương theo nhóm vị trí")

    grouped['luong_tb'] = grouped['luong_tb'].round(1)
    grouped = grouped.sort_values('luong_tb', ascending=True)

    colors = [NEUTRAL_GRAY] * len(grouped)
    colors[0] = '#EF553B'   # thấp nhất — đỏ
    colors[-1] = BRAND_GREEN  # cao nhất — xanh thương hiệu

    fig = px.bar(
        grouped, x='luong_tb', y='nhom_vi_tri', orientation='h', text='luong_tb',
        labels={'luong_tb': 'Lương trung bình (triệu VNĐ)', 'nhom_vi_tri': 'Nhóm vị trí'},
    )
    fig.update_traces(
        marker_color=colors, texttemplate='%{text} tr', textposition='outside'
    )
    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=160, r=50, t=10, b=10))
    return fig


# ===================================================
# EX-3: Nếu biết kỹ năng Python, nên ứng tuyển vào nhóm vị trí nào?
# ===================================================
def create_python_position_recommendation_chart(df):
    needed = {'ky_nang', 'nhom_vi_tri'}
    if df.empty or not needed.issubset(df.columns):
        return _empty_fig("Không có dữ liệu")

    valid = df.dropna(subset=['ky_nang'])
    has_python = valid['ky_nang'].apply(
        lambda x: 'python' in [s.strip().lower() for s in str(x).split(',')]
    )
    python_df = valid[has_python]
    if python_df.empty:
        return _empty_fig("Không có tin tuyển dụng nào yêu cầu Python")

    job_counts = python_df.groupby('nhom_vi_tri').size().reset_index(name='so_luong')
    salary_valid = python_df.dropna(subset=['luong_tb']) if 'luong_tb' in python_df.columns else python_df.iloc[0:0]
    salary_means = salary_valid.groupby('nhom_vi_tri')['luong_tb'].mean().round(1).reset_index(name='luong_tb_trung_binh')

    summary = job_counts.merge(salary_means, on='nhom_vi_tri', how='left')
    summary = summary.sort_values('so_luong', ascending=False)

    # Dùng biểu đồ tổ hợp (cột = số lượng, đường = lương TB trên trục phụ) thay vì
    # mã hoá lương qua MÀU (color=) — vì extract_csv_from_figure chỉ đọc được x/y
    # thật của từng trace, không đọc được giá trị màu liên tục. Tách thành 2 trace
    # số liệu rõ ràng đảm bảo AI nhận xét có ĐẦY ĐỦ cả 2 chỉ số, không chỉ số lượng.
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary['nhom_vi_tri'], y=summary['so_luong'], name='so_luong_tin',
        marker_color=BRAND_GREEN, text=summary['so_luong'], textposition='outside'
    ))
    fig.add_trace(go.Scatter(
        x=summary['nhom_vi_tri'], y=summary['luong_tb_trung_binh'], name='luong_tb_trieu_vnd',
        mode='lines+markers', marker=dict(color='#EF553B', size=8),
        line=dict(color='#EF553B', width=2), yaxis='y2'
    ))
    fig.update_layout(
        xaxis=dict(tickangle=-45),
        yaxis=dict(title='Số lượng tin tuyển dụng'),
        yaxis2=dict(title='Lương TB (triệu VNĐ)', overlaying='y', side='right', showgrid=False),
    )
    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=20, r=20, t=10, b=110), showlegend=True,
                       legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1))
    return fig


# ===================================================
# EX-4: Chức danh công việc nào xuất hiện phổ biến nhất trong các tin tuyển dụng IT?
# ===================================================
def create_top_job_titles_chart(df):
    if df.empty or 'ten_cong_viec' not in df.columns:
        return _empty_fig("Không có dữ liệu")

    counts = df['ten_cong_viec'].dropna().value_counts().reset_index()
    counts.columns = ['chuc_danh', 'so_luong']
    top15 = counts.head(15).sort_values('so_luong', ascending=True)
    if top15.empty:
        return _empty_fig("Không có dữ liệu chức danh")

    fig = px.bar(
        top15, x='so_luong', y='chuc_danh', orientation='h', text='so_luong',
        labels={'so_luong': 'Số lượng tin tuyển dụng', 'chuc_danh': 'Chức danh công việc'},
    )
    fig.update_traces(marker_color=BRAND_GREEN, textposition='outside')
    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=200, r=30, t=10, b=10))
    return fig


# ===================================================
# EX-5: Hình thức làm việc phân bố khác nhau như thế nào giữa các nhóm vị trí?
# ===================================================
def create_work_type_by_position_chart(df):
    needed = {'nhom_vi_tri', 'hinh_thuc_lam_viec'}
    if df.empty or not needed.issubset(df.columns):
        return _empty_fig("Không có dữ liệu")

    valid = df.dropna(subset=['nhom_vi_tri', 'hinh_thuc_lam_viec'])
    grouped = valid.groupby(['nhom_vi_tri', 'hinh_thuc_lam_viec']).size().reset_index(name='so_luong')
    if grouped.empty:
        return _empty_fig("Không đủ dữ liệu")

    total_by_group = valid.groupby('nhom_vi_tri').size().reset_index(name='tong_so')
    grouped = grouped.merge(total_by_group, on='nhom_vi_tri')
    order = total_by_group.sort_values('tong_so', ascending=False)['nhom_vi_tri'].tolist()

    fig = px.bar(
        grouped, x='nhom_vi_tri', y='so_luong', color='hinh_thuc_lam_viec', barmode='stack',
        labels={
            'nhom_vi_tri': 'Nhóm vị trí công việc', 'so_luong': 'Số lượng tin tuyển dụng',
            'hinh_thuc_lam_viec': 'Hình thức làm việc'
        },
        category_orders={'nhom_vi_tri': order},
    )
    apply_layout_styles(fig)
    fig.update_layout(
        xaxis_tickangle=-45, margin=dict(l=20, r=20, t=10, b=110), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


# ===================================================
# EX-6: Những kỹ năng nào thường xuất hiện cùng nhau nhiều nhất trong 1 tin tuyển dụng?
# ===================================================
def create_top_skill_pairs_chart(df):
    if df.empty or 'ky_nang' not in df.columns:
        return _empty_fig("Không có dữ liệu")

    # Lọc kỹ năng phi kỹ thuật (Sales, Financial, Ngân hàng...) giống hàm
    # _get_tech_skills — nếu không, các cặp phổ biến nhất sẽ toàn kỹ năng mềm/tài
    # chính (thường đi kèm nhau trong tin đăng đa ngành), không phản ánh đúng câu hỏi.
    def clean_tech_skills(skills_str):
        raw = [s.strip() for s in str(skills_str).split(',') if s.strip()]
        return sorted({s for s in raw if len(s) >= 3 and s.lower() not in NON_TECH_SKILLS})

    pair_counter = Counter()
    for skills_str in df['ky_nang'].dropna():
        skills = clean_tech_skills(skills_str)
        pair_counter.update(itertools.combinations(skills, 2))

    if not pair_counter:
        return _empty_fig("Không đủ dữ liệu kỹ năng")

    top20 = pair_counter.most_common(20)
    plot_df = pd.DataFrame(
        [(f"{a} + {b}", c) for (a, b), c in top20], columns=['cap_ky_nang', 'so_lan']
    ).sort_values('so_lan', ascending=True)

    fig = px.bar(
        plot_df, x='so_lan', y='cap_ky_nang', orientation='h', text='so_lan',
        labels={'so_lan': 'Số tin tuyển dụng có chứa cặp kỹ năng', 'cap_ky_nang': 'Cặp kỹ năng'},
    )
    fig.update_traces(marker_color=BRAND_GREEN, textposition='outside')
    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=260, r=30, t=10, b=10))
    return fig
