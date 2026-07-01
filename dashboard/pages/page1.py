# =============================================================================
# Import thư viện chuẩn và Dash
# os, pandas để xử lý file/dữ liệu; Path để tạo đường dẫn đa nền tảng;
# dash và các thành phần html/dcc để xây dựng giao diện và callback.
# =============================================================================
import os
import pandas as pd
from pathlib import Path
import dash
from dash import html, dcc, callback, Input, Output, State

# Import các hàm vẽ biểu đồ từ module nội bộ charts1
from dashboard.utils import charts1

# Đăng ký trang này là trang chủ (path='/')
dash.register_page(__name__, path='/')

# =============================================================================
# Xác định đường dẫn tuyệt đối tới file CSV
# Dùng Path(__file__) để tính đường dẫn tương đối từ vị trí file hiện tại,
# tránh lỗi khi chạy từ thư mục khác.
# =============================================================================
current_dir = Path(__file__).parent.resolve()
root_dir = current_dir.parent.parent.resolve()
csv_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"

# =============================================================================
# Tải dữ liệu từ CSV vào DataFrame
# Nếu file không tồn tại, tạo DataFrame rỗng với các cột cần thiết
# để tránh lỗi khi khởi tạo layout và callback.
# =============================================================================
if csv_path.exists():
    df = pd.read_csv(csv_path)
else:
    df = pd.DataFrame(columns=[
        'ten_cong_viec', 'ten_cong_ty', 'nhom_vi_tri', 'cap_do_kinh_nghiem', 
        'tinh_thanh', 'vung_mien', 'luong_tb', 'hinh_thuc_lam_viec', 'ngay_dang', 
        'thang_dang', 'nguon'
    ])

# =============================================================================
# Khởi tạo các tùy chọn cho bộ lọc (filter options)
# Lấy danh sách duy nhất, bỏ NaN, sắp xếp để hiển thị trong Dropdown/Checklist.
# Mỗi Dropdown có thêm lựa chọn "Tất cả" (value='All') đứng đầu danh sách.
# =============================================================================

# Nguồn tuyển dụng: dùng cho Checklist (chọn nhiều)
sources = sorted(df['nguon'].dropna().unique().tolist()) if not df.empty else []

# Nhóm vị trí công việc
positions = sorted(df['nhom_vi_tri'].dropna().unique().tolist()) if not df.empty else []
position_options = [{'label': 'Tất cả vị trí', 'value': 'All'}] + [{'label': p, 'value': p} for p in positions]

# Cấp độ kinh nghiệm: chỉ lấy các cấp thực sự có trong dữ liệu, giữ thứ tự cố định
exp_levels = ['Intern', 'Fresher', 'Junior', 'Middle', 'Senior', 'Không rõ']
present_levels = [lvl for lvl in exp_levels if lvl in df['cap_do_kinh_nghiem'].unique()] if not df.empty else []
experience_options = [{'label': 'Tất cả cấp bậc', 'value': 'All'}] + [{'label': lvl, 'value': lvl} for lvl in present_levels]

# Vùng miền địa lý
regions = sorted(df['vung_mien'].dropna().unique().tolist()) if not df.empty else []
region_options = [{'label': 'Tất cả vùng miền', 'value': 'All'}] + [{'label': r, 'value': r} for r in regions]

