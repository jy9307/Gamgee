import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGridLayout, QDialog, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont, QIcon
import firebase_admin
from firebase_admin import credentials, firestore

from functions.course_track import CourseTrackHome
from filehandler import *

# Firestore 초기화
cred = credentials.Certificate('gamgee-bed2b-e8385da2215e.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')
        
        main_layout = QVBoxLayout()
        self.label = QLabel(self)  # QLabel 생성
        pixmap = QPixmap('gamgee_title.png')  # 이미지 파일을 QPixmap으로 로드
        self.label.setPixmap(pixmap)  # QLabel에 QPixmap 설정
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

        self.setLayout(main_layout)

    # 로그인 처리 함수
    def login(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()

        # Firestore에서 ID와 PW 확인
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()

        if user.exists and user.to_dict().get('password') == password:
            QMessageBox.information(self, 'Login', '로그인 성공!')
            self.openHomeScreen()  # 홈 화면 열기
        else:
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
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gamgee v0.3')
        layout = QVBoxLayout()

        self.label = QLabel('홈 화면')
        self.course_track_btn = QPushButton('연수 자동 이수', self)
        self.course_track_btn.clicked.connect(self.course_track_run)

        self.grade_input_button = QPushButton('나이스 성적 자동 입력', self)

        layout.addWidget(self.label)
        layout.addWidget(self.course_track_btn)
        layout.addWidget(self.grade_input_button)

        self.setLayout(layout)

    def course_track_run(self) :
        self.hide()
        self.course_track_home = CourseTrackHome()
        self.course_track_home.exec_()

        self.show()

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
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())