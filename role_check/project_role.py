import gspread
from google.oauth2.service_account import Credentials

class RoleChecker() :

    def __init__(self) :
        return
    
    def get_values(self) :


        # 서비스 계정 인증 범위 설정
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        # JSON 키 파일 경로 설정
        json_keyfile = 'sacred-flash-391009-e274ab063b25.json'  # 실제 파일 경로로 변경하세요

        # 자격 증명 생성
        credentials = Credentials.from_service_account_file(json_keyfile, scopes=scopes)

        # gspread 클라이언트 생성
        gc = gspread.authorize(credentials)

        # 스프레드시트 열기 (스프레드시트 URL 또는 ID 필요)
        spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1OrU5zjwyB7qeZ4JSHf61iaYMfZxOzAEkX7nXHI_Bfr8/edit?usp=sharing')  # 실제 스프레드시트 URL로 변경하세요

        # 워크시트 선택
        worksheet = spreadsheet.worksheet('1인 1역 체크')  # 또는 worksheet = spreadsheet.worksheet('Sheet1')

        values = worksheet.get('F4:F30')
        names = worksheet.get('B4:B30')
        roles = worksheet.get('C4:C30')

        role_dict = {}
        for i, n in enumerate(names) :
             print(n)
             role_dict[n[0]] = roles[i][0]
        miss_role = [cell[0] for cell in values]  # 각 행의 첫 번째 요소를 가져옵니다.
        
        data = []
        for m in miss_role :
            data.append(f"{m} - {role_dict[m]}")

        return data