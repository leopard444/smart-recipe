# AI 智能食谱生成 (Smart Recipe AI)

全栈 AI 食谱生成平台 — Vue3 前端 + Flask 后端 + MySQL + Redis + Docker 部署

## 功能特性

- 🤖 **AI 智能生成**：接入 GPT-4o/DeepSeek/通义千问等多个大模型，根据食材、口味、饮食需求自动生成标准化食谱
- 📋 **标准化食谱**：每份食谱包含食材清单、详细步骤、营养数据、烹饪小贴士
- ⭐ **收藏系统**：注册登录后可收藏喜欢的食谱，支持分类筛选
- 💬 **美食社区**：发帖分享烹饪成果，评论点赞互动
- 🔧 **管理后台**：食谱审核、分类管理、用户管理、数据仪表盘
- ⚡ **Redis 缓存**：AI 生成结果缓存 24 小时，避免重复 API 调用
- 🐳 **Docker 一键部署**：4 个容器（Nginx + Flask + MySQL + Redis）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Vite + TypeScript + Element Plus + Pinia + Axios |
| 后端 | Flask + SQLAlchemy + Marshmallow + JWT + Gunicorn |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| AI | OpenAI API / DeepSeek / 通义千问 |
| 部署 | Docker Compose + Nginx |

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.12+
- Docker & Docker Compose（生产部署）

### 开发环境

**1. 前端**
```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

**2. 后端**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # 编辑 .env 配置数据库和API密钥
flask run                 # http://localhost:5000
```

**3. 数据库**
```bash
# 使用 Docker 启动 MySQL + Redis
docker run -d --name mysql-recipe -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=smart_recipe -p 3306:3306 mysql:8.0
docker run -d --name redis-recipe -p 6379:6379 redis:7-alpine

# 初始化数据
python backend/scripts/seed_data.py
```

### Docker 一键部署

```bash
# 1. 构建前端
cd frontend && npm install && npm run build

# 2. 配置环境变量
cp backend/.env.example .env
# 编辑 .env：设置 LLM_API_KEY、数据库密码等

# 3. 启动所有服务
docker compose up -d

# 4. 初始化数据库（首次运行）
docker exec smart-recipe-flask python scripts/seed_data.py

# 访问 http://localhost
```

## 项目结构

```
smart-recipe/
├── frontend/              # Vue3 前端
│   ├── src/
│   │   ├── api/           # API 接口层
│   │   ├── components/    # 通用组件
│   │   ├── composables/   # 状态管理
│   │   ├── layouts/       # 页面布局
│   │   ├── router/        # 路由配置
│   │   ├── types/         # TypeScript 类型
│   │   ├── views/         # 页面组件
│   │   └── assets/        # 样式资源
│   └── package.json
├── backend/               # Flask 后端
│   ├── app/
│   │   ├── api/v1/        # REST API 端点
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── services/      # 业务逻辑层
│   │   └── utils/         # 工具函数
│   ├── scripts/           # 备份/种子脚本
│   └── Dockerfile
├── nginx/                 # Nginx 配置
├── scripts/               # 部署脚本
├── docker-compose.yml     # Docker 编排
└── README.md
```

## API 接口

详见 [backend/app/api/v1/](backend/app/api/v1/)

| 模块 | 路径前缀 |
|------|----------|
| 认证 | `/api/v1/auth` |
| 食谱 | `/api/v1/recipes` |
| 社区 | `/api/v1/community` |
| 上传 | `/api/v1/upload` |
| 管理后台 | `/api/v1/admin` |

## 备份

每日凌晨 3:00 自动备份数据库和上传文件，保留 30 天。
```bash
# 手动备份
bash scripts/backup.sh
```

## 管理员账号

默认管理员：`admin@recipe.com` / `admin123`（首次部署后请立即修改）

## License

MIT
