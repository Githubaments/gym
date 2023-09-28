import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
import plotly.graph_objects as go



# This function attempts to convert the value to an integer.
# If it fails, it returns a default value.
def safe_int_conversion(value, default_value=0):
    try:
        return int(value)
    except ValueError:
        return default_value
        

# Add custom CSS styles
st.markdown(
    """
    <style>
    /* Define CSS rules for mobile devices (screen width less than 600px) */
    @media (max-width: 600px) {
        .custom-columns {
            display: block;
        }
        .custom-column {
            width: 100%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive", ],
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
selected_workout = st.radio('Select a workout', df['Workout'].unique().tolist())

# Filter the data by the selected workout
df_workout = df[df['Workout'] == selected_workout]

# Option to view all data
with st.expander("Click to expand"):
    reversed_df = df_workout.iloc[::-1]
    st.write(reversed_df)

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
    st.markdown(f'<div style="text-align: center;"><strong>{exercise}</strong></div>', unsafe_allow_html=True)

    # define default values for the input fields
    weight = previous_values[exercise]['weight']
    set1 = previous_values[exercise]['set1']
    set2 = previous_values[exercise]['set2']
    set3 = previous_values[exercise]['set3']

    if exercise == 'Plate':
        col1, col2 = st.columns(2)
        # Apply custom CSS class to the columns
        
        col1.markdown('<div class="custom-columns custom-column">', unsafe_allow_html=True)
        col2.markdown('<div class="custom-columns custom-column">', unsafe_allow_html=True)

        
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
                previous_values[exercise][f'set{i}'] = f'{set_val1}x{set_val2}'


        user_input = {
            'Workout': selected_workout,
            'Date': latest_date,
            'Exercise': exercise,
            'Weight': None,
            'Set 1': previous_values['Plate']['set1'],
            'Set 2': previous_values['Plate']['set2'],
            'Set 3': previous_values['Plate']['set3'],
            "PO": "No"

        }



    else:
        previous_values[exercise] = {
            'weight': float(weight) if isinstance(weight, (int, float)) else 0,
            'set1': int(set1) if isinstance(set1, (int, float)) else 0,
            'set2': int(set2) if isinstance(set2, (int, float)) else 0,
            'set3': int(set3) if isinstance(set3, (int, float)) else 0,
        }

        # Fetch the value of Progressive Overload for the specific exercise
        progressive_overload = df_date[df_date['Exercise'] == exercise]['PO'].iloc[0]


        # Increment each integer by one
        if previous_values[exercise]['set1'] > 0: previous_values[exercise]['set1'] += 1
        if previous_values[exercise]['set2'] > 0: previous_values[exercise]['set1'] += 1
        if previous_values[exercise]['set3'] > 0: previous_values[exercise]['set1'] += 1
        
        if progressive_overload == "Yes":
            if set1 >= 12 and set2 >= 12 and set3 >= 12:
                # Set all integers to 6
                previous_values[exercise]['set1'] = previous_values[exercise]['set2'] = previous_values[exercise][
                    'set3'] = 6
                st.error("Progressive Overload. Increase the weight")
            else:
                pass
            
        try:
            weight = st.number_input('Weight', value=previous_values[exercise]['weight'], step=0.5,
                                     key=f'{exercise}-weight')

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
            'Set 3': set3,
            "PO": df_date[df_date['Exercise'] == exercise]['PO'].iloc[0]

        }

    # add the user input dictionary to the list of user data
    user_data.append(user_input)

# create a new DataFrame with the user input data
new_df = pd.DataFrame(user_data)
new_df['Date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
new_df['Workout'] = selected_workout
new_df['Comments'] = ''
# Reorder columns
new_df = new_df[['Date', 'Workout', 'Exercise', 'Weight', 'Set 1', 'Set 2', 'Set 3', 'PO','Comments']]


selected_exercise = st.selectbox('Exercise', exercise_list)

# Button to add a custom exercise
if st.button("Add Custom Exercise"):
    custom_exercise = st.text_input("Enter your exercise:")
    
    if custom_exercise:  # Check if it's not an empty string
        selected_exercise = custom_exercise


if selected_exercise != '':
    latest_row = df.loc[df['Exercise'] == selected_exercise].iloc[-1]
  #  st.markdown(f"**{latest_row}**")
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
        'Set 3': set3,
        "PO": df_date[df_date['Exercise'] == exercise]['PO'].iloc[0]

    }
    # Convert the dictionary to a DataFrame
    extra_user_input_df = pd.DataFrame([extra_user_input])

    # Concatenate with new_df
    new_df = pd.concat([new_df, extra_user_input_df], ignore_index=True)

new_df = st.data_editor(new_df)

with st.form(key='my_form'):
    if st.form_submit_button(label="Submit"):
        try:
            new_df = new_df.fillna(0)
            new_df["Weight"] = new_df["Weight"].astype(str)

            update_details = f"{selected_workout} ({latest_date})"
            # Get the number of rows that have data
            num_rows = len(sheet.get_all_values())

            # Calculate the starting cell for new data (considering the header is only added once)
            start_cell = f"A{num_rows + 1}" if num_rows > 0 else "A1"

            # Append the data
            if num_rows == 0:
                # If the sheet is empty, also include the headers
                sheet.update(start_cell, [new_df.columns.values.tolist()] + new_df.values.tolist())
            else:
                # Otherwise, just append the data rows
                sheet.update(start_cell, new_df.values.tolist())

                st.write(f"New data written to sheet: {update_details}")

        except Exception as e:
            st.error(f"An error occurred: {e}")



# Title
st.title('Workout Progression Visualization')

# Dropdown to select a specific workout
df = pd.DataFrame(data)

# Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Now format 'Date' column to string in 'YYYY-MM-DD' format
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')



# Filter data based on selected workout
df_workout = df[df['Workout'] == selected_workout]

# Filtering df_workout based on the values in "Exercise" of new_df
df_workout = df_workout[df_workout['Exercise'].isin(new_df['Exercise'])]


# Calculate the frequency of each exercise
exercise_counts = df_workout['Exercise'].value_counts()

# Sort exercises by frequency
sorted_exercises = exercise_counts.index.tolist()

# Plot for weights with user choice between line and dot
weight_plot_type = st.radio(f"Select plot type for weights:", ["Line", "Dot"])
    

for exercise in sorted_exercises:
    st.subheader(exercise)

    # Inside the loop, right after filtering the dataframe
    df_filtered = df_workout[df_workout['Exercise'] == exercise].copy(deep=True)  # Add .copy(deep=True)
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])

    
    if exercise != "Plate":
        # Simply copy the weight column for non-Plate exercises
        df_filtered['Weight_Num'] = df_filtered['Weight'].apply(safe_int_conversion)

        # Plot for reps using stacked bars
        trace1 = go.Bar(x=df_filtered['Date'], y=df_filtered['Set 1'], name='Set 1')
        trace2 = go.Bar(x=df_filtered['Date'], y=df_filtered['Set 2'], name='Set 2')
        trace3 = go.Bar(x=df_filtered['Date'], y=df_filtered['Set 3'], name='Set 3')

        layout = go.Layout(title='Reps Over Time for Selected Exercise', barmode='stack',
                   xaxis_title="Date", yaxis_title="Reps")

        fig_reps = go.Figure(data=[trace1, trace2, trace3], layout=layout)

        st.plotly_chart(fig_reps)



        if df_filtered['Weight_Num'].max() > 0:
            st.subheader(exercise)
            if weight_plot_type == "Line":
               fig_weights = px.line(df_filtered, x='Date', y='Weight_Num', title=f'Weight for {exercise}', labels={'Weight_Num': 'Weight'})
            else:
             fig_weights = px.scatter(df_filtered, x='Date', y='Weight_Num', title=f'Weight for {exercise}', labels={'Weight_Num': 'Weight'})
    
            st.plotly_chart(fig_weights)


    else:
        # Parse weight and reps from 'Set 1', 'Set 2', and 'Set 3'
        df_filtered[['Weight_Set1', 'Reps_Set1']] = df_filtered['Set 1'].str.split('x', expand=True)
        df_filtered[['Weight_Set2', 'Reps_Set2']] = df_filtered['Set 2'].str.split('x', expand=True)
        df_filtered[['Weight_Set3', 'Reps_Set3']] = df_filtered['Set 3'].str.split('x', expand=True)
    
        # Convert to integers for plotting
        weight_cols = ['Weight_Set1', 'Weight_Set2', 'Weight_Set3']
        reps_cols = ['Reps_Set1', 'Reps_Set2', 'Reps_Set3']
        
        df_filtered[["Set 1","Set 2","Set 3"]] = df_filtered[["Set 1","Set 2","Set 3"]].fillna(0)
        
        # Skip plotting if weights are zero
        if df_filtered[weight_cols].sum().sum() == 0:
            continue
    
        # Plot for weights using stacked bars
        fig_weights = px.bar(df_filtered, x='Date', y=weight_cols, title='Weight Over Time for Plate Exercise', height=400)
        st.plotly_chart(fig_weights)

        # Plot for reps using line chart
        fig_reps = px.line(df_filtered, x='Date', y=reps_cols, title='Reps Over Time for Plate Exercise', height=400)
        st.plotly_chart(fig_reps)
    
        






