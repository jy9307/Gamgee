import sys
import os
import json
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QFrame, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from filehandler import *

##------------- GUI elements --------------
class CourseTrackHome(QWidget):
    def __init__(self, saved_id, save_account):
        super().__init__()

        # 기존 설정 확인
        self.saved_id = saved_id
        self.save_account = save_account

        # 윈도우 기본 설정
        self.setWindowTitle('Gamgee v0.3-beta')

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
        self.state = self.show_password_checkbox.checkState()
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        account_setting_grid_layout.addWidget(self.show_password_checkbox, 0, 1)

        # 메인 레이아웃에 추가
        main_layout.addLayout(account_setting_grid_layout)

        # 메인 레이아웃 설정
        self.setLayout(main_layout)

    def update_status(self, message):
        self.progress_dialog.update_status(message)

    def checkbox_changed(self, state):
        data = load_setting()

        data["coursetrack_id"] = self.id_input.text() if state == Qt.Checked else None
        data["coursetrack_save_account"] = state == Qt.Checked

            # 해제 시 처리할 이벤트 추가 가능

        save_setting(data)

    def run_button_clicked(self):
        #계정 입력 상태 확인
        id_input = self.id_input.text()
        pw_input = self.pw_input.text()
        course_name = self.course_input.text()
        if not id_input or not pw_input:
            QMessageBox.warning(self, "계정 입력 오류", "아이디와 비밀번호를 모두 입력했는지 확인해주세요!")
            return
        
        if not course_name:
            QMessageBox.warning(self, '수강 과정 입력', "수강하고 싶은 강의를 적었는지 확인해주세요!")
            return

        # CourseTrack 스레드 생성 및 시작
        self.tracker = CourseTrack(id_input, pw_input, course_name)
        self.tracker.progress_signal.connect(self.update_status)


        # ProgressDialog 설정
        self.progress_dialog = ProgressDialog(thread=self.tracker)

        # 두 class 사이의 연결
        self.progress_dialog.hide_signal.connect(self.tracker.hide_browser)
        self.progress_dialog.restore_signal.connect(self.tracker.restore_browser)
        self.progress_dialog.mute_signal.connect(self.tracker.mute_browser)
        self.progress_dialog.show()
        self.tracker.start()

    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.pw_input.setEchoMode(QLineEdit.Normal)
        else:
            self.pw_input.setEchoMode(QLineEdit.Password)

class ProgressDialog(QDialog):
    hide_signal = pyqtSignal()
    restore_signal = pyqtSignal()
    mute_signal = pyqtSignal()

    def __init__(self, thread, parent=None):
        super().__init__(parent)
        self.thread = thread
        self.setWindowTitle("진행 상황")

        # 항상 최상단에 표시되도록 설정
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout()

        # 진행 상황을 표시할 라벨
        self.status_label = QLabel('진행 상황: 준비 중...')
        main_layout.addWidget(self.status_label)

        # 중지 버튼
        button_layout = QHBoxLayout()

        self.hide_button = QPushButton('화면 숨기기')
        self.hide_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 14px;
                background-color: #4a90e2;  # 부드러운 파란색
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #388e3c;  # 진한 녹색
            }
        """)
        self.hide_button.clicked.connect(self.emit_hide_signal)

        self.restore_button = QPushButton('다시 드러내기')
        self.restore_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 14px;
                background-color: #4a90e2;  # 부드러운 파란색
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #388e3c;  # 진한 녹색
            }
        """)
        self.restore_button.clicked.connect(self.emit_restore_signal)

        button_layout.addWidget(self.hide_button)
        button_layout.addWidget(self.restore_button)

        self.stop_button = QPushButton('중지')
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

        self.mute_check = QCheckBox('자동 음소거')
        self.mute_check.stateChanged.connect(self.emit_mute_signal)
        main_layout.addWidget(self.mute_check)
        
        main_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    # 시그널을 받아서 진행 상황 업데이트
    def update_status(self, status):
        self.status_label.setText(status)  # 전달받은 메시지를 라벨에 표시

    def emit_hide_signal(self):
        self.hide_signal.emit()

    def emit_restore_signal(self):
        self.restore_signal.emit()

    def emit_mute_signal(self, state):
        if state == Qt.Checked:  # 체크박스가 선택된 경우
            self.mute_signal.emit()

    # 프로그램 중지
    def stop_program(self):
        self.close()  # 프로그램 종료
        self.thread.stop()
        self.thread.quit()

