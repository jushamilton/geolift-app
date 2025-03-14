import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import io
import base64

app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Lift-Lab: GeoLift Analysis"),
    
    dcc.Upload(
        id="upload-data",
        children=html.Button("Upload CSV"),
        multiple=False
    ),
    
    html.Div(id="output-data-upload"),
    
    html.Label("Select Column for Analysis:"),
    dcc.Dropdown(id="column-selector", options=[], multi=False),
    
    html.Button("Run Analysis", id="run-analysis"),
    
    dcc.Graph(id="output-graph")
])

# Store uploaded data
data_store = {}

# Callback: Handle CSV Upload
@app.callback(
    Output("output-data-upload", "children"),
    Output("column-selector", "options"),
    Input("upload-data", "contents"),
    State("upload-data", "filename")
)
def update_table(contents, filename):
    if contents is None:
        return None, []

    # Decode the uploaded file
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Read CSV into DataFrame
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    data_store["df"] = df  # Store it for later use

    # Create table and dropdown options
    table = dash_table.DataTable(data=df.head().to_dict("records"), page_size=5)
    options = [{"label": col, "value": col} for col in df.select_dtypes(include=["number"]).columns]  # Only numeric columns

    return table, options

# Callback: Run Analysis
@app.callback(
    Output("output-graph", "figure"),
    Input("run-analysis", "n_clicks"),
    State("column-selector", "value"),
    prevent_initial_call=True
)
def run_analysis(n_clicks, column):
    df = data_store.get("df")  # Retrieve stored DataFrame
    if df is None or column is None:
        return px.scatter(title="No data available")  # Placeholder chart

    # Create Plotly chart
    fig = px.histogram(df, x=column, title=f"Distribution of {column}")
    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
