import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Coordinates of Vietnam provinces/cities present in the dataset
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

# Professional Colors - Warm Editorial Theme
REGION_COLORS = {
    'Bắc': '#FA6781',       # Coral Red
    'Nam': '#59B292',       # Sage Green
    'Trung': '#FFC94D',     # Amber Gold
    'Từ xa / Remote': '#0d9488', # Teal
    'Khác': '#9ca3af'       # Grey
}

def apply_layout_styles(fig):
    fig.update_layout(
        font_family="Inter, system-ui, -apple-system, sans-serif",
        font_color="#111827",
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="closest",
        showlegend=False,
        # Smooth transition animation when figure updates
        transition=dict(
            duration=400,
            easing="cubic-in-out"
        ),
        # Clean custom tooltip styled like modern HTML popovers (Shadcn Dark Style)
        hoverlabel=dict(
            bgcolor="#1e293b",
            bordercolor="rgba(0,0,0,0)",
            font_size=12,
            font_family="Inter, system-ui, -apple-system, sans-serif",
            font_color="#ffffff",
            namelength=-1
        )
    )
    return fig

def create_time_trend_chart(df):
    """
    Line chart showing the recruitment trend over time, with a 3-month moving average
    """
    trend_df = df.dropna(subset=['thang_dang']).copy()
    
    if trend_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu thời gian", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig
        
    trend_data = trend_df.groupby('thang_dang').size().reset_index(name='job_count')
    
    # Convert thang_dang to datetime before sorting and calculations
    trend_data['thang_dang_dt'] = pd.to_datetime(trend_data['thang_dang'] + '-01', format='%Y-%m-%d')
    trend_data = trend_data.sort_values('thang_dang_dt')
    
    # Calculate 3-month moving average
    trend_data['moving_avg'] = trend_data['job_count'].rolling(window=3, min_periods=1).mean()
    
    fig = go.Figure()
    
    # 3-Month Moving Average (Dashed Grey Line)
    fig.add_trace(go.Scatter(
        x=trend_data['thang_dang'],
        y=trend_data['moving_avg'],
        mode='lines',
        name='Trung bình trượt',
        line=dict(color='#9ca3af', width=2, dash='dash'),
        hovertemplate="%{y:,.0f} tin<extra></extra>"
    ))
    
    # Main Job Count Line (Solid Sage Green Line, No markers)
    fig.add_trace(go.Scatter(
        x=trend_data['thang_dang'],
        y=trend_data['job_count'],
        mode='lines',
        name='Tin tuyển dụng',
        line=dict(color='#59B292', width=2.5),
        hovertemplate="%{y:,.0f} tin<extra></extra>"
    ))
    
    # Highlight Peak Month
    if not trend_data.empty:
        peak_idx = trend_data['job_count'].idxmax()
        peak_row = trend_data.loc[peak_idx]
        peak_month = peak_row['thang_dang']
        peak_count = peak_row['job_count']
        
        # Single marker for peak month
        fig.add_trace(go.Scatter(
            x=[peak_month],
            y=[peak_count],
            mode='markers',
            name='Tháng cao điểm',
            marker=dict(size=8, color='#FA6781', symbol='circle', line=dict(width=1.5, color='#ffffff')),
            hoverinfo='skip'
        ))
        
        # Peak annotation
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
        title_font=dict(size=10, color='#4b5563')
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor='#f1f5f9',
        linecolor='#e5e7eb',
        tickfont=dict(size=9, color='#4b5563'),
        title_font=dict(size=10, color='#4b5563')
    )
    
    apply_layout_styles(fig)
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=40, r=10, t=50, b=35),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.9,
            xanchor="right",
            x=1,
            font=dict(size=9, color='#4b5563')
        )
    )
    return fig

