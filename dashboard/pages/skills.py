import dash
from dash import html

dash.register_page(__name__, path='/skills')

layout = html.Div([
    html.Div([
        html.H2("02 Kỹ năng & Công nghệ", className="placeholder-title"),
        html.P("Trang phân tích kỹ năng và công nghệ tuyển dụng IT đang trong quá trình phát triển.", className="placeholder-text")
    ], className="placeholder-card")
], className="placeholder-container")
