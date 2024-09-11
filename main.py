import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QFrame, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontDatabase, QFont
from coursetrack import CourseTrack
import json

###----------------Tools-----------------------


# 리소스 파일 경로를 가져오는 함수
def get_resource_path(relative_path):
    """ PyInstaller에서 리소스를 접근할 수 있는 경로 반환 """
    try:
        # PyInstaller로 빌드된 경우
        base_path = sys._MEIPASS
    except AttributeError:
        # PyInstaller로 빌드되지 않은 경우 (개발 환경)
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_exe_directory():
    """ 현재 실행 중인 exe 파일의 디렉토리 반환 """
    if getattr(sys, 'frozen', False):  # PyInstaller로 빌드된 경우
        exe_dir = os.path.dirname(sys.executable)
    else:
        # 개발 중인 경우
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    return exe_dir

def get_user_data_path(filename):
    """ 현재 exe 파일이 위치한 디렉토리에 파일 저장 경로 반환 """
    exe_dir = get_exe_directory()
    user_data_dir = os.path.join(exe_dir, '.user_data')  # exe 파일 위치에 .gamgee_data 디렉토리 생성

    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)  # 디렉토리가 없을 경우 생성

    # 저장할 파일의 전체 경로 반환
    return os.path.join(user_data_dir, filename)

def load_data(filename):
    """ 사용자 데이터 또는 리소스 파일을 불러오는 함수 """
    # 먼저 사용자 데이터 디렉토리에서 파일이 있는지 확인
    user_data_path = get_user_data_path(filename)
    if os.path.exists(user_data_path):
        print(f"Loading data from user path: {user_data_path}")
        return user_data_path
    else:
        # 사용자 데이터가 없으면 리소스 파일에서 불러옴
        resource_path = get_resource_path(filename)
        print(f"Loading data from resource path: {resource_path}")
        return resource_path

##------------- GUI elements --------------

class ProgressDialog(QDialog):
    def __init__(self, thread, parent=None):
        super().__init__(parent)
        self.thread = thread
        self.setWindowTitle("진행 상황")

        # 항상 최상단에 표시되도록 설정
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        # 진행 상황을 표시할 라벨
        self.status_label = QLabel('진행 상황: 준비 중...')
        layout.addWidget(self.status_label)

        # 중지 버튼
        self.stop_button = QPushButton('중지', self)
        self.stop_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 14px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.stop_button.clicked.connect(self.stop_program)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    # 시그널을 받아서 진행 상황 업데이트
    def update_status(self, status):
        self.status_label.setText(status)  # 전달받은 메시지를 라벨에 표시

    # 프로그램 중지
    def stop_program(self):
        self.close()  # 프로그램 종료
        self.thread.stop()
        self.thread.quit()


