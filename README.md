# DoctorX 智能问诊

Vue 3 / TypeScript / Quasar 前端与 Flask 后端，支持患者管理、问诊对话、检查图片 OCR、病历生成、患者端与医生端展示及下载。当前问诊提示词面向泌尿外科。

## 目录

- `doctor-front-main/src/pages/`：患者管理、问诊与两种病历页面。
- `doctor-front-main/src/adaptor/`：统一 API 请求、患者 UID 解析、问诊及病历适配。
- `doctor-backend-main/flask_app.py`：主 API 服务与模型、OCR、语音服务适配。
- `doctor-backend-main/patient_store.py`：SQLite 患者登记、导入及软删除。
- `doctor-backend-main/session_manager.py`：按 UID 保存会话 JSON、OCR 记录和病历缓存。
- `doctor-backend-main/prompts.py`：问诊、病历提示词及结构化字段定义。
- `doctor-backend-main/tests/test_api.py`：使用独立临时目录和模拟外部服务的接口测试。
- `doctor-backend-main/streamlit*.py`、`search_app.py`：独立实验程序，不是当前前端的后端服务。

## 本地配置

在前后端目录分别复制 `local_settings.example.json` 为 `local_settings.json` 并填写配置。后端优先读取同名环境变量，再读取本地 JSON；空配置使用默认值。

- 问诊、病历生成与结构化默认使用 DeepSeek：填写 `DEEPSEEK_API_KEY`。
- 各环节可以通过 `QA_*`、`REPORT_*`、`JSON_*` 下的 `API_KEY`、`BASE_URL`、`MODEL` 独立覆盖。端点须兼容 OpenAI Chat Completions；结构化端点须支持 JSON 模式。
- OCR 填写 `BAIDU_OCR_APP_ID`、`BAIDU_OCR_API_KEY`、`BAIDU_OCR_SECRET_KEY`。
- 语音转写为可选功能：需要独立的 `AUDIO_API_KEY`、`AUDIO_BASE_URL` 和 `AUDIO_MODEL`（默认 `whisper-1`），端点须支持音频转写。DeepSeek 文本接口不能替代转写接口；未配置时页面提示使用文字输入。
- `DATA_DIR` 可指定本地数据目录，默认后端目录；`FRONTEND_URL` 可覆盖患者链接的站点地址。
- 前端 `PATIENT_MANAGEMENT_PASSWORD` 为页面访问密码；`API_BASE_URL` 默认为 `/api`，可通过环境变量覆盖。

真实配置、SQLite 数据库、会话 JSON、上传图片和导出内容均已忽略，不提交到 Git。前端页面密码会进入浏览器资源，并不是服务端身份认证；当前版本用于本机联调，不应直接公开包含真实患者数据的 API。

## 启动（Windows PowerShell）

在项目根目录执行，后端建议 Python 3.11：

```powershell
cd doctor-backend-main
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-api.txt
.\.venv\Scripts\python.exe -m flask --app flask_app --no-debug run --host 127.0.0.1 --port 8503
```

另开终端，从项目根目录启动前端：

```powershell
cd doctor-front-main
npm ci
npm run dev
```

打开 <http://127.0.0.1:8504/#/patient-management>。Quasar 开发服务器将 `/api` 请求代理至 `http://127.0.0.1:8503`。从患者行进入问诊，再生成或查看病历；页面在跳转时保留患者 UID。旧的 hash 前查询参数链接也兼容，未指定 UID 的访客按浏览器标签页隔离。

生产构建使用 `npm run build`；部署时需为 `/api` 配置反向代理，或在构建前设置 `API_BASE_URL`。

## 接口与数据

- `GET /api/health`：健康状态和语音配置状态。
- `GET/POST /api/patients`、`GET/PUT/DELETE /api/patients/<uid>`：患者列表、新建、查询、修改与软删除。
- `POST /api/import_local_patients`：导入旧浏览器患者列表，保留 UID、重复导入不新增，冲突时整批回滚。
- `POST /api/generate_response`、`GET /api/get_conversation_history`：真实问答与会话历史。
- `GET /api/get_conversation_rounds`、`POST /api/get_multiple_conversation_rounds`：实际保存的问诊轮数。
- `POST /api/upload_check_record`：上传检查图片并识别文字。
- `POST /api/generate_report`、`POST /api/change_medical_record`、`GET /api/download_report`：病历生成、结构化和 UTF-8 文本下载。
- `POST /api/upload_audio`：可选语音转写。

新建患者使用服务端 UUID；非空病历号在未删除患者间唯一。删除患者隐藏登记记录，保留会话和检查资料。会话采用单进程按患者加锁和原子文件替换，模型失败不写入半轮对话。病历缓存随登记信息、对话、OCR 内容变化失效。医生端目前用于查看生成结果，不提供病历编辑保存；未提供的检查指标显示“未提供”。

## 验证

从项目根目录运行：

```powershell
.\doctor-backend-main\.venv\Scripts\python.exe -m unittest discover -s doctor-backend-main/tests -v
cd doctor-front-main
npm run build
```

测试覆盖患者增删改查及持久化、导入冲突回滚、问诊/OCR/病历/下载闭环、缓存失效、模型失败、输入校验和跨域方法。测试不会调用付费模型，也不会读写真实患者目录。

2026-11-24 本机另以明确标注的虚构患者完成浏览器与真实服务联调：创建患者、DeepSeek 问答、百度 OCR、DeepSeek 病历生成与结构化、病历展示和下载。真实语音转写尚未配置和验证。

## 提交与推送

项目已配置 `origin`，无需再次 `git remote add`。先检查改动，再明确选择源码文件提交：

```powershell
git status
git diff
git add <需要提交的源码文件>
git diff --cached --stat
git commit -m "说明本次修改"
git push origin main
```

推送完成后，可用 `git rev-parse HEAD` 和 `git ls-remote origin refs/heads/main` 核对本地与远程提交一致。旧实验程序仍依赖独立配置和较早版本接口，主服务的 `requirements-api.txt` 不覆盖这些实验依赖。
