from prometheus_client import Counter, Histogram, Gauge

# API 성능 메트릭
API_RESPONSE_TIME = Histogram(
    'api_response_time_seconds',
    'API 응답 시간',
    ['endpoint', 'method']
)

API_REQUESTS_TOTAL = Counter(
    'api_requests_total',
    '총 API 요청 수',
    ['endpoint', 'method', 'status']
)

REQUEST_TIMESTAMP = Gauge(
    'request_timestamp',
    '요청 타임스탬프',
    ['endpoint', 'method']
)