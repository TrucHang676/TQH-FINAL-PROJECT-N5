# Nhập các thư viện cần thiết cho tính toán và vẽ biểu đồ Plotly
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from backend.utils.charts_common import apply_layout_styles

# Các cấp bậc được xem là "nhân sự trẻ" trong mục tiêu 4
YOUNG_LEVELS = ['Intern', 'Fresher', 'Junior']
# Nhóm vị trí "Other" là nhóm gộp không phân loại được, không có ý nghĩa hướng nghiệp
EXCLUDED_POSITION = 'Other'
UNKNOWN_LEVEL = 'Không rõ'
# Số tin tối thiểu có ghi rõ cấp bậc để tỷ lệ % cởi mở đủ tin cậy thống kê
MIN_SAMPLE_SIZE = 10

# Thứ tự "thang bậc sự nghiệp" và mã màu ngữ nghĩa:
# nhóm trẻ tô xanh nổi bật (đối tượng của mục tiêu 4), Middle/Senior tô xám lùi về sau
LEVEL_ORDER = ['Intern', 'Fresher', 'Junior', 'Middle', 'Senior']
LEVEL_COLORS = {
    'Intern':  '#c7f0dd',   # Xanh nhạt
    'Fresher': '#8fd3b6',   # Xanh vừa
    'Junior':  '#59B292',   # Xanh chủ đạo (đậm dần theo kinh nghiệm)
    'Middle':  '#cbd5e1',   # Xám lam nhạt (lùi về sau)
    'Senior':  '#94a3b8',   # Xám lam đậm
}

# Số mẫu (Intern + Fresher có lương) tối thiểu để một nhóm vị trí đủ điều kiện vẽ box plot
MIN_BOX_SAMPLE = 20
# Kiểu màu Intern / Fresher trong box plot: viền đậm để hộp nổi rõ, nền tô bán trong
# suốt để hộp "đặc" dễ thấy (khắc phục hộp rỗng khó nhìn). Amber vs Xanh tương phản mạnh.
STARTER_STYLE = {
    'Intern':  {'line': '#D99400', 'fill': 'rgba(255, 201, 77, 0.35)'},   # Hổ phách đậm
    'Fresher': {'line': '#2F7D60', 'fill': 'rgba(89, 178, 146, 0.35)'},   # Xanh đậm
}


