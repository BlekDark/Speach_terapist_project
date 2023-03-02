from googleapiclient.discovery import build
import os
from utils import get_credentials, db_connection


# Добавление листа в таблицу
def add_list_to_google_table(list_name):
    credentials = get_credentials()
    spredsheat_id = os.environ.get("SPREADSHEET_ID")
    service = build(
        'sheets', 'v4', credentials=credentials).spreadsheets()
    data = {
        'requests': [
            {
                'addSheet': {
                    'properties': {'title': list_name}
                }
            }
        ]
    }
    service.batchUpdate(
        spreadsheetId=spredsheat_id,
        body=data
    ).execute()

    array = {'values': [
        ['ФИО', 'Дата', 'ссылка']]}
    service.values().append(
        spreadsheetId=spredsheat_id,
        range=list_name,
        valueInputOption='USER_ENTERED',
        body=array
    ).execute()
    return


# получение кода регистрации
def get_user_code(full_name):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"INSERT INTO Users (full_name) VALUES ('{full_name}')")
        cursor.execute(
            f"SELECT id FROM `Users` WHERE full_name = '{full_name}' && tg_id IS NULL")
        id = str(cursor.fetchall()[0][0])
        connection.commit()
        connection.close()
    except:
        connection.close()
        raise Exception(
            "ошибка при запросе к базе данных в методе get_user_code")
    return id


def delete_tg_id_for_db(user_id):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"SELECT full_name FROM `Users` WHERE id = {int(user_id)}")
        result = cursor.fetchall()
        if result == (()):
            connection.close()
            raise Exception(
                "Ошибка при удалении пользователя: пользователя с таким id нет")
        cursor.execute(
            f"UPDATE Users SET tg_id = 0 WHERE id = {int(user_id)}")
        connection.commit()
        connection.close()
    except:
        connection.close()
        raise Exception(
            "ошибка при запросе к базе данных в методе delete_tg_id_for_db")
    return result[0][0]
