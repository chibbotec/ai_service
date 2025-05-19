import dramatiq
from app.db.redis import RedisConnection
from app.services.interview.evaluate import evaluate_single_answer

# Redis 연결 초기화
redis_conn = RedisConnection()

if __name__ == "__main__":
    dramatiq.run()