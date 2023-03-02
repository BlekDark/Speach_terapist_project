from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build

import datetime
import os
import io

from utils import db_connection, get_credentials, get_list_name


# авторизация пользователя
def user_authorization(user_id, tg_id):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"SELECT full_name FROM `Users` WHERE id = {int(user_id)} && tg_id IS NULL")
        result = cursor.fetchall()
        if result == (()):
            connection.close()
            raise Exception(
                "Код некорректный")

        cursor.execute(
            f"UPDATE Users SET enable = FALSE WHERE tg_id = '{int(tg_id)}'")
        cursor.execute(
            f"UPDATE Users SET tg_id={int(tg_id)}, enable = TRUE WHERE id = {int(user_id)}")
        connection.commit()
        connection.close()
    except:
        connection.close()
        raise Exception(
            "Попробуйте позже или обратитесь к администратору. Ошибка: 3508")
    return result[0][0]


# Переключение пользователя
def switch_user(full_name, tg_id):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"SELECT full_name FROM Users WHERE tg_id = {tg_id} AND full_name = '{full_name}'")
        result = cursor.fetchall()
        if result == (()):
            connection.close()
            return
        cursor.execute(
            f"UPDATE Users SET enable = TRUE WHERE tg_id = {tg_id} AND full_name = '{full_name}'")
        cursor.execute(
            f"UPDATE Users SET enable = FALSE WHERE tg_id = {tg_id} AND full_name != '{full_name}'")
        connection.commit()
        connection.close()
    except:
        connection.close()


def get_users(tg_id):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"SELECT full_name, enable FROM `Users` WHERE tg_id = {tg_id}")
        result = cursor.fetchall()
        if result == (()):
            connection.close()
            raise Exception(
                "Для использования введите код, который вам сообщил логопед")
        connection.close()
        users = list(result)
        for user in users:
            user = {"full_name": user[0], "enable": user[1]}
        return users
    except:
        connection.close()
        raise Exception(
            "Попробуйте позже или обратитесь к администратору. Ошибка: 3508")


def get_active_user(tg_id):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"SELECT full_name, id FROM `Users` WHERE tg_id = {int(tg_id)} &&  enable = TRUE")
        result = cursor.fetchall()
        if result == (()):
            connection.close()
            raise Exception(
                "Для использования введите код, который вам сообщил логопед")
        full_name = result[0][0]
        id = result[0][1]
        return full_name, id
    except:
        connection.close()
        raise Exception(
            "Попробуйте позже или обратитесь к администратору. Ошибка: 3508")


def add_folder(name, id=None):
    credentials = get_credentials()
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if id != None:
        file_metadata['parents'] = [id]
    file = service.files().create(body=file_metadata, fields='id'
                                  ).execute()
    id = file.get('id')
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"INSERT INTO Folders (name, link) VALUES ('{name}', '{id}')")
        connection.commit()
        connection.close()
    except:
        connection.close()
        raise Exception(
            "Попробуйте позже или обратитесь к администратору. Ошибка: 3508")
    return id


def get_folder():
    connection = db_connection()
    cursor = connection.cursor()
    date = datetime.datetime.now()
    name_folder = f"{date.month}.{date.year}"
    try:
        cursor.execute(
            f"SELECT link FROM `Folders` WHERE name = '{name_folder}'")
        response_folder_sql = cursor.fetchall()
    except:
        connection.close()
        raise Exception(
            "Попробуйте позже или обратитесь к администратору. Ошибка: 3508")
    if response_folder_sql == (()):
        try:
            id_folder = add_folder(name_folder, os.environ.get("ROOT_FOLDER"))
        except Exception as e:
            raise e
    else:
        id_folder = response_folder_sql[0][0]
    return id_folder


def save_voice_to_google_drive(downloaded_file, list_name):
    date = str(datetime.datetime.now())
    date = date.replace(':', '_')
    name_downloaded_file = f'{list_name}_{date}.ogg'
    try:
        id_folder = get_folder()
    except Exception as e:
        raise e
    credentials = get_credentials()
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': name_downloaded_file, 'parents': [id_folder]}
    media = MediaIoBaseUpload(io.BytesIO(
        downloaded_file), mimetype='audio/ogg', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media,
                                  fields='webViewLink').execute()
    return file["webViewLink"]


def save_to_google_sheets(link, full_name, id):
    credentials = get_credentials()
    SAMPLE_SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
    service = build(
        'sheets', 'v4', credentials=credentials).spreadsheets().values()
    date = str(datetime.datetime.now())
    date = date.replace(':', '_')
    array = {'values': [
        [full_name, date, link]]}
    list_name = get_list_name(full_name, id)
    service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=list_name,
        valueInputOption='USER_ENTERED',
        body=array
    ).execute()
