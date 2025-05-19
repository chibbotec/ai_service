import os
from dotenv import load_dotenv
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

# 환경 변수 로드
load_dotenv(verbose=True)

class RedisConnection:
    _instance = None
    _broker = None
    _result_backend = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisConnection, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance
    
    def _init_connection(self):
        """Redis 연결 및 Dramatiq 설정 초기화"""
        print("=== Redis 설정 확인 ===")
        redis_config = {
            "host": os.getenv('REDIS_HOST', 'localhost'),
            "port": int(os.getenv('REDIS_PORT', 6379)),
            "db": int(os.getenv('REDIS_DB', 0)),
            "password": os.getenv('REDIS_PASSWORD', None)
        }
        print(f"Redis Host: {redis_config['host']}")
        print(f"Redis Port: {redis_config['port']}")
        print(f"Redis DB: {redis_config['db']}")
        print("=====================")

        try:
            # Redis URL 구성
            redis_url = f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
            if redis_config['password']:
                redis_url = f"redis://:{redis_config['password']}@{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"

            # Dramatiq 설정
            self._broker = RedisBroker(url=redis_url)
            self._result_backend = RedisBackend(url=redis_url)
            self._broker.add_middleware(Results(backend=self._result_backend))
            dramatiq.set_broker(self._broker)
            
            print("Redis 연결 및 Dramatiq 설정 완료!")
        except Exception as e:
            print(f"Redis 연결 실패: {e}")
            raise

    def get_broker(self):
        """Dramatiq broker 반환"""
        return self._broker

    def get_result_backend(self):
        """Dramatiq result backend 반환"""
        return self._result_backend

    async def check_connection(self):
        """Redis 연결 상태 확인"""
        try:
            # Redis 연결 테스트
            self._broker.client.ping()
            print("Redis 연결 성공!")
            return True
        except Exception as e:
            print(f"Redis 연결 실패: {e}")
            print("Redis가 실행 중인지 확인해주세요.")
            raise

    def close(self):
        """Redis 연결 종료"""
        if self._broker:
            self._broker.close()