import pymysql
import os
from dotenv import load_dotenv


load_dotenv()
os.environ
# Подключение к БД, удаление! старой бд и создание новой
connection = pymysql.connect(host=os.environ.get("HOST_BD"), port=int(os.environ.get("PORT_BD")), user=os.environ.get(
    "LOGIN_BD"), passwd=os.environ.get("PASSWORD_BD"), database=os.environ.get("TABLENAME_BD"))
cursor = connection.cursor()
try:
    cursor.execute("DROP TABLE IF EXISTS Users")
    cursor.execute("DROP TABLE IF EXISTS Folders")
    print("DROP 200")
except:
    print("error when drop tables")
try:
    cursor.execute(
        "CREATE TABLE Users (id INT AUTO_INCREMENT PRIMARY KEY, full_name VARCHAR(100) NOT NULL, tg_id VARCHAR(100), enable BOOLEAN);")
    cursor.execute(
        "CREATE TABLE Folders (name VARCHAR(100) PRIMARY KEY, link TEXT);")
    print("CREATE 200")
except:
    print("error when create tables")

connection.close()
