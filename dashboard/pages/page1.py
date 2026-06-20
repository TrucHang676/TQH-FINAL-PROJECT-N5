import os
import pandas as pd
from pathlib import Path
import dash
from dash import html, dcc, callback, Input, Output, State

# Import chart functions from charts1
from dashboard.pages import charts1

# Register this page as the index page
dash.register_page(__name__, path='/')

# Resolve CSV Path relative to this file
current_dir = Path(__file__).parent.resolve()
root_dir = current_dir.parent.parent.resolve()
csv_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"

# Load the dataset
if csv_path.exists():
    df = pd.read_csv(csv_path)
else:
    # Fallback to an empty dataframe if file doesn't exist
    df = pd.DataFrame(columns=[
        'ten_cong_viec', 'ten_cong_ty', 'nhom_vi_tri', 'cap_do_kinh_nghiem', 
        'tinh_thanh', 'vung_mien', 'luong_tb', 'hinh_thuc_lam_viec', 'ngay_dang', 
        'thang_dang', 'nguon'
    ])

# Populate filter options
sources = sorted(df['nguon'].dropna().unique().tolist()) if not df.empty else []

positions = sorted(df['nhom_vi_tri'].dropna().unique().tolist()) if not df.empty else []
position_options = [{'label': 'Tất cả vị trí', 'value': 'All'}] + [{'label': p, 'value': p} for p in positions]

exp_levels = ['Intern', 'Fresher', 'Junior', 'Middle', 'Senior', 'Không rõ']
present_levels = [lvl for lvl in exp_levels if lvl in df['cap_do_kinh_nghiem'].unique()] if not df.empty else []
experience_options = [{'label': 'Tất cả cấp bậc', 'value': 'All'}] + [{'label': lvl, 'value': lvl} for lvl in present_levels]

regions = sorted(df['vung_mien'].dropna().unique().tolist()) if not df.empty else []
region_options = [{'label': 'Tất cả vùng miền', 'value': 'All'}] + [{'label': r, 'value': r} for r in regions]

