# Nhập các thư viện cần thiết cho tính toán và vẽ biểu đồ Plotly
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json

from backend.utils.charts_common import PROVINCE_COORDINATES, REGION_COLORS, apply_layout_styles


# Vẽ biểu đồ đường xu hướng tuyển dụng theo thời gian và trung bình trượt 3 tháng
def create_time_trend_chart(df):
    trend_df = df.dropna(subset=['thang_dang']).copy()

    if trend_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu thời gian", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    # Group dữ liệu theo tháng và đếm số lượng tin tuyển dụng
    trend_data = trend_df.groupby('thang_dang').size().reset_index(name='job_count')
    trend_data['thang_dang_dt'] = pd.to_datetime(trend_data['thang_dang'] + '-01', format='%Y-%m-%d')
    trend_data = trend_data.sort_values('thang_dang_dt')
    # Tính đường trung bình trượt 3 tháng để làm mịn đường xu hướng
    trend_data['moving_avg'] = trend_data['job_count'].rolling(window=3, min_periods=1).mean()

    fig = go.Figure()

    # Đường vẽ trung bình trượt nét đứt
    fig.add_trace(go.Scatter(
        x=trend_data['thang_dang'],
        y=trend_data['moving_avg'],
        mode='lines',
        name='Trung bình trượt',
        line=dict(color='#9ca3af', width=2, dash='dash'),
        hovertemplate="<b>%{y:,.0f}</b> tin<extra></extra>"
    ))

    # Đường xu hướng tuyển dụng chính nét liền xanh
    fig.add_trace(go.Scatter(
        x=trend_data['thang_dang'],
        y=trend_data['job_count'],
        mode='lines',
        name='Tin tuyển dụng',
        line=dict(color='#59B292', width=2.5),
        hovertemplate="<b>%{y:,.0f}</b> tin<extra></extra>"
    ))

    # Đánh dấu chấm tròn và chú thích tại tháng có số lượng tuyển dụng cao nhất
    if not trend_data.empty:
        peak_idx = trend_data['job_count'].idxmax()
        peak_row = trend_data.loc[peak_idx]
        peak_month = peak_row['thang_dang']
        peak_count = peak_row['job_count']

        fig.add_trace(go.Scatter(
            x=[peak_month],
            y=[peak_count],
            mode='markers',
            name='Tháng cao điểm',
            marker=dict(size=8, color='#FA6781', symbol='circle', line=dict(width=1.5, color='#ffffff')),
            hoverinfo='skip'
        ))

        fig.add_annotation(
            x=peak_month,
            y=peak_count,
            text=f"Đỉnh: {peak_count:,} tin",
            showarrow=True,
            arrowhead=0,
            ax=0,
            ay=-18,
            font=dict(size=9, color='#FA6781', weight='bold'),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#FA6781",
            borderwidth=1,
            borderpad=2
        )

    fig.update_xaxes(
        showgrid=False,
        linecolor='#e5e7eb',
        tickangle=-30,
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Thời gian đăng tuyển",
        title_font=dict(size=10, color='#4b5563', weight='bold'),
        tickformat="T%-m/%Y",
        hoverformat="<span style='color:#59B292'>▍</span> T%-m/%Y"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Số lượng tin tuyển dụng",
        title_font=dict(size=10, color='#4b5563', weight='bold'),
        range=[0, max(800, peak_count * 1.6)] if not trend_data.empty else None
    )

    apply_layout_styles(fig)
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=40, r=10, t=25, b=35),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0)",
            bordercolor="rgba(255, 255, 255, 0)",
            borderwidth=0,
            font=dict(size=9, color='#4b5563')
        )
    )
    return fig


