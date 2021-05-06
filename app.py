import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

import csv
import requests

CSV_URL = 'https://cdn-ps-la-1.ufile.io/get/hnbkp59d?token=MmY0ZTk2ZTcxMWEzMWQwYWZiNDZiMTNiODdhMjZmMzAxMDFlNjY0ODQ1Zjc0ODY4N2NkOGFlZjJkZDgzZTllNjAyOWRlZTdlNjczMWQ3ZDFkOWFjYjU2NzQ4ZDJlZjZhM2ExNTgxODM5OTBiNDY4Mjc5OTE1ZDUyZmM4ZjRmMzBRbmVWZlVDeGNTTXJZczNHZ2JralVRZlJIVncxVlBDOEUvY2hPTjMweWMzKzZzRXNJQWkzVjcvQ1FvR3JoaW9Uelc2Nys3eExEUnFRUEFoeDh6S1c5TVN6Tk5MS3lPOFJqWmxlZ0UwTGgrWW1aNWZpdjBzSjI3dXNuWS9oNkNlVHRHVzlpa2tFTWI5M2MvQ3ZHejRBV0E1czBib2VxSWJhanc3WWd2clFyNG1kZTFoeTd0Szk4QkF3R1NnUEg5c3pVNkJ5dUNmZ243ZG94VW5JUG9JL2dHTHBUUmFwN3FwWXZZeUIwWEZseGdJPQ=='
with requests.Session() as s:
    download = s.get(CSV_URL)

    decoded_content = download.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    df = pd.DataFrame(my_list)
    
df.to_csv('Motor_Vehicle_Collisions_-_Crashes.csv', index = False)
    
DATA_URL = (
    "Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application s a streamlit dashboard that can be used to analyze motor Vehicle Collisions in NYC ðŸ—½")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates= [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data


st.header("Where are most people injured in nyc")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0,19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))


st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collision between %i:00 and %i:00" % (hour,(hour + 1)%24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
    "latitude": midpoint[0],
    "longitude": midpoint[1],
    "zoom": 11,
    "pitch": 50,
    },
    layers = [
       pdk.Layer(
       "HexagonLayer",
       data= data[['date/time', 'latitude', 'longitude']],
       get_position=['longitude', 'latitude'],
       radius=100, #radius of hexagon
       extruded=True, #3-d visulations
       pickable=True,
       elevation_range=[0,1000],
       ),
    ]
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour,(hour+1)))
filtered = data[
    (data['date/time'].dt.hour >= hour ) & (data['date/time'].dt.hour <( hour+1 ))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range= (0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select=st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrains':
    st.write(original_data.query("injured_pedstrains >=1")[["on_street_name", "injured_pedstrains"]].sort_values(by=['injured_pedstrains'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >=1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclistss'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >=1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False):
	st.subheader('Raw Data')
	st.write(data)
