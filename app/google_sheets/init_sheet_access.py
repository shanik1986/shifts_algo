import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import json

def get_google_sheet_data(sheet_name, tab_name):
    # Define the scope and authenticate
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # First, try to get credentials from environment variable
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        if creds_json:
            # Parse the JSON string from environment variable
            creds_dict = json.loads(creds_json)
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Fallback to file for local development
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            credentials_path = os.path.join(project_root, 'google sheets access key.json')
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    
        # Authorize the client
        client = gspread.authorize(credentials)

        # Open the sheet by name and access a specific tab
        sheet = client.open(sheet_name)
        worksheet = sheet.worksheet(tab_name)

        # Get all data from the worksheet
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
        
    except Exception as e:
        print(f"Error accessing Google Sheets: {str(e)}")
        raise
