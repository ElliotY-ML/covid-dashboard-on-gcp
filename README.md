# Overview
This repository contains Python code and data for a dashboard deployed on the Google Cloud Platform (GCP) App Engine. 
The interactive Plotly Dash dashboard visualizes reported U.S. cases of COVID-19 in line graphs, bar charts, and bubble maps.

![Created using Dash](/img/DashGCPScreenShot.JPG)
[Link to Dash dashboard deployed on GCP](https://covid-dash-374301.ue.r.appspot.com/)


# Table of Contents
- [Introduction](#introduction)
- [Dependencies](#dependencies)
- [Data Sources](#data-sources)
- [Data Preparation](#data-preparation)
- [Plotly Dash Dashboard](#dashboard)
- [Deploy Dashboard Using GCP App Engine](#gcp-app)
- [License](#license)


# Introduction
This project presents a different aspect than those seen on New York Times [1] and U.S. CDC analysis [2] by analyzing totals of new COVID-19 cases reported in the past 14 days.  

Estimates of the percentage of each state population that is currently infected with COVID-19 is calculated by normalizing the past 14 day new case totals to their respective state populations. 
The data is presented as a percentage because it may be more intuitively understood by the general population, as opposed to using a basis of per million or per 100,000 people.

The author selected time intervals of 14-days based on studies that show that an average period of COVID-19 infectiousness and risk of transmission is between 3 days before and 8 days after symptom onset, 
and COVID-19 RNA usually becomes undetectable from upper respiratory tract samples about 2 weeks after symptom onset[3, 4, 5].

[1]  https://www.nytimes.com/interactive/2021/us/covid-cases.html  
[2]  https://covid.cdc.gov/covid-data-tracker/#datatracker-home  
[3]  https://www.cdc.gov/coronavirus/2019-ncov/your-health/quarantine-isolation.html  
[4]  Peeling RW, Heymann DL, Teo Y, Garcia PJ. Diagnostics for COVID-19: moving from pandemic response to control. Lancet. Published online December 20, 2021: https://doi.org/10.1016/S0140-6736(21)02346-1  
[5]  https://www.nytimes.com/interactive/2022/01/22/science/charting-omicron-infection.html


# Dependencies
This repo requires Python3 and the following libraries:  
- SQLite3
- Requests
- pandas
- Numpy
- Plotly
- Dash
- Gunicorn
- Werkzeug==2.0.3


# Data Sources
## CDC U.S. COVID-19 Cases and Deaths By State  
U.S. CDC reports daily COVID-19 cases and death counts online at this [link](https://data.cdc.gov/Case-Surveillance/United-States-COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36).  
The data is a collection of the most recent numbers reported by states, territories, and other jurisdictions to the CDC.  

**Notes**:
-  This dataset includes Confirmed Cases and Probable Cases, as defined by CSTE [6]. Confirmed cases meet molecular laboratory testing evidence, while Probable cases meet clinical criteria without laboratory evidence. 
Many jurisdictions include both their confirmed and probable cases ("pnew_case") into reported "Total Cases" and "New Case" counts.
-  Counts for New York City and New York State are provided separately.  This data must be recombined to analyze them as one New York state.

**Update as of 2023**
-  This daily-updated dataset was discontinued October 20, 2022 and replaced by a weekly-updated dataset. This project supports only the daily-updated dataset.
-  A copy of the daily-updated dataset retrieved on November 14, 2022 is located in [`./datasets/United_States_COVID-19_Cases_and_Deaths_by_State_over_Time_Nov_14_22.csv`](./datasets/United_States_COVID-19_Cases_and_Deaths_by_State_over_Time_Nov_14_22.csv).

## U.S. Census Bureau - 2019 American Community Survey 5-year Estimate 
The population of each state is obtained from the most recent U.S. Census Bureau American Community Survey 5-Year Estimate 2015-2019 [7].  Detailed descriptions about this data can be found through this [link](https://www.census.gov/acs/www/data/data-tables-and-tools/narrative-profiles/2019/report.php?geotype=nation&usVal=us)   
 
This data can be viewed and exported interactively on the U.S. Census Bureau [website](https://data.census.gov/cedsci/table?g=0100000U.S.,%240400000&tid=ACSST5Y2019.S0101)  

## American National Standards Institute (ANSI) Codes for States
The conversion from state names to state abbreviations is needed to combine the U.S. CDC COVID-19 and the U.S. Census ACS datasets. 
 
This information can be found on the U.S. Census Bureau reference library: https://www.census.gov/library/reference/code-lists/ansi/ansi-codes-for-states.html  
Download the "National FIPS and GNIS Codes File" from the reference library.

[6]  https://ndc.services.cdc.gov/case-definitions/coronavirus-disease-2019-2021/  
[7]  https://data.census.gov/cedsci/table?g=0100000U.S.&d=ACS%205-Year%20Estimates%20Subject%20Tables


# Data Preparation
Information on data preparation using GCP-BigQuery, Python, SQLite3, and Requests can be found in this repository: 
https://github.com/ElliotY-ML/Covid_Cases_By_Percent_Population

The following features are calculated from the datasets:
1.  `Daily New Cases as Percent of State Population = New Cases/State Population`
2.  `New Cases in Last 14 Days = Sum(New Cases) Between Submit Date and Previous 13 Dates`
3.  `New Cases in Last 14 Days as Percent of State Population = Cases Last 14 Days/State Population`


# <a name="dashboard"></a>Plotly Dash Dashboard
This interactive Plotly Dash dashboard displays reported U.S. COVID-19 cases in line graphs, bar charts, and bubble maps. 
Interactive features including selecting Dates, Date Ranges, and filtering on States are created with Dash callbacks.  

The Python code for this dashboard is [`covid-dash-app.py`](./covid-dash-app.py)


# <a name="gcp-app"></a>Deploy Dashboard Using GCP App Engine
Google Cloud Platform provides documentation for [Building a Python 3 App on App Engine](https://cloud.google.com/appengine/docs/standard/python3/building-app).  

The project directory must have the following file structure to deploy on GCP AppEngine:  
- `project-directory/`
	- `app.yaml`
	- `main.py` (called `covid-dash-app.py` in this project)
	- `requirements.txt`
	- `static/` (called `assets/` in this project)
        - `style.css`
		- `favicon.ico`

Please refer to individual files for details

# License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md)

[Back to Top](#table-of-contents)