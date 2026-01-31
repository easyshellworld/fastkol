# fastKOL - Web3 自动化内容生成与 YouTube 分发系统

## 🌟 项目简介

fastKOL 是一个基于 AI 的 Web3 自动化内容生成与视频分发系统，专注于：

- 🚀 快速捕捉市场热点  
- 🎬 自动生成专业视频内容  
- 📤 一键发布至 YouTube 平台  

帮助 Web3 创作者实现内容规模化生产。

---

## 🎯 核心价值

- ⚡ 极速响应：分钟级完成热点 → 视频发布  
- 🤖 全流程自动化：无需人工剪辑  
- 🎬 专业级视频内容生成  
- 💰 低成本 AI 集成方案  

---

## ✨ 主要特性

✅ 实时 Polymarket 热点监控  
✅ AI 自动生成视频脚本  
✅ MCP 驱动视频生成引擎（HeyGen / AI 视频流）  
✅ 一键上传发布至 YouTube  
✅ 可视化任务监控  
✅ 灵活参数与人工审核支持  

---

## 🏗️ 系统架构

Frontend (React + Vite)
↓
SpoonOS Agent 编排层
↓
MCP 服务集群
↓
外部 AI & Web3 API


---

## 🧰 技术栈

### 前端
- React + TypeScript + Vite  
- TailwindCSS  

### 后端
- Python 3.11+  
- FastAPI + SpoonOS Agent  

### AI & 数据
- LLM 内容生成  
- 视频生成 MCP 服务  
- Polymarket API  

### 部署
- Docker + Docker Compose  

---

# 🚀 部署与安装

项目支持：

✔ 本地开发运行  
✔ Docker 一键部署（推荐）

---

## 📍 本地开发模式

### 后端启动

```bash

pip install -r requirements.txt&#41;)

uvicorn src.server:app --reload --host 0.0.0.0 --port 8000&#41;)


### 前端启动

```bash
cd frontend
npm install
npm run dev


    访问：

Frontend → http://localhost:5173

Backend API → http://localhost:8000


🐳 Docker 一键部署（推荐）
1️⃣ 配置环境变量
cp .env.example .env


填写你的 API Key。

2️⃣ 启动服务
docker compose up -d --build

3️⃣ 访问服务

Frontend: http://localhost:5173

Backend API: http://localhost:8000

4️⃣ 停止服务
docker compose down

🔑 环境变量说明
服务	用途
OpenAI / Gemini / Claude	内容脚本生成
Polymarket API	热点数据获取
视频生成 MCP	视频自动制作
YouTube API	自动发布视频
📋 自动化工作流
启动
 ↓
获取热点
 ↓
生成脚本
 ↓
视频生成
 ↓
审核（可选）
 ↓
发布到 YouTube

📁 项目结构
fastkol/
├── src/                  # 后端服务
├── frontend/             # 前端界面
├── docker-compose.yml   # 一键部署
├── Dockerfile.backend
├── frontend/Dockerfile
├── .dockerignore
├── .env.example
└── readme.md

⚙ MCP 服务集成

Polymarket MCP — 市场数据

Video MCP — 视频生成

YouTube MCP — 自动上传

❓ 常见问题

Q: MCP 服务无法连接？
检查环境变量与 MCP 进程是否启动。

Q: 视频生成失败？
确认视频生成服务 API Key 配额。

Q: 上传失败？
确认 YouTube API 权限。

🚧 开发规划

多语言视频生成

内容效果分析

发布时间智能调度

更多视频生成服务接入

📄 License

MIT License

🤝 贡献

欢迎 PR 与 Issue！