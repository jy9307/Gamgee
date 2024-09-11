from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import time
import time
import sys




class CourseTrack(QThread) :

    progress_signal = pyqtSignal(str)

    def __init__(self, id, pw, course_name) -> None:
        super().__init__()
        self.id = id
        self.pw = pw
        self.course_name = course_name
        self._is_running = True

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

##------------- Thread process --------------

    def log_in(self) :
        
        
        passing = 0

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
                EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/button'))
            )
            element.click()

        while 1 :
            #음소거 우선    
            try :
                video_player = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[9]'))
                )
                # JavaScript로 mouseover 이벤트 트리거
                actions = ActionChains(self.driver)
                actions.move_to_element(video_player).perform()

                mute_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="lx-player"]/div[9]/div[1]/button')))
                mute_btn.click()

            except :
                self.pass_quiz()
                continue

            try :

                # XPath를 사용하여 비디오 플레이어 요소 찾기

                # ActionChains를 사용하여 마우스를 비디오 플레이어 위로 이동        
                self.progress_signal.emit("영상 길이 찾아내는 중...")
                get_time_start = time.time()
                
                #영상 길이 찾아내기 
                total_time=''

                while (total_time == '') or (total_time == '-:-') or (current_time == '') or (current_time == '-:-'):

                    actions = ActionChains(self.driver)
                    actions.move_to_element(video_player).perform()

                    total_time = self.driver.find_element(By.XPATH, '//*[@id="lx-player"]/div[9]/div[4]/span[2]').text.strip()
                    current_time = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "vjs-current-time-display"))).text.strip()

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