# =============================================================================
# Định nghĩa layout trang 1: Sidebar lọc dữ liệu + Panel chính hiển thị KPI/biểu đồ
# Toàn bộ layout được bọc trong html.Div với id="page1-container"
# =============================================================================
layout = html.Div([
    html.Div([

        # =====================================================================
        # Sidebar: Bộ lọc dữ liệu
        # Gồm tiêu đề, nút "Đặt lại" và 4 bộ lọc độc lập.
        # Các filter thay đổi sẽ kích hoạt callback cập nhật toàn bộ dashboard.
        # =====================================================================
        html.Div([
            html.Div([
                html.Span("Bộ lọc", className="sidebar-title"),
                html.Button("Đặt lại", id="btn-reset", className="btn-reset", n_clicks=0)
            ], className="sidebar-title-section"),
            
            # Filter 1: Nguồn tuyển dụng — Checklist cho phép chọn nhiều nguồn cùng lúc
            html.Div([
                html.Label("Nguồn tuyển dụng", className="filter-label"),
                dcc.Checklist(
                    id="filter-sources",
                    options=[{'label': f" {src}", 'value': src} for src in sources],
                    value=sources,
                    className="source-checklist"
                )
            ], className="filter-group"),
            
            # Filter 2: Nhóm vị trí công việc — Dropdown đơn, mặc định "Tất cả"
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
            
            # Filter 3: Cấp độ kinh nghiệm — Dropdown đơn, mặc định "Tất cả"
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
            
            # Filter 4: Vùng miền địa lý — Dropdown đơn, mặc định "Tất cả"
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
        
        # =====================================================================
        # Main Panel: Khu vực hiển thị KPI và biểu đồ
        # =====================================================================
        html.Div([

            # -----------------------------------------------------------------
            # Hàng KPI: 4 thẻ tóm tắt chỉ số quan trọng
            # Nội dung được cập nhật động qua callback (id="kpi-*")
            # -----------------------------------------------------------------
            html.Div([

                # KPI 1: Tổng số tin tuyển dụng sau khi lọc
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("Tổng tin tuyển dụng", className="kpi-title"),
                            html.Span("Năm 2024", className="kpi-badge")
                        ], className="kpi-header"),
                        html.Div(id="kpi-total-jobs", className="kpi-body")
                    ], className="kpi-card-info")
                ], className="kpi-card"),
                
                # KPI 2: Tháng có số lượng tin cao nhất (peak month)
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("Tháng cao điểm", className="kpi-title"),
                            html.Span("Đỉnh", className="kpi-badge")
                        ], className="kpi-header"),
                        html.Div(id="kpi-peak-month", className="kpi-body")
                    ], className="kpi-card-info")
                ], className="kpi-card"),
                
                # KPI 3: Tỉnh/thành phố có nhiều tin nhất
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("Địa bàn lớn nhất", className="kpi-title"),
                            html.Span("Hot", className="kpi-badge")
                        ], className="kpi-header"),
                        html.Div(id="kpi-top-location", className="kpi-body")
                    ], className="kpi-card-info")
                ], className="kpi-card"),
                
                # KPI 4: Hình thức làm việc phổ biến nhất
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("Hình thức chủ đạo", className="kpi-title"),
                            html.Span("Phổ biến", className="kpi-badge")
                        ], className="kpi-header"),
                        html.Div(id="kpi-dominant-work", className="kpi-body")
                    ], className="kpi-card-info")
                ], className="kpi-card")
            ], className="kpi-row"),
            
            # -----------------------------------------------------------------
            # Khu vực biểu đồ: chia 2 cột (trái: bản đồ, phải: xu hướng + donut)
            # -----------------------------------------------------------------
            html.Div([

                # Panel trái: Bản đồ / biểu đồ cột theo vùng miền
                # RadioItems cho phép chuyển đổi giữa 2 chế độ hiển thị
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span([
                                html.Span("01", className="chart-title-num"),
                                "Bản đồ phân bố tuyển dụng"
                            ], className="chart-title"),
                            html.Span("Bản đồ phân bố địa lý Việt Nam", className="chart-subtitle")
                        ]),
                        # Toggle chuyển đổi giữa bản đồ và biểu đồ cột theo vùng
                        html.Div([
                            dcc.RadioItems(
                                id="map-bar-toggle",
                                options=[
                                    {'label': html.Span('Bản đồ', className='radio-label-text'), 'value': 'map'},
                                    {'label': html.Span('Theo vùng', className='radio-label-text'), 'value': 'region_chart'}
                                ],
                                value='map',
                                className="toggle-switch",
                                labelClassName="toggle-label"
                            )
                        ], className="toggle-container")
                    ], className="chart-header map-header"),
                    # Vùng hiển thị biểu đồ bản đồ, bọc trong Loading để có spinner khi đang tải
                    html.Div([
                        dcc.Loading(
                            type="default",
                            color="#59B292",
                            delay_show=150,
                            delay_hide=100,
                            parent_style={"height": "100%", "width": "100%"},
                            children=dcc.Graph(
                                id="map-chart",
                                config={
                                    "displayModeBar": False,
                                    "responsive": True,
                                    "scrollZoom": False,
                                    "doubleClick": "reset"
                                },
                                style={"height": "100%", "width": "100%"}
                            )
                        )
                    ], className="chart-content"),
                    # Chú thích động bên dưới bản đồ, cập nhật theo chế độ hiển thị
                    html.Div(id="map-chart-caption", className="chart-caption")
                ], className="chart-card map-card"),
                
                # Panel phải: Xu hướng theo tháng + Hình thức làm việc
                html.Div([

                    # Biểu đồ 02: Xu hướng tuyển dụng theo tháng (line/bar chart)
                    html.Div([
                        html.Div([
                            html.Span([
                                html.Span("02", className="chart-title-num"),
                                "Xu hướng tuyển dụng theo tháng"
                            ], className="chart-title"),
                            html.Span("Số lượng tin tuyển dụng IT theo thời gian", className="chart-subtitle")
                        ], className="chart-header"),
                        html.Div([
                            dcc.Loading(
                                type="default",
                                color="#59B292",
                                delay_show=150,
                                delay_hide=100,
                                parent_style={"height": "100%", "width": "100%"},
                                children=dcc.Graph(
                                    id="trend-chart",
                                    config={
                                        "displayModeBar": False,
                                        "responsive": True,
                                        "scrollZoom": False,
                                        "doubleClick": "reset"
                                    },
                                    style={"height": "100%", "width": "100%"}
                                )
                            )
                        ], className="chart-content"),
                        html.Div("Biểu đồ thời gian chỉ tính các tin có thang_dang.", className="chart-caption")
                    ], className="chart-card trend-card"),
                    
                    # Hàng dưới: Biểu đồ 03 — Hình thức làm việc (donut chart)
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span([
                                    html.Span("03", className="chart-title-num"),
                                    "Hình thức làm việc chủ đạo"
                                ], className="chart-title"),
                                html.Span("Tỷ lệ hình thức làm việc tuyển dụng", className="chart-subtitle")
                            ], className="chart-header"),
                            html.Div([
                                dcc.Loading(
                                    type="default",
                                    color="#59B292",
                                    delay_show=150,
                                    delay_hide=100,
                                    parent_style={"height": "100%", "width": "100%"},
                                    children=dcc.Graph(
                                        id="work-type-chart",
                                        config={
                                            "displayModeBar": False,
                                            "responsive": True,
                                            "scrollZoom": False,
                                            "doubleClick": "reset"
                                        },
                                        style={"height": "100%", "width": "100%"}
                                    )
                                )
                            ], className="chart-content")
                        ], className="chart-card donut-card")
                    ], className="split-row")
                ], className="charts-right-panel")
            ], className="charts-container")
        ], className="main-panel")
    ], className="workspace")
], id="page1-container")


