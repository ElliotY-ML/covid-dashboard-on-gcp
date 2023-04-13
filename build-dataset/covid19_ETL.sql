/* SQL query to combine CDC Covid 19 Cases, Census ACS 5-year Survey Results, 
and ANSI State Codes.  Calculations for 
1. new covid cases as percentage of population for individual states
2. sum of new covid cases on a 14-day basis, as a percentage of population for individual states    

Query was completed on Google Cloud Platform BigQuery.  The tables were named for files as follows:
1. datasets/United_States_COVID-19_Cases_and_Deaths_by_State_over_Time.csv AS `cdc_covid_cases_Jan_13`
2. datasets/ACSST5Y2019.S0101_2022-01-14T1743264/ACSST5Y2019.S0101_data_with_overlays_2021-12-10T154120.csv AS `acs_5Y_2019` 
3. datasets/state_abbrev.txt AS `state_abbreviations`
*/

WITH 
    data_cleaned AS(
        SELECT 
            CAST(REPLACE(submission_date, '/', '-') AS DATE FORMAT 'MM-DD-YYYY') AS submit_date,
            CASE
                WHEN state='NYC' THEN 'NY'
                ELSE state
                END AS state_n,
            SUM(CAST(REPLACE(tot_cases, ',','') AS INT64)) AS tot_cases,
            SUM(CAST(REPLACE(conf_cases, ',','') AS INT64)) as conf_cases,
            SUM(CAST(REPLACE(prob_cases, ',','') AS INT64)) as prob_cases,
            SUM(CAST(REPLACE(new_case, ',','') AS INT64)) as new_case,
            SUM(CAST(REPLACE(pnew_case, ',','') AS INT64)) as pnew_case,
            SUM(CAST(REPLACE(tot_death, ',','') AS INT64)) as tot_death,
            SUM(CAST(REPLACE(conf_death, ',','') AS INT64)) as conf_death,
            SUM(CAST(REPLACE(prob_death, ',','') AS INT64)) as prob_death,
            SUM(CAST(REPLACE(new_death, ',','') AS INT64)) AS new_death,
            SUM(CAST(REPLACE(pnew_death, ',','') AS INT64)) AS pnew_death
        FROM
            `coursera-analytics-class.covid_by_percent.cdc_covid_cases_Jan_19`  --change dataset Date
        GROUP BY 
            state_n, submit_date
	),
    rolling_cases AS(
        SELECT 
            submit_date,
            state_n,
            SUM(new_case) OVER(
                PARTITION BY state_n
                ORDER BY submit_date ASC
                ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
            ) AS sum_cases_last_14_days
        FROM
            data_cleaned
        ORDER BY 
            submit_date DESC
	),

	-- Merge sum_cases_last_14_days into other data.

    cases_by_state AS(
        SELECT 
            cdc.submit_date,
            state_n AS state,
            SUM(cdc.tot_cases) AS total_cases,
            SUM(cdc.new_case) AS new_cases,
            SUM(cdc.tot_death) AS total_deaths,
            SUM(cdc.new_death) AS new_deaths
        FROM
            data_cleaned as cdc 
        GROUP BY
            state, submit_date
        ORDER BY 
            submit_date DESC
	),
    state_population AS(    
        SELECT 
            acs.*, abb.STUSAB as state_abb
        FROM
            `coursera-analytics-class.covid_by_percent.acs_5Y_2019` AS acs
        INNER JOIN 
            `coursera-analytics-class.covid_by_percent.state_abbreviations` as abb
        ON acs.Geographic_Area_Name=abb.STATE_NAME 
	)


SELECT 
    cs.*,
    rc.sum_cases_last_14_days,
    pop.Estimate__Total__Total_population AS state_pop,
    cs.new_cases/pop.Estimate__Total__Total_population AS new_cases_percent,
    rc.sum_cases_last_14_days/pop.Estimate__Total__Total_population AS cases_last_14_pop_percent 
FROM 
    cases_by_state AS cs
INNER JOIN 
    rolling_cases AS rc
ON 
    cs.submit_date=rc.submit_date AND cs.state=rc.state_n
LEFT JOIN 
    state_population AS pop
ON 
    cs.state=pop.state_abb
ORDER BY 
    cs.submit_date DESC 
