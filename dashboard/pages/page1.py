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

# Page 1 Layout (Sidebar + Main Panel)
layout = html.Div([
    html.Div([
        # Sidebar Filter Panel
        html.Div([
            html.Div([
                html.Span("Bộ lọc", className="sidebar-title"),
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
                        html.Span("Tổng tin tuyển dụng", className="kpi-title"),
                        html.Span(id="kpi-total-jobs", className="kpi-value")
                    ], className="kpi-card-info")
                ], className="kpi-card"),
                
                # KPI Card 2: Peak Month
                html.Div([
                    html.Div([
                        html.Span("Tháng cao điểm", className="kpi-title"),
                        html.Span(id="kpi-peak-month", className="kpi-value")
                    ], className="kpi-card-info")
                ], className="kpi-card"),
                
                # KPI Card 3: Top Location
                html.Div([
                    html.Div([
                        html.Span("Địa bàn lớn nhất", className="kpi-title"),
                        html.Span(id="kpi-top-location", className="kpi-value")
                    ], className="kpi-card-info")
                ], className="kpi-card"),
                
                # KPI Card 4: Dominant Work Type
                html.Div([
                    html.Div([
                        html.Span("Hình thức chủ đạo", className="kpi-title"),
                        html.Span(id="kpi-dominant-work", className="kpi-value")
                    ], className="kpi-card-info")
                ], className="kpi-card")
            ], className="kpi-row"),
            
            # Quick Insights Strip
            html.Div(id="insights-strip", className="insights-strip"),
            
            # Charts Container
            html.Div([
                # Left Panel: Geography Map
                html.Div([
                    html.Div([
                        html.Span([
                            html.Span("01", className="chart-title-num"),
                            "Phân bố tuyển dụng theo tỉnh/thành"
                        ], className="chart-title"),
                        html.Span("Bản đồ phân bố địa lý Việt Nam", className="chart-subtitle")
                    ], className="chart-header"),
                    html.Div([
                        dcc.Graph(
                            id="map-chart",
                            config={"displayModeBar": False, "scrollZoom": False},
                            style={"height": "100%", "width": "100%"}
                        )
                    ], className="chart-content"),
                    html.Div("Không hiển thị nhóm Khác và Từ xa/Remote trên bản đồ do không có tọa độ địa lý cụ thể.", className="chart-caption")
                ], className="chart-card map-card"),
                
                # Right Panel: Stacked Charts
                html.Div([
                    # Time Trend Card
                    html.Div([
                        html.Div([
                            html.Span([
                                html.Span("02", className="chart-title-num"),
                                "Xu hướng tuyển dụng theo tháng"
                            ], className="chart-title"),
                            html.Span("Số lượng tin tuyển dụng IT theo thời gian", className="chart-subtitle")
                        ], className="chart-header"),
                        html.Div([
                            dcc.Graph(
                                id="trend-chart",
                                config={"displayModeBar": False},
                                style={"height": "100%", "width": "100%"}
                            )
                        ], className="chart-content"),
                        html.Div("Biểu đồ thời gian chỉ tính các tin có thang_dang.", className="chart-caption")
                    ], className="chart-card trend-card"),
                    
                    # Bottom Split Row
                    html.Div([
                        # Working Form Card
                        html.Div([
                            html.Div([
                                html.Span([
                                    html.Span("03", className="chart-title-num"),
                                    "Hình thức làm việc chủ đạo"
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
                                    html.Span("04", className="chart-title-num"),
                                    "Nhu cầu tuyển dụng theo vùng miền"
                                ], className="chart-title"),
                                html.Span("So sánh số lượng và tỷ trọng tin tuyển dụng theo vùng", className="chart-subtitle")
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
        Output('kpi-peak-month', 'children'),
        Output('kpi-top-location', 'children'),
        Output('kpi-dominant-work', 'children'),
        Output('insights-strip', 'children'),
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
    if df.empty:
        empty_fig = charts1.apply_layout_styles(dash.go.Figure())
        empty_insights = [
            html.Div([html.Span("Dữ liệu:", className="insight-label"), html.Span("Không có dữ liệu.", className="insight-text")], className="insight-item")
        ]
        return "0", "N/A", "N/A", "N/A", empty_insights, empty_fig, empty_fig, empty_fig, empty_fig

    dff = df.copy()
    
    # 1. Filter by recruitment sources
    if selected_sources:
        dff = dff[dff['nguon'].isin(selected_sources)]
    else:
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

    total_jobs = len(dff)
    kpi_total = f"{total_jobs:,}"
    
    # Init default insights
    insight_1 = "Không có thông tin địa bàn."
    insight_2 = "Không có thông tin hình thức."
    insight_3 = "Không đủ dữ liệu thời gian."

    # --- KPI 2: Peak Month ---
    if total_jobs > 0:
        trend_dff = dff.dropna(subset=['thang_dang'])
        if not trend_dff.empty:
            month_counts = trend_dff['thang_dang'].value_counts()
            if not month_counts.empty:
                peak_month = month_counts.index[0]
                peak_count = month_counts.iloc[0]
                kpi_peak = f"{peak_month} · {peak_count:,} tin"
                insight_3 = f"Nhu cầu tuyển dụng đạt đỉnh vào tháng {peak_month} với {peak_count:,} tin tuyển dụng."
            else:
                kpi_peak = "N/A"
        else:
            kpi_peak = "N/A"
    else:
        kpi_peak = "N/A"

    # --- KPI 3: Top Location ---
    if total_jobs > 0:
        top_city_series = dff['tinh_thanh'].value_counts()
        if not top_city_series.empty:
            top_city = top_city_series.index[0]
            top_city_count = top_city_series.iloc[0]
            top_city_pct = (top_city_count / total_jobs) * 100
            kpi_location = f"{top_city} · {top_city_pct:.1f}%"
            insight_1 = f"{top_city} là trung tâm lớn nhất, chiếm {top_city_pct:.1f}% nhu cầu tuyển dụng."
        else:
            kpi_location = "N/A"
    else:
        kpi_location = "N/A"

    # --- KPI 4: Dominant Work Type ---
    if total_jobs > 0:
        work_series = dff['hinh_thuc_lam_viec'].value_counts()
        if not work_series.empty:
            top_work = work_series.index[0]
            top_work_count = work_series.iloc[0]
            top_work_pct = (top_work_count / total_jobs) * 100
            kpi_work = f"{top_work} · {top_work_pct:.1f}%"
            insight_2 = f"{top_work} là hình thức chiếm ưu thế vượt trội với tỷ lệ {top_work_pct:.1f}%."
        else:
            kpi_work = "N/A"
    else:
        kpi_work = "N/A"

    # --- Generate Insights Strip Elements ---
    insights_children = [
        html.Div([
            html.Span("Địa bàn lớn nhất:", className="insight-label"),
            html.Span(insight_1, className="insight-text")
        ], className="insight-item"),
        html.Div([
            html.Span("Hình thức làm việc:", className="insight-label"),
            html.Span(insight_2, className="insight-text")
        ], className="insight-item"),
        html.Div([
            html.Span("Điểm đỉnh xu hướng:", className="insight-label"),
            html.Span(insight_3, className="insight-text")
        ], className="insight-item")
    ]

    # --- Generate Charts ---
    trend_fig = charts1.create_time_trend_chart(dff)
    map_fig = charts1.create_vietnam_map(dff)
    work_fig = charts1.create_work_type_chart(dff)
    region_fig = charts1.create_region_chart(dff)

    return kpi_total, kpi_peak, kpi_location, kpi_work, insights_children, trend_fig, map_fig, work_fig, region_fig


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