# Danh sách ánh xạ tên tỉnh thành sang thuộc tính Name tương ứng trong GeoJSON
PROVINCE_NAME_MAPPING = {
    'TP.HCM': 'Ho Chi Minh City',
    'Hà Nội': 'Ha Noi City',
    'Đà Nẵng': 'Da Nang City',
    'Hải Phòng': 'Hai Phong City',
    'Cần Thơ': 'Can Tho City',
    'Đồng Nai': 'Dong Nai Province',
    'Đắk Lắk': 'Dak Lak Province',
    'Thừa Thiên Huế': 'Thua Thien Hue Province',
    'Hưng Yên': 'Hung Yen Province',
    'Bà Rịa - Vũng Tàu': 'Ba Ria - Vung Tau Province',
    'Bình Dương': 'Binh Duong Province',
    'Bắc Ninh': 'Bac Ninh Province',
    'Thái Nguyên': 'Thai Nguyen Province',
    'Khánh Hòa': 'Khanh Hoa Province',
    'Quảng Ninh': 'Quang Ninh Province',
    'Lâm Đồng': 'Lam Dong Province',
    'Nghệ An': 'Nghe An Province'
}


# Tạo bản đồ phân bố tin tuyển dụng dạng bản đồ nhiệt theo tỉnh thành sử dụng file GeoJSON
def create_vietnam_map(df):
    city_counts = df['tinh_thanh'].value_counts().reset_index(name='job_count')
    city_counts = city_counts[~city_counts['tinh_thanh'].isin(['Khác', 'Từ xa / Remote'])]

    if city_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu tỉnh thành", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    city_counts['geojson_name'] = city_counts['tinh_thanh'].apply(
        lambda x: PROVINCE_NAME_MAPPING.get(x, x)
    )

    # Đọc dữ liệu GeoJSON chứa ranh giới các tỉnh/thành Việt Nam
    geojson_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'geo', 'vietnam_provinces.geojson')
    with open(geojson_path, 'r', encoding='utf-8') as f:
        vn_geojson = json.load(f)

    # Thêm các tỉnh không có dữ liệu vào dataframe với số lượng = 0 để bản đồ hiển thị đủ hình dáng chữ S
    all_provinces = [feature['properties']['Name'] for feature in vn_geojson['features']]
    existing_provinces = city_counts['geojson_name'].tolist()
    missing_provinces = set(all_provinces) - set(existing_provinces)
    
    if missing_provinces:
        missing_df = pd.DataFrame({
            'tinh_thanh': list(missing_provinces),
            'job_count': [0] * len(missing_provinces),
            'geojson_name': list(missing_provinces)
        })
        city_counts = pd.concat([city_counts, missing_df], ignore_index=True)

    # Bảng màu custom: 0 = Xám/Be, sau đó chuyển từ xanh nhạt sang xanh lục đậm
    custom_colorscale = [
        [0.0, "#eae5db"],   # 0 jobs (Beige/Gray)
        [0.01, "#a7f3d0"],  # Rất ít jobs
        [0.5, "#59B292"],   # Trung bình
        [1.0, "#064e3b"]    # Rất nhiều jobs
    ]

    # Vẽ bản đồ phân bố bằng Plotly choropleth_map
    fig = px.choropleth_map(
        city_counts,
        geojson=vn_geojson,
        featureidkey="properties.Name",
        locations="geojson_name",
        color="job_count",
        color_continuous_scale=custom_colorscale,
        hover_name="tinh_thanh",
        hover_data={"geojson_name": False, "job_count": True},
        labels={'job_count': 'Số lượng tin'},
        center={"lat": 16.2, "lon": 107.5},
        zoom=4.5,
        map_style="carto-positron"
    )

    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="white",
        hovertemplate=" &nbsp;<b><span style='color:#59B292'>▍</span> %{hovertext}</b>&nbsp; <br><span style='font-size:4px'> </span><br><span style='color:#5a4000'> &nbsp;Nhu cầu tuyển dụng: <b>%{z:,} tin</b>&nbsp; </span><extra></extra>"
    )

    apply_layout_styles(fig)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title="",
            thicknessmode="pixels", thickness=15,
            lenmode="pixels", len=150,
            yanchor="bottom", y=0.02,
            xanchor="left", x=0.02,
            tickfont=dict(size=9, color="#4b5563")
        )
    )
    return fig


