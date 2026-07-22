# Nhập các thư viện cần thiết cho tính toán và vẽ biểu đồ Plotly
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

from backend.utils.charts_common import apply_layout_styles, REGION_COLORS

# ===================================================
# HẰNG SỐ: Danh sách kỹ năng phi kỹ thuật cần lọc bỏ
# ===================================================
NON_TECH_SKILLS = {
    'english', 'fresher accepted', 'business development', 'financial',
    'finance', 'tài chính', 'ngân hàng', 'banking', 'sales', 'marketing',
    'communication', 'teamwork', 'problem solving', 'leadership',
    'management', 'project management', 'scrum master', 'agile', 'scrum',
    'kanban', 'jira', 'confluence', 'trello', 'ms office', 'word', 'excel',
    'powerpoint', 'japanese', 'korean', 'chinese', 'presentation', 'writing',
    'reading', 'listening', 'speaking', 'soft skills', 'time management',
    'critical thinking', 'detail oriented', 'research', 'work ethic',
    'adaptability', 'flexibility', 'creativity', 'innovation',
    'customer service', 'negotiation', 'analytical', 'ielts', 'toeic',
    'toefl', 'n2', 'n3', 'n4', 'business analysis', 'business analyst',
    'product management', 'product owner', 'ux', 'ui', 'design thinking',
    'requirements', 'documentation', 'report', 'reporting',
    'fresher', 'intern', 'junior', 'middle', 'senior', 'lead',
    'mentor', 'coach', 'training', 'teaching',
    'nhiệt tình', 'có sức khỏe tốt', 'sức khỏe tốt', 'trung thực',
    'chăm chỉ', 'nhanh nhẹn', 'cẩn thận', 'giao tiếp', 'làm việc nhóm',
    'điện lực', 'công nghệ thông tin', 'nam', 'nữ', 'sức khỏe'
}

# ===================================================
# HẰNG SỐ: Nhóm công nghệ mới nổi để phân tích xu hướng
# ===================================================
EMERGING_TECH_GROUPS = {
    'AI / ML': ['AI', 'Machine Learning', 'Deep Learning', 'LLM', 'Generative AI', 'NLP',
                'Computer Vision', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
                'Data Science', 'Natural Language Processing'],
    'Cloud': ['Cloud', 'AWS', 'Azure', 'GCP', 'Google Cloud', 'Amazon Web Services',
              'Microsoft Azure', 'Serverless', 'Lambda', 'EC2', 'S3'],
    'DevOps / Container': ['DevOps', 'Docker', 'Kubernetes', 'K8s', 'CI/CD', 'Jenkins',
                            'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible',
                            'SRE', 'Microservices', 'Infrastructure'],
    'Data Engineering': ['Spark', 'Kafka', 'Airflow', 'BigQuery', 'Snowflake',
                         'Data Engineering', 'Data Pipeline', 'ETL', 'Databricks',
                         'Hadoop', 'Hive', 'Flink'],
}

# Màu sắc cho 4 nhóm công nghệ (đảm bảo độ tương phản cao, dễ phân biệt)
EMERGING_COLORS = {
    'AI / ML': '#FA6781',           # Coral Red (Đỏ san hô)
    'Cloud': '#4A89F3',             # Soft Sky Blue (Xanh dương sáng dịu nhẹ đại diện cho Cloud)
    'DevOps / Container': '#FFC94D', # Amber Gold (Vàng hổ phách)
    'Data Engineering': '#0D9488',  # Teal (Xanh mòng két)
}


def _get_tech_skills(df):
    """
    Hàm nội bộ: Tách cột ky_nang thành series các kỹ năng,
    lọc bỏ kỹ năng phi kỹ thuật và kỹ năng rỗng.
    Trả về Series chứa tất cả kỹ năng kỹ thuật (đã làm sạch).
    """
    if df.empty or 'ky_nang' not in df.columns:
        return pd.Series([], dtype=str)

    # Tách các kỹ năng theo dấu phẩy, strip khoảng trắng
    skills = df['ky_nang'].dropna().str.split(',').explode().str.strip()
    skills = skills[skills != '']

    # Lọc bỏ kỹ năng phi kỹ thuật (case-insensitive)
    skills = skills[~skills.str.lower().isin(NON_TECH_SKILLS)]

    # Lọc bỏ kỹ năng quá ngắn (1-2 ký tự, thường là viết tắt vô nghĩa)
    skills = skills[skills.str.len() >= 3]

    return skills


