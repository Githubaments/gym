import streamlit as st
import gspread
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

# Allow the user to choose a workout to filter by
selected_workout = st.sidebar.selectbox('Select a workout', workouts)

# Filter the data by the selected workout
workout_data = [d for d in data if d['Workout'] == selected_workout]

# Extract the exercises, weights, and sets data
exercises = [d['Exercise'] for d in workout_data]
weights = [[d['Set 1'], d['Set 2'], d['Set 3']] for d in workout_data]

# Display the data in a Streamlit app
st.write('Exercises:', exercises)
st.write('Weights:', weights)
