import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

database = mysql.connector.connect(
    host = "localhost",
    user = user,
    passwd = password,
)

cursorObject = database.cursor()

cursorObject.execute("CREATE DATABASE ecommerce")

print("Db connected")