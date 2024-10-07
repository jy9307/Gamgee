import os, sys, json, shutil

def get_resource_path(relative_path):
    """PyInstaller 환경과 개발 환경에서 리소스 파일의 경로를 반환합니다."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def get_exe_directory():
    """현재 실행 중인 스크립트 또는 실행 파일의 디렉토리를 반환합니다."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def file_check(dir,filename) :
    data_dir = os.path.join(get_exe_directory(), dir) # 현재 디렉토리 확인
    return os.path.exists(os.path.join(data_dir, filename))

def load_data(filename, last_dir='.user_data'):
    """사용자 데이터 디렉토리에서 파일을 로드하거나, 없으면 리소스 디렉토리에서 로드합니다."""

    # 현재 디렉토리의 상위 디렉토리 확인
    current_dir = get_exe_directory()
    parent_dir = os.path.dirname(current_dir)  # 상위 디렉토리

    data_dir = os.path.join(parent_dir, last_dir)  # 상위 디렉토리에 last_dir 추가
    os.makedirs(data_dir, exist_ok=True)  # 디렉토리가 없으면 생성

    # 대상 파일 경로 설정
    data_path = os.path.join(data_dir, filename)

    if os.path.exists(data_path):
        print(f"사용자 경로에서 데이터 로드: {data_path}")
        return data_path
    else:
        resource_path = get_resource_path(filename)
        print(f"리소스 경로에서 데이터 로드: {resource_path}")
        return resource_path
  
def save_data(source_file_path, filename, last_dir='.user_data'):
    """사용자 데이터 디렉토리에 파일을 복사해서 저장합니다."""

    data_dir = os.path.join(get_exe_directory(), last_dir) # 현재 디렉토리 확인
    os.makedirs(data_dir, exist_ok=True)  # 디렉토리가 없으면 생성

    # 대상 파일 경로 설정
    destination_path = os.path.join(data_dir, filename)

    # shutil을 사용하여 파일 복사
    shutil.copy(source_file_path, destination_path)
    print(f"파일이 복사되었습니다: {destination_path}")

    return destination_path

def load_setting() :
    json_path = load_data('settings.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data

def save_setting(data) :
    json_path = load_data('settings.json')
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"설정이 저장되었습니다: {json_path}")