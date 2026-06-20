import dash
import dash_bootstrap_components as dbc
from dash import html

# Initialize Dash application with multi-page support
# Assets folder is relative to this file: dashboard/assets/
# Pages folder is relative to this file: dashboard/pages/
app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    assets_folder="assets",
    title="IT Recruitment Analysis Dashboard",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Root application layout
app.layout = html.Div([
    dash.page_container
])

# Run server
if __name__ == '__main__':
    # Set debug=False in production, True for development
    print("Starting IT Recruitment Dashboard Server on http://127.0.0.1:8050...")
    app.run(debug=True, host='127.0.0.1', port=8050)
