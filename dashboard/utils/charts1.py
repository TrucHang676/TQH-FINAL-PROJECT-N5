import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json

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
    'Bắc': '#FA6781',       # Coral Red (hong)
    'Nam': '#59B292',       # Sage Green (xanh la)
    'Trung': '#FFC94D',     # Amber Gold (vang)
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

def create_vietnam_map(df):
    """
    Choropleth Map of Vietnam Provinces using maplibre (Plotly 5.24+)
    """
    city_counts = df['tinh_thanh'].value_counts().reset_index(name='job_count')
    # Filter out Khác and Từ xa
    city_counts = city_counts[~city_counts['tinh_thanh'].isin(['Khác', 'Từ xa / Remote'])]
    
    if city_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu tỉnh thành", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    # Map dataset province names to GeoJSON property 'Name'
    city_counts['geojson_name'] = city_counts['tinh_thanh'].apply(
        lambda x: PROVINCE_NAME_MAPPING.get(x, x)
    )

    geojson_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'geo', 'vietnam_provinces.geojson')
    with open(geojson_path, 'r', encoding='utf-8') as f:
        vn_geojson = json.load(f)

    fig = px.choropleth_map(
        city_counts,
        geojson=vn_geojson,
        featureidkey="properties.Name",
        locations="geojson_name",
        color="job_count",
        color_continuous_scale="Viridis",
        hover_name="tinh_thanh",
        hover_data={"geojson_name": False, "job_count": True},
        labels={'job_count': 'Số lượng tin'},
        center={"lat": 16.2, "lon": 107.5},
        zoom=4.5,
        map_style="white-bg"
    )
    
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="white",
        hovertemplate="<b>%{hovertext}</b><br>Nhu cầu tuyển dụng: <b>%{z:,} tin</b><extra></extra>"
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

def create_regional_vietnam_map(df):
    """
    Choropleth Map of Vietnam Regions using maplibre (Plotly 5.24+)
    Colors provinces based on their region.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu vùng miền", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig

    # Get total jobs per region
    region_totals = df['vung_mien'].value_counts().to_dict()

    # Build map data for all unique provinces in dataset
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
        map_style="white-bg"
    )
    
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="white",
        hovertemplate="<b>Vùng %{hovertext}</b><br>Tỉnh: %{customdata[0]}<br>Tổng nhu cầu vùng: <b>%{customdata[1]:,} tin</b><extra></extra>"
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

def create_provincial_bar_chart(df):
    """
    Horizontal bar chart for Top provinces (Alternative to map)
    """
    city_counts = df['tinh_thanh'].value_counts().reset_index(name='count')
    # Exclude remote/other
    city_counts = city_counts[~city_counts['tinh_thanh'].isin(['Khác', 'Từ xa / Remote'])]
    
    if city_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Không có dữ liệu tỉnh thành", showarrow=False, font=dict(size=12, color="#9ca3af"))
        apply_layout_styles(fig)
        return fig
        
    # Get top 15 for better display
    city_counts = city_counts.head(15).sort_values('count', ascending=True)
    
    # Map colors based on region
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
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        hovertemplate="<b>%{y}</b><br>Nhu cầu: %{x:,} tin<extra></extra>"
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
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=20)
    )
    
    return fig

def create_sparkline(data, color="#294669"):
    """
    Minimal line chart for KPI cards
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
        
        # Add a subtle area fill
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
