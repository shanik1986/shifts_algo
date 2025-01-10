import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets API setup
def get_google_sheet_data(sheet_name, tab_name):
    # Define the scope and authenticate
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Load credentials from the JSON key file
    credentials = ServiceAccountCredentials.from_json_keyfile_name('google sheets access key.json', scope)
    
    # Authorize the client
    client = gspread.authorize(credentials)

# Open the sheet by name and access a specific tab
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(tab_name)

    # Get all data from the worksheet
    data = worksheet.get_all_records()
    return pd.DataFrame(data)
