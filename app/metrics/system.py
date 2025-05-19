from prometheus_client import Gauge
import psutil
import os

# 시스템 리소스 메트릭
CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU 사용률',
    ['method']
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    '메모리 사용량',
    ['method']
)

def update_system_metrics(method: str):
    process = psutil.Process(os.getpid())
    CPU_USAGE.labels(method=method).set(process.cpu_percent())
    MEMORY_USAGE.labels(method=method).set(process.memory_info().rss)