import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QFrame
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontDatabase, QFont
from coursetrack import CourseTrack
import json

# JSON 파일을 열고 파싱하기


class ProgressDialog(QDialog):
    def __init__(self, thread, parent = None):
        super().__init__()

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
        self.combo_label.setStyleSheet("font-size: 12px;")  # 폰트 크기를 14px로 설정
        main_layout.addWidget(self.combo_label)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)  # 수평선 설정
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)  # 메인 레이아웃에 선 추가

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
        self.course_help_label.setStyleSheet("font-size: 12px;")  # 폰트 크기를 14px로 설정
        course_layout.addWidget(self.course_help_label, 1, 0, 1, 2)

        # 메인 레이아웃에 추가
        main_layout.addLayout(course_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)  # 수평선 설정
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)  # 메인 레이아웃에 선 추가

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


        account_grid_layout.addWidget(self.id_label, 0, 0)  # ID label at row 0, column 0
        account_grid_layout.addWidget(self.id_input, 0, 1)  # ID input at row 0, column 1

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
        account_grid_layout.addWidget(self.pw_label, 1, 0)  # PW label at row 1, column 0
        account_grid_layout.addWidget(self.pw_input, 1, 1)  # PW input at row 1, column 1

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

        self.run_button.setFixedHeight(60)  # 버튼 높이 설정 (원하는 높이로 조절 가능)
        self.run_button.clicked.connect(self.run_button_clicked)


        # 버튼을 그리드에서 두 줄 높이로 설정 (가로는 그대로, 높이만 꽉 차게)
        account_grid_layout.addWidget(self.run_button, 0, 2, 2, 1)  # 2개의 행을 차지하게 설정


        # 메인 레이아웃에 그리드 레이아웃 추가
        main_layout.addLayout(account_grid_layout)

        account_setting_grid_layout = QGridLayout()

        # 계정 관련 설정 체크박스
        ## 아이디 기억하기
        self.saved_id_checkbox = QCheckBox('아이디 기억하기')
        if self.save_account == True :
            # 체크박스를 체크된 상태로 설정
            self.saved_id_checkbox.setChecked(True)
            # 입력 필드에 기본값 설정
            self.id_input.setText(self.saved_id)

        account_setting_grid_layout.addWidget(self.saved_id_checkbox, 0, 0)
        ## 비밀번호 보이기
        self.show_password_checkbox = QCheckBox('비밀번호 보이기')
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        account_setting_grid_layout.addWidget(self.show_password_checkbox, 0, 1)

        ## 메인 레이아웃에 추가
        main_layout.addLayout(account_setting_grid_layout)
        
        # 메인 레이아웃 설정
        self.setLayout(main_layout)



    def update_status(self, message):
        # 시그널을 받아서 상태 업데이트
        self.progress_dialog.update_status(message)

        
    # 실행 버튼 클릭 시 동작할 함수
    def run_button_clicked(self):

        # QLineEdit에서 ID와 PW 텍스트 가져오기
        id_input = self.id_input.text()
        pw_input = self.pw_input.text()
        course_name = self.course_input.text()

        # CourseTrack 스레드 생성 및 시작
        self.tracker = CourseTrack(id_input, pw_input, course_name)
        self.tracker.progress_signal.connect(self.update_status)  # 시그널 연결

        # ProgressDialog 설정
        self.progress_dialog = ProgressDialog(thread=self.tracker)
        self.progress_dialog.show()  # 진행 상황 창 표시
        self.tracker.start()  # 스레드 시작

    # 비밀번호 보이기/숨기기 토글 기능
    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.pw_input.setEchoMode(QLineEdit.Normal)  # 비밀번호 보이기
        else:
            self.pw_input.setEchoMode(QLineEdit.Password)  # 비밀번호 숨기기

        # 창이 닫힐 때 동작을 정의하는 closeEvent 재정의
    def closeEvent(self, event):
        # 체크박스 상태에 따라 저장할 데이터를 결정
        if self.saved_id_checkbox.isChecked():
            data = {
                "id": self.id_input.text(),  # 입력된 ID 저장
                "save_account": True
            }
        else:
            data = {
                "id": None,
                "save_account": False
            }

        # JSON 파일에 저장
        with open('account_setting.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        print("설정이 저장되었습니다.")
        event.accept()  # 창을 닫는 이벤트 허용

        



if __name__ == '__main__':

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon('gamgee_icon.ico')) 
    
    # 폰트 파일을 애플리케이션에 추가
    font_id = QFontDatabase.addApplicationFont("./NanumSquareR.ttf")
   
    # 폰트가 제대로 추가되었는지 확인
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 12))  # 로드된 폰트 이름을 사용
    else:
        print("폰트를 로드할 수 없습니다.")

    #json 파일 파싱
    with open('account_setting.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        save_account = data["save_account"]
        saved_id = data["id"]

    ex = MyApp(saved_id=saved_id, save_account=save_account)
    ex.show()
    sys.exit(app.exec_())