# Tạo bản đồ phân bố màu sắc đại diện cho nhu cầu tuyển dụng các vùng miền
def create_regional_vietnam_map(df):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu vùng miền", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    region_totals = df['vung_mien'].value_counts().to_dict()

    map_data = []
    unique_cities = df['tinh_thanh'].unique()
    for city in unique_cities:
        if city in ['Khác', 'Từ xa / Remote']:
            continue
        region = df[df['tinh_thanh'] == city]['vung_mien'].iloc[0]
        count = region_totals.get(region, 0)
        geojson_name = PROVINCE_NAME_MAPPING.get(city, city)
        map_data.append({
            'tinh_thanh': city,
            'geojson_name': geojson_name,
            'Vùng miền': region,
            'Tổng tin vùng': count
        })

    map_df = pd.DataFrame(map_data)

    if map_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu vùng miền", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    geojson_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'geo', 'vietnam_provinces.geojson')
    with open(geojson_path, 'r', encoding='utf-8') as f:
        vn_geojson = json.load(f)

    fig = px.choropleth_map(
        map_df,
        geojson=vn_geojson,
        featureidkey="properties.Name",
        locations="geojson_name",
        color="Vùng miền",
        color_discrete_map=REGION_COLORS,
        hover_name="Vùng miền",
        hover_data={"geojson_name": False, "Vùng miền": False, "tinh_thanh": True, "Tổng tin vùng": True},
        center={"lat": 16.2, "lon": 107.5},
        zoom=4.5,
        map_style="carto-positron"
    )

    region_text_colors = {
        'Bắc': '#881337',
        'Nam': '#064e3b',
        'Trung': '#78350f',
        'Từ xa / Remote': '#115e59',
        'Khác': '#374151'
    }
    
    # Tạo danh sách text hover với định dạng màu sắc tiêu đề theo vùng miền
    hover_texts = []
    for idx, row in map_df.iterrows():
        r = row['Vùng miền']
        t_color = region_text_colors.get(r, '#374151')
        hover_texts.append(
            f"<span style='font-size:4px'> </span><br>"
            f" &nbsp;<b><span style='color:{t_color}'>▍</span> Vùng {r}</b>&nbsp; <br>"
            f"<span style='font-size:4px'> </span><br>"
            f" &nbsp;Tỉnh: <b>{row['tinh_thanh']}</b>&nbsp; <br>"
            f" &nbsp;Tổng tin vùng: <b>{row['Tổng tin vùng']:,} tin</b>&nbsp; <br>"
            f"<span style='font-size:4px'> </span>"
        )
    map_df['hover_text'] = hover_texts

    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="white",
        hovertemplate="%{customdata[2]}<extra></extra>",
        customdata=np.stack((map_df['tinh_thanh'], map_df['Tổng tin vùng'], map_df['hover_text']), axis=-1),
        hoverlabel=dict(
            font=dict(color='#1a1a1a')
        )
    )

    apply_layout_styles(fig)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            yanchor="bottom",
            y=0.02,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#e5e7eb",
            borderwidth=1,
            title_font=dict(size=10, weight='bold'),
            font=dict(size=9),
            orientation="v"
        ),
        showlegend=True
    )

    return fig


