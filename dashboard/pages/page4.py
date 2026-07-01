import dash
from dash import html

dash.register_page(__name__, path='/entry-level')

layout = html.Div([
    html.Div([
        html.H2("04 Nhân sự trẻ", className="placeholder-title"),
        html.P("Trang phân tích cơ hội việc làm cho nhân sự trẻ đang trong quá trình phát triển.", className="placeholder-text")
    ], className="placeholder-card")
], className="placeholder-container")
