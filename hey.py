from pywinauto import Desktop, Application

# 활성화된 모든 창 가져오기
windows = Desktop(backend="uia").windows()

for w in windows:
    print(f"Title: {w.window_text()}, Handle: {w.handle}")

# 원하는 제목의 창 선택 (예: 'Microsoft Edge' 또는 'Chrome')
for w in windows:
    if "나이스" in w.window_text():
        # 해당 창의 핸들로 Application 객체를 연결


        print(neis)