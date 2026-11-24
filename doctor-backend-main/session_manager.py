"""Per-patient JSON storage, retaining compatibility with existing sessions."""
import json
import os
import re
import tempfile
from pathlib import Path
from threading import RLock


def validate_uid(uid):
    if not isinstance(uid, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', uid):
        raise ValueError('uid 必须为 1 至 80 位字母、数字、下划线或短横线')
    return uid


class SessionManager:
    def __init__(self, base_dir='json_session'):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._locks = {}
        self._guard = RLock()

    def lock(self, uid):
        validate_uid(uid)
        with self._guard:
            return self._locks.setdefault(uid, RLock())

    def get_file_path(self, uid):
        return self.base_dir / f'{validate_uid(uid)}.json'

    def load_user_sessions(self, uid):
        with self.lock(uid):
            path = self.get_file_path(uid)
            return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}

    def save_user_sessions(self, uid, user_sessions):
        with self.lock(uid):
            handle, tmp = tempfile.mkstemp(dir=self.base_dir, suffix='.tmp')
            try:
                with os.fdopen(handle, 'w', encoding='utf-8') as stream:
                    json.dump(user_sessions, stream, ensure_ascii=False)
                os.replace(tmp, self.get_file_path(uid))
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