# ===================================================
# BIỂU ĐỒ: Treemap quy mô & độ cởi mở với nhân sự trẻ theo nhóm vị trí
# Trả lời câu hỏi: "Những nhóm vị trí công việc nào cởi mở nhất và có nhu cầu
# tuyển dụng đối tượng Fresher/Intern cao nhất?"
# ===================================================
def create_youth_opportunity_treemap(df):
    """
    Kích thước ô = tổng số tin tuyển dụng của nhóm vị trí (quy mô thị trường).
    Màu ô = tỷ lệ % tin dành cho Intern/Fresher/Junior trong số tin có ghi rõ
    cấp bậc của nhóm đó (độ cởi mở với nhân sự trẻ).
    """
    if df.empty or 'nhom_vi_tri' not in df.columns or 'cap_do_kinh_nghiem' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    work_df = df[df['nhom_vi_tri'] != EXCLUDED_POSITION].copy()

    total_counts = work_df.groupby('nhom_vi_tri').size()

    known_df = work_df[work_df['cap_do_kinh_nghiem'] != UNKNOWN_LEVEL]
    known_counts = known_df.groupby('nhom_vi_tri').size()
    young_counts = known_df[known_df['cap_do_kinh_nghiem'].isin(YOUNG_LEVELS)].groupby('nhom_vi_tri').size()

    summary = pd.DataFrame({'tong_tin': total_counts})
    summary = summary.join(known_counts.rename('tin_co_cap_bac')).fillna(0)
    summary = summary.join(young_counts.rename('tin_tre')).fillna(0)

    # Chỉ giữ các nhóm có đủ dữ liệu cấp bậc để tính tỷ lệ cởi mở đáng tin cậy
    summary = summary[summary['tin_co_cap_bac'] >= MIN_SAMPLE_SIZE]

    if summary.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không đủ dữ liệu cấp bậc để phân tích", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    summary['ty_le_tre'] = (summary['tin_tre'] / summary['tin_co_cap_bac'] * 100)
    summary = summary.sort_values('tong_tin', ascending=False).reset_index().rename(columns={'index': 'nhom_vi_tri'})

    # Bảng màu xanh lá đồng nhất với Heatmap kỹ năng (Dashboard trang 2) và bản đồ tỉnh thành (trang 1)
    custom_colorscale = [
        [0.0, "#f8f5f0"],
        [0.1, "#d4ede3"],
        [0.4, "#7ec8a7"],
        [0.7, "#59B292"],
        [1.0, "#1a5944"],
    ]

    # Tự nội suy màu hex cho từng ô thay vì để plotly.js dùng chế độ colorscale.
    # Lý do: ở chế độ colorscale, plotly.js tô root node màu tối và bỏ qua
    # root.color → sinh ra dải xám đậm + khung tối bao quanh treemap.
    def _hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def _interp_color(t):
        for (p0, c0), (p1, c1) in zip(custom_colorscale, custom_colorscale[1:]):
            if t <= p1:
                f = (t - p0) / (p1 - p0) if p1 > p0 else 0
                r0, g0, b0 = _hex_to_rgb(c0)
                r1, g1, b1 = _hex_to_rgb(c1)
                return f"rgb({round(r0 + (r1 - r0) * f)},{round(g0 + (g1 - g0) * f)},{round(b0 + (b1 - b0) * f)})"
        return custom_colorscale[-1][1]

    pct_min = float(summary['ty_le_tre'].min())
    pct_max = float(summary['ty_le_tre'].max())
    pct_span = (pct_max - pct_min) or 1.0
    tile_colors = [_interp_color((p - pct_min) / pct_span) for p in summary['ty_le_tre']]

    hover_texts = [
        f"<span style='font-size:4px'> </span><br>"
        f" &nbsp;<b><span style='color:#59B292'>▍</span> {row['nhom_vi_tri']}</b>&nbsp; <br>"
        f"<span style='font-size:4px'> </span><br>"
        f"<span style='color:#5a4000'>"
        f" &nbsp;Tổng số tin tuyển dụng: <b>{int(row['tong_tin']):,} tin</b>&nbsp; <br>"
        f" &nbsp;Tỷ lệ dành cho Intern/Fresher/Junior: <b>{row['ty_le_tre']:.1f}%</b>&nbsp; <br>"
        f" &nbsp;(trên {int(row['tin_co_cap_bac']):,} tin có ghi rõ cấp bậc)&nbsp;"
        f"</span><br><span style='font-size:4px'> </span>"
        for _, row in summary.iterrows()
    ]

    fig = go.Figure(go.Treemap(
        labels=summary['nhom_vi_tri'],
        parents=[''] * len(summary),
        values=summary['tong_tin'],
        branchvalues='remainder',
        customdata=summary['ty_le_tre'],
        texttemplate="<b>%{label}</b><br>%{value:,} tin<br>%{customdata:.1f}% trẻ",
        textposition='middle center',
        textfont=dict(size=12, color='#111827'),
        marker=dict(
            colors=tile_colors,
            line=dict(width=2, color='#ffffff')
        ),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>",
        pathbar=dict(visible=False),
        # Root node tô trắng để hòa vào nền card (chế độ màu rời rạc mới tôn trọng root.color)
        root=dict(color='#ffffff'),
        tiling=dict(pad=2)
    ))

    # Trace scatter ẩn chỉ để hiển thị colorbar thang "% trẻ" (treemap ở chế độ
    # màu rời rạc không tự sinh colorbar được)
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(
            colorscale=custom_colorscale,
            cmin=pct_min, cmax=pct_max,
            color=[pct_min],
            showscale=True,
            colorbar=dict(
                title=dict(text="% trẻ", font=dict(size=9, color='#4b5563')),
                thicknessmode="pixels", thickness=12,
                lenmode="pixels", len=140,
                yanchor="middle", y=0.5,
                xanchor="left", x=1.0,
                tickfont=dict(size=9, color="#4b5563")
            )
        ),
        hoverinfo='skip', showlegend=False
    ))

    apply_layout_styles(fig)
    fig.update_layout(
        margin=dict(l=4, r=56, t=4, b=4),
        # Ẩn hệ trục do trace scatter ẩn sinh ra
        xaxis=dict(visible=False), yaxis=dict(visible=False)
    )

    return fig


