class AppUserState:
    def __init__(self):
        self.user_id = None

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

# 전역적으로 사용할 인스턴스 생성
app_user_state = AppUserState()
