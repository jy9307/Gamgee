import sys, os, json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QFrame, QSystemTrayIcon, QMenu, QAction,
    QPushButton, QMessageBox, QGridLayout, QDialog, QHBoxLayout, QCheckBox
)
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont, QIcon
from functions import CourseTrackHome, ProjectNeisHome
from tools import *

# 로그인 화면
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.load_account_settings()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')
        
        main_layout = QVBoxLayout()
        self.label = QLabel(self)  # QLabel 생성
        pixmap = QPixmap('gamgee_title.png')  # 이미지 파일을 QPixmap으로 로드
        self.label.setPixmap(pixmap)  # QLabel에 QPixmap 설정
        self.label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label)
        # 레이아웃
        account_layout = QGridLayout()

        # ID와 PW 입력 필드

        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText('ID 입력')
        self.pw_input = QLineEdit(self)
        self.pw_input.setPlaceholderText('Password 입력')
        self.pw_input.setEchoMode(QLineEdit.Password)

        # 로그인 버튼
        self.login_button = QPushButton('로그인', self)
        self.login_button.setFixedHeight(60)
        self.login_button.clicked.connect(self.login)

        # 회원가입 버튼
        self.signup_button = QPushButton('회원가입', self)
        self.signup_button.setFixedHeight(60)
        self.signup_button.clicked.connect(self.signup)

        # 레이아웃에 위젯 추가
        account_layout.addWidget(self.id_input,0,0)
        account_layout.addWidget(self.pw_input,1,0)
        account_layout.addWidget(self.login_button,0,1,2,1)
        account_layout.addWidget(self.signup_button,0,2,2,1)

        main_layout.addLayout(account_layout)

        # 계정 관련 설정 세팅
        account_setting_layout = QHBoxLayout()

        save_main_id_checkbox = QCheckBox('아이디 기억하기')
        if self.save_account:
            save_main_id_checkbox.setChecked(True)
            self.id_input.setText(self.saved_id)
        # 체크박스가 활성화되거나 비활성화될 때 이벤트 발생
        save_main_id_checkbox.stateChanged.connect(self.checkbox_changed)

        show_main_pw_checkbox = QCheckBox('비밀번호 보이기')
        show_main_pw_checkbox.stateChanged.connect(self.toggle_password_visibility)

        account_setting_layout.addWidget(save_main_id_checkbox)
        account_setting_layout.addWidget(show_main_pw_checkbox)

        main_layout.addLayout(account_setting_layout)

        self.setLayout(main_layout)

    def load_account_settings(self):
        try:
            # JSON 파일 로드
            json_path = load_data('settings.json')
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("account_setting.json 파일을 찾을 수 없거나 형식이 잘못되었습니다.")
            data = {}

        self.saved_id = data.get("main_id", "")  # 'main_id'가 없으면 빈 문자열로 처리
        self.save_account = data.get("main_save_account", False)  # 'main_save_account'가 없으면 False로 처리

    def checkbox_changed(self, state):
        data = load_setting()

        data["main_id"] = self.id_input.text() if state == Qt.Checked else None
        data["main_save_account"] = state == Qt.Checked

        # 변경된 설정 저장
        save_setting(data)

    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.pw_input.setEchoMode(QLineEdit.Normal)
        else:
            self.pw_input.setEchoMode(QLineEdit.Password)

    # 로그인 처리 함수
    def login(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()

        #Firestore에서 ID PW확인후 로그인   
        if login_check(user_id,password):
            app_user_state.set_user_id(user_id)

            #로그 기록
            total_field_count_up("total_login_count")

            self.openHomeScreen()  # 홈 화면 열기
        else:
            send_log_to_user_firestore(event_result = "failure", event_description=f"로그인 실패")
            QMessageBox.warning(self, 'Login', 'ID 또는 비밀번호가 일치하지 않습니다.')

    # 회원가입 처리 함수
    def signup(self):
        self.hide()

        self.sign_in_window = SignInWindow()
        self.sign_in_window.exec_()

        self.show()

    # 홈 화면 열기
    def openHomeScreen(self):
        self.home_screen = HomeScreen()
        self.home_screen.show()
        self.close()

# 회원가입 화면
class SignInWindow(QDialog) :

    def __init__(self) :
        super().__init__()
        self.initUI()

    def initUI(self) :
        self.setWindowTitle("회원 가입")
        main_layout = QVBoxLayout()

        id_layout = QHBoxLayout()
        id_input_label = QLabel("ID")
        self.id_input_line = QLineEdit()
        id_duplicate_check_btn = QPushButton("중복확인")
        id_duplicate_check_btn.clicked.connect(self.duplicate_check)
        self.id_duplicate = False

        id_layout.addWidget(id_input_label)
        id_layout.addWidget(self.id_input_line)
        id_layout.addWidget(id_duplicate_check_btn)

        main_layout.addLayout(id_layout)

        pw_layout = QHBoxLayout()
        pw_input_label = QLabel("PW")
        self.pw_input_line = QLineEdit()

        pw_layout.addWidget(pw_input_label)
        pw_layout.addWidget(self.pw_input_line)

        main_layout.addLayout(pw_layout)

        sign_in_btn = QPushButton("회원가입")
        sign_in_btn.clicked.connect(self.signup)

        main_layout.addWidget(sign_in_btn)
        main_layout.addStretch(2)


        self.setLayout(main_layout)

    def signup(self):
        if self.id_duplicate == False :
            QMessageBox.warning(self, "중복 검사", "ID 중복 검사가 필요합니다.")
            return
        user_id = self.id_input_line.text()
        password = self.pw_input_line.text()

        if user_id and password :
            # Firestore에 새로운 유저 추가
            user_ref = db.collection('users').document(user_id)
            user_ref.set({'pw': password})

            QMessageBox.information(self, 'Sign Up', '회원가입 성공!')
            self.close()
        else :
            QMessageBox.warning(self, "ID, PW 확인", "ID와 PW를 잘 입력했는지 확인해주세요.")

    def duplicate_check(self) :
        if self.id_input_line.text() :
            # 'users' 컬렉션의 'a' 문서 참조
            doc_ref = db.collection('users').document(self.id_input_line.text())
            # 문서 존재 여부 확인
            doc = doc_ref.get()

            if doc.exists:
                QMessageBox.warning(self, "중복","이미 존재하는 ID입니다.")
            else:
                QMessageBox.warning(self, "사용 가능", "사용할 수 있는 ID입니다.")
                self.id_duplicate = True
        else :
            QMessageBox.warning(self, "ID입력", "ID를 입력해주세요!")

# 로그인 후 홈 화면
class HomeScreen(QWidget):

    def __init__(self):
        super().__init__()
        # 시스템 트레이 설정
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('gamgee_icon.ico'))  # 트레이에 사용할 아이콘 설정
        self.tray_icon.setVisible(True)

        # 트레이 메뉴 설정
        tray_menu = QMenu()

        restore_action = QAction("열기", self)
        restore_action.triggered.connect(self.showNormal)  # 복원 액션 연결
        tray_menu.addAction(restore_action)

        quit_action = QAction("종료", self)
        quit_action.triggered.connect(QApplication.quit)  # 종료 액션 연결
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)  # 트레이 메뉴 설정

        # 트레이 아이콘 더블클릭 시 창 복구 기능 연결
        self.tray_icon.activated.connect(self.restore_window)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gamgee v0.3')

        # 메인 레이아웃 (전체를 감싸는 레이아웃)
        main_layout = QVBoxLayout()

        # 환영 메시지 레이아웃
        welcome_layout = QHBoxLayout()
        self.label = QLabel(f'{app_user_state.get_user_id()}님 환영합니다!')
        # QLabel에 스타일 적용 (배경색, 글자색, 패딩 등)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #e0f7fa;  /* 연한 하늘색 배경 */
                color: #006064;             /* 진한 색 텍스트 */
                padding: 10px;              /* 텍스트 주위에 여백 */
                border-radius: 5px;         /* 모서리 둥글게 */
                font-size: 16px;            /* 글꼴 크기 */
            }
        """)
        welcome_layout.addWidget(self.label)
        main_layout.addLayout(welcome_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()  # 버튼들을 배열하기 위해 GridLayout 사용
        self.course_track_btn = QPushButton('연수 도우미', self)
        self.course_track_btn.setFixedSize(140, 100)
        self.course_track_btn.clicked.connect(self.course_track_run)

        self.grade_input_button = QPushButton('성적 도우미', self)
        self.grade_input_button.setFixedSize(140, 100)
        self.grade_input_button.clicked.connect(self.project_neis_run)

        self.dev_button = QPushButton('개발 중', self)
        self.dev_button.setFixedSize(140, 100)

        # 버튼들을 GridLayout에 추가 (2행으로 정렬 가능)
        button_layout.addWidget(self.course_track_btn)
        button_layout.addWidget(self.grade_input_button)
        button_layout.addWidget(self.dev_button)

        # 메인 레이아웃에 환영 메시지 레이아웃과 버튼 레이아웃을 추가
        main_layout.addLayout(button_layout)

        # 최종 레이아웃 설정
        self.setLayout(main_layout)

    def course_track_run(self) :
        self.hide()
        self.course_track_home = CourseTrackHome(self)
        self.course_track_home.exec_()

        self.show()

    def project_neis_run(self) :
        self.hide()
        self.project_neis_home = ProjectNeisHome(self)
        self.project_neis_home.exec_()

        self.show()

    def closeEvent(self, event):
        """창을 닫을 때 시스템 트레이로 최소화"""
        if self.tray_icon.isVisible():
            self.hide()  # 창을 숨김
            self.tray_icon.showMessage(
                "앱이 트레이로 최소화되었습니다.",
                "앱을 다시 열려면 트레이 아이콘을 클릭하세요.",
                QSystemTrayIcon.Information,
                2000  # 알림이 2초 동안 표시됩니다.
            )
            event.ignore()  # 창이 닫히지 않도록 막음

    
    def restore_window(self, reason):
        """트레이 아이콘 더블클릭 시 창을 복구"""
        if reason == QSystemTrayIcon.DoubleClick:  # 더블클릭한 경우에만 창을 복구
            self.showNormal()  # 창을 복구
            self.activateWindow()  # 창을 활성화

if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = load_data('gamgee_icon.ico')
    app.setWindowIcon(QIcon(icon_path))

    # 폰트 파일을 애플리케이션에 추가
    font_path = load_data('NanumSquareR.ttf')
    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 10))
    else:
        print("폰트를 로드할 수 없습니다.")
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())