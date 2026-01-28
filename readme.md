# fastKOL - Web3 自动化内容生成与分发系统 

[![Version](https://img.shields.io/badge/version-1.0-blue)](https://github.com/yourusername/fastKOL)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node.js-18%2B-green)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-compose-orange)](https://www.docker.com/)
[![Web3](https://img.shields.io/badge/Web3-Enabled-purple)](https://web3js.org/)
[![AI](https://img.shields.io/badge/AI-Powered-yellow)](https://openai.com/)
[![Automation](https://img.shields.io/badge/100%25-Automated-red)]()

## 🌟 项目简介

fastKOL 是一个基于 AI 的 Web3 自动化内容生成与分发系统，旨在帮助 Web3 从业者快速捕捉市场热点，自动生成专业视频内容，并分发到社交媒体平台。

### 🎯 核心价值
- **快速响应**：从热点捕捉到内容发布仅需几分钟
- **完全自动化**：减少人工干预，提高效率
- **专业内容**：生成高质量的 Web3 专业内容
- **成本优化**：整合多个免费/低成本 AI 服务

## ✨ 主要特性

✅ **实时市场监控** - 自动获取 Polymarket 预测市场热点  
✅ **智能脚本生成** - AI 分析数据并生成吸引人的视频脚本  
✅ **AI 视频制作** - 使用 Google Veo 2 等模型自动生成短视频  
✅ **多平台分发** - 一键发布到 Twitter/X 等社交平台  
✅ **可视化监控** - 实时查看工作流执行状态  
✅ **灵活配置** - 支持人工审核、参数调整等自定义选项  

## 🏗️ 系统架构

```
前端界面 (React + Vite) → SpoonOS Agent 编排层 → MCP 服务层 → 外部 API
```

### 核心技术栈
- **前端**: React 18 + TypeScript + Vite 5 + TailwindCSS
- **后端**: Python 3.11+ + SpoonOS Agent 框架
- **AI 服务**: GPT-4/Claude/Gemini + Google Veo 2
- **数据源**: Polymarket API + Twitter API
- **部署**: Docker + Docker Compose

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- 至少 8GB RAM

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/fastKOL.git
cd fastKOL

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的 API 密钥

# 3. 启动服务
docker-compose up -d --build

# 4. 访问应用
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000
```

### 配置 API 密钥
您需要配置以下 API 密钥：
- **OpenAI/Anthropic/Gemini** - 用于内容生成
- **Polymarket API** - 用于市场数据
- **Google API** - 用于视频生成
- **Twitter API** - 用于内容发布

## 📋 工作流程

1. **热点采集** - 监控 Polymarket 市场趋势
2. **内容策划** - AI 生成专业视频脚本
3. **视频制作** - 自动生成短视频内容
4. **内容审核** - 可选的人工审核环节
5. **社交分发** - 发布到 Twitter/X 平台

```
启动 → 获取热点 → 生成脚本 → 制作视频 → 审核? → 发布 → 完成
```

## 📁 项目结构

```
fastKOL/
├── backend/           # Python 后端服务
├── frontend/          # React 前端界面
├── docker-compose.yml # 容器编排
├── .env.example       # 环境变量模板
└── README.md          # 本文档
```

## 🔧 配置详解

### MCP 服务集成
系统通过 MCP 协议集成多个服务：
- **Polymarket MCP** - 市场数据获取
- **Google Veo 2 MCP** - AI 视频生成
- **Twitter MCP** - 社交媒体发布
- **InVideo AI MCP** - 免费视频生成备选方案

## 📊 监控与维护

- 详细的执行日志记录
- Prometheus 指标收集
- 自动错误重试机制
- 资源使用监控
- 告警系统配置

## ❓ 常见问题

**Q: MCP Server 连接失败怎么办？**  
A: 检查 npm 包安装和环境变量配置，使用 `npx @modelcontextprotocol/inspector` 调试。

**Q: 视频生成失败？**  
A: 检查 Google Cloud 配额和账单设置，或切换到 InVideo AI 免费方案。

**Q: Twitter 发布失败？**  
A: 确认 API 权限和速率限制，考虑升级套餐或降低频率。

## 🚧 开发计划

### 近期规划
- [ ] 支持更多视频生成服务
- [ ] 多语言内容生成
- [ ] 智能发布时间优化
- [ ] 内容 A/B 测试功能

### 长期愿景
打造 Web3 领域最智能的内容自动化平台，建立完整的 AI KOL 生态系统。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！请参考项目中的贡献指南。

## 📞 支持与联系

如有问题或建议，请：
- 提交 GitHub Issue
- 查看项目文档
- 联系维护团队

---

**fastKOL - 让 Web3 内容创作更简单！** 🚀

*自动化您的 Web3 内容策略，专注于更有价值的工作。*