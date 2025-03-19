suppressMessages(library(GeoLift))
suppressMessages(library(dplyr))
suppressMessages(library(tidyverse))

# Read the data and selections CSV
data <- read.csv("input_data.csv")
selections <- read.csv("selections.csv")

# Extract selections from the CSV
date_col <- selections$date_col
geo_col <- selections$geo_col
treatment_group <- strsplit(selections$treatment_group, ", ")[[1]]
y_col <- selections$y_col

# Ensure 'date' is in the correct format
data[[date_col]] <- as.Date(data[[date_col]], format = "%Y-%m-%d")


# Prepare data for GeoLift
GeoTestData <- GeoDataRead(data = data,
                           date_id = date_col,
                           location_id = geo_col,
                           Y_id = y_col,
                           format = "yyyy-mm-dd",
                           summary = TRUE)

# Print summary for debugging
print(summary(GeoTestData))

# Save the plot
png("geo_lift_plot.png", width = 800, height = 600)
print("Columns in GeoTestData after GeoDataRead:")
print(colnames(GeoTestData))



# GeoPlot(GeoTestData,
#         Y_id = "Y",
#         time_id = "time",
#         location_id = "location",
#         treatment_start = 50)

GeoTest_test_analysis <- GeoLift(Y_id = "Y",
                         data = GeoTestData,
                         locations = treatment_group ,
                          treatment_start_time = 40,
                          treatment_end_time = 70,

                         )
print(summary(GeoTest_test_analysis))

plot(GeoTest_test_analysis, type = "Lift", subtitle = "Installs", treatment_end_date = '2025-01-06')

# plot(GeoTest_test_analysis, type = "Lift", subtitle = "Installs", treatment_end_date = '2025-01-06')
# plot(GeoTest_test_analysis, type = "ATT", subtitle = "Installs", treatment_end_date = '2024-10-06')
