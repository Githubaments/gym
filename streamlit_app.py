import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)


# Open the Google Sheet by name
sheet = conn.open('Gym').sheet1

# Read the data from the sheet
data = sheet.get_all_records()

# Display the data in a Streamlit app
st.write(data)
