import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import io
import base64
import subprocess
import os

app = dash.Dash(__name__)

# File storage paths
UPLOAD_FOLDER = "uploads"
RESULTS_FILE = "results.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    
    html.Div(id="analysis-output"),
    
    # Display the generated plot
    html.Img(id="output-graph", style={"width": "800px", "height": "600px"})
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

import subprocess

def run_analysis(n_clicks, date_col, geo_col, treatment_group, y_col):
    df = data_store.get("df")
    
    if df is None or not date_col or not geo_col or not treatment_group or not y_col:
        return "Please complete all selections before running analysis.", None

    # Save dataframe to CSV for R to process
    df.to_csv("input_data.csv", index=False)

    # Save selections to CSV
    selections = pd.DataFrame({
        "date_col": [date_col],
        "geo_col": [geo_col],
        "treatment_group": [", ".join(treatment_group)],
        "y_col": [y_col]
    })
    selections.to_csv("selections.csv", index=False)

    # Ensure selections.csv is saved correctly before running the R script
    if not os.path.exists("selections.csv"):
        return "Error: Selections CSV file not saved.", None

    # Run the R script and capture output live
    process = subprocess.Popen(
        ["Rscript", "geolift_analysis.R"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    full_output = ""

    # Read stdout and stderr together in real-time
    for line in process.stdout:
        full_output += line
        print(line, end="")  # Print R output in real-time for debugging

    for line in process.stderr:
        full_output += line
        print(line, end="")  # Print R errors in real-time for debugging

    process.wait()  # Ensure process completes

    # If the script failed, return the full output
    if process.returncode != 0:
        return f"Error in R script:\n{full_output}", None

    # Check if the PNG file was created
    plot_path = "geo_lift_plot.png"
    if not os.path.exists(plot_path):
        return f"GeoLift analysis completed, but no plot was generated.\n{full_output}", None

    # Convert the PNG file to Base64 for display in Dash
    with open(plot_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
    img_src = f"data:image/png;base64,{encoded_image}"

    return f"GeoLift analysis completed successfully.\n{full_output}", img_src

 # Callback: Run Analysis and Display Results
@app.callback(
    [Output("analysis-output", "children"), Output("output-graph", "src")],
    Input("run-analysis", "n_clicks"),
    State("date-selector", "value"),
    State("geo-selector", "value"),
    State("treatment-selector", "value"),
    State("y-selector", "value"),
    prevent_initial_call=True
)
def update_analysis_output(n_clicks, date_col, geo_col, treatment_group, y_col):
    return run_analysis(n_clicks, date_col, geo_col, treatment_group, y_col)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