# Dashboard layout
layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("HỆ THỐNG PHÂN TÍCH NHU CẦU TUYỂN DỤNG IT VIỆT NAM", className="header-title"),
            html.Span("Phân tích trực quan xu hướng tuyển dụng và phân bố địa lý thị trường công nghệ", className="header-subtitle")
        ], className="header-title-container"),
        html.Div([
            html.Div("Live Data", className="badge-live"),
            html.Div(f"Tổng tin tuyển dụng gốc: {len(df):,}", className="header-subtitle", style={"font-weight": "500"})
        ], className="header-info")
    ], className="header-bar"),
    
    # Workspace
    html.Div([
        # Sidebar Filter Panel
        html.Div([
            html.Div([
                html.Span("Bộ lọc phân tích", className="sidebar-title"),
                html.Button("Đặt lại", id="btn-reset", className="btn-reset", n_clicks=0)
            ], className="sidebar-title-section"),
            
            # Filter 1: Nguồn tuyển dụng
            html.Div([
                html.Label("Nguồn tuyển dụng", className="filter-label"),
                dcc.Checklist(
                    id="filter-sources",
                    options=[{'label': f" {src}", 'value': src} for src in sources],
                    value=sources,
                    className="source-checklist"
                )
            ], className="filter-group"),
            
            # Filter 2: Nhóm vị trí
            html.Div([
                html.Label("Nhóm vị trí công việc", className="filter-label"),
                dcc.Dropdown(
                    id="filter-position",
                    options=position_options,
                    value='All',
                    clearable=False,
                    searchable=True
                )
            ], className="filter-group"),
            
            # Filter 3: Cấp độ kinh nghiệm
            html.Div([
                html.Label("Cấp độ kinh nghiệm", className="filter-label"),
                dcc.Dropdown(
                    id="filter-experience",
                    options=experience_options,
                    value='All',
                    clearable=False,
                    searchable=True
                )
            ], className="filter-group"),
            
            # Filter 4: Vùng miền
            html.Div([
                html.Label("Vùng miền địa lý", className="filter-label"),
                dcc.Dropdown(
                    id="filter-region",
                    options=region_options,
                    value='All',
                    clearable=False,
                    searchable=True
                )
            ], className="filter-group")
        ], className="sidebar"),
        
        # Main Panel
        html.Div([
            # KPI Row
            html.Div([
                # KPI Card 1: Total Jobs
                html.Div([
                    html.Div([
                        html.Span("Số lượng việc làm", className="kpi-title"),
                        html.Span(id="kpi-total-jobs", className="kpi-value")
                    ], className="kpi-card-info"),
                    html.Div("💼", className="kpi-icon-container")
                ], className="kpi-card"),
                
                # KPI Card 2: Average Salary
                html.Div([
                    html.Div([
                        html.Span("Lương trung bình", className="kpi-title"),
                        html.Span(id="kpi-avg-salary", className="kpi-value")
                    ], className="kpi-card-info"),
                    html.Div("💵", className="kpi-icon-container")
                ], className="kpi-card"),
                
                # KPI Card 3: Top Location
                html.Div([
                    html.Div([
                        html.Span("Địa bàn lớn nhất", className="kpi-title"),
                        html.Span(id="kpi-top-location", className="kpi-value")
                    ], className="kpi-card-info"),
                    html.Div("📍", className="kpi-icon-container")
                ], className="kpi-card"),
                
                # KPI Card 4: Full-time Ratio
                html.Div([
                    html.Div([
                        html.Span("Tỷ lệ Full-time", className="kpi-title"),
                        html.Span(id="kpi-fulltime-ratio", className="kpi-value")
                    ], className="kpi-card-info"),
                    html.Div("🕒", className="kpi-icon-container")
                ], className="kpi-card")
            ], className="kpi-row"),
            
            # Charts Container
            html.Div([
                # Left Panel: Geography Map
                html.Div([
                    html.Div([
                        html.Span([
                            html.Span("🗺️", className="chart-title-icon"),
                            " Bản đồ nhu cầu tuyển dụng theo tỉnh/thành"
                        ], className="chart-title"),
                        html.Span("Bản đồ phân bố địa lý Việt Nam", className="chart-subtitle")
                    ], className="chart-header"),
                    html.Div([
                        dcc.Graph(
                            id="map-chart",
                            config={"displayModeBar": False, "scrollZoom": False},
                            style={"height": "100%", "width": "100%"}
                        )
                    ], className="chart-content")
                ], className="chart-card map-card"),
                
                # Right Panel: Stacked Charts
                html.Div([
                    # Time Trend Card
                    html.Div([
                        html.Div([
                            html.Span([
                                html.Span("📈", className="chart-title-icon"),
                                " Biến động nhu cầu tuyển dụng IT theo thời gian"
                            ], className="chart-title"),
                            html.Span("Phân tích số lượng tin tuyển dụng qua các tháng", className="chart-subtitle")
                        ], className="chart-header"),
                        html.Div([
                            dcc.Graph(
                                id="trend-chart",
                                config={"displayModeBar": False},
                                style={"height": "100%", "width": "100%"}
                            )
                        ], className="chart-content")
                    ], className="chart-card trend-card"),
                    
                    # Bottom Split Row
                    html.Div([
                        # Working Form Donut Card
                        html.Div([
                            html.Div([
                                html.Span([
                                    html.Span("📊", className="chart-title-icon"),
                                    " Cơ cấu hình thức làm việc"
                                ], className="chart-title"),
                                html.Span("Tỷ lệ hình thức làm việc tuyển dụng", className="chart-subtitle")
                            ], className="chart-header"),
                            html.Div([
                                dcc.Graph(
                                    id="work-type-chart",
                                    config={"displayModeBar": False},
                                    style={"height": "100%", "width": "100%"}
                                )
                            ], className="chart-content")
                        ], className="chart-card donut-card"),
                        
                        # Region Job Demands
                        html.Div([
                            html.Div([
                                html.Span([
                                    html.Span("🌐", className="chart-title-icon"),
                                    " Nhu cầu tuyển dụng theo vùng miền"
                                ], className="chart-title"),
                                html.Span("So sánh số lượng tin tuyển dụng các miền", className="chart-subtitle")
                            ], className="chart-header"),
                            html.Div([
                                dcc.Graph(
                                    id="region-chart",
                                    config={"displayModeBar": False},
                                    style={"height": "100%", "width": "100%"}
                                )
                            ], className="chart-content")
                        ], className="chart-card region-card")
                    ], className="split-row")
                ], className="charts-right-panel")
            ], className="charts-container")
        ], className="main-panel")
    ], className="workspace")
], id="page1-container")