# Vẽ biểu đồ cột ngang thể hiện tỷ trọng và số lượng tin của từng hình thức làm việc
def create_work_type_chart(df):
    work_counts = df['hinh_thuc_lam_viec'].value_counts().reset_index(name='count')

    if work_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu hình thức", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    total_work = work_counts['count'].sum()
    work_counts['pct'] = (work_counts['count'] / total_work) * 100
    work_counts = work_counts.sort_values('count', ascending=True)

    y_labels = [row['hinh_thuc_lam_viec'] for _, row in work_counts.iterrows()]

    fig = go.Figure(data=[go.Bar(
        x=work_counts['count'],
        y=y_labels,
        orientation='h',
        text=[f"{row['count']:,}" for _, row in work_counts.iterrows()],
        textposition='outside',
        cliponaxis=False,
        marker=dict(
            color='#59B292',
            line=dict(width=0)
        ),
        hovertext=[f"<span style='font-size:4px'> </span><br> &nbsp;<b><span style='color:#59B292'>▍</span> {row['hinh_thuc_lam_viec']}</b>&nbsp; <br><span style='font-size:4px'> </span><br><span style='color:#5a4000'> &nbsp;Số lượng: <b>{row['count']:,} tin</b>&nbsp; <br> &nbsp;Tỉ lệ: <b>{row['pct']:.1f}%</b>&nbsp; </span><br><span style='font-size:4px'> </span>" for _, row in work_counts.iterrows()],
        hovertemplate="%{hovertext}<extra></extra>"
    )])

    max_count = work_counts['count'].max()
    fig.update_xaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        range=[0, max_count * 1.12] if not pd.isna(max_count) else None,
        title_text="Số lượng tin tuyển dụng",
        title_font=dict(size=10, color='#4b5563', weight='bold')
    )

    fig.update_yaxes(
        showgrid=False,
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#111827', weight='bold')
    )

    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=20))

    return fig


# Vẽ biểu đồ cột ngang thể hiện phân bố tuyển dụng theo vùng miền
def create_region_chart(df):
    region_counts = df['vung_mien'].value_counts().reset_index(name='count')

    if region_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu vùng miền", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    total_region = region_counts['count'].sum()
    region_counts['pct'] = (region_counts['count'] / total_region) * 100
    region_counts = region_counts.sort_values('count', ascending=True)

    y_labels = [row['vung_mien'] for _, row in region_counts.iterrows()]

    region_text_colors = {
        'Bắc': '#881337',
        'Nam': '#064e3b',
        'Trung': '#78350f',
        'Từ xa / Remote': '#115e59',
        'Khác': '#374151'
    }
    colors = [REGION_COLORS.get(r, '#9ca3af') for r in region_counts['vung_mien']]

    fig = go.Figure(data=[go.Bar(
        x=region_counts['count'],
        y=y_labels,
        orientation='h',
        text=[f"{row['count']:,} | {row['pct']:.1f}%" for _, row in region_counts.iterrows()],
        textposition='outside',
        cliponaxis=False,
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        hovertext=[
            f"<span style='font-size:4px'> </span><br>"
            f" &nbsp;<b><span style='color:#59B292'>▍</span> Vùng {row['vung_mien']}</b>&nbsp; <br>"
            f"<span style='font-size:4px'> </span><br>"
            f"<span style='color:#5a4000'>"
            f" &nbsp;Số lượng: <b>{row['count']:,} tin</b>&nbsp; <br>"
            f" &nbsp;Tỉ lệ: <b>{row['pct']:.1f}%</b>&nbsp; "
            f"</span><br><span style='font-size:4px'> </span>"
            for _, row in region_counts.reset_index(drop=True).iterrows()
        ],
        hovertemplate="%{hovertext}<extra></extra>",
        hoverlabel=dict(
            font=dict(color='#1a1a1a')
        )
    )])

    fig.update_xaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563')
    )

    fig.update_yaxes(
        showgrid=False,
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#111827', weight='bold')
    )

    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=20))

    return fig