class CourseTrack(QThread) :

    progress_signal = pyqtSignal(str)

    def __init__(self, id, pw, course_name) -> None:
        super().__init__()
        self.id = id
        self.pw = pw
        self.course_name = course_name
        self._is_running = True
        self.mute_mode = False

        options = webdriver.ChromeOptions()

        # 브라우저 윈도우 사이즈
        options.add_argument('window-size=1920x1080')

        # 자동화 메시지 제거 설정
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # 사람처럼 보이게 하는 옵션들
        options.add_argument("disable-gpu")   # 가속 사용 x
        options.add_argument("lang=ko_KR")    # 가짜 플러그인 탑재
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정

        # 드라이버 위치 경로 입력
        self.driver = webdriver.Chrome(options=options)

        # navigator.webdriver 속성 삭제
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

##------------- Tools --------------

    def pass_quiz(self) :
        quiz_btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lxPlayerIframe"]/div[2]')))
        if quiz_btn :
            quiz_btn.click()
        next_btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="next-btn"]')))
        next_btn.click()

    def check_running(self):
        if not self._is_running:
            print("Thread Stopped")  # 예외를 발생시키지 않고 종료 알림
            return False  # 작업을 중단할 수 있도록 False 반환
        return True  # 계속 진행

    def countdown_timer(self, seconds):
        for remaining in range(seconds, 0, -1):
            self.progress_signal.emit(f"남은 시간: {remaining}초")
    
            time.sleep(1)
        self.progress_signal.emit("타이머 종료!")
    
    def hide_browser(self) :
        self.driver.set_window_position(-2000, 0)

    def restore_browser(self) :
        self.driver.set_window_position(500, 0)
    
    def mute_browser(self):
        self.mute_mode = True  # 음소거 신호가 들어오면 상태를 True로 변경

