from prometheus_client import Counter, Histogram

# 평가 관련 메트릭
EVALUATION_DURATION = Histogram(
    'evaluation_duration_seconds',
    'Time spent evaluating answers',
    ['method']
)

EVALUATION_COUNTER = Counter(
    'evaluation_total',
    'Total number of evaluations',
    ['method', 'status']
)

EVALUATION_ERROR_COUNTER = Counter(
    'evaluation_errors_total',
    'Total number of evaluation errors',
    ['method', 'error_type']
)