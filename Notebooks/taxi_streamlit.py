import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl

import datetime 
from datetime import timedelta

import calendar
import seaborn as sns
from matplotlib import rcParams
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from bokeh.plotting import figure, show
import pydeck as pdk



st.set_page_config(layout="wide")
#layout the top section of the app

from PIL import Image


with open("trips_2021.pkl", "rb") as f:
    data = pkl.load(f)


with open("trips_agg.pkl", "rb") as f:
    data_agg = pkl.load(f)
df_agg=data_agg.copy()

#Data Processing    
convert_dict = {'trip_seconds': 'float32', 
                'trip_miles': 'float32', 
                'dropoff_community_area': 'float32',
                'fare': 'float32', 
                'trip_total': 'float32',
                'dropoff_centroid_latitude': 'float32',
                'dropoff_centroid_longitude': 'float32',
                'pickup_community_area': 'float32',
                'pickup_centroid_latitude': 'float32',
                'pickup_centroid_longitude': 'float32'}
  


df_full = data.astype(convert_dict)
    
df_full['trip_start_timestamp'] = pd.to_datetime(df_full["trip_start_timestamp"], format="%Y-%m-%dT%H:%M:%S.%f")
df_full['trip_date'] = df_full['trip_start_timestamp'].dt.date
df_full['trip_day'] = (df_full['trip_start_timestamp']).dt.day_name()

df_full['trip_month'] = df_full['trip_start_timestamp'].dt.month_name()





df_full=df_full.assign(timezone=pd.cut(df_full['trip_start_timestamp'].dt.hour,
                            [0,6,12,18,23],
                            labels=['Night','Morning','Afternoon','Evening'],
                            include_lowest=True))


#st.set_page_config(layout="wide")




with st.container():
    row1_1,row1_2,row1_3 = st.columns((1,2,2))




    with row1_1:
    
        st.write('''
        ## Chicago Taxi Trips Analysis 
        Data 
        Taxi trip database can be reached from [City of Chicago Transportation website] (https://data.cityofchicago.org/Transportation). This data includes trip information between 2021-01-01 and 2021-10-01.
        By sliding the slider you can explore trips information in different time periods.
         ''')#This documentation provides a basic exploratory analysis to get insights about the taxi trips data to help applying machine learning techniques on the data set.  

        st.write('Select Trip Info')
        months = df_full['trip_month'].unique()
        time_zone = df_full['timezone'].unique()
        metrics = ['Total trips', 'Total fare', 'Total miles']
        #pickup_zone =set( df['pickup_community_area'])
        #companys = df['company'].unique()

        month_choice = st.selectbox('Month:', months)
    
        time_choice = st.selectbox('Time of day', time_zone)
    #st.write('time',time_choice)
    #timezone_dict =dict(zip(time_zone, range(0,5)))
    #time_z = timezone_dict.get(time_choice, 2)
    #st.write('time',time_choice)
    #st.write('time',type(time_z))
   
    
    #metric_choice = st.selectbox('Metric',metrics)
    
    #pickup_choice = st.selectbox('Pickup Zone', pickup_zone)
    #company_choice = st.selectbox('Company', companys)




    with row1_2:
        pic=df_full.loc[(df_full['trip_month'] == month_choice) &(df_full['timezone']==time_choice)].groupby('pickup_community_area').trip_id.count().reset_index().sort_values('trip_id',ascending= False).head(5)
        fig3 = px.bar(pic, x="trip_id", y="pickup_community_area", orientation='h',labels={'trip_id': 'Number of trips','pickup_community_area':'Pickup community area'}, title="Total number of trips over the selected period")
        fig3.update_yaxes(type='category')
        st.plotly_chart(fig3)
    with row1_3:
        df_day_in = df_full.groupby(['trip_month','timezone','trip_day']).agg({'trip_id':'count', 'fare':'sum','trip_seconds':'sum'}).reset_index()
        df_day = (df_day_in[(df_day_in['trip_month'] == month_choice) &(df_day_in['timezone']== time_choice)])
        df_day['Fare/Hour'] = df_day['fare']*3600/df_day['trip_seconds']
        df_day.rename(columns={'trip_day': 'Day'}, inplace=True)
        df_day = df_day[['Day', 'Fare/Hour']]
        pic4=df_day.groupby('Day')['Fare/Hour'].mean().reset_index()
        fig4 = px.bar(pic4, x="Fare/Hour", y="Day", orientation='h',title="Average Fare per Hour over the selected period")
        st.plotly_chart(fig4)   
        
  #LAYOUT THE MIDDLE SECTION 
row2_1, row2_2,row2_3 = st.columns((1,1,2))  
with row2_1:
    st.write('''Pickup Location ''')
    map_pickup = df_full.loc[(df_full['trip_month'] == month_choice) &(df_full['timezone']==time_choice), ['pickup_centroid_latitude', 'pickup_centroid_longitude']]
    map_pickup.rename(columns={'pickup_centroid_latitude': 'latitude', 'pickup_centroid_longitude': 'longitude'}, inplace=True)
    st.map(map_pickup)
    
with row2_2:
    st.write('''Drop-off Location ''')
    map_dropoff = df_full.loc[(df_full['trip_month'] == month_choice) &(df_full['timezone']==time_choice), ['dropoff_centroid_latitude', 'dropoff_centroid_longitude']]
    map_dropoff.rename(columns={'dropoff_centroid_latitude': 'latitude', 'dropoff_centroid_longitude': 'longitude'}, inplace=True)
    st.map(map_pickup)   
    


    
with row2_3:
    df_com_in = df_full.groupby(['trip_month','timezone','company']).agg({'trip_id':'count', 'fare':'sum','trip_miles':'sum'}).reset_index()

    df_com = (df_com_in[(df_com_in['trip_month'] == month_choice) &(df_com_in['timezone']== time_choice)])
    df_com = df_com.sort_values('trip_id', ascending=False).head(5)
    df_com['Fare/Mile'] = df_com['fare']/df_com['trip_miles']
    df_com['Mile/Trip'] = df_com['trip_miles']/df_com['trip_id']
    #df_com['Fare/Hour'] = df_com['fare']*3600/df_com['trip_seconds'].map('{:,.2f}'.format)
    df_com.rename(columns={'company': 'Company','trip_id': 'Total'}, inplace=True)
    df_com = df_com[['Company', 'Total', 'Fare/Mile','Mile/Trip']]    
    df_com['Fare/Mile'] = df_com['Fare/Mile'].map('{:,.2f}'.format)
    df_com['Mile/Trip'] = df_com['Mile/Trip'].map('{:,.2f}'.format)
    
    #st.write('Taxi Company Metrics')
    fig1 = go.Figure(data=[go.Table(
            header=dict(values=list(df_com.columns),
    #                 line_color='darkslategreen',
                    fill_color='lightskyblue',
                    align='center'),
            cells=dict(values=[list(df_com['Company']),
                        list(df_com['Total']),
                        list(df_com['Fare/Mile']),
                        list(df_com['Mile/Trip'])],
    #                line_color='darkslategray',
    #                fill_color='lightcyan',
                    align=['left','center']))
            ])
    fig1.update_layout(title='Taxi Company Metrics', autosize=True)
    st.plotly_chart(fig1)
    #st.dataframe(dummy)
        

    
 



        