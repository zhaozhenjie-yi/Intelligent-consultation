"""Persistent patient registry. Deletion hides a patient; clinical files are retained."""
from contextlib import contextmanager
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from session_manager import validate_uid


class PatientStore:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS patients (uid TEXT PRIMARY KEY, record_number TEXT, payload TEXT NOT NULL, deleted INTEGER NOT NULL DEFAULT 0)')
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS patient_record_number ON patients(record_number) WHERE deleted=0 AND record_number != ''")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            with db:
                yield db
        finally:
            db.close()

    def list(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute('SELECT payload FROM patients WHERE deleted=0 ORDER BY rowid DESC')]

    def get(self, uid):
        validate_uid(uid)
        with self.connect() as db:
            row = db.execute('SELECT payload FROM patients WHERE uid=? AND deleted=0', (uid,)).fetchone()
        if row is None:
            raise LookupError('就诊人不存在')
        return json.loads(row[0])

    @staticmethod
    def normalize(data, uid, original=None):
        if not isinstance(data, dict):
            raise ValueError('就诊人信息必须为 JSON 对象')
        result = dict(original or {})
        for key in ('name', 'gender', 'notes', 'medical_record_number'):
            value = data.get(key, result.get(key, ''))
            if not isinstance(value, str):
                raise ValueError(f'{key} 必须是文字')
            result[key] = value.strip()
        if not result['name'] or len(result['name']) > 100:
            raise ValueError('请输入有效的就诊人姓名')
        age = data.get('age', result.get('age', 0))
        if isinstance(age, bool) or not isinstance(age, int) or not 0 <= age <= 150:
            raise ValueError('年龄必须为 0 至 150 的整数')
        result.update(uid=validate_uid(uid), age=age)
        result.setdefault('createdAt', datetime.now(timezone.utc).isoformat())
        return result

    def save(self, data, uid=None):
        original = self.get(uid) if uid else None
        uid = uid or uuid.uuid4().hex
        patient = self.normalize(data, uid, original)
        try:
            with self.connect() as db:
                if original:
                    db.execute('UPDATE patients SET record_number=?, payload=? WHERE uid=? AND deleted=0', (patient['medical_record_number'], json.dumps(patient, ensure_ascii=False), uid))
                else:
                    db.execute('INSERT INTO patients(uid,record_number,payload) VALUES(?,?,?)', (uid, patient['medical_record_number'], json.dumps(patient, ensure_ascii=False)))
        except sqlite3.IntegrityError:
            raise ValueError('病历号已存在，请使用其他病历号') from None
        return patient

    def delete(self, uid):
        self.get(uid)
        with self.connect() as db:
            db.execute('UPDATE patients SET deleted=1 WHERE uid=?', (uid,))

    def import_local(self, patients):
        if not isinstance(patients, list) or len(patients) > 1000:
            raise ValueError('patients 必须为最多 1000 项的列表')
        count = 0
        try:
            with self.connect() as db:
                for data in patients:
                    uid = validate_uid(data.get('uid') if isinstance(data, dict) else None)
                    # Never overwrite a server record or resurrect a deleted patient.
                    if db.execute('SELECT 1 FROM patients WHERE uid=?', (uid,)).fetchone():
                        continue
                    patient = self.normalize(data, uid)
                    db.execute('INSERT INTO patients(uid,record_number,payload) VALUES(?,?,?)', (uid, patient['medical_record_number'], json.dumps(patient, ensure_ascii=False)))
                    count += 1
        except sqlite3.IntegrityError:
            raise ValueError('导入的病历号重复，未导入任何数据') from None
        return count
