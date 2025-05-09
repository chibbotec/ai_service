
import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()

class MySQLConnection:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MySQLConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def __init__(self):
        if not self.connection:
            self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', 'root123414'),
                database=os.getenv('MYSQL_DB_NAME', 'chibbo_interview')
            )
            print("MySQL 데이터베이스 연결 성공")
        except Error as e:
            print(f"Error: MySQL 연결 실패: {e}")
            raise e

    def get_connection(self):
        if self.connection and self.connection.is_connected():
            return self.connection
        self.connect()
        return self.connection

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL 연결이 종료되었습니다.")

    def execute_query(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            # SELECT 쿼리인 경우
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return result
            # INSERT, UPDATE, DELETE 쿼리인 경우
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Error as e:
            print(f"Error: 쿼리 실행 실패: {e}")
            if self.connection:
                self.connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()