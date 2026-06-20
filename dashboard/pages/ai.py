import dash
from dash import html

dash.register_page(__name__, path='/ai')

layout = html.Div([
    html.Div([
        html.H2("05 AI phân tích", className="placeholder-title"),
        html.P("Trang phân tích thị trường bằng AI đang trong quá trình phát triển.", className="placeholder-text")
    ], className="placeholder-card")
], className="placeholder-container")
