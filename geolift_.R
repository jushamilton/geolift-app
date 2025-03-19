
library(gridExtra)
library(grid)
getwd()
 library(GeoLift)
library(gridExtra)
library(ggplot2)
library(grid)
library(bigrquery)
library(tidyverse)
 

head(data)

# things we need
the raw uploaded data
identification of what column name within data identifies date 
identification of what column name within data identifies location 
identification of what column name within data identifies y 
list of selected treatment values


GeoTestData_installs <- GeoDataRead(data = data,
                                 date_id = "date",
                                 location_id = "dma_name",
                                 Y_id = "installs",
                                 X = c(),
                                 format = "yyyy-mm-dd",
                                 summary = TRUE)
GeoTestData_installs

GeoPlot(GeoTestData_installs,
        Y_id = "Y",
        time_id = "time",
        location_id = "location",
        treatment_start = 344 
        )

# GeoTest_test_analysis <- GeoLift(Y_id = "Y",
#                          data = GeoTestData_installs,
#                          locations = c(
#                            "bend or",
#                            "atlanta ga",
#                            "greenville-spartanburg sc",
#                            "columbus oh",
#                            "milwaukee wi",
#                            "tampa-st petersburg (sarasota) fl",
#                            "raleigh-durham (fayetteville) nc",
#                            "san antonio tx",
#                            "orlando-daytona beach fl",
#                            "miami-ft. lauderdale fl",
#                            "grand rapids-kalamazoo mi",
#                            "green bay-appleton wi",
#                            "springfield mo",
#                            "rochester ny",
#                            "tri-cities tn-va",
#                            "harrisburg-lancaster-york pa",
#                            "wilkes barre-scranton pa",
#                            "chattanooga tn",
#                            "greensboro-winston salem nc",
#                            "duluth mn-superior wi"
#                          ),
#                           treatment_start_time = 344,
#                          treatment_end_time = 371
#                          )

# GeoTest_test_analysis
# summary(GeoTest_test_analysis)
# # Save plots to PDF
# plot(GeoTest_test_analysis, type = "Lift", subtitle = "Installs", treatment_end_date = '2025-01-06')
# plot(GeoTest_test_analysis, type = "ATT", subtitle = "Installs", treatment_end_date = '2024-10-06')

# write.csv(GeoTestData_installs, file = '/Users/justin.hamilton/Downloads/export20250310.csv')
# # Print summary directly to PDF
# summary_ga4_spend <- summary(GeoTest_spend)
# geo_lift_summary("Spend", summary_ga4_spend)




