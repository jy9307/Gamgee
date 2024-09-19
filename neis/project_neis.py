from pywinauto import application
from pywinauto.keyboard import send_keys
import pandas as pd
import pyautogui, random, pyperclip, time
from PyQt5.QtCore import QThread, pyqtSignal

class ProjectNeis(QThread) :

    def __init__(self) -> None:
        super().__init__()
        self.class_info = pd.read_csv("학생정보.csv", encoding="cp949")
        self.app = application(backend='uia').connect(title_re =".*Microsoft.*Edge.*")
        self.neis = self.app["4세대 지능형 나이스 시스템 외 페이지 1개 - 프로필 1 - Microsoft​ Edge', Chrome_WidgetWin_1"]

    def tabs(n) :
        for i in range(n):
            send_keys('{TAB}')
            time.sleep(1)

    def  print_identifier(target):
        target = target
        target.print_control_identifiers()

    #과목 누가기록 자동입력
    def subject_observation(self, subject_name, student_number,last_student_number) :
        subject_file = subject_name+'.csv'


        #학생정보 및 날짜 정보 추출
        subject = pd.read_csv(subject_file,encoding='cp949')

        dates = subject['날짜'].dropna()
        subject = subject.iloc[:,:-1].dropna()

        # subject_cols = subject.columns
        # dates['label'] = pd.qcut(dates, len(subject_cols), labels=subject_cols)
        # print(dates)

        #번호별로 돌아가면서 누가기록 작성
        for i in range(student_number-1,last_student_number) :
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
    def aggregate_subject_observation(self,student_number, last_student_number) :
        for i in range(student_number-1,last_student_number) :

            if i == last_student_number-1 :
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
    def aggregate_extra_observation(self,student_number, last_student_number) :
        for i in range(student_number-1,last_student_number) :

            if i == last_student_number-1 :
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
    def sports_club(self,start_index, end_index) :
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





## 과목 이름 / 학생 번호 순서

#과목 누가기록 등록(과목, 첫학생 번호, 끝학생 번호)
#subject_observation("수학",1,23)

#과목 누가기록 통합(교과학습발달사항)
#aggregate_subject_observation(1,23)

#창체 특기사항(창체 누가기록 가져오기)
#aggregate_extra_observation(1,23)

#스포츠클럽 가져오기
#sports_club(2,18)


#print_identifier(self.neis)