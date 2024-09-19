import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from project_role import RoleChecker

# PyQt5 애플리케이션 클래스 정의
class SpreadsheetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.role_checker = RoleChecker()  # initUI 이전에 초기화
        self.initUI()

    def initUI(self):
        # 윈도우 설정
        self.setWindowTitle('오늘의 1인 1역')
        self.setFixedSize(500,800)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.setSpacing(20)  # 위젯 간의 간격 설정

        # 라벨 추가
        label = QLabel('오늘의 1인 1역')
        label.setAlignment(Qt.AlignCenter)

        # 라벨 폰트 설정
        label_font = QFont('맑은 고딕', 18, QFont.Bold)
        label.setFont(label_font)
        layout.addWidget(label)

        # 리스트 위젯 추가
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # 리스트 아이템 폰트 설정
        item_font = QFont('맑은 고딕', 16)
        self.list_widget.setFont(item_font)

        # 데이터 가져오기 및 리스트에 추가
        data = self.role_checker.get_values()
        self.list_widget.addItems(data)

        # 레이아웃 설정
        self.setLayout(layout)

        # 전체 윈도우 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
            }
            QLabel {
                color: #333;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QListWidget::item {
                padding: 10px;
            }
        """)

# 메인 함수
def main():
    app = QApplication(sys.argv)
    ex = SpreadsheetApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
