import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# Authenticate and authorize the API client with your service account key
creds = Credentials.from_service_account_file('path/to/your/service_account_key.json')
client = gspread.authorize(creds)

# Open the Google Sheet by name
sheet = client.open('MySheetName').sheet1

# Read the data from the sheet
data = sheet.get_all_records()

# Display the data in a Streamlit app
st.write(data)
