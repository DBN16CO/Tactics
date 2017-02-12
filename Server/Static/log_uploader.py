
from __future__ import print_function
import httplib2
import os
from datetime import datetime

from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = tools.argparser.parse_args([])
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Tactics Server Log Uploader'
TACTICS_LOG_FOLDER = '0B5q4eSlDOuaxVFRISDA4S3doT0E'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

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

def upload_logs():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    file_metadata = {
        'name': 'trace.log-%s' % str(datetime.now()),
        'parents': [ TACTICS_LOG_FOLDER ]

    }
    media = MediaFileUpload('../trace.log',
                        mimetype='text/plain')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print("File ID: %s" % file.get('id'))

    file_metadata = {
        'name': 'matchmaking.log-%s' % str(datetime.now()),
        'parents': [ TACTICS_LOG_FOLDER ]

    }
    media = MediaFileUpload('../matchmaking.log',
                        mimetype='text/plain')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print("File ID: %s" % file.get('id'))

if __name__ == '__main__':
    upload_logs()