def create_vietnam_map(df):
    """
    Map of Vietnam using scatter_mapbox with carto-positron style
    """
    city_counts = df['tinh_thanh'].value_counts().reset_index(name='job_count')
    
    map_data = []
    for _, row in city_counts.iterrows():
        city = row['tinh_thanh']
        count = row['job_count']
        if city in PROVINCE_COORDINATES:
            lat_lon = PROVINCE_COORDINATES[city]
            sample_row = df[df['tinh_thanh'] == city]
            region = sample_row['vung_mien'].iloc[0] if not sample_row.empty else 'Khác'
            
            map_data.append({
                'Tỉnh/Thành': city,
                'Vùng miền': region,
                'lat': lat_lon['lat'],
                'lon': lat_lon['lon'],
                'Số lượng tuyển dụng': count
            })
            
    if not map_data:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu bản đồ phù hợp", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig
        
    map_df = pd.DataFrame(map_data)
    
    # Academic Square Root size scaling
    # Prevents huge metropolitan centers from overshadowing regional data
    map_df['marker_size'] = map_df['Số lượng tuyển dụng'].apply(lambda x: 4 + np.sqrt(x) * 0.42)
    
    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="Số lượng tuyển dụng",
        color="Vùng miền",
        color_discrete_map=REGION_COLORS,
        custom_data=["Tỉnh/Thành", "Vùng miền", "Số lượng tuyển dụng"],
        size_max=24,
        zoom=4.5,
        center={"lat": 16.2, "lon": 107.5},
        mapbox_style="carto-positron"
    )
    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Vùng miền: %{customdata[1]}<br>Nhu cầu tuyển dụng: <b>%{customdata[2]:,} tin</b><extra></extra>"
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

def create_work_type_chart(df):
    """
    Horizontal bar chart showing working format breakdown (Academic styled, replacing donut)
    """
    work_counts = df['hinh_thuc_lam_viec'].value_counts().reset_index(name='count')
    
    if work_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu hình thức", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig
        
    total_work = work_counts['count'].sum()
    work_counts['pct'] = (work_counts['count'] / total_work) * 100
    
    # Sort ascending for horizontal display (largest at top)
    work_counts = work_counts.sort_values('count', ascending=True)
    
    # Form academic detailed labels on Y-axis
    y_labels = [row['hinh_thuc_lam_viec'] for _, row in work_counts.iterrows()]
    
    fig = go.Figure(data=[go.Bar(
        x=work_counts['count'],
        y=y_labels,
        orientation='h',
        text=[f"{row['count']:,} | {row['pct']:.1f}%" for _, row in work_counts.iterrows()],
        textposition='outside',
        marker=dict(
            color='#59B292', # Uniform academic sage green
            line=dict(width=0)
        ),
        hovertext=[f"<b>{row['hinh_thuc_lam_viec']}</b><br>Số lượng: {row['count']:,}<br>Tỉ lệ: {row['pct']:.1f}%" for _, row in work_counts.iterrows()],
        hovertemplate="%{hovertext}<extra></extra>"
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

def create_region_chart(df):
    """
    Horizontal bar chart showing job distribution by region
    """
    region_counts = df['vung_mien'].value_counts().reset_index(name='count')
    
    if region_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu vùng miền", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig
        
    total_region = region_counts['count'].sum()
    region_counts['pct'] = (region_counts['count'] / total_region) * 100
    
    # Sort ascending for horizontal display (largest at top)
    region_counts = region_counts.sort_values('count', ascending=True)
    
    y_labels = [row['vung_mien'] for _, row in region_counts.iterrows()]
    
    fig = go.Figure(data=[go.Bar(
        x=region_counts['count'],
        y=y_labels,
        orientation='h',
        text=[f"{row['count']:,} | {row['pct']:.1f}%" for _, row in region_counts.iterrows()],
        textposition='outside',
        marker=dict(
            color=[REGION_COLORS.get(r, '#9ca3af') for r in region_counts['vung_mien']],
            line=dict(width=0)
        ),
        hovertext=[f"<b>{row['vung_mien']}</b><br>Số lượng: {row['count']:,}<br>Tỉ lệ: {row['pct']:.1f}%" for _, row in region_counts.iterrows()],
        hovertemplate="%{hovertext}<extra></extra>"
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
