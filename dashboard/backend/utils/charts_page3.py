"""
Charts utilities cho Trang 3: Phân tích mức lương thị trường IT Việt Nam.
Chứa các hàm tạo biểu đồ Plotly phục vụ phân tích lương.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from backend.utils.charts_common import apply_layout_styles, REGION_COLORS


# ============================================================================
# Bảng màu riêng cho Page 3 (Salary theme)
# ============================================================================
SALARY_COLORS = {
    'primary': '#59B292',       # Sage Green (Theme chính)
    'secondary': '#469d7e',     # Darker Sage
    'accent': '#FA6781',        # Coral Red (cho Median)
    'gradient_low': '#59B292',  
    'gradient_mid': '#FFC94D',  
    'gradient_high': '#FFC94D', # Amber Gold (cho Mean)
}

# Bảng màu cho từng cấp độ kinh nghiệm
EXPERIENCE_COLORS = {
    'Intern': '#94a3b8',
    'Fresher': '#60a5fa',
    'Junior': '#34d399',
    'Middle': '#fbbf24',
    'Senior': '#f87171',
    'Không rõ': '#d1d5db',
}

# Thứ tự hiển thị kinh nghiệm
EXPERIENCE_ORDER = ['Intern', 'Fresher', 'Junior', 'Middle', 'Senior', 'Không rõ']


def create_sparkline(data, color="#FAE7CB"):
    """
    Tạo biểu đồ sparkline nhỏ để hiển thị trend bên dưới KPI.
    Reuse pattern từ Page 1/2.
    """
    fig = go.Figure()

    if data and len(data) > 0:
        fig.add_trace(go.Scatter(
            y=data,
            mode='lines',
            fill='tozeroy',
            line=dict(color=color, width=2, shape='spline'),
            fillcolor=f'rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},0.15)',
            hoverinfo='skip',
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=40,
        showlegend=False,
    )
    return fig


def create_salary_distribution_chart(dff):
    """
    Biểu đồ 1: Histogram phân bố mức lương trung bình.
    Trả lời: Mức lương TB phân bố như thế nào?
    """
    fig = go.Figure()

    # Lọc chỉ các tin có dữ liệu lương
    salary_df = dff.dropna(subset=['luong_tb'])

    if salary_df.empty:
        fig.add_annotation(
            text="Không có dữ liệu lương để hiển thị",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#9ca3af")
        )
        apply_layout_styles(fig)
        fig.update_layout(height=350)
        return fig

    median_val = float(salary_df['luong_tb'].median())
    mean_val = float(salary_df['luong_tb'].mean())

    # Tạo histogram
    fig.add_trace(go.Histogram(
        x=salary_df['luong_tb'],
        xbins=dict(start=0, end=salary_df['luong_tb'].quantile(0.98) + 5, size=5),
        marker=dict(
            color=SALARY_COLORS['primary'],
            line=dict(color='white', width=1),
            opacity=0.85,
        ),
        hovertemplate=(
            '<b>Khoảng lương:</b> %{x} triệu<br>'
            '<b>Số tin tuyển dụng:</b> %{y}<extra></extra>'
        ),
        showlegend=False,
    ))

    # --- Thêm mini Donut chart (Inset) thể hiện tỷ lệ công khai lương ---
    total_jobs = len(dff)
    with_salary = len(salary_df)
    without_salary = total_jobs - with_salary

    if total_jobs > 0:
        fig.add_trace(go.Pie(
            labels=['Công khai lương', 'Không công khai'],
            values=[with_salary, without_salary],
            domain=dict(x=[0.75, 0.95], y=[0.65, 0.95]),  # Thu nhỏ hơn nữa, đẩy lên góc
            hole=0.7,
            marker=dict(colors=[SALARY_COLORS['primary'], '#e5e7eb']), # Màu đồng bộ với dashboard, phần còn lại xám nhạt
            textinfo='none',
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value} tin<br>Tỷ lệ: %{percent}<extra></extra>',
            showlegend=False,
        ))
        
        pct = (with_salary / total_jobs * 100)
        fig.add_annotation(
            text=f"<b>{pct:.1f}%</b><br><span style='font-size:9px'>Công khai</span>",
            x=0.85, y=0.8, # Tâm mới của domain
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=11, color=SALARY_COLORS['primary']),
            xanchor="center", yanchor="middle"
        )

    # Dummy traces cho Legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='lines',
        line=dict(color=SALARY_COLORS['accent'], width=2, dash='dash'),
        name=f"Median: {median_val:.1f}tr"
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='lines',
        line=dict(color=SALARY_COLORS['gradient_high'], width=2, dash='dot'),
        name=f"Trung bình: {mean_val:.1f}tr"
    ))

    # Đường thực tế trên biểu đồ
    fig.add_vline(x=median_val, line=dict(color=SALARY_COLORS['accent'], width=2, dash='dash'))
    fig.add_vline(x=mean_val, line=dict(color=SALARY_COLORS['gradient_high'], width=2, dash='dot'))

    apply_layout_styles(fig)
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
            bgcolor='rgba(0,0,0,0)',
        ),
        xaxis=dict(
            title=dict(text="Mức lương trung bình (triệu VNĐ)", font=dict(size=10, color='#4b5563', weight='bold')),
            tickfont=dict(size=9, color='#4b5563'),
            gridcolor='rgba(0,0,0,0.05)',
            tick0=10,
            dtick=10,
        ),
        yaxis=dict(
            title=dict(text="Số tin tuyển dụng", font=dict(size=10, color='#4b5563', weight='bold')),
            tickfont=dict(size=9, color='#4b5563'),
            gridcolor='rgba(0,0,0,0.05)',
        ),
        bargap=0.05,
    )
    return fig


def create_salary_by_position_experience_chart(dff):
    """
    Biểu đồ 2: Heatmap - Lương TB theo Nhóm vị trí & Kinh nghiệm.
    Trả lời: Mức lương chênh lệch giữa các nhóm vị trí và kinh nghiệm?
    """
    fig = go.Figure()

    salary_df = dff.dropna(subset=['luong_tb', 'nhom_vi_tri', 'cap_do_kinh_nghiem'])

    if salary_df.empty:
        fig.add_annotation(
            text="Không có dữ liệu lương để hiển thị",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#9ca3af")
        )
        apply_layout_styles(fig)
        fig.update_layout(height=400)
        return fig

    # Lọc ra 8 vị trí có số lượng tin nhiều nhất để tránh quá dài
    top_positions = salary_df['nhom_vi_tri'].value_counts().nlargest(8).index.tolist()
    salary_df = salary_df[salary_df['nhom_vi_tri'].isin(top_positions)]

    # Tính mean và count
    pivot = salary_df.groupby(['nhom_vi_tri', 'cap_do_kinh_nghiem']).agg(
        avg_salary=('luong_tb', 'mean'),
        count=('luong_tb', 'count')
    ).reset_index()

    # Trục ngang: theo thứ tự user yêu cầu
    exp_order = ['Intern', 'Fresher', 'Junior', 'Middle', 'Senior']

    # Trục dọc: sắp xếp theo mức lương trung bình chung của các vị trí đó (tăng dần để vị trí cao nhất lên trên do plotly vẽ từ dưới lên)
    pos_order = pivot.groupby('nhom_vi_tri')['avg_salary'].mean().sort_values(ascending=True).index.tolist()

    z_values = []
    text_values = []
    hover_text = []

    for pos in pos_order:
        z_row = []
        text_row = []
        hover_row = []
        for exp in exp_order:
            row_data = pivot[(pivot['nhom_vi_tri'] == pos) & (pivot['cap_do_kinh_nghiem'] == exp)]
            if not row_data.empty:
                val = float(row_data['avg_salary'].iloc[0])
                cnt = int(row_data['count'].iloc[0])
                z_row.append(val)
                text_row.append(f"{val:.1f}")
                hover_row.append(f"<b>{pos}</b><br>Kinh nghiệm: {exp}<br>Lương TB: {val:.1f}tr<br>Số tin: {cnt}")
            else:
                z_row.append(None)
                text_row.append("-")
                hover_row.append(f"<b>{pos}</b><br>Kinh nghiệm: {exp}<br>Chưa có dữ liệu")
        z_values.append(z_row)
        text_values.append(text_row)
        hover_text.append(hover_row)

    # Rút gọn tên nhóm vị trí cho gọn gàng (không bị cảm giác gom nhóm quá nhiều)
    short_pos_map = {
        'Software Development': 'Software Dev',
        'AI / ML / Data Science': 'AI / ML',
        'Mobile / Game / Embedded': 'Mobile / Game',
        'Cloud / DevOps / SRE': 'Cloud / DevOps',
        'QA / Testing': 'QA / Testing',
        'Data Engineering / Database': 'Data Engineering',
        'Product / Business / UX': 'Product / UX',
        'Management / Architecture': 'Management'
    }

    # Custom colorscale dùng theme màu giống Page 2
    custom_colorscale = [
        [0.0, "#f8f5f0"],
        [0.1, "#d4ede3"],
        [0.4, "#7ec8a7"],
        [0.7, "#59B292"],
        [1.0, "#1a5944"],
    ]

    # Tính min, max để xác định ô nào xanh đậm thì dùng chữ trắng nổi bật (dùng HTML span trong text)
    valid_z = [v for row in z_values for v in row if v is not None]
    z_min = min(valid_z) if valid_z else 0
    z_max = max(valid_z) if valid_z else 1
    z_span = (z_max - z_min) or 1.0

    formatted_text_matrix = []
    for z_row in z_values:
        f_row = []
        for val in z_row:
            if val is None:
                f_row.append("-")
            else:
                c = "#ffffff" if (val - z_min) / z_span > 0.5 else "#111827"
                f_row.append(f"<span style='color:{c}'>{val:.1f}</span>")
        formatted_text_matrix.append(f_row)

    # Map lại pos_order sang tên ngắn gọn
    display_pos_order = [short_pos_map.get(pos, pos) for pos in pos_order]

    fig.add_trace(go.Heatmap(
        z=z_values,
        x=exp_order,
        y=display_pos_order,
        text=formatted_text_matrix,
        texttemplate="%{text}",
        textfont=dict(size=9.5),
        hoverinfo="text",
        hovertext=hover_text,
        colorscale=custom_colorscale,
        showscale=True,
        colorbar=dict(
            thickness=10,
            len=0.7,
            tickfont=dict(size=9, color='#4b5563'),
            outlinewidth=0
        ),
        xgap=2,
        ygap=2,
    ))

    apply_layout_styles(fig)
    fig.update_xaxes(showline=False, ticks="")
    fig.update_yaxes(showline=False, ticks="")
    fig.update_layout(
        height=400,
        xaxis=dict(
            title=dict(text="Cấp độ kinh nghiệm", font=dict(size=10, color='#4b5563', weight='bold')),
            side="bottom",
            tickfont=dict(size=9, color='#111827', weight='bold') # Size 9 giống Page 2
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=9, color='#111827', weight='bold'), # Size 9 giống Page 2
            autorange="reversed", # Để hiển thị từ trên xuống dưới
        ),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def create_salary_by_location_chart(dff):
    """
    Biểu đồ 3: Horizontal Bar chart - Lương TB theo Thành phố & Hình thức làm việc.
    Trả lời: Chênh lệch lương giữa HN/HCM/ĐN và Remote?
    """
    fig = go.Figure()

    salary_df = dff.dropna(subset=['luong_tb'])

    if salary_df.empty:
        fig.add_annotation(
            text="Không có dữ liệu lương để hiển thị",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#9ca3af")
        )
        apply_layout_styles(fig)
        fig.update_layout(height=400)
        return fig

    # Định nghĩa các thành phố và Remote cần lấy
    target_locations = ['TP.HCM', 'Hà Nội', 'Đà Nẵng']
    
    # Lấy dữ liệu 3 thành phố
    city_df = salary_df[salary_df['tinh_thanh'].isin(target_locations)]
    
    # Lấy dữ liệu Remote (từ tinh_thanh hoặc vung_mien)
    remote_df = salary_df[
        salary_df['tinh_thanh'].str.contains('Remote|Từ xa', case=False, na=False) |
        salary_df['vung_mien'].str.contains('Remote|Từ xa', case=False, na=False)
    ]
    
    # Gom lại
    combined_df = pd.concat([city_df, remote_df]).drop_duplicates()
    
    # Xử lý đổi tên Remote cho thống nhất (bỏ icon ngôi nhà và chữ Từ xa)
    def map_location(loc):
        if pd.isna(loc):
            return loc
        if 'Remote' in loc or 'Từ xa' in loc:
            return 'Từ xa / Remote'
        return loc

    combined_df['location_group'] = combined_df['tinh_thanh'].apply(map_location)
    
    # Tính mean và count
    city_salary = (
        combined_df.groupby('location_group')['luong_tb']
        .agg(['mean', 'count'])
        .reset_index()
    )
    city_salary.columns = ['location', 'avg_salary', 'count']

    # Sắp xếp từ cao xuống thấp. Plotly vẽ từ trên xuống nếu yaxis autorange="reversed"
    city_salary['avg_salary'] = city_salary['avg_salary'].round(1)
    city_salary = city_salary.sort_values('avg_salary', ascending=False)

    # Tính lương trung bình toàn ngành
    global_avg = salary_df['luong_tb'].mean()

    # Map vùng miền cho từng thành phố để tô màu
    city_region_map = salary_df.groupby('tinh_thanh')['vung_mien'].first().to_dict()

    colors = []
    for loc in city_salary['location']:
        if 'Remote' in str(loc):
            colors.append(REGION_COLORS.get('Từ xa / Remote', '#3B82F6'))
        else:
            region = city_region_map.get(loc, 'Khác')
            colors.append(REGION_COLORS.get(region, '#9ca3af'))

    # Không bôi đậm text trên cột
    text_vals = [f"{v:.1f}tr ({c} tin)" for v, c in zip(city_salary['avg_salary'], city_salary['count'])]
    
    # Không bôi đậm nhãn trục y
    y_labels = city_salary['location']

    fig.add_trace(go.Bar(
        y=y_labels,
        x=city_salary['avg_salary'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0),
            opacity=0.9,
        ),
        text=text_vals,
        textposition='outside',
        textfont=dict(size=9.5, color='#1e293b'),
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Lương TB: %{x:.1f} triệu VNĐ<extra></extra>'
        ),
        cliponaxis=False,
    ))

    # Thêm đường lương trung bình toàn ngành (nằm lớp dưới 'below' để không cắt đè vào chữ)
    fig.add_vline(
        x=global_avg,
        line=dict(color='#ea580c', width=2, dash='dash'),
        layer="below"
    )
    
    # Text annotation nổi hẳn lên trên biểu đồ để không bị đè vào cột
    fig.add_annotation(
        x=global_avg,
        y=1.05,
        xref="x",
        yref="paper",
        text=f"TB toàn ngành: {global_avg:.1f}tr",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color='#ea580c', size=12, family="Inter")
    )

    apply_layout_styles(fig)
    fig.update_layout(
        height=400,
        xaxis=dict(
            title=dict(text="Lương trung bình (triệu VNĐ)", font=dict(size=11, color='#1e293b', weight='bold')),
            tickfont=dict(size=10, color='#374151', weight='bold'),
            showgrid=False,
            showline=True,
            linecolor='#cbd5e1',
            linewidth=1,
            zeroline=False,
            ticks="",
            range=[0, float(city_salary['avg_salary'].max()) * 1.35],
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11, color='#0f172a', weight='bold'),
            autorange="reversed", # Hiển thị từ trên xuống dưới
            showgrid=False,
            showline=False,
            ticks="",
        ),
        margin=dict(l=10, r=85, t=30, b=40),
    )
    return fig


def create_salary_box_chart(dff):
    """
    Biểu đồ 1B (toggle): Box Plot phân bố lương theo cấp độ kinh nghiệm.
    Cung cấp góc nhìn khác so với Histogram - thể hiện phân vị, median, outliers.
    """
    fig = go.Figure()

    salary_df = dff.dropna(subset=['luong_tb', 'cap_do_kinh_nghiem'])

    if salary_df.empty:
        fig.add_annotation(
            text="Không có dữ liệu lương để hiển thị",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="#9ca3af")
        )
        apply_layout_styles(fig)
        fig.update_layout(height=350)
        return fig

    # Vẽ box plot theo từng cấp kinh nghiệm
    for exp in EXPERIENCE_ORDER:
        exp_data = salary_df[salary_df['cap_do_kinh_nghiem'] == exp]
        if exp_data.empty:
            continue

        fig.add_trace(go.Box(
            y=exp_data['luong_tb'],
            name=exp,
            marker_color=EXPERIENCE_COLORS.get(exp, '#9ca3af'),
            boxmean='sd',
            line=dict(width=1.5),
            fillcolor=EXPERIENCE_COLORS.get(exp, '#9ca3af'),
            opacity=0.8,
            hovertemplate=(
                f'<b>{exp}</b><br>'
                'Lương: %{y:.1f} triệu<extra></extra>'
            ),
        ))

    apply_layout_styles(fig)
    fig.update_layout(
        height=350,
        showlegend=False,
        xaxis=dict(
            title=dict(text="Cấp độ kinh nghiệm", font=dict(size=10, color='#4b5563', weight='bold')),
            tickvals=EXPERIENCE_ORDER,
            ticktext=EXPERIENCE_ORDER,
            tickfont=dict(size=10, color='#111827', weight='bold'),
            gridcolor='rgba(0,0,0,0.05)',
        ),
        yaxis=dict(
            title=dict(text="Mức lương trung bình (triệu VNĐ)", font=dict(size=10, color='#4b5563', weight='bold')),
            tickfont=dict(size=9, color='#4b5563'),
            gridcolor='rgba(0,0,0,0.05)',
        ),
        boxmode='group',
        margin=dict(l=10, r=10, t=10, b=40),
    )
    return fig
