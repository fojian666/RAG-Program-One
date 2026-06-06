# Agentic Image RAG（多模态图像知识库）

基于 LangGraph 的多模态 Agentic RAG 图像知识库系统。支持批量图片入库、语义向量检索、跨时间对比，全程纯本地运行，无需 Docker。

## 核心能力

- **多模态图像理解**：调用阿里百炼 Qwen-VL 自动生成图片描述
- **语义向量检索**：基于文本嵌入向量进行相似度匹配
- **跨时间对比**：T1/T2 图片分库存储，可分别检索或交叉对比
- **查询流程**：Query Understanding → Query Expansion → Vector Recall → Rerank → Explain → Result
- **批量入库**：支持并发控制与重试，适合几万张图片规模
- **前后端分离**：React 前端 + FastAPI 后端，通过 RESTful API 交互

## 技术栈

### 后端

| 层级 | 方案 |
|------|------|
| 视觉模型 | 阿里百炼 Qwen-VL-Max |
| 文本嵌入 | 阿里百炼 text-embedding-v3 |
| 数据库 | SQLite（本地文件，无需 PostgreSQL） |
| 对象存储 | 本地文件系统（无需 MinIO） |
| 向量存储 | 本地 JSON 索引 + 余弦相似度（无需 Qdrant） |
| 工作流 | LangGraph |
| API 框架 | FastAPI |

### 前端

| 层级 | 方案 |
|------|------|
| 框架 | React 18 + TypeScript |
| 构建工具 | Vite |
| 样式 | Tailwind CSS |
| 路由 | React Router v6 |
| 状态管理 | Zustand |
| 动效 | Canvas 粒子背景、3D 倾斜卡片、数字动画、鼠标光晕、滚动触发动画 |

## 项目结构

```text
.
├── T1_30/                          （原始图片：T1 时间点）
├── T2_30/                          （原始图片：T2 时间点）
├── backend/                        （后端服务）
│   ├── scripts/
│   │   └── batch_ingest_t1_t2.py   （T1/T2 批量入库脚本）
│   ├── src/                        （源码）
│   │   ├── agents/                 （各类 Agent：意图识别、检索、重排等）
│   │   ├── batch_tasks/            （批处理任务：归档、去重、统计等）
│   │   ├── caption/                （图片描述生成：Qwen-VL 封装）
│   │   ├── config/                 （配置管理、日志）
│   │   ├── database/               （数据库模型与仓库）
│   │   ├── embeddings/             （文本嵌入模型封装）
│   │   ├── evaluation/             （评估指标）
│   │   ├── graph/                  （LangGraph 工作流定义）
│   │   ├── ingestion/              （图片入库流水线）
│   │   ├── llm/                    （大模型客户端）
│   │   ├── models/                 （DTO、Schema）
│   │   ├── prompts/                （Agent Prompt 模板）
│   │   ├── retrieval/              （检索模块：向量、元数据、混合检索）
│   │   ├── storage/                （对象存储抽象：本地/MinIO）
│   │   └── vector_store/           （向量存储抽象：本地/Qdrant）
│   ├── tests/                      （单元测试）
│   ├── main.py                     （FastAPI 入口）
│   ├── .env.example                （环境变量配置模板）
│   └── pyproject.toml              （依赖配置）
├── frontend/                       （前端应用）
│   ├── src/
│   │   ├── components/             （UI 组件：粒子背景、3D 卡片、对比滑块等）
│   │   ├── pages/                  （页面：向量库、搜索、对比）
│   │   ├── hooks/                  （自定义 Hooks：滚动触发动画等）
│   │   ├── api.ts                  （API 请求封装）
│   │   ├── store.ts                （全局状态管理）
│   │   └── index.css               （全局样式与动画关键帧）
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── data/                           （运行后自动生成的数据目录）
│   ├── agentic_image_rag.db        （SQLite 数据库）
│   ├── images/
│   │   ├── t1_images/              （T1 图片本地存储副本）
│   │   └── t2_images/              （T2 图片本地存储副本）
│   └── vectors/
│       ├── t1_caption_embeddings.json  （T1 描述向量）
│       └── t2_caption_embeddings.json  （T2 描述向量）
└── start.sh                        （一键启动前后端脚本）
```

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -e .
```

### 2. 配置环境变量

复制 `backend/.env.example` 为 `backend/.env`，填入你的阿里百炼 API Key：

```ini
# 阿里百炼（一个 Key 同时用于 LLM + 视觉 + 嵌入）
LLM_API_KEY=sk-你的密钥
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo

VISION_API_KEY=sk-你的密钥
VISION_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
VISION_MODEL=qwen-vl-max

EMBEDDING_API_KEY=sk-你的密钥
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_MODEL=text-embedding-v3

# 纯本地后端（无需 Docker）
DB_BACKEND=sqlite
DATABASE_URL=sqlite+aiosqlite:///./data/agentic_image_rag.db
VECTOR_BACKEND=local
STORAGE_BACKEND=local

# 批量入库并发控制
INGESTION_CONCURRENCY=8
INGESTION_MAX_RETRIES=3
```

### 3. 批量入库 T1/T2 图片

```bash
cd backend
python scripts/batch_ingest_t1_t2.py
```

执行后：
- 图片存入 `data/images/t1_images/` 和 `t2_images/`
- 描述向量存入 `data/vectors/t1_caption_embeddings.json` 和 `t2_caption_embeddings.json`
- 元数据存入 SQLite `data/agentic_image_rag.db`

### 4. 启动服务

#### 方式一：一键启动（推荐）

在项目根目录执行：

```bash
./start.sh
```

该脚本会自动启动后端（`localhost:8000`）和前端（`localhost:5173`），并支持 `Ctrl+C` 一键关闭并清理临时文件。

#### 方式二：手动启动

```bash
# 终端 1：启动后端
cd backend
python main.py

# 终端 2：启动前端
cd frontend
npm install
npm run dev
```

### 5. 前端功能

| 页面 | 功能 |
|------|------|
| **向量库** (`/vectors`) | 查看所有入库图片，支持按 T1/T2 筛选，图片卡片带 3D 倾斜效果 |
| **搜索** (`/search`) | 文本查询 + 图片参考检索，支持相似度阈值调节和来源筛选 |
| **对比** (`/compare`) | 选择 T1/T2 图片对进行并排对比，显示相似度分数和视觉差异滑块 |

### 6. 查询示例（API）

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -F "q=找出有农田的卫星图"
```

## 检索能力验证

已实测验证：

| 场景 | 相似度 |
|------|--------|
| 同集合检索（T1 搜 T1） | 1.0000（自身）/ 0.85+（相似图） |
| 跨集合检索（T1 搜 T2） | 0.85 ~ 0.91（语义相关图） |

说明语义向量检索有效，能够识别语义相近的地理图片。

## 注意事项

- `.env` 中的 API Key 请妥善保管，不要提交到仓库
- `data/` 目录包含生成的数据库和向量文件，已加入 `.gitignore`
- 如需处理几万张以上图片，建议开启 `SIGLIP_MODEL_PATH` 使用本地 SigLIP 模型，以节省 API 调用费用