# ===================================================
# BIỂU ĐỒ 1: Top 15 Kỹ năng công nghệ được săn đón nhất
# Horizontal Bar Chart — trả lời câu hỏi 1
# ===================================================
def create_top_skills_chart(df):
    """
    Vẽ biểu đồ cột ngang hiển thị Top 15 kỹ năng công nghệ
    được yêu cầu nhiều nhất trong thị trường tuyển dụng IT.
    Đã loại bỏ các kỹ năng phi kỹ thuật như English, Sales, ...
    """
    skills = _get_tech_skills(df)

    if skills.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Không có dữ liệu kỹ năng",
            showarrow=False,
            font=dict(size=12, color="#9ca3af")
        )
        apply_layout_styles(fig)
        return fig

    # Đếm tần suất và lấy top 15
    skill_counts = skills.value_counts().head(15).reset_index()
    skill_counts.columns = ['ky_nang', 'count']
    total = len(df.dropna(subset=['ky_nang']))
    skill_counts['pct'] = (skill_counts['count'] / total * 100).round(1)

    # Sắp xếp tăng dần để biểu đồ hiển thị cao nhất ở trên
    skill_counts = skill_counts.sort_values('count', ascending=True)

    # Rút gọn nhãn chữ nếu quá dài để tránh vỡ khung biểu đồ
    seen = {}
    display_names = []
    for name in skill_counts['ky_nang']:
        trunc = name[:15] + '...' if len(name) > 18 else name
        while trunc in seen:
            trunc += ' '  # Thêm khoảng trắng để tạo sự khác biệt cho Plotly tránh gộp nhóm
        seen[trunc] = True
        display_names.append(trunc)
    skill_counts['ky_nang_display'] = display_names

    fig = go.Figure(data=[go.Bar(
        x=skill_counts['count'],
        y=skill_counts['ky_nang_display'],
        orientation='h',
        text=[f"{row['count']:,}" for _, row in skill_counts.iterrows()],
        textposition='outside',
        cliponaxis=False,
        marker=dict(
            color='#59B292',
            line=dict(width=0)
        ),
        hovertext=[
            f"<span style='font-size:4px'> </span><br>"
            f" &nbsp;<b><span style='color:#59B292'>▍</span> {row['ky_nang']}</b>&nbsp; <br>"
            f"<span style='font-size:4px'> </span><br>"
            f"<span style='color:#5a4000'>"
            f" &nbsp;Số lượng tin: <b>{row['count']:,} tin</b>&nbsp; <br>"
            f" &nbsp;Tỉ lệ: <b>{row['pct']:.1f}%</b>&nbsp; "
            f"</span><br><span style='font-size:4px'> </span>"
            for _, row in skill_counts.iterrows()
        ],
        hovertemplate="%{hovertext}<extra></extra>"
    )])

    max_count = skill_counts['count'].max()
    fig.update_xaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Số lượng tin tuyển dụng",
        title_font=dict(size=10, color='#4b5563', weight='bold'),
        range=[0, max_count * 1.12] if not pd.isna(max_count) else None
    )

    fig.update_yaxes(
        showgrid=False,
        linecolor='#e5e7eb',
        tickfont=dict(size=10, color='#111827', weight='bold'),
        automargin=True
    )

    apply_layout_styles(fig)
    # Tự động tính margin trái dựa trên nhãn dài nhất để tránh bị cắt chữ khi lọc
    max_label_len = max(len(name) for name in display_names) if display_names else 10
    left_margin = max(80, min(max_label_len * 7 + 10, 140))
    fig.update_layout(margin=dict(l=left_margin, r=35, t=10, b=20))

    return fig