##------------- Thread process --------------

    def log_in(self) :
        
        
        passing = 0
        self.hide_browser()

        while passing ==0 : 
            if not self.check_running(): return
            try:
                self.driver.find_element(By.NAME, 'userInputId').send_keys(self.id)
                self.driver.find_element(By.NAME,'userInputPw').send_keys(self.pw)
                self.driver.find_element(By.XPATH,'/html/body/section/form/div/div/a').click()
                passing = 1
                time.sleep(1)
            except :
                self.driver.get('https://www.neti.go.kr/system/login/login.do')
    
    
    def load_course(self) :
        if not self.check_running(): return
        print("still work")
        self.driver.get('https://www.neti.go.kr/lh/ms/cs/atnlcListView.do?menuId=1000006046')

        time.sleep(1)

        course_elements = self.driver.find_elements(By.XPATH, "//ul[@class='course_list_box type_02']//a[@class='title']")
        target_text = self.course_name
        target_element = None

        # 요소 중에서 텍스트를 비교하여 원하는 요소 찾기
        for element in course_elements:
        
            if target_text in element.text:
                target_element = element
                break
        if target_element:
            self.progress_signal.emit("강의를 찾았습니다!")

            # 2. 해당 요소 하위의 '이어보기' 버튼 클릭
            parent_li = target_element.find_element(By.XPATH, "./../../..")  # li 요소로 거슬러 올라가기
            continue_button = parent_li.find_element(By.XPATH, ".//a[contains(text(), '이어보기') or contains(text(), '학습하기')]")

            
            # '이어보기' 버튼 클릭
            continue_button.click()

            print("이어보기 버튼을 클릭했습니다!")
        else:
            self.progress_signal.emit("강의를 발견하지 못했습니다. 다시 시도해주세요.")
    

    
    def handle_course(self) :
        print("still work")
        if not self.check_running(): return

        # 기존 창 핸들 저장``
        original_window = self.driver.current_window_handle

        # 모든 창 핸들 가져오기
        WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
        all_windows = self.driver.window_handles

        # 새로운 창 핸들 찾기 및 전환
        for window_handle in all_windows:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                print(self.driver.title)  # 새 창의 제목 출력
                break
            
        #퀴즈 페이지일 경우 - class가 "quiz-type"이면 우측 하단에 '학습 완료 후 여기를 클릭하세요'가 나온다.
        #div id= page-info의 text가 01 / 02일 경우 두 번 오른쪽으로 넘겨야됨
        try :
            self.pass_quiz()

        except :

        #퀴즈 페이지 아닐 경우 재생 버튼 나올때까지 기다려서 클릭
            element = WebDriverWait(self.driver, 3).until(
                EC.any_of(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/button')),
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[4]/button[2]'))
            ))
            element.click()

        while 1 :
            #음소거 우선
            if self.mute_mode :
                try :
                    video_player = WebDriverWait(self.driver, 10).until(
                        EC.any_of(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[9]')),
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[10]'))
                    ))
                    # JavaScript로 mouseover 이벤트 트리거
                    actions = ActionChains(self.driver)
                    actions.move_to_element(video_player).perform()

                    mute_btn = WebDriverWait(self.driver, 10).until(
                        EC.any_of(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[9]/div[1]/button')),
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[10]/div[1]/button')),
                            ))
                    mute_btn.click()

                except :
                    self.pass_quiz()
                    continue

            else :
                try :
                    self.pass_quiz()
                    continue
                
                except :
                    video_player = WebDriverWait(self.driver, 10).until(
                        EC.any_of(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[9]')),
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[10]'))
                    ))
                    # JavaScript로 mouseover 이벤트 트리거
                    actions = ActionChains(self.driver)
                    actions.move_to_element(video_player).perform()
                    
            try :

                # XPath를 사용하여 비디오 플레이어 요소 찾기
                # ActionChains를 사용하여 마우스를 비디오 플레이어 위로 이동        
                self.progress_signal.emit("영상 길이 찾아내는 중...")
                get_time_start = time.time()
                
                #영상 길이 찾아내기 
                total_time=''

                actions = ActionChains(self.driver)
                actions.move_to_element(video_player).perform()

                while (total_time == '') or (total_time == '-:-') or (current_time == '') or (current_time == '-:-'):

                    self.progress_signal.emit("영상 길이 찾아내는 중...")

                    total_time = WebDriverWait(self.driver, 3).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="lx-player"]/div[9]/div[4]/span[2]')),
                        EC.presence_of_element_located((By.XPATH, '//*[@id="lx-player"]/div[10]/div[4]/span[2]')),
                    ))
                    total_time = total_time.text.strip()
                    self.progress_signal.emit("현재 시점 찾아내는 중...")
                    current_time = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "vjs-current-time-display"))).text.strip()
                    print(total_time, current_time)

                total_time = total_time.split(":")
                total_time = int(total_time[0])*60 + int(total_time[1])

                current_time = current_time.split(":")
                current_time = int(current_time[0])*60 + int(current_time[1])

                remain_time = total_time-current_time    
                get_time_end = time.time()

                self.progress_signal.emit(f"영상 길이 확인 완료! 확인에 걸린 시간 : {get_time_end - get_time_start: 0.1f}초")
                self.progress_signal.emit(f"영상 길이: {remain_time}")

                self.countdown_timer(remain_time+4)
                    
                #다음 누르기
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="next-btn"]'))
                )
                element.click()
                self.progress_signal.emit("다음 강의 시작!")

            except Exception as e :
                print(f"오류 : {e}")

    def run(self):
        # 스레드에서 로그인, 강의 로드, 강의 처리 메서드 실행
        self.log_in()
        self.load_course()
        self.handle_course()

    def stop(self) :
        self._is_running = False
        self.driver.quit()
        self.terminate()
