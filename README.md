# Chicago Taxi Trips Data Analysis

## Motivation :
The purpose of this project is to analyze and get insight about taxi cab demand and fare by time and location in Chicage. The insight can be used to predict taxi transportation metrics like taxi trip miles, duration, fare as well as staff scheduling and eventually help Chicago taxi cab companies to optimize their revenue. 

## Data and Workflow:

- Data Acquisition - Soda API
- Data Storage - SQL, SQLAlchemy
- Data Process - Python 
- Web App - Streamlit

The data is collected from the [City of Chicago Transportation](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew/data) website by using SODA API and saved to SQL database. The project covers over 2million trip information data from January, 2021 to October, 2021. 
Next the EDA is conducted in Python with sqlalchemy, pandas, seaborn, matplot libraries. Finally, the web app is created with Streamlit. 

![Chicage Taxi Trip Analysis](/app.png)


