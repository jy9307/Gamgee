import os
import subprocess
import time
from PyQt5 import QtWidgets
from selenium import webdriver
from selenium.webdriver.common.by import By

class ChromeControlApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chrome Controller')
        self.setGeometry(100, 100, 300, 200)

        self.label = QtWidgets.QLabel('Chrome 제어 앱', self)
        self.label.move(50, 50)

        self.control_btn = QtWidgets.QPushButton('브라우저 제어 시작', self)
        self.control_btn.move(50, 100)
        self.control_btn.clicked.connect(self.run_and_control_browser)

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
        driver = webdriver.Chrome(options=options)

        # 구글 검색창에 '셀레니움' 입력 후 검색
        driver.get('http://www.google.com')
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys('셀레니움')
        search_box.submit()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ex = ChromeControlApp()
    ex.show()
    app.exec_()