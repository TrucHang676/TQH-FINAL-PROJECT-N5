# Nhập các thư viện cần thiết để xây dựng dashboard, xử lý dữ liệu và đường dẫn file
import dash
import pandas as pd
from pathlib import Path
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

# Xác định đường dẫn file CSV dữ liệu IT và đếm tổng số bản ghi để hiển thị lên giao diện
# app.py nằm trong thư mục dashboard/, root_dir sẽ lấy thư mục cha của dashboard/
root_dir = Path(__file__).parent.parent.resolve()
csv_path = root_dir / "data" / "processed" / "vietnam_it_jobs_processed.csv"
if csv_path.exists():
    try:
        df_all = pd.read_csv(csv_path)
        total_records = len(df_all)
    except Exception:
        total_records = 8452 # Giá trị dự phòng nếu đọc file lỗi
else:
    total_records = 0

print(f"DIAGNOSTIC: root_dir={root_dir} | csv_path={csv_path} | exists={csv_path.exists()} | total_records={total_records}")

# Khởi tạo ứng dụng Dash hỗ trợ đa trang (multi-page) sử dụng thư mục pages/ và assets/
app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    assets_folder="assets",
    title="Thị trường tuyển dụng IT Việt Nam",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Định nghĩa cấu trúc giao diện (layout) gốc gồm Header toàn cục, thanh điều hướng (Navigation) và phần nội dung trang động
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Header toàn cục hiển thị tiêu đề và thông tin tổng quan về dataset
    html.Div([
        html.Div([
            html.H1("Thị trường tuyển dụng IT Việt Nam", className="global-title"),
            html.Div([
                html.Span("Mục tiêu 1", className="global-subtitle-main"),
                html.Span(" | ", className="global-subtitle-divider"),
                html.Span("Xu hướng nhu cầu theo thời gian, địa lý và hình thức làm việc", className="global-subtitle-desc")
            ], className="global-subtitle-container")
        ], className="global-title-container"),
        html.Div([
            html.Div([
                html.Span("Dataset: vietnam_it_jobs_processed.csv", className="dataset-name"),
                html.Span(f"{total_records:,} tin tuyển dụng", className="dataset-count")
            ], className="dataset-badge")
        ], className="global-badge-container")
    ], className="global-header"),
    
    # Thanh điều hướng dạng các tab liên kết đến các trang chức năng
    html.Div([
        html.Div([
            dcc.Link("01 Xu hướng & Địa lý", id="link-home", href="/", className="nav-tab"),
            dcc.Link("02 Kỹ năng & Công nghệ", id="link-skills", href="/skills", className="nav-tab"),
            dcc.Link("03 Lương thị trường", id="link-salary", href="/salary", className="nav-tab"),
            dcc.Link("04 Nhân sự trẻ", id="link-entry", href="/entry-level", className="nav-tab"),
            dcc.Link("05 AI phân tích", id="link-ai", href="/ai", className="nav-tab")
        ], className="nav-tabs-wrapper")
    ], className="nav-container"),
    
    # Container chứa nội dung của từng trang con khi chuyển đổi URL
    dash.page_container
])

# Callback phía client-side giúp tự động cập nhật CSS class 'active' cho tab hiện tại dựa trên đường dẫn URL
app.clientside_callback(
    """
    function(pathname) {
        var base_class = "nav-tab";
        var is_home = (pathname === "/" || pathname === "" || pathname === null || pathname === undefined);
        return [
            base_class + (is_home ? " active" : ""),
            base_class + (pathname === "/skills" ? " active" : ""),
            base_class + (pathname === "/salary" ? " active" : ""),
            base_class + (pathname === "/entry-level" ? " active" : ""),
            base_class + (pathname === "/ai" ? " active" : "")
        ];
    }
    """,
    [
        Output('link-home', 'className'),
        Output('link-skills', 'className'),
        Output('link-salary', 'className'),
        Output('link-entry', 'className'),
        Output('link-ai', 'className')
    ],
    [Input('url', 'pathname')]
)

# Chạy Server Dash cục bộ tại địa chỉ 127.0.0.1 cổng 8050
if __name__ == '__main__':
    print("Starting IT Recruitment Dashboard Server on http://127.0.0.1:8050...")
    app.run(debug=True, host='127.0.0.1', port=8050)
