import os, sys

def get_resource_path(relative_path):
    """PyInstaller 환경과 개발 환경에서 리소스 파일의 경로를 반환합니다."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def get_exe_directory():
    """현재 실행 중인 스크립트 또는 실행 파일의 디렉토리를 반환합니다."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_user_data_path(filename):
    """실행 파일 위치의 '.user_data' 디렉토리에 파일의 전체 경로를 반환합니다."""
    user_data_dir = os.path.join(get_exe_directory(), '.user_data')
    os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, filename)

def load_data(filename):
    """사용자 데이터 디렉토리에서 파일을 로드하거나, 없으면 리소스 디렉토리에서 로드합니다."""
    user_data_path = get_user_data_path(filename)
    if os.path.exists(user_data_path):
        print(f"사용자 경로에서 데이터 로드: {user_data_path}")
        return user_data_path
    else:
        resource_path = get_resource_path(filename)
        print(f"리소스 경로에서 데이터 로드: {resource_path}")
        return resource_path