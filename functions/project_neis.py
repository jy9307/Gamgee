import sys, os, shutil, json, subprocess, csv, io, warnings
import pandas as pd
import pyautogui, random, pyperclip, time
from functools import partial
from filehandler import * 
## COM 초기화 에러 해결

warnings.simplefilter("ignore", UserWarning) 
sys.coinit_flags = 2 # STA

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QFileDialog, 
    QTableWidget, QTableWidgetItem, QAbstractItemView, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt

from pywinauto import application
from pywinauto.keyboard import send_keys

#### ------- TOOLS

def table_to_df(table):
    # 테이블의 열 수와 행 수 가져오기
    row_count = table.rowCount()
    column_count = table.columnCount()

    # 헤더(첫 번째 행)를 리스트 컴프리헨션으로 처리
    headers = [
        table.horizontalHeaderItem(column).text() if table.horizontalHeaderItem(column) else f"Column {column + 1}"
        for column in range(column_count)
    ]

    # 데이터를 리스트 컴프리헨션으로 처리
    data = [
        [table.item(row, column).text() if table.item(row, column) else '' for column in range(column_count)]
        for row in range(row_count)
    ]

    # pandas DataFrame으로 변환
    df = pd.DataFrame(data, columns=headers)

    return df

class ProjectNeisHome(QDialog) :

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle('나이스 입력 도우미')
        self.setStyleSheet("background-color: #f0f0f0;")

        self.setting_data = load_setting()
        if self.setting_data['save_class_info'] :
            
            self.class_info_destination_path = self.setting_data['save_class_info']
        else :
            self.class_info_destination_path = None


        self.initUI()
    
    def initUI(self) : 

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        
        # 학급 정보 레이아웃
        ## 제목 레이아웃
        class_info_title_layout = QVBoxLayout()
        
        self.class_info_label = QLabel('- 학급 정보 입력 - ')
        class_info_title_layout.addWidget(self.class_info_label)

        main_layout.addLayout(class_info_title_layout)

        ## 메인 레이아웃
        class_info_layout = QHBoxLayout()

        self.class_info_download_button = QPushButton('양식 다운로드', self)
        self.class_info_download_button.setFixedSize(130,60)
        class_info_open = partial(self.open_file, file_path=r'C:\Gamgee\neis\example\class_info_example.csv')
        self.class_info_download_button.clicked.connect(class_info_open)
        class_info_layout.addWidget(self.class_info_download_button)

        self.class_info_upload_button = QPushButton('파일 업로드')
        self.class_info_upload_button.setFixedSize(130,60)
        self.class_info_upload_button.clicked.connect(self.class_info_upload_file)
        class_info_layout.addWidget(self.class_info_upload_button)

        ### 업로드 제목
        self.class_info_file_title_label = QLabel('학급 정보 :')
        class_info_layout.addWidget(self.class_info_file_title_label)

        ### 업로드 여부 확인
        self.class_info_file_status_label = QLabel('미입력')
        class_info_layout.addWidget(self.class_info_file_status_label)
        if self.class_info_destination_path :
            self.class_info_file_status_label.setText('입력됨') # 선택된 파일 경로를 라벨에 표시
            self.class_info_file_status_label.setStyleSheet("color: blue; text-decoration: underline;")
            self.class_info_file_status_label.mousePressEvent = partial(self.open_file, self.class_info_destination_path)
            self.project_neis = ProjectNeis(self.class_info_destination_path)

        class_info_layout.addStretch(2)

        ## 정보 저장 체크 레아이웃
        class_info_save_layout = QHBoxLayout()
        
        class_info_save_layout.addStretch(2)
       
        main_layout.addLayout(class_info_layout)
        main_layout.addLayout(class_info_save_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 교과 
        ## 제목 레이아웃
        subject_title_layout = QVBoxLayout()
        subject_label = QLabel("- 교과 입력 -")

        subject_title_layout.addWidget(subject_label)
        main_layout.addLayout(subject_title_layout)

        ## 메인 레이아웃
        subject_layout = QHBoxLayout()


        subject_observation_btn = QPushButton('교과 누가기록')
        subject_observation_btn.setFixedSize(130,60)
        subject_observation_btn.clicked.connect(self.subject_obs_run)
        subject_layout.addWidget(subject_observation_btn)

        agg_subject_observation_btn = QPushButton('교과 발달사항')
        agg_subject_observation_btn.setFixedSize(130,60)
        agg_subject_observation_btn.clicked.connect(self.agg_subject_obs_run)
        subject_layout.addWidget(agg_subject_observation_btn)

        subject_grade_btn = QPushButton('교과 성적입력')
        subject_grade_btn.setFixedSize(130,60)
        subject_grade_btn.setEnabled(False)
        subject_layout.addWidget(subject_grade_btn)

        subject_layout.addStretch(2)
        
        
        main_layout.addLayout(subject_layout)


        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)


        # 창체
        ## 제목 레이아웃
        extra_title_layout = QVBoxLayout()
        extra_label = QLabel("- 창체 입력 -")

        extra_title_layout.addWidget(extra_label)
        main_layout.addLayout(extra_title_layout)
        
        ## 메인 레이아웃
        extra_layout = QHBoxLayout()
        
        extra_observation_btn = QPushButton("창체 누가기록")
        extra_observation_btn.setFixedSize(130,60)
        extra_observation_btn.setEnabled(False)
        extra_layout.addWidget(extra_observation_btn)

        extra_observation_aggregation_btn = QPushButton("창체 특기사항")
        extra_observation_aggregation_btn.setFixedSize(130,60)
        extra_observation_aggregation_btn.clicked.connect(self.agg_extra_obs_run)
        extra_layout.addWidget(extra_observation_aggregation_btn)

        extra_sports_club_btn = QPushButton("스포츠 클럽")
        extra_sports_club_btn.setFixedSize(130,60)
        extra_sports_club_btn.clicked.connect(self.extra_sports_club_run)
        extra_layout.addWidget(extra_sports_club_btn)

        extra_layout.addStretch(2)

        main_layout.addLayout(extra_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        ## 메인 레이아웃
        extra_sports_club_layout = QGridLayout()

        extra_sports_club_btn = QPushButton("스포츠 클럽 자동 입력")
        


        self.setLayout(main_layout)

    def open_file(self, file_path, event=None):
        # 파일 다운로드 경로 및 파일명 설정
        file_path =  file_path # 다운로드할 파일의 URL
        if os.path.exists(file_path):
            try:
                # 파일을 시스템 기본 프로그램으로 열기
                if sys.platform.startswith('darwin'):  # macOS
                    subprocess.call(('open', file_path))
                elif os.name == 'nt':  # Windows
                    os.startfile(file_path)

            except Exception as e:
                # 오류 발생 시 메시지 출력
                print(f'파일 열기 실패: {str(e)}')
        else:
            # 파일이 없을 경우 오류 메시지
            print(f'파일을 찾을 수 없음: {file_path}')
      
    def class_info_check(self) :
        if not self.class_info_destination_path:
            QMessageBox.warning(self,"학급 정보 입력","먼저 학급 정보를 입력해주세요!")
            return False
        else :
            return True

    def class_info_upload_file(self):

        # 파일 선택 대화 상자 열기
        file_path, _ = QFileDialog.getOpenFileName(self, '파일 선택', '', 'CSV 파일 (*.csv)')
        
        if file_path:

            # 선택된 파일을 .user_data에 복사
            try:
                self.class_info_destination_path = save_data(file_path,'class_info.csv')

                self.class_info_file_status_label.setText('입력됨') # 선택된 파일 경로를 라벨에 표시
                self.class_info_file_status_label.setStyleSheet("color: blue; text-decoration: underline;")
                self.class_info_file_status_label.mousePressEvent = partial(self.open_file, self.class_info_destination_path)

                #Json에 경로 입력
                data = load_setting()
                data["save_class_info"] = self.class_info_destination_path
                save_setting(data)

                print(f"파일이 성공적으로 {self.class_info_destination_path}로 복사되었습니다.")
            except Exception as e:
                print(f"파일 복사 중 오류 발생: {e}")

    def subject_obs_run(self) :
        if not self.class_info_check(): return

        # parent는 self, class_info는 self.class_info_destination_path
        self.subject_obs_dialog = SubjectObs(class_info=self.class_info_destination_path, parent=self)
        self.subject_obs_dialog.exec_()

    def agg_subject_obs_run(self) :
        if not self.class_info_check(): return

        # parent는 self, class_info는 self.class_info_destination_path
        self.agg_subject_obs_dialog = AggSubjectObs(parent=self)
        self.agg_subject_obs_dialog.exec_()

    def agg_extra_obs_run(self) :
        if not self.class_info_check(): return

        # parent는 self, class_info는 self.class_info_destination_path
        self.agg_extra_obs_dialog = AggExtraObs(parent=self)
        self.agg_extra_obs_dialog.exec_()

    def extra_sports_club_run(self) :
        if not self.class_info_check(): return

        # parent는 self, class_info는 self.class_info_destination_path
        self.extra_sports_club_dialog = ExtraSportsClub(parent=self)
        self.extra_sports_club_dialog.exec_()



class SubjectObs(QDialog) :

    def __init__(self, class_info, parent=None):
        super().__init__(parent)

        # 메인 레이아웃
        self.setWindowTitle("교과 누가기록")
        self.resize(800, 600)
        main_layout = QVBoxLayout()

        # ProjectNeis 인스턴스 생성, class_info 전달
        self.project_neis = ProjectNeis(class_info)

        self.subject_obs_title = QLabel("- 교과 누가기록 입력 도우미 -")
        main_layout.addWidget(self.subject_obs_title)

        # 과목 누가기록 선택창 레이아웃
        self.subject_obs_layout = QGridLayout()

        self.subject_obs_example_btn = QPushButton("양식 다운로드")
        self.subject_obs_example_btn.clicked.connect(self.subject_obs_download_file)
        self.subject_obs_example_btn.setFixedSize(140, 50)
        self.subject_obs_layout.addWidget(self.subject_obs_example_btn,0,0)

        self.subject_obs_auto_btn = QPushButton("자동 제작")
        self.subject_obs_auto_btn.setEnabled(False)
        self.subject_obs_auto_btn.setFixedSize(100,50)
        self.subject_obs_layout.addWidget(self.subject_obs_auto_btn,0,1)

        self.subject_obs_upload_btn = QPushButton("파일 업로드")
        self.subject_obs_upload_check = False
        self.subject_obs_upload_btn.setFixedSize(100,50)
        self.subject_obs_upload_btn.clicked.connect(self.subject_obs_upload_file)
        self.subject_obs_layout.addWidget(self.subject_obs_upload_btn,0,2)

        ## 과목 누가기록 업로드 확인창 레이아웃
        self.subject_obs_process_layout = QVBoxLayout()
        self.subject_obs_process_label = QLabel("파일을 업로드 해주세요!")
        # self.subject_obs_process_label.setFixedWidth(150)
        self.subject_obs_process_layout.addWidget(self.subject_obs_process_label)

        self.subject_obs_layout.addLayout(self.subject_obs_process_layout,0,3)

        main_layout.addLayout(self.subject_obs_layout)


        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 미리보기 추가
        preview_btn = QPushButton("- 업로드된 파일 미리보기 및 수정 -")
        preview_btn.clicked.connect(self.subject_obs_previw)

        main_layout.addWidget(preview_btn)

        self.subject_obs_table = QTableWidget()
        self.subject_obs_table.setRowCount(20)
        self.subject_obs_table.setColumnCount(4)

        self.subject_obs_table.setEditTriggers(QAbstractItemView.DoubleClicked)
 
        main_layout.addWidget(self.subject_obs_table)

        subject_obs_run_layout = QHBoxLayout()

        start_num_input = QLineEdit()
        start_num_input.setFixedSize(180,50)
        start_num_input.setPlaceholderText("시작 학생 번호")

        end_num_input = QLineEdit()
        end_num_input.setPlaceholderText("끝 학생 번호")
        end_num_input.setFixedSize(180,50)

        run_btn =QPushButton("Neis 자동입력 실행")
        run_btn.clicked.connect(lambda: self.subject_obs_run(
            table_to_df(self.subject_obs_table),
            start_num_input.text(),
            end_num_input.text()
        ))
        run_btn.setFixedSize(180,50)


        subject_obs_run_layout.addWidget(start_num_input)
        subject_obs_run_layout.addWidget(end_num_input)
        subject_obs_run_layout.addWidget(run_btn)

        main_layout.addLayout(subject_obs_run_layout)
        
        # 최종 레이아웃 설정
        self.setLayout(main_layout)

    def subject_obs_download_file(self):
        # 파일 다운로드 경로 및 파일명 설정
        file_path = r'C:\Gamgee\neis\example\subject_obs_example.csv'  # 다운로드할 파일의 URL
        if os.path.exists(file_path):
            try:
                # 파일을 시스템 기본 프로그램으로 열기
                if sys.platform.startswith('darwin'):  # macOS
                    subprocess.call(('open', file_path))
                elif os.name == 'nt':  # Windows
                    os.startfile(file_path)

            except Exception as e:
                # 오류 발생 시 메시지 출력
                print(f'파일 열기 실패: {str(e)}')
        else:
            # 파일이 없을 경우 오류 메시지
            print(f'파일을 찾을 수 없음: {file_path}')

    def subject_obs_upload_file(self):
        # 교과 누가기록 대화 상자 열기
        file_path, _ = QFileDialog.getOpenFileName(self, '교과 누가기록 파일 선택', '', 'CSV 파일 (*.csv)')
        
        if file_path:
            # 선택된 파일 경로를 라벨에 표시
            self.subject_obs_process_label.setText(f'업로드한 파일 : {file_path}')
            
            # 파일을 지정된 경로로 복사 (예: /uploads/ 디렉토리)
            current_directory = os.path.dirname(os.path.abspath(__file__))
            destination_directory = os.path.join(current_directory, 'uploads')

            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
            
            self.subject_obs_destination_path = os.path.join(destination_directory, 'subject_obs_example.csv')

            try:
                shutil.copy(file_path, self.subject_obs_destination_path)
                print(f"파일이 성공적으로 {self.subject_obs_destination_path}로 복사되었습니다.")
            except Exception as e:
                print(f"파일 복사 중 오류 발생: {e}")

    def subject_obs_previw(self) :
        # Assuming self.subject_obs_destination_path contains the path to the CSV file
        csv_file_path = self.subject_obs_destination_path

        # Open and read the CSV file
        with open(csv_file_path, newline='', encoding='cp949') as csv_file:
            reader = csv.reader(csv_file)

            # Clear the table first in case there is existing data
            self.subject_obs_table.setRowCount(0)
            self.subject_obs_table.setColumnCount(0)

            # Iterate over the CSV file
            for row_index, row_data in enumerate(reader):
                if row_index == 0:
                    # Set the column count based on the header row
                    self.subject_obs_table.setColumnCount(len(row_data))
                    # Add the header row
                    self.subject_obs_table.setHorizontalHeaderLabels(row_data)
                else:
                    # Add a new row
                    self.subject_obs_table.insertRow(self.subject_obs_table.rowCount())
                    # Populate the row with data
                    for column_index, cell_data in enumerate(row_data):
                        item = QTableWidgetItem(cell_data)
                        self.subject_obs_table.setItem(row_index - 1, column_index, item)

    def subject_obs_run(self, df, start_num, end_num) :
        
        self.project_neis.subject_observation(subject_df=df,
                                              start_num=start_num,
                                              end_num=end_num)

class AggSubjectObs(QDialog) :

    def __init__(self, parent=None) :
        super().__init__(parent)
        self.initUI()

    def initUI(self) :
        
        main_layout = QHBoxLayout()

        main_layout.addStretch(2)

        start_num_input = QLineEdit()
        start_num_input.setPlaceholderText("시작 학생 번호")
        start_num_input.setFixedSize(180,50)

        end_num_input = QLineEdit()
        end_num_input.setPlaceholderText("끝 학생 번호")
        end_num_input.setFixedSize(180,50)

        run_btn =QPushButton("Neis 자동입력 실행")
        run_btn.clicked.connect(lambda: self.agg_subject_obs_run(
            start_num_input.text(),
            end_num_input.text()
        ))
        run_btn.setFixedSize(180,50)

        main_layout.addWidget(start_num_input)
        main_layout.addWidget(end_num_input)
        main_layout.addWidget(run_btn)

        self.setLayout(main_layout)

    def agg_subject_obs_run(self, start_num, end_num) :
        
        self.project_neis.aggregate_subject_observation(
                                              start_num=start_num,
                                              end_num=end_num)

class SubjectGrade(QDialog) :

    def __init__(self) :
        super().__init__()

class AggExtraObs(QDialog) :

    def __init__(self, parent=None) :
        super().__init__(parent)
        self.initUI()

    def initUI(self) :
        
        main_layout = QHBoxLayout()

        main_layout.addStretch(2)

        start_num_input = QLineEdit()
        start_num_input.setPlaceholderText("시작 학생 번호")
        start_num_input.setFixedSize(180,50)

        end_num_input = QLineEdit()
        end_num_input.setPlaceholderText("끝 학생 번호")
        end_num_input.setFixedSize(180,50)

        run_btn =QPushButton("Neis 자동입력 실행")
        run_btn.clicked.connect(lambda: self.agg_extra_obs_run(
            start_num_input.text(),
            end_num_input.text()
        ))
        run_btn.setFixedSize(180,50)

        main_layout.addWidget(start_num_input)
        main_layout.addWidget(end_num_input)
        main_layout.addWidget(run_btn)

        self.setLayout(main_layout)

    def agg_extra_obs_run(self, start_num, end_num) :
        
        self.project_neis.aggregate_extra_observation(
                                              start_num=start_num,
                                              end_num=end_num)

class ExtraSportsClub(QDialog) :
        
    def __init__(self, parent=None) :
        super().__init__(parent)
        self.initUI()

    def initUI(self) :

        main_layout = QHBoxLayout()

        main_layout.addStretch(2)

        start_num_input = QLineEdit()
        start_num_input.setPlaceholderText("시작 행 번호")
        start_num_input.setFixedSize(180,50)

        end_num_input = QLineEdit()
        end_num_input.setPlaceholderText("끝 행 번호")
        end_num_input.setFixedSize(180,50)

        run_btn =QPushButton("Neis 자동입력 실행")
        run_btn.clicked.connect(lambda: self.extra_sports_club_run(
            start_num_input.text(),
            end_num_input.text()
        ))
        run_btn.setFixedSize(180,50)

        main_layout.addWidget(start_num_input)
        main_layout.addWidget(end_num_input)
        main_layout.addWidget(run_btn)

        self.setLayout(main_layout)

    def extra_sports_club_run(self, start_num, end_num) :
        
        self.project_neis.extra_sports_club(start_num=start_num,
                                      end_num=end_num)

class ProjectNeis() :

    def __init__(self, class_info) -> None:
        super().__init__()
        self.class_info = pd.read_csv(class_info, encoding="cp949")

        # self.app = application(backend='uia').connect(title_re =".*Microsoft.*Edge.*")
        # self.neis = self.app["4세대 지능형 나이스 시스템 외 페이지 1개 - 프로필 1 - Microsoft​ Edge', Chrome_WidgetWin_1"]

    def tabs(n) :
        for i in range(n):
            send_keys('{TAB}')
            time.sleep(1)

    def print_identifier(target):
        target = target
        target.print_control_identifiers()

    #과목 누가기록 자동입력
    def subject_observation(self, subject_df, start_num,end_num) :

        #학생정보 및 날짜 정보 추출
        subject = subject_df

        dates = subject['날짜'].dropna()
        subject = subject.iloc[:,:-1].dropna()

        # subject_cols = subject.columns
        # dates['label'] = pd.qcut(dates, len(subject_cols), labels=subject_cols)
        # print(dates)

        #번호별로 돌아가면서 누가기록 작성
        for i in range(int(start_num)-1,int(end_num)) :
            #학생 이름 클릭
            print(self.class_info.iloc[i,1])
            student = self.neis[f'{self.class_info.iloc[i,0]}행 마지막 열 성명 {self.class_info.iloc[i,1]} link']
            student.click_input()

            #다음 학생 눌렀을 때 

            send_keys('{DOWN}')

            add_row = self.neis['행추가']
            add_row.click_input()
            add_row.click_input()

            #겹치지 않는 2개 열 선택
            if len(subject.columns) <=2 :
                random_cols_1 = 0
                random_cols_2 = 1
            else :
                random_cols_1 = int(random.sample(range(0, len(subject.columns)//2),1)[0])
                random_cols_2 = int(random.sample(range(len(subject.columns)//2, len(subject.columns)),1)[0])

            print(random_cols_1)
            print(random_cols_2)

            #랜덤한 행(영역에 맞게 누가기록 추출)
            random_rows = random.sample(range(0,len(subject)), 2)

            #겹치지 않게 날짜 설정
            day1 = dates[random.randint(0,len(dates)//2)]
            day2 = dates[random.randint(len(dates)//2,len(dates)-1)]



            content1 = subject.iloc[random_rows[0],random_cols_1]
            content2 = subject.iloc[random_rows[1],random_cols_2]

            print(day1)
            print(content1)
            print(day2)
            print(content2)

            #첫번째 날짜 기입
            #######아래 좌표만 바꿔주면 됨#########
            pyautogui.click(2792,514)
            pyperclip.copy(day1)
            send_keys("^v")

            self.tabs(2)
            #첫번째 내용 기입
            pyperclip.copy(content1)
            send_keys("^v")

            self.tabs(3)
            #두번째 날짜 기입
            pyperclip.copy(day2)
            send_keys("^v")

            self.tabs(2)
            #두번째 내용 기입
            pyperclip.copy(content2)
            send_keys("^v")


            #저장 버튼 클릭
            save_btn = self.neis['저장Button']
            save_btn.click_input()
            #확인 컨펌
            confirm_button = self.neis['확인Button']
            confirm_button.click_input()

            #한번 더 확인
            confirm_button = self.neis['확인Button']
            confirm_button.click_input()

    #교과발달사항에 통합해서 입력(과목 누가기록)
    def aggregate_subject_observation(self,start_num, end_num) :
        for i in range( int(start_num)-1, int(end_num) ) :

            if i == end_num-1 :
                take_window = self.neis[f"{i+1}행 마지막 행 조회/가져오기 조회/가져오기 button"]
            
            else : 
                take_window = self.neis[f"{i+1}행 조회/가져오기 조회/가져오기 button"]

            #가져오기 창 열기
            
            take_window.click_input()
            
            # '행 전체선택' 체크박스 찾기
            all_checkbox = self.neis['행 전체선택CheckBox2']
            all_checkbox.click_input()

            copy_button = self.neis['복사(줄바꿈 없음)Button']
            copy_button.click_input()

            reflect_button = self.neis['반영']        
            reflect_button.click_input()

            confirm_button = self.neis['확인']   
            confirm_button.click_input()

    #창체 특기사항(누가기록 가져오기)
    def aggregate_extra_observation(self,start_num, end_num) :
        for i in range( int(start_num)-1, int(end_num) ) :

            if i == end_num-1 :
                take_window = self.neis[f"{self.class_info.iloc[i,0]}행 마지막 열 성명 {self.class_info.iloc[i,1]} link"]
            
            else : 
                take_window = self.neis[f"{self.class_info.iloc[i,0]}행 {self.class_info.iloc[i,1]} 링크 {self.class_info.iloc[i,1]} link"]
            print(self.class_info.iloc[i,0])
            print(self.class_info.iloc[i,1])
            #가져오기 창 열기
            
            take_window.click_input()
            
            # '행 전체선택' 체크박스 찾기
            obs_list = self.neis['누가기록 목록']
            all_checkbox = obs_list['행 전체선택']
            all_checkbox.click_input()

            copy_button = self.neis['누가기록복사(줄바꿈 없음)Button']
            copy_button.click_input()

            reflect_button = self.neis['적용Button']        
            reflect_button.click_input()

            confirm_button = self.neis['확인Button']   
            confirm_button.click_input()

            confirm_button = self.neis['확인Button']   
            confirm_button.click_input()

            send_keys('{DOWN}')

    #스포츠클럽 등록하기
    def extra_sports_club(self,start_index, end_index) :
        sports_csv = pd.read_csv("스포츠클럽.csv", encoding='cp949')
        

        for i in range(start_index-2, end_index-1) :
            date = sports_csv.iloc[i,0],sports_csv.iloc[i,1]
            activity_contents = sports_csv.iloc[i,2]

            print(date)
            register_btn = self.neis['등록']
            register_btn.click_input()

            add_students_btn = self.neis['참가자 추가']
            add_students_btn.click_input()


            students_list = self.neis['클럽구성원 목록 리스트']
            students_checkbox = students_list['행 전체선택']
            students_checkbox.click_input()
        
            add_confirm_btn = self.neis['추가']
            add_confirm_btn.click_input()

            pyperclip.copy(date)
            date_input = self.neis['참가일시Edit']
            date_input.click_input()
            send_keys("^v")


            self.tabs(2)
            pyperclip.copy('20')
            send_keys("^v")

            #활동명/대회명
            self.tabs(1)
            pyperclip.copy('배드민턴 연습하기')
            send_keys("^v")

            self.tabs(2)
            pyperclip.copy(activity_contents)
            send_keys("^v")

            students_list = self.neis['활동내역 참가자 리스트']
            students_checkbox = students_list['행 전체선택']
            students_checkbox.click_input()

            self.apply_contents = self.neis['활동내용 일괄적용']
            self.apply_contents.click_input()
            self.apply_time = self.neis['활동시간 일괄적용']
            self.apply_time.click_input()

            save_btn = self.neis['저장']
            save_btn.click_input()

            for i in range(2) :
                confirm_btn = self.neis['확인Button']
                confirm_btn.click_input()