# ===================================================
# BIỂU ĐỒ 2: Heatmap Kỹ năng × Nhóm vị trí công việc
# Trả lời câu hỏi 2
# ===================================================
def create_skills_heatmap(df):
    """
    Vẽ Heatmap thể hiện sự phân bố của các kỹ năng công nghệ
    hàng đầu theo từng nhóm vị trí công việc (Software Dev, AI/ML, Mobile, ...).
    Giúp thấy rõ sự khác biệt về yêu cầu kỹ năng giữa các nhóm.
    """
    if df.empty or 'nhom_vi_tri' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Không có dữ liệu",
            showarrow=False,
            font=dict(size=12, color="#9ca3af")
        )
        apply_layout_styles(fig)
        return fig

    # Lấy top 10 kỹ năng kỹ thuật toàn bộ
    all_tech_skills = _get_tech_skills(df)
    if all_tech_skills.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu kỹ năng", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    top_skills = all_tech_skills.value_counts().head(10).index.tolist()

    # Các nhóm vị trí chính (lọc các nhóm có đủ dữ liệu)
    main_positions = [
        'Software Development',
        'AI / ML / Data Science',
        'Mobile / Game / Embedded',
        'Cloud / DevOps / SRE',
        'QA / Testing',
        'Data Engineering / Database',
    ]

    # Lọc df chỉ lấy các nhóm vị trí chính
    df_pos = df[df['nhom_vi_tri'].isin(main_positions)]

    # Xây dựng ma trận heatmap: rows = skills, cols = positions
    matrix = []
    for skill in top_skills:
        row = []
        for pos in main_positions:
            pos_df = df_pos[df_pos['nhom_vi_tri'] == pos]
            if pos_df.empty:
                row.append(0)
                continue
            # Đếm số tin trong nhóm vị trí đó có chứa kỹ năng này
            count = pos_df['ky_nang'].dropna().str.contains(
                rf'(?<![a-zA-Z]){skill}(?![a-zA-Z])', case=False, regex=True
            ).sum()
            row.append(int(count))
        matrix.append(row)

    z = np.array(matrix, dtype=float)

    # Rút gọn tên nhóm vị trí để vừa trục X
    pos_labels = [
        'Software\nDev',
        'AI / ML',
        'Mobile /\nGame',
        'Cloud /\nDevOps',
        'QA /\nTesting',
        'Data\nEngineering',
    ]

    # Tạo text annotation hiển thị số liệu trong từng ô
    text_matrix = [[str(int(v)) if v > 0 else '' for v in row] for row in z]

    # Tạo hovertext matrix chi tiết
    hover_matrix = []
    for i, skill in enumerate(top_skills):
        hover_row = []
        for j, pos in enumerate(main_positions):
            val = int(z[i][j])
            pos_total = len(df[df['nhom_vi_tri'] == pos])
            pct = (val / pos_total * 100) if pos_total > 0 else 0
            hover_row.append(
                f"<span style='font-size:4px'> </span><br>"
                f" &nbsp;<b><span style='color:#59B292'>▍</span> {skill}</b>&nbsp; <br>"
                f"<span style='font-size:4px'> </span><br>"
                f"<span style='color:#5a4000'>"
                f" &nbsp;Nhóm: <b>{pos}</b>&nbsp; <br>"
                f" &nbsp;Số tin: <b>{val:,} tin</b>&nbsp; <br>"
                f" &nbsp;Trong nhóm: <b>{pct:.1f}%</b>&nbsp; "
                f"</span><br><span style='font-size:4px'> </span>"
            )
        hover_matrix.append(hover_row)

    # Bảng màu custom: nền beige → xanh đậm
    custom_colorscale = [
        [0.0, "#f8f5f0"],
        [0.1, "#d4ede3"],
        [0.4, "#7ec8a7"],
        [0.7, "#59B292"],
        [1.0, "#1a5944"],
    ]

    # Tính min, max để xác định ô nào xanh đậm thì dùng chữ trắng (dùng HTML span trong text)
    flat_z = [val for row in z for val in row if val is not None]
    z_min = min(flat_z) if flat_z else 0
    z_max = max(flat_z) if flat_z else 1
    z_span = (z_max - z_min) or 1.0

    formatted_text_matrix = []
    for row in z:
        f_row = []
        for val in row:
            if val is None or val == 0:
                f_row.append("-")
            else:
                c = "#ffffff" if (val - z_min) / z_span > 0.5 else "#111827"
                f_row.append(f"<span style='color:{c}'>{val:.1f}</span>")
        formatted_text_matrix.append(f_row)

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=pos_labels,
        y=top_skills,
        text=formatted_text_matrix,
        texttemplate="%{text}",
        textfont=dict(size=9),
        colorscale=custom_colorscale,
        showscale=True,
        hovertext=hover_matrix,
        hovertemplate="%{hovertext}<extra></extra>",
        colorbar=dict(
            title="",
            thicknessmode="pixels", thickness=12,
            lenmode="pixels", len=120,
            yanchor="middle", y=0.5,
            xanchor="left", x=1.01,
            tickfont=dict(size=9, color="#4b5563")
        )
    ))

    fig.update_xaxes(
        side='bottom',
        tickfont=dict(size=9, color='#374151', weight='bold'),
        showgrid=False,
        showline=False,
        ticks=""
    )

    fig.update_yaxes(
        tickfont=dict(size=9, color='#111827', weight='bold'),
        showgrid=False,
        showline=False,
        ticks="",
        dtick=1
    )

    apply_layout_styles(fig)
    fig.update_layout(
        margin=dict(l=120, r=50, t=10, b=10),
        showlegend=False
    )

    return fig


