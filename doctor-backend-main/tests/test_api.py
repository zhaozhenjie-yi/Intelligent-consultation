import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
_boot = tempfile.TemporaryDirectory()
os.environ['DATA_DIR'] = _boot.name
import flask_app as api
from patient_store import PatientStore
from session_manager import SessionManager


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        api.DATA_DIR = Path(self.directory.name)
        api.patient_store = PatientStore(api.DATA_DIR / 'patients.sqlite3')
        api.session_manager = SessionManager(api.DATA_DIR / 'json_session')
        self.client = api.app.test_client()

    def create(self, **values):
        response = self.client.post('/api/patients', json={'name': '虚构测试患者', 'age': 30, 'gender': '男', **values})
        self.assertEqual(response.status_code, 201)
        return response.json['patient']['uid']

    def test_patient_crud_persistence_and_record_number_conflicts(self):
        uid = self.create(medical_record_number='TEST-1')
        self.assertEqual(PatientStore(api.patient_store.path).get(uid)['age'], 30)
        duplicate = self.client.post('/api/patients', json={'name': '重复', 'age': 20, 'medical_record_number': 'TEST-1'})
        self.assertEqual(duplicate.status_code, 400)
        updated = self.client.put(f'/api/patients/{uid}', json={'name': '修改后的虚构患者', 'age': 31})
        self.assertEqual(updated.json['patient']['age'], 31)
        api.session_manager.save_user_sessions(uid, {'conversation_history': [{'role': 'user', 'content': '测试'}]})
        listed = self.client.get('/api/patients').json['patients']
        self.assertEqual(listed[0]['consultationCount'], 1)
        self.assertEqual(self.client.delete(f'/api/patients/{uid}').status_code, 200)
        self.assertEqual(self.client.get('/api/patients').json['patients'], [])
        self.assertEqual(self.client.get(f'/api/patients/{uid}').status_code, 404)
        self.assertTrue(api.session_manager.get_file_path(uid).exists())

    def test_import_idempotency_and_atomic_conflict(self):
        patient = {'uid': 'legacy_001', 'name': '导入测试', 'age': 30, 'medical_record_number': 'LEGACY-1'}
        for expected in (1, 0):
            response = self.client.post('/api/import_local_patients', json={'patients': [patient]})
            self.assertEqual(response.json['imported'], expected)
        response = self.client.post('/api/import_local_patients', json={'patients': [dict(patient, uid='new', medical_record_number='FREE'), dict(patient, uid='conflict')]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(api.patient_store.list()), 1)

    def test_conversation_ocr_report_json_download_and_cache(self):
        uid = self.create()
        fields = dict.fromkeys(api.RECORD_SCHEMA['required'], '不详')
        fields.update(name='虚构测试患者', age=None, gender='男')
        with patch.object(api, 'complete', side_effect=['请问年龄？', '这是测试病历', json.dumps(fields)]) as complete:
            self.assertEqual(self.client.post('/api/generate_response', json={'uid': uid, 'text': '虚构测试患者'}).status_code, 200)
            history = self.client.get('/api/get_conversation_history', query_string={'uid': uid}).json['conversation_history']
            self.assertEqual(len(history), 2)
            self.assertEqual(self.client.get('/api/get_conversation_rounds', query_string={'uid': uid}).json['rounds'], 1)
            self.assertEqual(self.client.post('/api/get_multiple_conversation_rounds', json={'uids': [uid]}).json['results'][0]['rounds'], 1)
            with patch.object(api, 'recognize_image', return_value={'words_result': [{'words': '合成报告'}]}):
                result = self.client.post('/api/upload_check_record', data={'uid': uid, 'image': (io.BytesIO(b'test fixture'), 'test.jpg', 'image/jpeg')})
                self.assertEqual(result.json['text'], '合成报告')
                self.assertTrue((api.DATA_DIR / result.json['image_path']).exists())
            for _ in range(2):
                self.assertEqual(self.client.post('/api/generate_report', json={'uid': uid}).json['report'], '这是测试病历')
            for _ in range(2):
                result = self.client.post('/api/change_medical_record', json={'uid': uid, 'text': '这是测试病历'})
                self.assertIsNone(json.loads(result.json['content'])['age'])
            self.assertEqual(complete.call_count, 3)
        result = self.client.get('/api/download_report', query_string={'uid': uid})
        self.assertEqual(result.status_code, 200)
        self.assertIn('合成报告', result.data.decode('utf-8-sig'))

    def test_report_uses_registration_and_invalidates_cache_after_edit(self):
        uid = self.create(medical_record_number='REGISTERED-1')
        self.assertEqual(self.client.post('/api/generate_report', json={'uid': uid}).status_code, 400)
        api.session_manager.save_user_sessions(uid, {'conversation_history': [{'role': 'user', 'content': '虚构测试'}]})
        with patch.object(api, 'complete', return_value='测试病历') as complete:
            self.assertEqual(self.client.post('/api/generate_report', json={'uid': uid}).status_code, 200)
            self.assertIn('REGISTERED-1', complete.call_args.args[1][1]['content'])
            self.client.put(f'/api/patients/{uid}', json={'name': '修改登记姓名'})
            self.assertEqual(self.client.get('/api/download_report', query_string={'uid': uid}).status_code, 400)
            self.assertEqual(self.client.post('/api/generate_report', json={'uid': uid}).status_code, 200)
            self.assertIn('修改登记姓名', complete.call_args.args[1][1]['content'])
            self.assertEqual(complete.call_count, 2)

    def test_failed_models_do_not_persist_incomplete_turns(self):
        with patch.object(api, 'complete', side_effect=api.UpstreamError('模型不可用')):
            result = self.client.post('/api/generate_response', json={'uid': 'test', 'text': '测试'})
        self.assertEqual(result.status_code, 502)
        self.assertEqual(api.session_manager.load_user_sessions('test'), {})

    def test_invalid_payloads_and_path_traversal(self):
        cases = [('/api/generate_response', {'text': '测试'}), ('/api/generate_response', {'uid': '../escape', 'text': '测试'}), ('/api/generate_response', {'uid': 'a', 'text': ''}), ('/api/get_multiple_conversation_rounds', {'uids': 'abc'}), ('/api/change_medical_record', {'uid': 'a'}), ('/api/generate_report', {'uid': 'a'})]
        for route, data in cases:
            with self.subTest(route=route, data=data):
                self.assertEqual(self.client.post(route, json=data).status_code, 400)
        self.assertEqual(self.client.post('/api/patients', data='not-json', content_type='application/json').status_code, 400)

    def test_bad_ocr_does_not_store_images(self):
        with patch.object(api, 'recognize_image', side_effect=api.UpstreamError('OCR 失败')):
            result = self.client.post('/api/upload_check_record', data={'uid': 'test', 'image': (io.BytesIO(b'test'), 'x.png', 'image/png')})
        self.assertEqual(result.status_code, 502)
        self.assertFalse((api.DATA_DIR / 'uploaded_images').exists())

    def test_bad_structured_output_is_not_cached(self):
        with patch.object(api, 'complete', return_value='{"name":"test"}'):
            result = self.client.post('/api/change_medical_record', json={'uid': 'test', 'text': '测试病历'})
        self.assertEqual(result.status_code, 502)
        self.assertEqual(api.session_manager.load_user_sessions('test'), {})

    def test_audio_and_cors(self):
        with patch.object(api, 'transcribe', return_value='合成语音'):
            result = self.client.post('/api/upload_audio', data={'audioFile': (io.BytesIO(b'test'), 'test.webm')})
            self.assertEqual(result.json['content'], '合成语音')
        with patch.object(api, 'transcribe', side_effect=api.UpstreamError('语音未配置')):
            result = self.client.post('/api/upload_audio', data={'audioFile': (io.BytesIO(b'test'), 'test.webm')})
            self.assertEqual(result.status_code, 502)
        result = self.client.options('/api/patients/test', headers={'Origin': 'http://localhost:8504', 'Access-Control-Request-Method': 'DELETE'})
        self.assertIn('DELETE', result.headers['Access-Control-Allow-Methods'])
        self.assertIn('PUT', result.headers['Access-Control-Allow-Methods'])


if __name__ == '__main__':
    unittest.main()
