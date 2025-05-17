from contextlib import contextmanager
from mysql.connector.pooling import MySQLConnectionPool
import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error

# 환경 변수 로드
load_dotenv(verbose=True)

class MySQLConnection:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MySQLConnection, cls).__new__(cls)
            cls._instance._init_pool()
        return cls._instance
    
    def _init_pool(self):
        """MySQL 연결 풀 초기화"""
        if self._pool is None:
            print("=== MySQL 설정 확인 ===")
            dbconfig = {
                "host": os.getenv('MYSQL_HOST'),
                "port": int(os.getenv('MYSQL_PORT', 3306)),
                "user": os.getenv('MYSQL_USER'),
                "password": os.getenv('MYSQL_PASSWORD'),
                "database": os.getenv('MYSQL_DB_NAME'),
            }
            print(f"MySQL Host: {dbconfig['host']}")
            print(f"MySQL Port: {dbconfig['port']}")
            print(f"MySQL Database: {dbconfig['database']}")
            print("=====================")

            try:
                self._pool = MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=10,
                    **dbconfig
                )
                print("MySQL 연결 풀 생성 완료!")
            except Error as e:
                print(f"MySQL 연결 풀 생성 실패: {e}")
                raise
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결을 가져오는 컨텍스트 매니저"""
        conn = self._pool.get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """SQL 쿼리 실행"""
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

    def check_connection(self):
        """MySQL 연결 상태 확인"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    print("MySQL 연결 성공!")
                    return True
        except Error as e:
            print(f"MySQL 연결 실패: {e}")
            print("MySQL이 실행 중인지 확인해주세요.")
            raise
