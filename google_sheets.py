import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from professor import Professor

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

def get_from_row(row, column_idx):
    """get the value from the specified column index, or return None if it's empty"""
    if (len(row) <= column_idx) or row[column_idx] == "":
        return None
    return row[column_idx]

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
                profs.append(Professor(name=get_from_row(row,2),
                                       school=get_from_row(row, 1),
                                       title=get_from_row(row,3),
                                       cv_url=get_from_row(row,4),
                                       graduation_year=get_from_row(row,5),
                                       staff_id=get_from_row(row,6),
                                       google_scholar_url=get_from_row(row,8),
                                       alt_name=get_from_row(row,9),
                                       graduation_school=get_from_row(row,10)))
        return profs

    def save_prof(self, prof):
        data = {'values':[[prof.slug(),
                           prof.school,
                           prof.name,
                           prof.title,
                           prof.cv_url,
                           prof.graduation_year,
                           prof.staff_id,
                           None, # hidden
                           prof.google_scholar_url,
                           prof.alt_name,
                           prof.graduation_school]]}
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

    # TODO: cache these results to make it more efficient
    def get_row_for_prof(self, prof):
        values = self.get_range('Professors') # get all the cells
        i = 1 # cells are one-indexed
        for row in values:
            if (row[0] == prof.slug()):
                return i
            i += 1
        return None

if __name__ == '__main__':
    gs = GoogleSheets()
    gs.read_profs()
