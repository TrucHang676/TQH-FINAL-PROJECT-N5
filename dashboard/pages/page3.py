import dash
from dash import html

dash.register_page(__name__, path='/salary')

layout = html.Div([
    html.Div([
        html.H2("03 Lương thị trường", className="placeholder-title"),
        html.P("Trang phân tích mức lương tuyển dụng IT đang trong quá trình phát triển.", className="placeholder-text")
    ], className="placeholder-card")
], className="placeholder-container")
