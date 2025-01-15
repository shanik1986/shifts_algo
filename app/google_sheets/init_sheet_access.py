import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# Google Sheets API setup
def get_google_sheet_data(sheet_name, tab_name):
    # Define the scope and authenticate
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Get the directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up to the root project directory (remove one dirname call)
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # Construct the path to the credentials file
    credentials_path = os.path.join(project_root, 'google sheets access key.json')

    # Load credentials from the JSON key file
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    
    # Authorize the client
    client = gspread.authorize(credentials)

# Open the sheet by name and access a specific tab
    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(tab_name)

    # Get all data from the worksheet
    data = worksheet.get_all_records()
    return pd.DataFrame(data)
