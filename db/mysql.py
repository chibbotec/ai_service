from contextlib import contextmanager
from mysql.connector.pooling import MySQLConnectionPool
import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error

class MySQLConnection:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MySQLConnection, cls).__new__(cls)
            cls._instance._init_pool()
        return cls._instance
    
    def _init_pool(self):
        if self._pool is None:
            dbconfig = {
                "host": os.getenv('MYSQL_HOST'),
                "port": int(os.getenv('MYSQL_PORT', 3306)),
                "user": os.getenv('MYSQL_USER'),
                "password": os.getenv('MYSQL_PASSWORD'),
                "database": os.getenv('MYSQL_DB_NAME'),
            }
            self._pool = MySQLConnectionPool(
                pool_name="mypool",
                pool_size=10,
                **dbconfig
            )
    
    # asynccontextmanager 대신 일반 contextmanager 사용
    @contextmanager
    def get_connection(self):
        conn = self._pool.get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    # async 제거
    def execute_query(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    return result
                else:
                    conn.commit()
                    return cursor.rowcount
            finally:
                cursor.close()