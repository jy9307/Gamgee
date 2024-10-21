import os
import subprocess
import time
import pandas as pd
from PyQt5 import QtWidgets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class ChromeControlApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chrome Controller')
        self.setGeometry(100, 100, 300, 200)

        layout = QtWidgets.QVBoxLayout()  # QVBoxLayout 사용

        self.label = QtWidgets.QLabel('Chrome 제어 앱', self)
        layout.addWidget(self.label)

        self.run_btn = QtWidgets.QPushButton('브라우저 오픈', self)
        self.run_btn.clicked.connect(self.run_chrome)
        layout.addWidget(self.run_btn)

        self.control_btn = QtWidgets.QPushButton('브라우저 제어', self)
        self.control_btn.clicked.connect(self.control_browser)
        layout.addWidget(self.control_btn)

        self.setLayout(layout)  # setCentralWidget 대신 setLayout 사용

    def run_and_control_browser(self):
        self.label.setText('Chrome을 디버깅 모드로 실행합니다...')
        self.run_chrome()
        time.sleep(2)  # Chrome이 실행될 때까지 잠시 대기
        self.label.setText('Chrome을 제어합니다...')
        self.control_browser()
        self.label.setText('작업이 완료되었습니다.')

    def run_chrome(self):
        # Chrome 실행 파일 경로를 정확하게 지정하십시오
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 실제 Chrome 설치 경로로 수정
        # chrome.exe 파일이 존재하는지 확인
        if not os.path.exists(chrome_path):
            self.label.setText('Chrome 실행 파일을 찾을 수 없습니다. chrome_path를 확인하십시오.')
            return
        subprocess.Popen([chrome_path, '--remote-debugging-port=9222', '--user-data-dir=C:\\chrometemp'])

    def control_browser(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('debuggerAddress', 'localhost:9222')
        driver_path = r"C:\Gamgee\chromedriver.exe"

        service = Service(executable_path = driver_path)
        driver = webdriver.Chrome(options=options,
                                  service=service)

        actions = ActionChains(driver)

        df = pd.read_csv("m_class.csv", encoding = 'cp949')
        names = list(df.iloc[:,1])

        for n in names :
            print(n)
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@aria-label="1행 마지막 열 성명 {n} link"]')))
            element.click()

            # if i != 1 :
            #     time.sleep(1)
            #     # 부모 요소를 먼저 찾음
            #     parent_element = driver.find_element(By.XPATH, '//*[@id="uuid-2sh"]/div[2]')
            #     print("parent : ", parent_element)

            time.sleep(1)
            # 2. '//*[@id="uuid-1ci"]/div' 버튼을 2번 클릭
            button = driver.find_element(By.XPATH, '//*[@aria-label="행추가"]')
            button.click()
            time.sleep(1)  # 클릭 사이에 1초 대기
            button.click()

            input_element = driver.find_element(By.XPATH, '//*[contains(@aria-label, "1행 일자")]')
            actions = ActionChains(driver)
            actions.move_to_element(input_element).click().send_keys(Keys.CONTROL, 'a').send_keys("2024093").perform()
            
            time.sleep(0.5)

            input_element = driver.find_element(By.XPATH, '//*[contains(@aria-label, "1행 내용")]')
            actions.move_to_element(input_element).click().send_keys("안녕하세요").perform()

            time.sleep(3)

            input_element = driver.find_element(By.XPATH, '//*[contains(@aria-label, "2행 마지막 행 일자")]')
            actions.move_to_element(input_element).click().send_keys(Keys.CONTROL, 'a').send_keys("20240825").perform()

            time.sleep(0.5)

            input_element = driver.find_element(By.XPATH, '//*[contains(@aria-label, "2행 마지막 행 내용")]')
            actions.move_to_element(input_element).click().send_keys("즐겁네요").perform()

            button = driver.find_element(By.XPATH, '//*[@aria-label="저장"]')
            button.click()

            element = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, ".btn-secondary.cl-control.cl-button.cl-unselectable")
))

            # 버튼 클릭
            element.click()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ex = ChromeControlApp()
    ex.show()
    app.exec_()