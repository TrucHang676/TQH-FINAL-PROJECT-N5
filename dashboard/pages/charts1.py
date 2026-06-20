import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Coordinates of Vietnam provinces/cities present in the dataset
# "Khác" and "Từ xa / Remote" are filtered out from coordinates as they are non-physical
PROVINCE_COORDINATES = {
    'TP.HCM': {'lat': 10.8231, 'lon': 106.6297},
    'Hà Nội': {'lat': 21.0285, 'lon': 105.8542},
    'Đà Nẵng': {'lat': 16.0544, 'lon': 108.2022},
    'Bắc Ninh': {'lat': 21.1861, 'lon': 106.0763},
    'Hải Phòng': {'lat': 20.8449, 'lon': 106.6881},
    'Thái Nguyên': {'lat': 21.5939, 'lon': 105.8442},
    'Khánh Hòa': {'lat': 12.2388, 'lon': 109.1967},
    'Đồng Nai': {'lat': 10.9574, 'lon': 106.8427},
    'Hưng Yên': {'lat': 20.6465, 'lon': 106.0511},
    'Thừa Thiên Huế': {'lat': 16.4633, 'lon': 107.5909},
    'Bà Rịa - Vũng Tàu': {'lat': 10.4113, 'lon': 107.1360},
    'Quảng Ninh': {'lat': 20.9599, 'lon': 107.0476},
    'Cần Thơ': {'lat': 10.0452, 'lon': 105.7469},
    'Lâm Đồng': {'lat': 11.9404, 'lon': 108.4583},
    'Nghệ An': {'lat': 19.1671, 'lon': 104.9126},
    'Đắk Lắk': {'lat': 12.6784, 'lon': 108.0383},
    'Bình Dương': {'lat': 10.9805, 'lon': 106.6518}
}

# Theme Colors
REGION_COLORS = {
    'Bắc': '#3b82f6',       # Royal Blue
    'Nam': '#10b981',       # Emerald Green
    'Trung': '#f59e0b',     # Amber Orange
    'Từ xa / Remote': '#06b6d4', # Teal
    'Khác': '#8b5cf6'       # Lavender Purple
}

WORK_TYPE_COLORS = {
    'Full-time': '#2563eb',   # Deep Blue
    'Internship': '#38bdf8',  # Sky Blue
    'Part-time': '#f59e0b',   # Amber
    'Contract': '#8b5cf6',    # Purple
    'Khác': '#94a3b8',        # Slate
    'Không rõ': '#cbd5e1'     # Light Slate
}

# Common layout styling helper
def apply_layout_styles(fig):
    fig.update_layout(
        font_family="Outfit, sans-serif",
        font_color="#0f172a",
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="closest",
        showlegend=False
    )
    return fig

def create_time_trend_chart(df):
    """
    Line chart showing the recruitment trend over time (months/years)
    """
    # Group by month and count jobs
    # Drop rows without dates
    trend_df = df.dropna(subset=['thang_dang']).copy()
    
    if trend_df.empty:
        # Return an empty figure with a placeholder message
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu thời gian", showarrow=False, font=dict(size=14, color="#94a3b8"))
        apply_layout_styles(fig)
        return fig
        
    trend_data = trend_df.groupby('thang_dang').size().reset_index(name='job_count')
    # Sort chronologically by thang_dang string 'YYYY-MM'
    trend_data = trend_data.sort_values('thang_dang')
    
    fig = go.Figure()
    
    # Area gradient under the line
    fig.add_trace(go.Scatter(
        x=trend_data['thang_dang'],
        y=trend_data['job_count'],
        mode='lines+markers',
        name='Số lượng việc làm',
        line=dict(color='#2563eb', width=3.5, shape='spline'),
        marker=dict(size=7, color='#2563eb', symbol='circle', line=dict(width=1.5, color='#ffffff')),
        fill='tozeroy',
        fillcolor='rgba(37, 99, 235, 0.08)',
        hoverinfo='text',
        hovertext=[f"<b>Tháng {row['thang_dang']}</b><br>Nhu cầu: {row['job_count']:,} tin tuyển dụng" for _, row in trend_data.iterrows()]
    ))
    
    fig.update_xaxes(
        showgrid=False,
        linecolor='#e2e8f0',
        tickangle=-30,
        tickfont=dict(size=10, color='#64748b'),
        title_font=dict(size=11, color='#64748b')
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e2e8f0',
        tickfont=dict(size=10, color='#64748b'),
        title_font=dict(size=11, color='#64748b')
    )
    
    apply_layout_styles(fig)
    # Adjust padding for line chart labels
    fig.update_layout(margin=dict(l=40, r=10, t=10, b=40))
    return fig