# =============================================================================
# Callback chính: Cập nhật toàn bộ dashboard khi bộ lọc thay đổi
# Nhận 5 Input (4 filter + toggle bản đồ), trả về 8 Output
# (4 KPI card + 3 figure + 1 caption).
# =============================================================================
@callback(
    [
        Output('kpi-total-jobs', 'children'),
        Output('kpi-peak-month', 'children'),
        Output('kpi-top-location', 'children'),
        Output('kpi-dominant-work', 'children'),
        Output('trend-chart', 'figure'),
        Output('map-chart', 'figure'),
        Output('work-type-chart', 'figure'),
        Output('map-chart-caption', 'children')
    ],
    [
        Input('filter-sources', 'value'),
        Input('filter-position', 'value'),
        Input('filter-experience', 'value'),
        Input('filter-region', 'value'),
        Input('map-bar-toggle', 'value')
    ]
)
def update_dashboard(selected_sources, selected_position, selected_experience, selected_region, map_bar_toggle):
    try:
        # Trả về giá trị rỗng nếu DataFrame không có dữ liệu
        if df.empty:
            empty_fig = charts1.apply_layout_styles(dash.go.Figure())
            return "0", "N/A", "N/A", "N/A", empty_fig, empty_fig, empty_fig, empty_fig
    
        # Tạo bản sao để lọc, không làm thay đổi df gốc
        dff = df.copy()
        
        # Bước 1: Lọc theo nguồn tuyển dụng (Checklist có thể chọn nhiều)
        # Nếu không chọn nguồn nào, trả về DataFrame rỗng
        if selected_sources:
            dff = dff[dff['nguon'].isin(selected_sources)]
        else:
            dff = dff.iloc[0:0]
    
        # Bước 2: Lọc theo nhóm vị trí, bỏ qua nếu chọn "Tất cả"
        if selected_position and selected_position != 'All':
            dff = dff[dff['nhom_vi_tri'] == selected_position]
    
        # Bước 3: Lọc theo cấp độ kinh nghiệm, bỏ qua nếu chọn "Tất cả"
        if selected_experience and selected_experience != 'All':
            dff = dff[dff['cap_do_kinh_nghiem'] == selected_experience]
    
        # Bước 4: Lọc theo vùng miền, bỏ qua nếu chọn "Tất cả"
        if selected_region and selected_region != 'All':
            dff = dff[dff['vung_mien'] == selected_region]
    
        # Tổng số tin sau khi áp dụng tất cả bộ lọc
        total_jobs = len(dff)
        
        # ---------------------------------------------------------------------
        # Sparkline dùng chung cho KPI 1 và KPI 2:
        # Tính số tin theo từng tháng, dùng làm dữ liệu đường mini-chart
        # ---------------------------------------------------------------------
        spark1_data = []
        if total_jobs > 0 and 'thang_dang' in dff.columns:
            monthly = dff.dropna(subset=['thang_dang']).groupby('thang_dang').size()
            spark1_data = monthly.tolist()
        
        spark_color = "#FAE7CB"
        spark1 = charts1.create_sparkline(spark1_data, spark_color)
        spark2 = charts1.create_sparkline(spark1_data, spark_color)
        
        # KPI 1: Tổng tin tuyển dụng — hiển thị số lớn + mô tả + sparkline
        kpi_total = [
            html.Div(f"{total_jobs:,}", className="kpi-main-val"),
            html.Div("Toàn bộ dữ liệu thu thập", className="kpi-desc"),
            dcc.Graph(figure=spark1, config={"displayModeBar": False}, style={"height": "40px", "marginTop": "4px"})
        ]
    
        # ---------------------------------------------------------------------
        # KPI 2: Tháng cao điểm
        # Tìm tháng có số tin nhiều nhất bằng idxmax() trên groupby tháng
        # ---------------------------------------------------------------------
        if total_jobs > 0:
            trend_dff = dff.dropna(subset=['thang_dang'])
            if not trend_dff.empty:
                month_counts = trend_dff.groupby('thang_dang').size()
                if not month_counts.empty:
                    peak_month = month_counts.idxmax()
                    peak_count = month_counts.max()
                    kpi_peak = [
                        html.Div(f"{peak_month}", className="kpi-main-val"),
                        html.Div(f"Đạt đỉnh với {peak_count:,} tin", className="kpi-desc"),
                        dcc.Graph(figure=spark2, config={"displayModeBar": False}, style={"height": "40px", "marginTop": "4px"})
                    ]
                else:
                    kpi_peak = "N/A"
            else:
                kpi_peak = "N/A"
        else:
            kpi_peak = "N/A"
    
        # ---------------------------------------------------------------------
        # KPI 3: Địa bàn lớn nhất
        # Dùng value_counts() để tìm tỉnh/thành có nhiều tin nhất,
        # tính phần trăm so với tổng và vẽ sparkline riêng cho địa bàn đó.
        # ---------------------------------------------------------------------
        if total_jobs > 0:
            top_city_series = dff['tinh_thanh'].value_counts()
            if not top_city_series.empty:
                top_city = top_city_series.index[0]
                top_city_count = top_city_series.iloc[0]
                top_city_pct = (top_city_count / total_jobs) * 100
                
                # Sparkline chỉ tính cho tỉnh/thành top 1
                loc_dff = dff[dff['tinh_thanh'] == top_city].dropna(subset=['thang_dang'])
                spark3_data = loc_dff.groupby('thang_dang').size().tolist()
                spark3 = charts1.create_sparkline(spark3_data, spark_color)
                
                kpi_location = [
                    html.Div(f"{top_city}", className="kpi-main-val"),
                    html.Div(f"Chiếm {top_city_pct:.1f}% toàn quốc", className="kpi-desc"),
                    dcc.Graph(figure=spark3, config={"displayModeBar": False}, style={"height": "40px", "marginTop": "4px"})
                ]
            else:
                kpi_location = "N/A"
        else:
            kpi_location = "N/A"
    
        # ---------------------------------------------------------------------
        # KPI 4: Hình thức làm việc chủ đạo
        # Tương tự KPI 3: tìm hình thức phổ biến nhất, tính tỷ lệ, vẽ sparkline.
        # ---------------------------------------------------------------------
        if total_jobs > 0:
            work_series = dff['hinh_thuc_lam_viec'].value_counts()
            if not work_series.empty:
                top_work = work_series.index[0]
                top_work_count = work_series.iloc[0]
                top_work_pct = (top_work_count / total_jobs) * 100
                
                # Sparkline chỉ tính cho hình thức làm việc top 1
                work_dff = dff[dff['hinh_thuc_lam_viec'] == top_work].dropna(subset=['thang_dang'])
                spark4_data = work_dff.groupby('thang_dang').size().tolist()
                spark4 = charts1.create_sparkline(spark4_data, spark_color)
                
                kpi_work = [
                    html.Div(f"{top_work}", className="kpi-main-val"),
                    html.Div(f"Chiếm {top_work_pct:.1f}% tổng thể", className="kpi-desc"),
                    dcc.Graph(figure=spark4, config={"displayModeBar": False}, style={"height": "40px", "marginTop": "4px"})
                ]
            else:
                kpi_work = "N/A"
        else:
            kpi_work = "N/A"
    
        # ---------------------------------------------------------------------
        # Tạo 3 biểu đồ chính từ dữ liệu đã lọc
        # map_bar_toggle quyết định biểu đồ 01 là bản đồ hay cột theo vùng miền
        # ---------------------------------------------------------------------
        trend_fig = charts1.create_time_trend_chart(dff)

        if map_bar_toggle == 'region_chart':
            # Chế độ biểu đồ cột theo vùng miền
            map_fig = charts1.create_region_vertical_chart(dff)
            caption = "Biểu đồ cột thể hiện nhu cầu tuyển dụng theo từng vùng miền."
        else:
            # Chế độ bản đồ choropleth Việt Nam
            map_fig = charts1.create_vietnam_map(dff)
            caption = "Không hiển thị nhóm Khác và Từ xa/Remote trên bản đồ do không có tọa độ địa lý cụ thể."

        work_fig = charts1.create_work_type_chart(dff)

        return kpi_total, kpi_peak, kpi_location, kpi_work, trend_fig, map_fig, work_fig, caption

    except Exception as e:
        # Ghi lỗi chi tiết ra file log để debug, sau đó re-raise để Dash hiển thị thông báo lỗi
        import traceback
        with open('d:/BaiTapKi2Nam3/TQHDL/Final/scratch/error.log', 'w') as f:
            f.write(traceback.format_exc())
        raise e


# =============================================================================
# Callback đặt lại bộ lọc về mặc định khi nhấn nút "Đặt lại"
# prevent_initial_call=True tránh kích hoạt khi trang mới tải xong.
# Trả về: tất cả nguồn được chọn, các Dropdown về giá trị 'All'.
# =============================================================================
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
    # Chỉ reset khi nút được nhấn ít nhất 1 lần
    if n_clicks > 0:
        return sources, 'All', 'All', 'All'
    return dash.no_update
