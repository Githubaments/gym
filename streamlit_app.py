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


# Loop through each exercise and show its details
for exercise in exercises:
    st.write(exercise)
    st.write('-' * len(exercise))
    
    # Get the previous values for this exercise
    if exercise in previous_values:
        weight = float(previous_values[exercise]['weight'])
        set1 = int(previous_values[exercise]['set1'])
        set2 = int(previous_values[exercise]['set2'])
        set3 = int(previous_values[exercise]['set3'])
    else:
        weight = 0.0
        set1 = 0
        set2 = 0
        set3 = 0
    
    # Create number input boxes for weight and sets
    weight = st.number_input('Weight', value=weight, key=f'{exercise}-weight')
    set1 = st.number_input('Set 1', value=set1, key=f'{exercise}-set1', min_value=0, max_value=100, step=1)
    set2 = st.number_input('Set 2', value=set2, key=f'{exercise}-set2', min_value=0, max_value=100, step=1)
    set3 = st.number_input('Set 3', value=set3, key=f'{exercise}-set3', min_value=0, max_value=100, step=1)
    
    # Add the exercise details to the dataframe
    df = df.append({'Date': date.today(), 'Exercise': exercise, 'Weight': weight, 'Set 1': set1, 'Set 2': set2, 'Set 3': set3}, ignore_index=True)
