#!/usr/bin/env python3

import os
import requests
import subprocess
import time
from typing import Dict, Optional


class ServiceManager:
    # 초기화 함수
    def __init__(self, socat_port: int = 9090, sleep_duration: int = 3) -> None:
        self.socat_port: int = socat_port
        self.sleep_duration: int = sleep_duration
        self.services: Dict[str, int] = {
            'ai_service_1': 9091,
            'ai_service_2': 9092
        }
        self.current_name: Optional[str] = None
        self.current_port: Optional[int] = None
        self.next_name: Optional[str] = None
        self.next_port: Optional[int] = None

    # 현재 실행 중인 서비스를 찾는 함수
    def _find_current_service(self) -> None:
        cmd: str = f"ps aux | grep 'socat -t0 TCP-LISTEN:{self.socat_port}' | grep -v grep | awk '{{print $NF}}'"
        current_service: str = subprocess.getoutput(cmd)
        if not current_service:
            self.current_name, self.current_port = 'ai_service_2', self.services['ai_service_2']
        else:
            self.current_port = int(current_service.split(':')[-1])
            self.current_name = next((name for name, port in self.services.items() if port == self.current_port), None)

    # 다음에 실행할 서비스를 찾는 함수
    def _find_next_service(self) -> None:
        self.next_name, self.next_port = next(
            ((name, port) for name, port in self.services.items() if name != self.current_name),
            (None, None)
        )

    # Docker 컨테이너를 제거하는 함수
    def _remove_container(self, name: str) -> None:
        os.system(f"docker stop {name} 2> /dev/null")
        os.system(f"docker rm -f {name} 2> /dev/null")

    # 명령 실행 및 로깅 헬퍼 함수
    def _run_command(self, cmd: str, log_output: bool = True) -> str:
        output = subprocess.getoutput(cmd)
        return output

    def _cleanup_dangling_images(self) -> None:
        # 특정 이미지 중 <none> 태그가 된 이미지만 정리
        cmd_list = "docker images | grep '.*/chibbotec/ai_service' | grep '<none>'"
        images = self._run_command(cmd_list)

        if not images:
            print("정리할 이미지가 없습니다.")
            return

        # 이미지 정리
        cmd_remove = "docker images | grep '.*/chibbotec/ai_service' | grep '<none>' | awk '{print $3}' | xargs -r docker rmi"
        output = self._run_command(cmd_remove)
        print("이미지 정리 완료")

        # 정리 후 이미지 목록 다시 확인
        remaining = self._run_command(cmd_list)
        if remaining:
            print("일부 이미지가 정리되지 않았습니다.")

    # Docker 컨테이너를 실행하는 함수
    def _run_container(self, name: str, port: int) -> None:
        os.system(
            f"docker run -d --name={name} --network=chibbotec-network "
            f"--network-alias=ai "
            f"--restart unless-stopped -p {port}:9090 -e TZ=Asia/Seoul "
            f"-e DB_HOST=172.30.1.23 -e DB_PORT=3306 -e DB_NAME=chibbo_interview -e DB_USER=root -e DB_PASSWORD=your_password "
            f"-v /dockerProjects/chibbotec/resume_service/repository/data:/app/repository/data "
            f"--pull always ghcr.io/chibbotec/ai_service")

    def _switch_port(self) -> None:
        # Socat 포트를 전환하는 함수
        cmd: str = f"ps aux | grep 'socat -t0 TCP-LISTEN:{self.socat_port}' | grep -v grep | awk '{{print $2}}'"
        pid: str = subprocess.getoutput(cmd)

        if pid:
            os.system(f"kill -9 {pid} 2>/dev/null")

        time.sleep(5)

        os.system(
            f"nohup socat -t0 TCP-LISTEN:{self.socat_port},fork,reuseaddr TCP:localhost:{self.next_port} &>/dev/null &")

    # 서비스 상태를 확인하는 함수
    def _is_service_up(self, port: int) -> bool:
        url = f"http://127.0.0.1:{port}/api/v1/health"  # FastAPI 헬스체크 엔드포인트로 조정
        try:
            response = requests.get(url, timeout=5)  # 5초 이내 응답 없으면 예외 발생
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        return False

    # 서비스를 업데이트하는 함수
    def update_service(self) -> None:
        self._find_current_service()
        self._find_next_service()

        self._remove_container(self.next_name)
        self._cleanup_dangling_images()
        self._run_container(self.next_name, self.next_port)

        # 새 서비스가 'UP' 상태가 될 때까지 기다림
        retry_count = 0
        max_retries = 20
        while not self._is_service_up(self.next_port) and retry_count < max_retries:
            print(f"Waiting for {self.next_name} to be 'UP'... (시도 {retry_count+1}/{max_retries})")
            time.sleep(self.sleep_duration)
            retry_count += 1
# ㅇㅇ
        if retry_count >= max_retries:
            print(f"ERROR: {self.next_name}가 {max_retries*self.sleep_duration}초 이내에 시작되지 않았습니다.")
            return
        
        # Dramatiq 워커 실행 (기존 컨테이너에서)
        os.system(f"docker exec -d {self.next_name} bash -c 'PYTHONPATH=/app dramatiq app.workers.evaluation_worker --processes 4 --threads 4 --no-prometheus'")
        print(f"Dramatiq 워커 실행 완료: {self.next_name}")
        
        self._switch_port()

        if self.current_name is not None:
            self._remove_container(self.current_name)

        print("Switched service successfully!")


if __name__ == "__main__":
    manager = ServiceManager()
    manager.update_service()