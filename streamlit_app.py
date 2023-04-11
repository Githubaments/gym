import streamlit as st
import gspread
import pandas as pd
from google.oauth2 import service_account

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[        "https://www.googleapis.com/auth/spreadsheets",        "https://www.googleapis.com/auth/drive",    ],
)


gc = gspread.authorize(credentials)

# Open the Google Sheet by name
sheet = gc.open('Gym Log').sheet1

# Read the data from the sheet
data = sheet.get_all_records()

# Extract the workout names
workouts = list(set([d['Workout'] for d in data]))

# Create Dataframe
df = pd.DataFrame(data)

# Convert Dates
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

# change the format of the dates to dd/mm/yy
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
df['Date'] = df['Date'].dt.date


# Allow the user to choose a workout to filter by
selected_workout = st.sidebar.selectbox('Select a workout', df['Workout'].unique().tolist())

# Filter the data by the selected workout
df = df[df['Workout'] == selected_workout]

# Filter by last dated workout

st.write(df)
latest_date = df['Date'].max()
df = df[df['Date'] == latest_date]

st.write(df)



# Create a list of exercises for the selected workout
exercises = list(set([d['Exercise'] for d in data if d['Workout'] == selected_workout]))

# Create a dictionary to store the previous values for each exercise
previous_values = {e: {'weight': None, 'set1': None, 'set2': None, 'set3': None} for e in exercises}

# Create a list to store the user input values
input_values = []

previous_values = {}
for _, row in df.iterrows():
    exercise = row['Exercise']
    if exercise not in previous_values:
        previous_values[exercise] = {'weight': 0, 'set1': 0, 'set2': 0, 'set3': 0}
    previous_values[exercise]['weight'] = row['Weight']
    previous_values[exercise]['set1'] = row['Set 1']
    previous_values[exercise]['set2'] = row['Set 2']
    previous_values[exercise]['set3'] = row['Set 3']

# Allow the user to input new values for each exercise
for exercise in previous_values:
    st.write(f'## {exercise}')
    weight = previous_values[exercise]['weight']
    if isinstance(weight, (int, float)):
        weight = st.number_input('Weight', value=weight)
    else:
        weight = st.number_input('Weight', value=0)
        
    set1 = previous_values[exercise]['set1']
    if isinstance(set1, (int, float)):
        set1 = st.number_input('Set 1', value=set1)
    else:
        set1 = st.number_input('Set 1', value=0)
        
    set2 = previous_values[exercise]['set2']
    if isinstance(set2, (int, float)):
        set2 = st.number_input('Set 2', value=set2)
    else:
        set2 = st.number_input('Set 2', value=0)
        
    set3 = previous_values[exercise]['set3']
    if isinstance(set3, (int, float)):
        set3 = st.number_input('Set 3', value=set3)
    else:
        set3 = st.number_input('Set 3', value=0)

    # Do something with the new values (e.g. update the Google Sheet)
    st.write(f'Weight: {weight}, Set 1: {set1}, Set 2: {set2}, Set 3: {set3}')