# Callbacks
@callback(
    [
        Output('kpi-total-jobs', 'children'),
        Output('kpi-avg-salary', 'children'),
        Output('kpi-top-location', 'children'),
        Output('kpi-fulltime-ratio', 'children'),
        Output('trend-chart', 'figure'),
        Output('map-chart', 'figure'),
        Output('work-type-chart', 'figure'),
        Output('region-chart', 'figure')
    ],
    [
        Input('filter-sources', 'value'),
        Input('filter-position', 'value'),
        Input('filter-experience', 'value'),
        Input('filter-region', 'value')
    ]
)
def update_dashboard(selected_sources, selected_position, selected_experience, selected_region):
    # Empty data check
    if df.empty:
        empty_fig = charts1.apply_layout_styles(dash.go.Figure())
        return "0", "N/A", "N/A", "0.0%", empty_fig, empty_fig, empty_fig, empty_fig

    dff = df.copy()
    
    # 1. Filter by recruitment sources
    if selected_sources:
        dff = dff[dff['nguon'].isin(selected_sources)]
    else:
        # If no sources checked, return empty data
        dff = dff.iloc[0:0]

    # 2. Filter by position
    if selected_position and selected_position != 'All':
        dff = dff[dff['nhom_vi_tri'] == selected_position]

    # 3. Filter by experience
    if selected_experience and selected_experience != 'All':
        dff = dff[dff['cap_do_kinh_nghiem'] == selected_experience]

    # 4. Filter by region
    if selected_region and selected_region != 'All':
        dff = dff[dff['vung_mien'] == selected_region]

    # --- Calculate KPIs ---
    # Total jobs
    total_jobs = len(dff)
    kpi_total = f"{total_jobs:,}"
    
    # Average salary
    # Take rows where salary is available and > 0 (to ignore anomalies)
    salary_dff = dff[dff['luong_tb'].notna() & (dff['luong_tb'] > 0)]
    if not salary_dff.empty:
        avg_salary = salary_dff['luong_tb'].mean()
        kpi_salary = f"{avg_salary:.1f} Tr"
    else:
        kpi_salary = "Thỏa thuận"

    # Top Location (Province/City)
    if total_jobs > 0:
        top_city_series = dff['tinh_thanh'].value_counts()
        if not top_city_series.empty:
            top_city = top_city_series.index[0]
            top_city_count = top_city_series.iloc[0]
            top_city_pct = (top_city_count / total_jobs) * 100
            kpi_location = f"{top_city} ({top_city_pct:.1f}%)"
        else:
            kpi_location = "N/A"
    else:
        kpi_location = "N/A"

    # Full-time Ratio
    if total_jobs > 0:
        ft_count = (dff['hinh_thuc_lam_viec'] == 'Full-time').sum()
        ft_ratio = (ft_count / total_jobs) * 100
        kpi_ft = f"{ft_ratio:.1f}%"
    else:
        kpi_ft = "0.0%"

    # --- Generate Charts ---
    trend_fig = charts1.create_time_trend_chart(dff)
    map_fig = charts1.create_vietnam_map(dff)
    work_fig = charts1.create_work_type_chart(dff)
    region_fig = charts1.create_region_chart(dff)

    return kpi_total, kpi_salary, kpi_location, kpi_ft, trend_fig, map_fig, work_fig, region_fig


# Reset button callback
@callback(
    [
        Output('filter-sources', 'value'),
        Output('filter-position', 'value'),
        Output('filter-experience', 'value'),
        Output('filter-region', 'value')
    ],
    [Input('btn-reset', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    if n_clicks > 0:
        return sources, 'All', 'All', 'All'
    return dash.no_update
