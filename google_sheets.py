import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from professor import Professor
from google_sheets_util import get_from_row

# based on https://developers.google.com/sheets/api/quickstart/python

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets' # read-write access
CLIENT_SECRET_FILE = 'google_api_client_secret.json'
APPLICATION_NAME = 'Kellogg Research Productivity'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = '.credentials'
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com_client.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class GoogleSheets:
    SHEET_ID = '1TT3l1CKt2GLG_ZUJOV2F7RHGBIECsgnGJLO7hQ0Y_qI'

    def __init__(self):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        self.service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

    def get_range(self, range):
        return self.service.spreadsheets().values().get(
            spreadsheetId=self.SHEET_ID, range=range).execute().get('values', [])

    def read_profs(self):
        """:return: a list of Professor objects"""
        values = self.get_range('Professors')
        print("read %d rows" % len(values))
        profs = []
        if not values:
            print('No data found.')
        else:
            saw_header = False;
            for row in values:
                if not saw_header:
                    saw_header = True
                    continue
                # skip hidden rows
                if get_from_row(row, 7) is not None:
                    continue
                profs.append(Professor.from_spreadsheet_row(row))
        return profs

    def save_prof(self, prof):
        data = {'values':[prof.spreadsheet_row()]}
        row = self.get_row_for_prof(prof)
        if row is None:
            # append new row
            self.service.spreadsheets().values().append(spreadsheetId=self.SHEET_ID,
                                                        valueInputOption='RAW',
                                                        insertDataOption="INSERT_ROWS",
                                                        range='Professors',
                                                        body=data).execute()
        else:
            # update row
            self.service.spreadsheets().values().update(spreadsheetId=self.SHEET_ID,
                                                        valueInputOption='RAW',
                                                        range='Professors!%d:%d' % (row, row),
                                                        body=data).execute()

    def update_profs(self, profs):
        """This only works if all the professors have already been saved to the spreadsheet."""
        rows = self.get_rows_for_profs(profs)
        updates = []
        i=0
        for p in profs:
            updates.append({'range':'Professors!%d:%d' % (rows[i], rows[i]),
                            'values':[p.spreadsheet_row()]})
            i += 1
        # batch update
        body = {
            'valueInputOption':'RAW',
            'data':updates
        }
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SHEET_ID,
                                                         body=body).execute()

    def append_profs(self, profs):
        """!!!: only call this if all the profs are new.  It will not try to update any rows, just append to the bottom."""
        data_values = []
        for p in profs:
            data_values.append(p.spreadsheet_row())
        self.service.spreadsheets().values().append(spreadsheetId=self.SHEET_ID,
                                                    valueInputOption='RAW',
                                                    insertDataOption="INSERT_ROWS",
                                                    range='Professors',
                                                    body={'values':data_values}).execute()

    def get_row_for_prof(self, prof):
        return self.get_rows_for_profs([prof])[0]

    def get_rows_for_profs(self, profs):
        row_indices = []
        values = self.get_range('Professors') # get all the cells
        for p in profs:
            i = 1 # cells are one-indexed
            matching_i = None
            for row in values:
                if (row[0] == p.slug()):
                    matching_i = i
                    break
                i += 1
            row_indices.append(matching_i)
        return row_indices

if __name__ == '__main__':
    gs = GoogleSheets()
    gs.read_profs()