# ===================================================
# BIỂU ĐỒ: Donut phân bố cấp bậc
# Trả lời câu hỏi: "Cơ hội việc làm dành cho nhóm ít kinh nghiệm (Intern, Fresher,
# Junior) chiếm tỷ trọng bao nhiêu?"
# ===================================================
def create_experience_distribution_chart(df):
    """
    Donut phân bố 5 cấp bậc (trên các tin có ghi rõ cấp bậc).
    Câu hỏi là quan hệ phần–trên–tổng thể nên donut là dạng phù hợp:
      - Nhóm trẻ (Intern/Fresher/Junior) tô xanh, xếp liền mạch thành 1 cung nổi bật.
      - Middle/Senior tô xám lùi về sau.
      - Số 31.5% (tỷ trọng nhóm trẻ) hiển thị to ở giữa lỗ donut — câu trả lời headline.
    """
    if df.empty or 'cap_do_kinh_nghiem' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    known_df = df[df['cap_do_kinh_nghiem'] != UNKNOWN_LEVEL]
    total_known = len(known_df)

    if total_known == 0:
        fig = go.Figure()
        fig.add_annotation(text="Không đủ dữ liệu cấp bậc", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    level_counts = known_df['cap_do_kinh_nghiem'].value_counts()
    # Giữ đúng thứ tự thang bậc để nhóm trẻ (3 cấp đầu) tạo thành cung liền nhau
    level_names = [lvl for lvl in LEVEL_ORDER if int(level_counts.get(lvl, 0)) > 0]
    values = [int(level_counts[lvl]) for lvl in level_names]
    colors = [LEVEL_COLORS[lvl] for lvl in level_names]
    # Nhãn ngoài kèm % (kiểu callout) — mỗi lát 1 dòng gọn: "Senior · 41.4%"
    slice_texts = [f"{lvl} · {cnt/total_known*100:.1f}%" for lvl, cnt in zip(level_names, values)]

    hover_texts = [
        f"<span style='font-size:4px'> </span><br>"
        f" &nbsp;<b><span style='color:#59B292'>▍</span> {lvl}</b>&nbsp; <br>"
        f"<span style='font-size:4px'> </span><br>"
        f"<span style='color:#5a4000'>"
        f" &nbsp;Số lượng: <b>{cnt:,} tin</b>&nbsp; <br>"
        f" &nbsp;Tỉ lệ: <b>{cnt/total_known*100:.1f}%</b>&nbsp; "
        f"</span><br><span style='font-size:4px'> </span>"
        for lvl, cnt in zip(level_names, values)
    ]

    fig = go.Figure(go.Pie(
        labels=level_names,
        values=values,
        hole=0.5,
        sort=False,
        direction='clockwise',
        rotation=0,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        text=slice_texts,
        texttemplate="%{text}",
        textposition='outside',
        textfont=dict(size=11, color='#374151'),
        automargin=False,
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=False
    ))

    apply_layout_styles(fig)
    # Margin trái/phải bằng nhau vừa đủ chứa nhãn ngoài, donut chiếm tối đa diện tích
    fig.update_layout(margin=dict(l=68, r=68, t=12, b=12), showlegend=False)
    return fig


# ===================================================
# BIỂU ĐỒ: Box plot lương khởi điểm Intern / Fresher theo nhóm vị trí
# Trả lời câu hỏi: "Mức lương khởi điểm thực tế dành cho đối tượng Intern và Fresher
# tại Việt Nam là bao nhiêu, và mức lương này chênh lệch thế nào giữa các nhóm vị trí?"
# ===================================================
def create_youth_salary_boxplot(df):
    """
    Box plot lương (luong_tb) cho Intern và Fresher, tách theo nhóm vị trí.
    Kỹ thuật nâng cao có chủ đích:
      - Phủ điểm dữ liệu thật (boxpoints='all' + jitter): vì cỡ mẫu nhỏ, chỉ nhìn
        hộp dễ hiểu sai → hiện từng điểm để thấy phân bố thực.
      - Cắt ngoại lệ ở phân vị 99 để tránh vài điểm lỗi kéo giãn trục tung.
      - Đường tham chiếu = trung vị lương chung của nhóm trẻ, làm mốc so sánh.
    """
    needed = {'cap_do_kinh_nghiem', 'nhom_vi_tri', 'luong_tb'}
    if df.empty or not needed.issubset(df.columns):
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu lương", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    starter = df[
        df['cap_do_kinh_nghiem'].isin(['Intern', 'Fresher'])
        & (df['nhom_vi_tri'] != EXCLUDED_POSITION)
    ].dropna(subset=['luong_tb']).copy()

    if starter.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không đủ dữ liệu lương Intern/Fresher", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    # Cắt ngoại lệ ở phân vị 99 (loại vài điểm lỗi kéo giãn trục)
    cap = starter['luong_tb'].quantile(0.99)
    starter = starter[starter['luong_tb'] <= cap]

    # Chỉ giữ các nhóm vị trí có đủ mẫu; sắp xếp theo trung vị lương giảm dần
    grp_size = starter.groupby('nhom_vi_tri').size()
    valid = grp_size[grp_size >= MIN_BOX_SAMPLE].index.tolist()
    starter = starter[starter['nhom_vi_tri'].isin(valid)]

    if starter.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không đủ mẫu để phân tích theo nhóm vị trí", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    order = starter.groupby('nhom_vi_tri')['luong_tb'].median().sort_values(ascending=False).index.tolist()

    fig = go.Figure()
    for level in ['Intern', 'Fresher']:
        sub = starter[starter['cap_do_kinh_nghiem'] == level]
        if sub.empty:
            continue
        style = STARTER_STYLE[level]
        fig.add_trace(go.Box(
            x=sub['nhom_vi_tri'],
            y=sub['luong_tb'],
            name=level,
            boxpoints='all', jitter=0.4, pointpos=0,
            marker=dict(color=style['line'], size=4, opacity=0.65),
            line=dict(color=style['line'], width=1.5),
            fillcolor=style['fill'],
            whiskerwidth=0.6,
            hovertemplate=(
                f"<b>{level}</b> · %{{x}}<br>Lương: <b>%{{y:.1f}} triệu</b><extra></extra>"
            )
        ))

    # Đường tham chiếu: trung vị lương chung của nhóm trẻ (mốc so sánh).
    # Không gán nhãn trong vùng vẽ (tránh chồng lên hộp) — thay bằng một trace
    # "giả" chỉ để chú thích đường nét đứt xuất hiện trong legend cạnh Intern/Fresher.
    overall_median = starter['luong_tb'].median()
    fig.add_hline(y=overall_median, line=dict(color='#9ca3af', width=1.2, dash='dash'))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='lines',
        line=dict(color='#9ca3af', width=1.2, dash='dash'),
        name=f"Trung vị chung ({overall_median:.1f} tr)",
        hoverinfo='skip'
    ))

    # Rút gọn nhãn nhóm vị trí cho vừa trục X
    short_map = {
        'Software Development': 'Software<br>Dev',
        'AI / ML / Data Science': 'AI / ML',
        'Mobile / Game / Embedded': 'Mobile /<br>Game',
        'Cloud / DevOps / SRE': 'Cloud /<br>DevOps',
        'QA / Testing': 'QA /<br>Testing',
        'Data Engineering / Database': 'Data<br>Eng.',
        'IT Support / ERP': 'IT<br>Support',
        'Product / Business / UX': 'Product /<br>UX',
        'Management / Architecture': 'Manage-<br>ment',
        'Cybersecurity': 'Cyber-<br>security',
    }
    fig.update_xaxes(
        categoryorder='array', categoryarray=order,
        ticktext=[short_map.get(p, p) for p in order], tickvals=order,
        tickfont=dict(size=9, color='#111827', weight='bold'),
        showgrid=False, linecolor='#e5e7eb'
    )
    fig.update_yaxes(
        showgrid=True, gridcolor='#f1f5f9', linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'), rangemode='tozero',
        title_text="Lương (triệu VNĐ)",
        title_font=dict(size=10, color='#4b5563', weight='bold'),
        title_standoff=6
    )

    apply_layout_styles(fig)
    fig.update_layout(
        boxmode='group',
        boxgroupgap=0.25,
        margin=dict(l=42, r=12, t=22, b=28),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0)", font=dict(size=10, color='#374151')
        )
    )
    return fig