class MyApp(QWidget):
    def __init__(self, saved_id, save_account):
        super().__init__()

        # 기존 설정 확인
        self.saved_id = saved_id
        self.save_account = save_account

        # 윈도우 기본 설정
        self.setWindowTitle('Gamgee v0.1-beta')

        self.setStyleSheet("background-color: #f0f0f0;")  # 배경색 설정

        # 레이아웃 설정
        main_layout = QVBoxLayout()

        self.combo_label = QLabel('현재까지 본 프로그램은 <중앙교육연수원>의 연수만을 지원합니다.')
        self.combo_label.setStyleSheet("font-size: 12px;")
        main_layout.addWidget(self.combo_label)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 강의 제목과 입력 창을 세로로 배치
        course_layout = QGridLayout()

        self.course_label = QLabel('강의 제목')
        course_layout.addWidget(self.course_label, 0, 0)

        self.course_input = QLineEdit(self)
        self.course_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                background-color: #ffffff;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
        """)
        course_layout.addWidget(self.course_input, 0, 1)

        self.course_help_label = QLabel('강의 제목에 포함된 단어 하나를 적어주세요. ex) 다문화, 안전')
        self.course_help_label.setStyleSheet("font-size: 12px;")
        course_layout.addWidget(self.course_help_label, 1, 0, 1, 2)

        # 메인 레이아웃에 추가
        main_layout.addLayout(course_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 입력 창 그리드 레이아웃 설정
        account_grid_layout = QGridLayout()

        # ID 입력 부분
        self.id_label = QLabel('ID')
        self.id_input = QLineEdit(self)
        self.id_input.setStyleSheet("""
        QLineEdit {
            padding: 5px;
            font-size: 14px;
            background-color: #ffffff;
            border: 2px solid #cccccc;
            border-radius: 5px;
        }
        """)

        account_grid_layout.addWidget(self.id_label, 0, 0)
        account_grid_layout.addWidget(self.id_input, 0, 1)

        # PW 입력 부분
        self.pw_label = QLabel('PW')
        self.pw_input = QLineEdit(self)
        self.pw_input.setStyleSheet("""
        QLineEdit {
            padding: 5px;
            font-size: 14px;
            background-color: #ffffff;
            border: 2px solid #cccccc;
            border-radius: 5px;
        }
        """)
        self.pw_input.setEchoMode(QLineEdit.Password)  # 비밀번호 숨김 설정
        account_grid_layout.addWidget(self.pw_label, 1, 0)
        account_grid_layout.addWidget(self.pw_input, 1, 1)

        # 실행 버튼 부분 (우측 배치)
        self.run_button = QPushButton('실행', self)
        self.run_button.setFont(QFont("Pretendard-Regular", 12, QFont.Bold))
        self.run_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.run_button.setFixedHeight(60)  # 버튼 높이 설정
        self.run_button.clicked.connect(self.run_button_clicked)

        # Enter 또는 Return 키로 버튼을 실행할 수 있도록 설정
        self.run_button.setDefault(True)

        # 버튼을 그리드에서 두 줄 높이로 설정
        account_grid_layout.addWidget(self.run_button, 0, 2, 2, 1)

        # 메인 레이아웃에 그리드 레이아웃 추가
        main_layout.addLayout(account_grid_layout)

        account_setting_grid_layout = QGridLayout()

        # 계정 관련 설정 체크박스
        self.saved_id_checkbox = QCheckBox('아이디 기억하기')
        if self.save_account:
            self.saved_id_checkbox.setChecked(True)
            self.id_input.setText(self.saved_id)
        # 체크박스가 활성화되거나 비활성화될 때 이벤트 발생
        self.saved_id_checkbox.stateChanged.connect(self.checkbox_changed)

        account_setting_grid_layout.addWidget(self.saved_id_checkbox, 0, 0)
        self.show_password_checkbox = QCheckBox('비밀번호 보이기')
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        account_setting_grid_layout.addWidget(self.show_password_checkbox, 0, 1)

        # 메인 레이아웃에 추가
        main_layout.addLayout(account_setting_grid_layout)

        # 메인 레이아웃 설정
        self.setLayout(main_layout)

    def update_status(self, message):
        self.progress_dialog.update_status(message)

    def checkbox_changed(self, state):
        if state == Qt.Checked:
            print("체크박스가 체크되었습니다.")
            data = {"id": self.id_input.text(), "save_account": True}

        else:
            data = {"id": None, "save_account": False}

            # 해제 시 처리할 이벤트 추가 가능

        json_path = get_user_data_path('account_setting.json')
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"설정이 저장되었습니다: {json_path}")

    def run_button_clicked(self):
        #계정 입력 상태 확인
        id_input = self.id_input.text()
        pw_input = self.pw_input.text()
        course_name = self.course_input.text()
        if not id_input or not pw_input:
            self.account_error_message()
            return
        
        if not course_name:
            self.course_error_message()
            return

        # CourseTrack 스레드 생성 및 시작
        self.tracker = CourseTrack(id_input, pw_input, course_name)
        self.tracker.progress_signal.connect(self.update_status)

        # ProgressDialog 설정
        self.progress_dialog = ProgressDialog(thread=self.tracker)
        self.progress_dialog.show()
        self.tracker.start()

    def account_error_message(self):
            # 메시지 박스 생성
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)  # 오류 메시지 아이콘 설정
            msg.setText("아이디와 비밀번호를 모두 입력했는지 확인해주세요!")
            msg.setWindowTitle("계정 입력 오류")
            msg.setStandardButtons(QMessageBox.Ok)  # 확인 버튼만 있는 메시지 박스
            
            # 메시지 박스 실행
            msg.exec_()

    def course_error_message(self):
            # 메시지 박스 생성
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)  # 오류 메시지 아이콘 설정
            msg.setText("수강하고 싶은 강의를 적었는지 확인해주세요!")
            msg.setWindowTitle("수강 과정 입력 오류")
            msg.setStandardButtons(QMessageBox.Ok)  # 확인 버튼만 있는 메시지 박스
            
            # 메시지 박스 실행
            msg.exec_()

    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.pw_input.setEchoMode(QLineEdit.Normal)
        else:
            self.pw_input.setEchoMode(QLineEdit.Password)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    icon_path = load_data('gamgee_icon.ico')
    app.setWindowIcon(QIcon(icon_path))

    # 폰트 파일을 애플리케이션에 추가
    font_path = load_data('NanumSquareR.ttf')
    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 12))
    else:
        print("폰트를 로드할 수 없습니다.")

    # JSON 파일 로드
    json_path = load_data('account_setting.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        save_account = data["save_account"]
        saved_id = data["id"]

    ex = MyApp(saved_id=saved_id, save_account=save_account)
    ex.show()
    sys.exit(app.exec_())