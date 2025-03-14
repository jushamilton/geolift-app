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
    
    # Step 1: File Upload
    dcc.Upload(
        id="upload-data",
        children=html.Button("Upload CSV"),
        multiple=False
    ),
    
    html.Div(id="output-data-upload"),
    
    # Step 2: Select Date Column
    html.Label("Select Date Column:"),
    dcc.Dropdown(id="date-selector", options=[], multi=False),
    
    # Step 3: Select Geo Field Column
    html.Label("Select Geo Field Column:"),
    dcc.Dropdown(id="geo-selector", options=[], multi=False),
    
    # Step 4: Select Treatment Group
    html.Label("Select Treatment Group:"),
    dcc.Dropdown(id="treatment-selector", options=[], multi=True),
    
    # Step 5: Select Variable of Study (Y)
    html.Label("Select Variable of Study (Y):"),
    dcc.Dropdown(id="y-selector", options=[], multi=False),
    
    html.Button("Run Analysis", id="run-analysis"),
    
    dcc.Graph(id="output-graph")
])

# Store uploaded data
data_store = {}

# Callback: Handle CSV Upload
@app.callback(
    [Output("output-data-upload", "children"),
     Output("date-selector", "options"),
     Output("geo-selector", "options")],
    Input("upload-data", "contents"),
    State("upload-data", "filename")
)
def update_table(contents, filename):
    if contents is None:
        return None, [], []

    # Decode and read CSV
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    data_store["df"] = df  # Store the DataFrame
    
    # Generate dropdown options for columns
    date_options = [{"label": col, "value": col} for col in df.columns if df[col].dtype == 'object']
    geo_options = [{"label": col, "value": col} for col in df.columns if df[col].dtype == 'object' and col != "date"]
    
    return dash_table.DataTable(data=df.head().to_dict("records"), page_size=5), date_options, geo_options

# Callback: Update Treatment Group Dropdown Based on Geo Field Selection
@app.callback(
    Output("treatment-selector", "options"),
    Input("geo-selector", "value")
)
def update_treatment_selector(geo_field):
    if geo_field:
        # Get unique values from the selected geo field
        df = data_store.get("df")
        geo_values = [{"label": geo, "value": geo} for geo in df[geo_field].unique()]
        return geo_values
    return []

# Callback: Update Variable of Study Dropdown Based on Column Selection
@app.callback(
    Output("y-selector", "options"),
    Input("geo-selector", "value")
)
def update_y_selector(geo_field):
    if geo_field:
        df = data_store.get("df")
        numeric_cols = [{"label": col, "value": col} for col in df.select_dtypes(include=["number"]).columns]
        return numeric_cols
    return []

# Callback: Run Analysis
@app.callback(
    Output("output-graph", "figure"),
    Input("run-analysis", "n_clicks"),
    State("date-selector", "value"),
    State("geo-selector", "value"),
    State("treatment-selector", "value"),
    State("y-selector", "value"),
    prevent_initial_call=True
)
def run_analysis(n_clicks, date_col, geo_col, treatment_group, y_col):
    df = data_store.get("df")
    
    if df is None or not date_col or not geo_col or not treatment_group or not y_col:
        return px.scatter(title="Please complete all selections")
    
    # Filter the DataFrame based on the treatment group
    treatment_df = df[df[geo_col].isin(treatment_group)]
    
    # Plot: Example, can be customized based on GeoLift analysis logic
    fig = px.line(treatment_df, x=date_col, y=y_col, color=geo_col, title=f"{y_col} over Time for Treatment Group")
    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
