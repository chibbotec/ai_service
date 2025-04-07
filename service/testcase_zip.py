import os
import zipfile

async def create_simple_test_case_zip(test_case_id: str, testcases: list) -> str:
    # 현재 디렉토리에 파일 생성
    current_dir = os.getcwd()
    zip_path = os.path.join(current_dir, f"{test_case_id}.zip")
    
    # 임시 파일 경로 생성 (현재 디렉토리 내)
    temp_dir = os.path.join(current_dir, f"{test_case_id}")
    os.makedirs(temp_dir, exist_ok=True)
    
    # 테스트 케이스 파일 생성
    for test_case in testcases:
        for file_name, content in test_case.items():
            file_path = os.path.join(temp_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
    
    # zip 파일 생성
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for test_case in testcases:
            for file_name in test_case.keys():
                file_path = os.path.join(temp_dir, file_name)
                # ZIP 파일 내 경로는 파일명만 사용 (디렉토리 경로 없이)
                zip_file.write(file_path, arcname=file_name)
    
    # 임시 파일 정리 (선택 사항)
    # import shutil
    # shutil.rmtree(temp_dir)
    
    return zip_path