FROM python:3.12-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 로그 디렉토리 생성
RUN mkdir -p /data/log/nginx

# Nginx 설정 복사
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Supervisor 설정 복사
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 포트 노출
EXPOSE 80

# Supervisor로 프로세스 실행
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]