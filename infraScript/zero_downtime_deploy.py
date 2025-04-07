#!/usr/bin/env python3

import os
import subprocess
import sys
import time
import requests
import socket

# 기본 경로 설정
BASE_DIR = "/dockerProjects/chibbotec/coding_test_service"

def run_command(command):
    """명령어를 실행하고 결과를 출력합니다."""
    print(f"실행: {command}")
    process = subprocess.run(command, shell=True, text=True, capture_output=True)
    if process.stdout:
        print(process.stdout)
    if process.stderr and process.returncode != 0:
        print(f"오류: {process.stderr}")
    return process.returncode == 0

def setup_directories():
    """필요한 디렉토리 구조를 생성합니다."""
    print("필요한 디렉토리 생성 중...")
    
    # OnlineJudge 관련 디렉토리
    os.makedirs(f"{BASE_DIR}/OnlineJudge/data/test_case", exist_ok=True)
    
    # 로그 및 실행 디렉토리
    os.makedirs(f"{BASE_DIR}/log", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/run", exist_ok=True)
    
    print("디렉토리 생성 완료")

def pull_images():
    """GitHub Container Registry에서 최신 이미지를 가져옵니다."""
    print("OnlineJudge 이미지 가져오는 중...")
    if not run_command("docker pull --pull always ghcr.io/chibbotec/onlinejudge:latest"):
        print("OnlineJudge 이미지 가져오기 실패")
        return False
    
    print("JudgeServer 이미지 가져오는 중...")
    if not run_command("docker pull --pull always ghcr.io/chibbotec/judgeserver:latest"):
        print("JudgeServer 이미지 가져오기 실패")
        return False
    
    print("이미지 가져오기 완료")
    return True

def deploy_containers():
    """컨테이너를 배포합니다."""
    # 작업 디렉토리로 이동
    os.chdir(BASE_DIR)
    
    print("컨테이너 배포 중...")
    if not run_command("docker-compose up -d"):
        print("컨테이너 배포 실패")
        return False
    
    return True

def wait_for_service(service_name, url, max_attempts=30, interval=5):
    """서비스가 정상적으로 실행될 때까지 대기합니다."""
    print(f"{service_name} 서비스 준비 상태 확인 중...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"{service_name} 서비스가 준비되었습니다 (시도 {attempt}/{max_attempts})")
                return True
            else:
                print(f"{service_name} 서비스 응답: HTTP {response.status_code} (시도 {attempt}/{max_attempts})")
        except requests.RequestException as e:
            print(f"{service_name} 서비스 확인 중 오류: {e} (시도 {attempt}/{max_attempts})")
        
        if attempt < max_attempts:
            print(f"{interval}초 후 다시 시도합니다...")
            time.sleep(interval)
    
    print(f"{service_name} 서비스가 준비되지 않았습니다. 최대 시도 횟수 초과.")
    return False

def check_container_status(container_name):
    """Docker 컨테이너의 상태를 확인합니다."""
    command = f"docker inspect --format='{{{{.State.Status}}}}' {container_name}"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    
    if result.returncode != 0:
        print(f"컨테이너 {container_name} 상태 확인 실패: {result.stderr}")
        return None
    
    status = result.stdout.strip()
    return status

def wait_for_container_health(container_name, max_attempts=30, interval=5):
    """컨테이너의 헬스체크 상태가 healthy가 될 때까지 대기합니다."""
    print(f"{container_name} 컨테이너의 헬스체크 상태 확인 중...")
    
    for attempt in range(1, max_attempts + 1):
        command = f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name}"
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        
        if result.returncode != 0:
            print(f"컨테이너 {container_name} 헬스체크 상태 확인 실패: {result.stderr}")
            
            # 컨테이너가 존재하는지 확인
            status = check_container_status(container_name)
            if status is None:
                print(f"컨테이너 {container_name}가 존재하지 않습니다.")
                return False
            if status != "running":
                print(f"컨테이너 {container_name}가 실행 중이 아닙니다. 현재 상태: {status}")
                return False
                
            # 헬스체크가 설정되지 않은 경우 컨테이너가 실행 중이면 정상으로 간주
            print(f"컨테이너 {container_name}에 헬스체크가 설정되지 않았을 수 있습니다. 컨테이너는 실행 중입니다.")
            return True
        
        health_status = result.stdout.strip()
        print(f"{container_name} 헬스체크 상태: {health_status} (시도 {attempt}/{max_attempts})")
        
        if health_status == "healthy":
            print(f"{container_name} 컨테이너가 정상 상태입니다.")
            return True
        
        if attempt < max_attempts:
            print(f"{interval}초 후 다시 확인합니다...")
            time.sleep(interval)
    
    print(f"{container_name} 컨테이너가 정상 상태가 되지 않았습니다. 최대 시도 횟수 초과.")
    return False

def check_service_availability():
    """배포된 서비스가 정상적으로 실행되고 있는지 확인합니다."""
    print("\n서비스 가용성 확인 중...")
    
    # 컨테이너 상태 확인
    run_command("docker ps")
    
    # OnlineJudge 컨테이너 헬스체크
    if not wait_for_container_health("onlinejudge-instance", max_attempts=12, interval=10):
        print("OnlineJudge 컨테이너의 헬스체크에 실패했습니다.")
        return False
    
    # 포트 연결 확인
    print("\n서비스 포트 확인 중...")
    
    # OnlineJudge 웹 서비스 (9050 포트)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('localhost', 9050))
    s.close()
    if result == 0:
        print("OnlineJudge 웹 서비스 (9050 포트): 연결 성공")
    else:
        print("OnlineJudge 웹 서비스 (9050 포트): 연결 실패")
        return False
    
    # JudgeServer (12358 포트)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('localhost', 12358))
    s.close()
    if result == 0:
        print("JudgeServer (12358 포트): 연결 성공")
    else:
        print("JudgeServer (12358 포트): 연결 실패")
        return False
    
    print("모든 서비스가 정상적으로 실행 중입니다.")
    return True

def main():
    """배포 과정의 메인 함수입니다."""
    print("===== OnlineJudge 시스템 배포 시작 =====")
    
    # 1. 필요한 디렉토리 생성
    setup_directories()
    
    # 2. 최신 이미지 가져오기
    if not pull_images():
        print("이미지 가져오기에 실패했습니다. 배포를 중단합니다.")
        return False
    
    # 3. 컨테이너 배포
    if not deploy_containers():
        print("컨테이너 배포에 실패했습니다.")
        return False
    
    # 4. 서비스 가용성 확인
    if not check_service_availability():
        print("서비스 가용성 확인에 실패했습니다. 배포가 완료되었지만, 서비스가 정상적으로 작동하지 않을 수 있습니다.")
        return False
    
    print("===== 배포 완료 =====")
    print("OnlineJudge 웹 인터페이스: http://localhost:9050")
    print("Judge 서버: http://localhost:12358")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)