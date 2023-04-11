import streamlit as st
import gspread
import pandas as pd
from google.oauth2 import service_account

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[        "https://www.googleapis.com/auth/spreadsheets",        "https://www.googleapis.com/auth/drive",    ],
)

st.markdown(
    '<div style="text-align: center;">'
    'This text will be center-justified.'
    '</div>',
    unsafe_allow_html=True
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

# define default values for previous input values
previous_values = {}
for exercise in df['Exercise'].unique():
    previous_values[exercise] = {
        'weight': df[df['Exercise'] == exercise]['Weight'].values[0],
        'set1': df[df['Exercise'] == exercise]['Set 1'].values[0],
        'set2': df[df['Exercise'] == exercise]['Set 2'].values[0],
        'set3': df[df['Exercise'] == exercise]['Set 3'].values[0],
    }

# display inputs for each exercise
for exercise in df['Exercise'].unique():
    st.markdown(f'<div style="text-align: center;">{exercise}</div>', unsafe_allow_html=True)



    # define default values for the input fields
    weight = previous_values[exercise]['weight']
    set1 = previous_values[exercise]['set1']
    set2 = previous_values[exercise]['set2']
    set3 = previous_values[exercise]['set3']

    if exercise == 'Plate':
        col1, col2 = st.beta_columns(2)
        for i in range(1, 4):
            if previous_values[exercise][f'set{i}'] != "":
                set_val = previous_values[exercise][f'set{i}']
                set_val = set_val.split('x') if set_val else ['', '']
                set_val1 = col1.number_input(f'Weight {i}', value=int(set_val[0]), key=f'{exercise}-set{i}-1')
                set_val2 = col2.number_input(f'Reps {i}', value=int(set_val[1]), key=f'{exercise}-set{i}-2')
                previous_values[exercise][f'set{i}'] = f'{set_val1}x{set_val2}'
            else:
                set_val1 = col1.number_input(f'Weight {i}', value=0, key=f'{exercise}-set{i}-1')
                set_val2 = col2.number_input(f'Reps {i}', value=0, key=f'{exercise}-set{i}-2')
    else:
        previous_values[exercise] = {
            'weight': float(weight) if isinstance(weight, (int, float)) else 0,
            'set1': int(set1) if isinstance(set1, (int, float)) else 0,
            'set2': int(set2) if isinstance(set2, (int, float)) else 0,
            'set3': int(set3) if isinstance(set3, (int, float)) else 0,
        }

        weight = st.number_input('Weight', value=previous_values[exercise]['weight'],step =1.0,  key=f'{exercise}-weight')
        set1 = st.number_input('Set 1', value=previous_values[exercise]['set1'], key=f'{exercise}-set1')
        set2 = st.number_input('Set 2', value=previous_values[exercise]['set2'], key=f'{exercise}-set2')
        set3 = st.number_input('Set 3', value=previous_values[exercise]['set3'] key=f'{exercise}-set3')