# Vẽ biểu đồ cột dọc thể hiện số lượng và phần trăm nhu cầu tuyển dụng theo vùng miền
# Được dùng thay thế cho bản đồ khi bật toggle "Theo vùng"
def create_region_vertical_chart(df):
    region_counts = df['vung_mien'].value_counts().reset_index(name='count')

    if region_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu vùng miền", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    total_region = region_counts['count'].sum()
    region_counts['pct'] = (region_counts['count'] / total_region) * 100
    region_counts = region_counts.sort_values('count', ascending=False)

    region_text_colors = {
        'Bắc': '#881337',
        'Nam': '#064e3b',
        'Trung': '#78350f',
        'Từ xa / Remote': '#115e59',
        'Khác': '#374151'
    }
    colors = [REGION_COLORS.get(r, '#9ca3af') for r in region_counts['vung_mien']]

    fig = go.Figure(data=[go.Bar(
        x=region_counts['vung_mien'],
        y=region_counts['count'],
        orientation='v',
        text=[f"{row['count']:,}" for _, row in region_counts.iterrows()],
        textposition='outside',
        cliponaxis=False,
        textfont=dict(size=10),
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        hovertext=[
            f"<span style='font-size:4px'> </span><br>"
            f" &nbsp;<b><span style='color:#59B292'>▍</span> Vùng {row['vung_mien']}</b>&nbsp; <br>"
            f"<span style='font-size:4px'> </span><br>"
            f"<span style='color:#5a4000'>"
            f" &nbsp;Số lượng: <b>{row['count']:,} tin</b>&nbsp; <br>"
            f" &nbsp;Tỉ lệ: <b>{row['pct']:.1f}%</b>&nbsp; "
            f"</span><br><span style='font-size:4px'> </span>"
            for _, row in region_counts.reset_index(drop=True).iterrows()
        ],
        hovertemplate="%{hovertext}<extra></extra>",
        hoverlabel=dict(
            font=dict(color='#1a1a1a')
        )
    )])

    fig.update_xaxes(
        showgrid=False,
        linecolor='#e5e7eb',
        tickfont=dict(size=11, color='#111827')
    )
    import pandas as pd
    max_count = region_counts['count'].max()

    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        title_text="Số lượng tin",
        title_font=dict(size=10, color='#6b7280'),
        range=[0, max_count * 1.15] if not pd.isna(max_count) else None
    )

    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=40, r=20, t=40, b=10), bargap=0.3)

    return fig


# Vẽ biểu đồ cột ngang biểu diễn Top 15 tỉnh thành tuyển dụng nhiều nhất (ngoài Khác/Remote)
def create_provincial_bar_chart(df):
    city_counts = df['tinh_thanh'].value_counts().reset_index(name='count')
    city_counts = city_counts[~city_counts['tinh_thanh'].isin(['Khác', 'Từ xa / Remote'])]

    if city_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu tỉnh thành", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    city_counts = city_counts.head(15).sort_values('count', ascending=True)

    colors = []
    for city in city_counts['tinh_thanh']:
        sample_row = df[df['tinh_thanh'] == city]
        region = sample_row['vung_mien'].iloc[0] if not sample_row.empty else 'Khác'
        colors.append(REGION_COLORS.get(region, '#9ca3af'))

    fig = go.Figure(data=[go.Bar(
        x=city_counts['count'],
        y=city_counts['tinh_thanh'],
        orientation='h',
        text=[f"{count:,}" for count in city_counts['count']],
        textposition='outside',
        cliponaxis=False,
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<span style='font-size:4px'> </span><br> &nbsp;<b>%{y}</b>&nbsp; <br><span style='font-size:4px'> </span><br><span style='color:#5a4000'> &nbsp;Số lượng: <b>%{x:,} tin</b>&nbsp; </span><br><span style='font-size:4px'> </span><extra></extra>"
    )])

    fig.update_xaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563')
    )
    fig.update_yaxes(
        showgrid=False,
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#111827', weight='bold')
    )

    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=20))

    return fig


# Tạo sparkline (biểu đồ đường mini không trục tọa độ) hiển thị bên trong các thẻ KPI
def create_sparkline(data, color="#294669"):
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

        # Thêm hiệu ứng tô màu mờ phía dưới đường vẽ
        fig.add_trace(go.Scatter(
            x=list(range(len(data))),
            y=data,
            mode='none',
            fill='tozeroy',
            fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
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
