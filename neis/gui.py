import sys, os, shutil, json, subprocess, csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QFileDialog, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from functools import partial

#### ------- TOOLS

def load_data(filename):
    """ 사용자 데이터 또는 리소스 파일을 불러오는 함수 """
    # 먼저 사용자 데이터 디렉토리에서 파일이 있는지 확인
    current_path = os.path.dirname(os.path.abspath(__file__))
    user_data_path = os.path.join(current_path, filename)

    return user_data_path

class NeisAssistantGUI(QWidget) :

    def __init__(self, save_class_info):
        super().__init__()

        self.setWindowTitle('Project_neis v0.1')
        self.setStyleSheet("background-color: #f0f0f0;")

        self.class_info_check = False
        self.save_class_info = save_class_info

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
        self.class_info_download_button.setFixedSize(100,30)
        class_info_open = partial(self.open_file, file_path=r'C:\Gamgee\neis\example\class_info_example.csv')
        self.class_info_download_button.clicked.connect(class_info_open)
        class_info_layout.addWidget(self.class_info_download_button)

        self.class_info_upload_button = QPushButton('파일 업로드')
        self.class_info_upload_button.setFixedSize(100,30)
        self.class_info_upload_button.clicked.connect(self.class_info_upload_file)
        class_info_layout.addWidget(self.class_info_upload_button)

        ### 업로드 제목
        self.class_info_file_title_label = QLabel('학급 정보 :')
        class_info_layout.addWidget(self.class_info_file_title_label)

        ### 업로드 여부 확인
        self.class_info_file_status_label = QLabel('미입력')
        class_info_layout.addWidget(self.class_info_file_status_label)

        class_info_layout.addStretch(2)

        ## 정보 저장 체크 레아이웃
        class_info_save_layout = QHBoxLayout()
        
        self.class_info_save = QCheckBox()
        self.class_info_save_label = QLabel("학급 정보 저장하기")
        if self.save_class_info:
            self.class_info_save.setChecked(True)

        class_info_save_layout.addWidget(self.class_info_save)
        class_info_save_layout.addWidget(self.class_info_save_label)
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
        subject_observation_btn.setFixedSize(100,30)
        subject_observation_btn.clicked.connect(self.subject_obs_run)
        subject_layout.addWidget(subject_observation_btn)

        subject_observation_aggregation_btn = QPushButton('교과 발달사항')
        subject_observation_aggregation_btn.setFixedSize(100,30)
        subject_layout.addWidget(subject_observation_aggregation_btn)

        subject_grade_btn = QPushButton('교과 성적입력')
        subject_grade_btn.setFixedSize(100,30)
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
        extra_layout = QGridLayout()
        
        extra_observation_btn = QPushButton("창체 누가기록")
        extra_layout.addWidget(extra_observation_btn,0,0)

        extra_observation_aggregation_btn = QPushButton("창체 특기사항")
        extra_layout.addWidget(extra_observation_aggregation_btn,0,1)

        main_layout.addLayout(extra_layout)

        # 구분선 추가
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)


        # 스포츠 클럽
        ## 제목 레이아웃
        sports_club_title_layout = QVBoxLayout()
        
        sports_club_title_label = QLabel("- 스포츠 클럽 - ")
        sports_club_title_layout.addWidget(sports_club_title_label)

        main_layout.addLayout(sports_club_title_layout)

        ## 메인 레이아웃
        sports_club_layout = QGridLayout()

        sports_club_btn = QPushButton("스포츠 클럽 자동 입력")
        


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

    def upload_file(self, file_path) :

        if file_path:         
            # 파일을 지정된 경로로 복사 (예: /uploads/ 디렉토리)
            current_directory = os.path.dirname(os.path.abspath(__file__))
            destination_directory = os.path.join(current_directory, 'uploads')

            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
        else :
            self.show_error_message_box(box_text="파일 경로가 올바르지 않습니다.",
                                        box_title="파일 경로 오류")
            


    def class_info_upload_file(self):
        # 파일 선택 대화 상자 열기
        file_path, _ = QFileDialog.getOpenFileName(self, '파일 선택', '', 'CSV 파일 (*.csv)')
        
        if file_path:
            # 선택된 파일 경로를 라벨에 표시
            self.class_info_file_status_label.setText('입력됨')
            destination_directory = self.upload_file(file_path)
            
            # 파일을 지정된 경로로 복사 (예: /uploads/ 디렉토리)
            self.class_info_destination_path = os.path.join(destination_directory, 'class_info.csv')
            try:
                shutil.copy(file_path, self.class_info_destination_path)
                print(f"파일이 성공적으로 {self.class_info_destination_path}로 복사되었습니다.")
            except Exception as e:
                print(f"파일 복사 중 오류 발생: {e}")

        
        self.class_info_check = True
        self.class_info_file_status_label.setStyleSheet("color: blue; text-decoration: underline;")
        self.class_info_file_status_label.mousePressEvent = partial(self.open_file, self.class_info_destination_path)


    def show_error_message_box(self,
                               box_title,
                               box_text):
        # 메시지 박스 생성
        msg = QMessageBox()
        msg.setText(box_text)
        msg.setWindowTitle(box_title)
        msg.setStandardButtons(QMessageBox.Ok)  # 확인 버튼만 있는 메시지 박스
        
        # 메시지 박스 실행
        msg.exec_()
    

    def subject_obs_run(self) :
        if self.class_info_check == False :
            self.show_error_message_box(box_text="먼저 학급 정보를 입력해주세요!",
                                        box_title="학급 정보 입력")
            return

        self.hide()

        self.grade_obs_dialog = SubjectObs()
        self.grade_obs_dialog.exec_()

        self.show()


class SubjectObs(QDialog) :

    def __init__(self) :
        super().__init__()

        # 메인 레이아웃
        self.setWindowTitle("교과 누가기록")
        self.resize(800, 600)
        main_layout = QVBoxLayout()

        self.subject_obs_title = QLabel("- 교과 누가기록 입력 도우미 -")
        main_layout.addWidget(self.subject_obs_title)

        # 과목 누가기록 선택창 레이아웃
        self.subject_obs_layout = QGridLayout()

        self.subject_obs_example_btn = QPushButton("양식 다운로드")
        self.subject_obs_example_btn.clicked.connect(self.subject_obs_download_file)
        self.subject_obs_example_btn.setFixedSize(100, 50)
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

        run_btn =QPushButton("Neis 자동입력 실행")
        run_btn.setFixedSize(180,50)
        main_layout.addWidget(run_btn,alignment=Qt.AlignCenter)
        
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
            
        
class SubjectObsAgg(QDialog) :

    def __init__(self) :
        super().__init__()

class SubjectGrade(QDialog) :

    def __init__(self) :
        super().__init__()

class SportsClub(QDialog) :

    def __init__(self) :
        super().__init__()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # JSON 파일 로드
    json_path = load_data('settings.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        save_class_info = data['save_class_info']

    project_neis_gui = NeisAssistantGUI(save_class_info)
    project_neis_gui.show()
    sys.exit(app.exec_())