def create_vietnam_map(df):
    """
    Map of Vietnam using scatter_mapbox with open-street-map background
    """
    # Count jobs per province
    city_counts = df['tinh_thanh'].value_counts().reset_index(name='job_count')
    
    # Map coordinates
    map_data = []
    total_active_jobs = 0
    
    for _, row in city_counts.iterrows():
        city = row['tinh_thanh']
        count = row['job_count']
        if city in PROVINCE_COORDINATES:
            lat_lon = PROVINCE_COORDINATES[city]
            # Find the region corresponding to this province in the dataframe
            sample_row = df[df['tinh_thanh'] == city]
            region = sample_row['vung_mien'].iloc[0] if not sample_row.empty else 'Khác'
            
            map_data.append({
                'Tỉnh/Thành': city,
                'Vùng miền': region,
                'lat': lat_lon['lat'],
                'lon': lat_lon['lon'],
                'Số lượng tuyển dụng': count
            })
            total_active_jobs += count
            
    if not map_data:
        # Return an empty map figure
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu bản đồ phù hợp", showarrow=False, font=dict(size=14, color="#94a3b8"))
        apply_layout_styles(fig)
        return fig
        
    map_df = pd.DataFrame(map_data)
    
    # Calculate scale factor for bubbles based on max count
    max_count = map_df['Số lượng tuyển dụng'].max()
    # Ensure bubble sizes are visible but not overriding the map
    # We use a custom size scaling function: size = log(count) or sqrt(count)
    map_df['marker_size'] = map_df['Số lượng tuyển dụng'].apply(lambda x: 8 + (x / max_count) * 28)
    
    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="Số lượng tuyển dụng",
        color="Vùng miền",
        color_discrete_map=REGION_COLORS,
        hover_name="Tỉnh/Thành",
        hover_data={
            "lat": False,
            "lon": False,
            "Vùng miền": True,
            "Số lượng tuyển dụng": ":,f"
        },
        size_max=32,
        zoom=4.8,
        center={"lat": 16.2, "lon": 107.5}, # Center of Vietnam
        mapbox_style="open-street-map"
    )
    
    apply_layout_styles(fig)
    # Map styling overrides
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), # Map occupies the full card space
        legend=dict(
            yanchor="bottom",
            y=0.02,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            title_font=dict(size=11, weight='bold'),
            font=dict(size=10),
            orientation="v"
        ),
        showlegend=True
    )
    
    return fig

def create_work_type_chart(df):
    """
    Donut chart showing working form breakdown
    """
    work_counts = df['hinh_thuc_lam_viec'].value_counts().reset_index(name='count')
    
    if work_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu hình thức", showarrow=False, font=dict(size=14, color="#94a3b8"))
        apply_layout_styles(fig)
        return fig
        
    fig = go.Figure(data=[go.Pie(
        labels=work_counts['hinh_thuc_lam_viec'],
        values=work_counts['count'],
        hole=0.55,
        marker=dict(colors=[WORK_TYPE_COLORS.get(label, '#94a3b8') for label in work_counts['hinh_thuc_lam_viec']]),
        textinfo='percent',
        textfont=dict(size=10, color='#ffffff'),
        insidetextorientation='radial',
        hoverinfo='label+value+percent',
        hovertemplate="<b>%{label}</b><br>Số lượng: %{value:,}<br>Tỷ lệ: %{percent}<extra></extra>"
    )])
    
    apply_layout_styles(fig)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=9),
            traceorder="normal"
        ),
        margin=dict(l=10, r=10, t=10, b=30)
    )
    
    return fig

def create_region_chart(df):
    """
    Horizontal bar chart showing job distribution by region
    """
    region_counts = df['vung_mien'].value_counts().reset_index(name='count')
    
    if region_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu vùng miền", showarrow=False, font=dict(size=14, color="#94a3b8"))
        apply_layout_styles(fig)
        return fig
        
    # Sort from smallest to largest for horizontal bar order (plotly plots from bottom to top)
    region_counts = region_counts.sort_values('count', ascending=True)
    
    fig = go.Figure(data=[go.Bar(
        x=region_counts['count'],
        y=region_counts['vung_mien'],
        orientation='h',
        marker=dict(
            color=[REGION_COLORS.get(r, '#8b5cf6') for r in region_counts['vung_mien']],
            line=dict(width=0)
        ),
        hoverinfo='text',
        hovertext=[f"<b>Miền {row['vung_mien']}</b><br>Nhu cầu: {row['count']:,} việc làm" for _, row in region_counts.iterrows()],
        text=region_counts['count'].map(lambda x: f" {x:,} "),
        textposition='outside',
        textfont=dict(size=10, color='#475569', weight='bold')
    )])
    
    fig.update_xaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e2e8f0',
        tickfont=dict(size=10, color='#64748b'),
        # Set generous max range to accommodate text labels outside bars
        range=[0, region_counts['count'].max() * 1.15]
    )
    
    fig.update_yaxes(
        showgrid=False,
        linecolor='#e2e8f0',
        tickfont=dict(size=10, color='#475569', weight='bold')
    )
    
    apply_layout_styles(fig)
    fig.update_layout(margin=dict(l=5, r=30, t=10, b=20))
    
    return fig