# ===================================================
# BIỂU ĐỒ 3: Xu hướng công nghệ mới theo thời gian (Multi-line)
# Trả lời câu hỏi 3
# ===================================================
def create_tech_trend_chart(df):
    """
    Vẽ biểu đồ đa đường thể hiện xu hướng tăng trưởng của các nhóm
    công nghệ mới (AI/ML, Cloud, DevOps, Data Engineering) theo thời gian.
    Mỗi điểm trên trục X là 1 tháng, trục Y là số lượng tin tuyển dụng
    có yêu cầu ít nhất 1 kỹ năng thuộc nhóm đó.
    """
    if df.empty or 'thang_dang' not in df.columns or 'ky_nang' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Không có dữ liệu xu hướng",
            showarrow=False,
            font=dict(size=12, color="#9ca3af")
        )
        apply_layout_styles(fig)
        return fig

    # Chỉ lấy từ 2024 trở đi để xu hướng rõ ràng hơn
    trend_df = df.dropna(subset=['thang_dang', 'ky_nang']).copy()
    trend_df = trend_df[trend_df['thang_dang'] >= '2024-01']

    if trend_df.empty:
        trend_df = df.dropna(subset=['thang_dang', 'ky_nang']).copy()

    # Lấy danh sách tháng duy nhất, sắp xếp
    all_months = sorted(trend_df['thang_dang'].unique())

    if len(all_months) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Không đủ dữ liệu thời gian", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    fig = go.Figure()

    for group_name, keywords in EMERGING_TECH_GROUPS.items():
        color = EMERGING_COLORS[group_name]

        # Với mỗi tháng, đếm số tin có chứa ít nhất 1 kỹ năng trong nhóm
        monthly_counts = []
        for month in all_months:
            month_df = trend_df[trend_df['thang_dang'] == month]
            # Tạo regex pattern khớp bất kỳ kỹ năng nào trong nhóm
            pattern = '|'.join([rf'(?<![a-zA-Z]){kw}(?![a-zA-Z])' for kw in keywords])
            count = month_df['ky_nang'].str.contains(pattern, case=False, regex=True, na=False).sum()
            monthly_counts.append(int(count))

        # Tính trung bình trượt 3 tháng để làm mịn đường
        monthly_series = pd.Series(monthly_counts)
        moving_avg = monthly_series.rolling(window=3, min_periods=1).mean()

        # Vẽ đường chính (nét liền)
        fig.add_trace(go.Scatter(
            x=all_months,
            y=monthly_counts,
            mode='lines',
            name=group_name,
            line=dict(color=color, width=2),
            opacity=0.4, # Make it slightly lighter (opacity 0.4 instead of 0.6) to differentiate more clearly
            showlegend=True,
            hovertemplate=f"<b>{group_name} (Thực tế)</b><br>%{{x}}: <b>%{{y:,}} tin</b><extra></extra>"
        ))

        # Vẽ đường trung bình trượt (nét liền đậm hơn)
        fig.add_trace(go.Scatter(
            x=all_months,
            y=moving_avg.round(1).tolist(),
            mode='lines',
            name=f'{group_name} (TB trượt)',
            line=dict(color=color, width=3), # Make it slightly thicker (width 3 instead of 2.5) to stand out
            showlegend=False,
            hovertemplate=f"<b>{group_name} (Trung bình 3 tháng)</b><br>%{{x}}: <b>%{{y:,.1f}} tin</b><extra></extra>"
        ))

    fig.update_xaxes(
        showgrid=False,
        linecolor='#e5e7eb',
        tickangle=-30,
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Thời gian đăng tuyển",
        title_font=dict(size=10, color='#4b5563', weight='bold')
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Số lượng tin tuyển dụng",
        title_font=dict(size=10, color='#4b5563', weight='bold'),
        rangemode='tozero'
    )

    apply_layout_styles(fig)
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=40, r=10, t=10, b=35),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            bgcolor="rgba(255, 255, 255, 0)",
            borderwidth=0,
            font=dict(size=10, color='#374151')
        )
    )

    return fig


# ===================================================
# KPI SPARKLINE: Tái sử dụng từ charts_page1
# ===================================================
def create_sparkline(data, color="#59B292"):
    """
    Tạo sparkline (biểu đồ đường mini không trục tọa độ) hiển thị
    bên trong các thẻ KPI để minh họa xu hướng theo thời gian.
    """
    if data is None or len(data) == 0:
        fig = go.Figure()
    else:
        fig = go.Figure(go.Scatter(
            x=list(range(len(data))),
            y=data,
            mode='lines',
            line=dict(color=color, width=2, shape='spline', smoothing=1.3),
            hoverinfo='skip'
        ))

        # Hiệu ứng tô màu mờ phía dưới đường vẽ
        hex_color = color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        fig.add_trace(go.Scatter(
            x=list(range(len(data))),
            y=data,
            mode='none',
            fill='tozeroy',
            fillcolor=f"rgba({r},{g},{b},0.1)",
            hoverinfo='skip'
        ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=40,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True)
    )
    return fig
