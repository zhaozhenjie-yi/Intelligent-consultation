import os
import json

class SessionManager:
    def __init__(self, base_dir='json_session'):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def get_file_path(self, uid):
        return os.path.join(self.base_dir, f'{uid}.json')

    def load_user_sessions(self, uid):
        file_path = self.get_file_path(uid)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return {}

    def save_user_sessions(self, uid, user_sessions):
        file_path = self.get_file_path(uid)
        with open(file_path, 'w') as file:
            json.dump(user_sessions, file)