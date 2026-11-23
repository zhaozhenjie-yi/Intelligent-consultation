# DoctorX 智能问诊

Vue 3 / TypeScript / Quasar 前端与 Flask 后端，包含问诊对话、检查报告 OCR、病历生成和结构化展示。当前提示词面向泌尿外科。

## 目录

- `doctor-front-main/`：前端页面、路由、接口适配层和病历模型。
- `doctor-backend-main/flask_app.py`：主 API 服务。
- `doctor-backend-main/session_manager.py`：本地 JSON 会话存储。
- `doctor-backend-main/streamlit*.py`：独立实验页面。
- `doctor-backend-main/search_app.py`：独立论文检索实验。

## 本地配置

在前后端目录分别复制 `local_settings.example.json` 为 `local_settings.json` 并填写配置。真实配置已加入 `.gitignore`，不要提交。后端优先读取同名环境变量，再读取本地 JSON。

主后端使用 `BAIDU_OCR_APP_ID`、`BAIDU_OCR_API_KEY`、`BAIDU_OCR_SECRET_KEY`、`FLASK_SECRET_KEY`、`DEEPSEEK_API_KEY`、`OPENAI_API_KEY`。其他 `MODEL_API_KEY_*` 为实验脚本或语音工具配置；按对应代码中的引用填写。

前端 `PATIENT_MANAGEMENT_PASSWORD` 是页面访问检查，最终会进入浏览器资源，不能当作服务端身份认证。修改它后需要重启前端。

## 启动（Windows PowerShell）

后端建议 Python 3.11：

```powershell
cd doctor-backend-main
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-api.txt
.\.venv\Scripts\python.exe -m flask --app flask_app --no-debug run --host 127.0.0.1 --port 8503
```

另开终端启动前端：

```powershell
cd doctor-front-main
npm ci
npm run dev
```

打开 http://127.0.0.1:8504/ 。前端当前直接请求本机 `127.0.0.1:8503`，部署到其他环境时需调整 API 地址。

## 当前限制

- 患者管理前端引用的 `/api/patients`、`/api/import_local_patients` 尚未在当前后端实现。
- 医生端大病历和部分语音适配器仍为演示功能；样例已换为虚构占位内容。
- 问诊规则主要通过提示词控制。模型与 OCR 功能需要可用的服务端点和密钥。
- 病历文本、会话 JSON、上传图片与导出文件保存在本地，不属于仓库源码。
- 旧实验脚本使用较早的依赖接口，需单独检查；`requirements-api.txt` 仅覆盖 Flask 主服务。

## 后续推送

在项目根目录执行，提交前检查差异，勿加入真实配置和患者数据：

```powershell
git status
git diff
git add <需要提交的文件>
git diff --cached --stat
git commit -m "说明本次修改"
git push origin main
```
