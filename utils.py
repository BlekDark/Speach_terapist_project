import pymysql

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import os


def get_list_name(full_name, id):
    while len(id) < 4:
        id = "0" + id
    return f"{full_name} {str(id)}"


def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file(
            'token.json', SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_drive.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    return credentials


def db_connection():
    connection = pymysql.connect(host=os.environ.get("HOST_BD"), port=int(os.environ.get("PORT_BD")), user=os.environ.get(
        "LOGIN_BD"), passwd=os.environ.get("PASSWORD_BD"), database=os.environ.get("TABLENAME_BD"))
    return connection
