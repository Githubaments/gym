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
exercises = list(set([d['Exercise'] for d in workout_data]))
latest_weights = []

for exercise in exercises:
    # Filter the data by exercise and sort by date in descending order
    exercise_data = [d for d in workout_data if d['Exercise'] == exercise]
    exercise_data.sort(key=lambda x: x['Date'], reverse=True)

    # Extract the latest weight for the exercise
    latest_weight = [exercise_data[0]['Set 1'], exercise_data[0]['Set 2'], exercise_data[0]['Set 3']]
    latest_weights.append(latest_weight)

# Display the data in a Streamlit app
st.write('Exercises:', exercises)
st.write('Latest weights:', latest_weights)
