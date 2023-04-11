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

# Iterate through the exercises and generate input boxes for each set
for exercise in exercises:
    st.write(exercise)
    weight = st.number_input('Weight', value=previous_values[exercise]['weight'])
    set1 = st.number_input('Set 1', value=previous_values[exercise]['set1'])
    set2 = st.number_input('Set 2', value=previous_values[exercise]['set2'])
    set3 = st.number_input('Set 3', value=previous_values[exercise]['set3'])
    
    # Store the user input values for each set in a dictionary
    input_values.append({'Exercise': exercise, 'Weight': weight, 'Set 1': set1, 'Set 2': set2, 'Set 3': set3})
    
    # Update the previous values dictionary with the current values
    previous_values[exercise]['weight'] = weight
    previous_values[exercise]['set1'] = set1
    previous_values[exercise]['set2'] = set2
    previous_values[exercise]['set3'] = set3
