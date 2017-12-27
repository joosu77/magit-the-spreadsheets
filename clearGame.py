import gspread
from oauth2client.service_account import ServiceAccountCredentials


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("mtg").worksheet("Field")

# Extract and print all of the values
for i in range(5):
    sheet.update_cell(2,3+i,'')
    sheet.update_cell(10,3+i,'')
for i in range(20):
    for o in range(6):
        sheet.update_cell(3+o,4+i,'')
        sheet.update_cell(11+o,4+i,'')
    
    