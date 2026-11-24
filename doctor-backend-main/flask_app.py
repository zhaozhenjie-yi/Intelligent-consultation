import io
import json
import os
import uuid
from functools import lru_cache
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from openai import OpenAI, OpenAIError
from aip import AipOcr
from local_config import env
from patient_store import PatientStore
from session_manager import SessionManager, validate_uid
from prompts import QA_PROMPT, REPORT_PROMPT, RECORD_SCHEMA

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(env('DATA_DIR', str(ROOT)))
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
CORS(app, resources={r'/api/*': {'origins': '*'}}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
session_manager = SessionManager(DATA_DIR / 'json_session')
patient_store = PatientStore(DATA_DIR / 'patients.sqlite3')


class UpstreamError(Exception):
    pass


def body():
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise ValueError('请求内容必须为 JSON 对象')
    return value


def uid_from(data):
    return validate_uid(data.get('uid'))


def text_from(data):
    text = data.get('text')
    if not isinstance(text, str) or not text.strip():
        raise ValueError('text 不能为空')
    if len(text) > 100000:
        raise ValueError('输入文字过长')
    return text.strip()


@app.errorhandler(Exception)
def api_error(error):
    if isinstance(error, HTTPException):
        status, message = error.code, error.description
    elif isinstance(error, ValueError):
        status, message = 400, str(error)
    elif isinstance(error, LookupError):
        status, message = 404, str(error)
    elif isinstance(error, UpstreamError):
        status, message = 502, str(error)
    else:
        # Never expose provider credentials, patient text or raw SDK errors to clients.
        app.logger.error('Request failed: %s', type(error).__name__)
        status, message = 500, '服务器处理失败，请稍后重试'
    return jsonify(status='error', message=message, error=message), status


@lru_cache(maxsize=3)
def model_client(purpose):
    key = env(f'{purpose}_API_KEY', env('DEEPSEEK_API_KEY', ''))
    if not key:
        raise UpstreamError('尚未配置模型 API 密钥')
    return OpenAI(api_key=key, base_url=env(f'{purpose}_BASE_URL', 'https://api.deepseek.com/v1'), timeout=60, max_retries=0)


def complete(purpose, messages, json_mode=False):
    kwargs = {'response_format': {'type': 'json_object'}} if json_mode else {}
    try:
        response = model_client(purpose).chat.completions.create(
            model=env(f'{purpose}_MODEL', 'deepseek-chat'), messages=messages, temperature=0, **kwargs)
        text = response.choices[0].message.content
        if not text:
            raise UpstreamError('模型返回空内容，请重试')
        return text
    except OpenAIError as error:
        app.logger.warning('%s upstream failed: %s', purpose, type(error).__name__)
        raise UpstreamError('模型服务不可用，请检查密钥、余额和服务地址后重试') from None


@lru_cache(maxsize=1)
def ocr_client():
    keys = [env(k, '') for k in ('BAIDU_OCR_APP_ID', 'BAIDU_OCR_API_KEY', 'BAIDU_OCR_SECRET_KEY')]
    if not all(keys):
        raise UpstreamError('尚未配置 OCR 服务')
    client = AipOcr(*keys)
    client.setConnectionTimeoutInMillis(10000)
    client.setSocketTimeoutInMillis(30000)
    return client


def recognize_image(content):
    try:
        result = ocr_client().basicGeneral(content)
    except Exception:
        raise UpstreamError('OCR 服务连接失败，请稍后重试') from None
    if result.get('error_code') or not result.get('words_result'):
        raise UpstreamError('检查报告未识别成功，请检查图片清晰度及 OCR 服务配置')
    return result


def transcribe(content, filename):
    key, url = env('AUDIO_API_KEY', ''), env('AUDIO_BASE_URL', '')
    if not key or not url:
        raise UpstreamError('语音转写尚未配置，请先使用文字输入，或配置 AUDIO_API_KEY 和 AUDIO_BASE_URL')
    try:
        result = OpenAI(api_key=key, base_url=url, timeout=60, max_retries=0).audio.transcriptions.create(
            model=env('AUDIO_MODEL', 'whisper-1'), file=(filename, content), language='zh')
        if not result.text:
            raise UpstreamError('未识别到语音，请重试')
        return result.text
    except OpenAIError:
        raise UpstreamError('语音服务不可用，请检查语音服务配置') from None


def rounds(uid):
    history = session_manager.load_user_sessions(uid).get('conversation_history', [])
    count = sum(message.get('role') == 'user' for message in history)
    return {'uid': uid, 'rounds': count, 'hasConsulted': count > 0}


def patient_view(patient):
    result = dict(patient)
    stats = rounds(result['uid'])
    origin = env('FRONTEND_URL', '').rstrip('/') or request.headers.get('Origin') or (
        request.headers.get('X-Forwarded-Proto', request.scheme) + '://' + request.headers.get('X-Forwarded-Host', request.host))
    result.update(consultationCount=stats['rounds'], consulted=stats['hasConsulted'],
                  link=f"{origin}/#/interaction?uid={result['uid']}",
                  casebookLink=f"{origin}/#/casebook/small?uid={result['uid']}")
    return result


@app.get('/api/health')
def health():
    return jsonify(status='success', audioConfigured=bool(env('AUDIO_API_KEY', '') and env('AUDIO_BASE_URL', '')))


@app.route('/api/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'GET':
        return jsonify(status='success', patients=[patient_view(p) for p in patient_store.list()])
    return jsonify(status='success', patient=patient_view(patient_store.save(body()))), 201


@app.route('/api/patients/<uid>', methods=['GET', 'PUT', 'DELETE'])
def patient(uid):
    if request.method == 'GET':
        return jsonify(status='success', patient=patient_view(patient_store.get(uid)))
    if request.method == 'DELETE':
        patient_store.delete(uid)
        return jsonify(status='success')
    return jsonify(status='success', patient=patient_view(patient_store.save(body(), uid)))


@app.post('/api/import_local_patients')
def import_local_patients():
    count = patient_store.import_local(body().get('patients'))
    return jsonify(status='success', imported=count, message=f'已导入 {count} 位就诊人')


@app.get('/api/get_conversation_history')
def get_conversation_history():
    uid = uid_from(request.args)
    return jsonify(status='success', conversation_history=session_manager.load_user_sessions(uid).get('conversation_history', []))


@app.get('/api/get_conversation_rounds')
def get_conversation_rounds():
    return jsonify(status='success', **rounds(uid_from(request.args)))


@app.post('/api/get_multiple_conversation_rounds')
def get_multiple_conversation_rounds():
    uids = body().get('uids')
    if not isinstance(uids, list) or len(uids) > 1000:
        raise ValueError('uids 必须为最多 1000 项的列表')
    return jsonify(status='success', results=[rounds(validate_uid(uid)) for uid in uids])


@app.post('/api/generate_response')
def generate_response():
    data = body()
    uid, text = uid_from(data), text_from(data)
    with session_manager.lock(uid):
        state = session_manager.load_user_sessions(uid)
        history = state.setdefault('conversation_history', [])
        reply = complete('QA', [{'role': 'system', 'content': QA_PROMPT}, *history, {'role': 'user', 'content': text}])
        history.extend([{'role': 'user', 'content': text}, {'role': 'assistant', 'content': reply}])
        session_manager.save_user_sessions(uid, state)
    return jsonify(status='success', text=reply)


@app.post('/api/upload_check_record')
def upload_image():
    uid = uid_from(request.form)
    file = request.files.get('image')
    if not file or file.mimetype not in ('image/png', 'image/jpeg', 'image/webp', 'image/bmp'):
        raise ValueError('请上传 PNG、JPEG、WEBP 或 BMP 图片')
    content = file.read()
    if not content:
        raise ValueError('图片不能为空')
    result = recognize_image(content)
    suffix = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp', 'image/bmp': '.bmp'}[file.mimetype]
    relative = Path('uploaded_images') / f'{uid}_{uuid.uuid4().hex}{suffix}'
    (DATA_DIR / relative).parent.mkdir(parents=True, exist_ok=True)
    with session_manager.lock(uid):
        (DATA_DIR / relative).write_bytes(content)
        state = session_manager.load_user_sessions(uid)
        state.setdefault('ocr_results', []).append({'image_path': relative.as_posix(), 'ocr_result': result})
        session_manager.save_user_sessions(uid, state)
    text = '\n'.join(item['words'] for item in result['words_result'])
    return jsonify(status='success', image_path=relative.as_posix(), ocr_result=result, text=text)


def patient_identity(uid):
    try:
        patient = patient_store.get(uid)
    except LookupError:
        return {}
    return {key: patient[key] for key in ('name', 'age', 'gender', 'medical_record_number')}


def report_inputs(state, uid):
    dialogue = '\n'.join(f"{'患者' if msg['role']=='user' else '医生'}: {msg['content']}" for msg in state.get('conversation_history', []))
    ocr = '\n'.join(word['words'] for result in state.get('ocr_results', []) for word in result['ocr_result'].get('words_result', []))
    identity = patient_identity(uid)
    if dialogue and identity:
        dialogue = '患者登记信息：' + json.dumps(identity, ensure_ascii=False) + '\n' + dialogue
    return dialogue, ocr


@app.post('/api/generate_report')
def generate_report():
    uid = uid_from(body())
    with session_manager.lock(uid):
        state = session_manager.load_user_sessions(uid)
        dialogue, ocr = report_inputs(state, uid)
        if not dialogue:
            raise ValueError('请先完成至少一轮问诊，再生成病历')
        cache = state.setdefault('report_str', {})
        key = dialogue + ocr
        if not cache.get(key):
            cache[key] = complete('REPORT', [{'role': 'system', 'content': REPORT_PROMPT},
                {'role': 'user', 'content': f'患者和你的聊天记录是：\n{dialogue}\n检查报告内容是：\n{ocr}'}])
            session_manager.save_user_sessions(uid, state)
        return jsonify(status='success', report=cache[key])


@app.post('/api/change_medical_record')
def change_medical_record():
    data = body()
    uid, text = uid_from(data), text_from(data)
    with session_manager.lock(uid):
        state = session_manager.load_user_sessions(uid)
        cache = state.setdefault('report_json', {})
        if not cache.get(text):
            result = complete('JSON', [{'role': 'system', 'content': '仅按输入病历提取 JSON，不得补充事实。缺失年龄为 null，其余缺失信息为“不详”。字段定义：' + json.dumps(RECORD_SCHEMA, ensure_ascii=False)}, {'role': 'user', 'content': text}], json_mode=True)
            try:
                parsed = json.loads(result)
                if not isinstance(parsed, dict) or any(key not in parsed for key in RECORD_SCHEMA['required']):
                    raise ValueError()
                age = parsed.get('age')
                parsed['age'] = age if isinstance(age, int) and not isinstance(age, bool) and 0 <= age <= 150 else None
                for key in RECORD_SCHEMA['required']:
                    if key != 'age' and not isinstance(parsed[key], str):
                        parsed[key] = '不详'
            except (ValueError, TypeError):
                raise UpstreamError('模型未返回完整病历结构，请重试') from None
            cache[text] = json.dumps(parsed, ensure_ascii=False)
            session_manager.save_user_sessions(uid, state)
        return jsonify(status='success', content=cache[text], patient=patient_identity(uid))


@app.get('/api/download_report')
def download_report():
    uid = uid_from(request.args)
    state = session_manager.load_user_sessions(uid)
    dialogue, ocr = report_inputs(state, uid)
    report = state.get('report_str', {}).get(dialogue + ocr)
    if not report:
        raise ValueError('请先生成最新病历')
    content = f'Dialogue:\n{dialogue}\n\nOCR Texts:\n{ocr}\n\nResult:\n{report}'
    return send_file(io.BytesIO(content.encode('utf-8-sig')), mimetype='text/plain; charset=utf-8', as_attachment=True, download_name=f'{uid}.txt')


@app.post('/api/upload_audio')
def upload_audio():
    file = request.files.get('audioFile')
    if not file:
        raise ValueError('请上传录音文件 audioFile')
    content = file.read()
    if not content:
        raise ValueError('录音不能为空')
    return jsonify(status='success', content=transcribe(content, Path(file.filename).name))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8503, debug=False)
