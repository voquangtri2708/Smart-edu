import mysql.connector
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy thông tin từ biến môi trường
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
SQL_FILE = os.getenv("SQL_FILE")

# Kiểm tra file SQL có tồn tại không
if not os.path.isfile(SQL_FILE):
    print(f"Error: File SQL '{SQL_FILE}' not exists!")
    exit(1)

try:
    # Kết nối MySQL (chưa chọn database)
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = connection.cursor()

    # Tạo database nếu chưa tồn tại
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
    print(f"Database '{DB_NAME}' đã được tạo hoặc đã tồn tại.")

    # Chọn database vừa tạo
    connection.database = DB_NAME

    # Đọc nội dung file SQL
    with open(SQL_FILE, "r", encoding="utf-8") as file:
        sql_commands = file.read()

    # Chạy các câu lệnh SQL trong file
    for command in sql_commands.split(";"):
        command = command.strip()
        if command:
            cursor.execute(command)

    connection.commit()
    print(f"File SQL '{SQL_FILE}' đã được thực thi thành công!")

except mysql.connector.Error as e:
    print(f"Lỗi MySQL: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
    print("🔄 Đã đóng kết nối MySQL.")
