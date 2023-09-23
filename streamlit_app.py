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

# Full list exercises
exercise_list = [''] + list(df['Exercise'].unique()) 

# Convert Dates
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

# change the format of the dates to dd/mm/yy
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
df['Date'] = df['Date'].dt.date


# Allow the user to choose a workout to filter by
selected_workout = st.selectbox('Select a workout', df['Workout'].unique().tolist())

# Filter the data by the selected workout
df_workout = df[df['Workout'] == selected_workout]


st.write(df_workout)
latest_date = df_workout['Date'].max()
df_date = df_workout[df_workout['Date'] == latest_date]

st.write(df_date)

# create an empty list to hold the user input data
user_data = []

# define default values for previous input values
previous_values = {}
for exercise in df_date['Exercise'].unique():
    previous_values[exercise] = {
        'weight': df_date[df_date['Exercise'] == exercise]['Weight'].values[0],
        'set1': df_date[df_date['Exercise'] == exercise]['Set 1'].values[0],
        'set2': df_date[df_date['Exercise'] == exercise]['Set 2'].values[0],
        'set3': df_date[df_date['Exercise'] == exercise]['Set 3'].values[0],
    }

# display inputs for each exercise
for exercise in df_date['Exercise'].unique():
    st.markdown(f'<div style="text-align: center;">{exercise}</div>', unsafe_allow_html=True)



    # define default values for the input fields
    weight = previous_values[exercise]['weight']
    set1 = previous_values[exercise]['set1']
    set2 = previous_values[exercise]['set2']
    set3 = previous_values[exercise]['set3']

    if exercise == 'Plate':
        col1, col2 = st.columns(2)
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
        try:
            weight = st.number_input('Weight', value=previous_values[exercise]['weight'],step=0.5, key=f'{exercise}-weight')

        except:
            weight = st.number_input('Weight', value=previous_values[exercise]['weight'], key=f'{exercise}-weight')
        set1 = st.number_input('Set 1', value=previous_values[exercise]['set1'], key=f'{exercise}-set1')
        set2 = st.number_input('Set 2', value=previous_values[exercise]['set2'], key=f'{exercise}-set2')
        set3 = st.number_input('Set 3', value=previous_values[exercise]['set3'], key=f'{exercise}-set3')

  # create a dictionary to hold the user input values for this exercise
    user_input = {
        'Workout': selected_workout,
        'Date': latest_date,
        'Exercise': exercise,
        'Weight': weight,
        'Set 1': set1,
        'Set 2': set2,
        'Set 3': set3
    }
    
    # add the user input dictionary to the list of user data
    user_data.append(user_input)
    



# create a new DataFrame with the user input data
new_df = pd.DataFrame(user_data)
new_df['Date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
new_df['Workout'] = selected_workout
new_df['Comments'] = ''
# Reorder columns
new_df = new_df[['Date', 'Workout', 'Exercise', 'Weight', 'Set 1', 'Set 2', 'Set 3', 'Comments']]




selected_exercise = st.selectbox('Exercise', exercise_list)

if selected_exercise != '':
    latest_row = df.loc[df['Exercise'] == selected_exercise].iloc[-1]
    st.write(latest_row)
    # Create an empty dictionary to store the selected values
    selected_values = {}
    # Create number input for weight
    weight = st.number_input('Weight:', value=0, step=1)

    # Create number inputs for sets
    set1 = st.number_input('Set 1:', value=0, step=1)
    set2 = st.number_input('Set 2:', value=0, step=1)
    set3 = st.number_input('Set 3:', value=0, step=1)
    
    extra_user_input = {
        'Date': latest_date,
        'Workout': selected_workout,
        'Exercise': selected_exercise,
        'Weight': weight,
        'Set 1': set1,
        'Set 2': set2,
        'Set 3': set3
    }
    new_df = new_df.append(extra_user_input, ignore_index=True)


new_df = st.experimental_data_editor(new_df)



with st.form(key='my_form'):
    if st.form_submit_button(label="Submit"):
        try:
            new_df = new_df.fillna(0)
            new_df["Weight"] = new_df["Weight"].astype(str)
    
                update_details = f"{selected_workout} ({latest_date})"
            # Get the number of rows that have data
            num_rows = len(worksheet.get_all_values())
            
            # Calculate the starting cell for new data (considering the header is only added once)
            start_cell = f"A{num_rows + 2}" if num_rows > 0 else "A1"
            
            # Append the data
            if num_rows == 0:
                # If the sheet is empty, also include the headers
                worksheet.update(start_cell, [new_df.columns.values.tolist()] + new_df.values.tolist())
            else:
                # Otherwise, just append the data rows
                worksheet.update(start_cell, new_df.values.tolist())
    
    
                st.write(f"New data written to sheet: {update_details}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

