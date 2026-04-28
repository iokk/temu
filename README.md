# 🍌 TuFlash 电商出图工作台

TuFlash 是一个基于 Streamlit 的电商出图工作台，用于商品素材整理、智能组图、图片翻译和标题生成。

当前仓库包含两部分：

1. 根目录：用于 Zeabur / Docker 部署的入口。
2. `image/`：最新 Streamlit 客户端源码和本地启动脚本。

Zeabur 默认会读取根目录 `Dockerfile`。这个 Dockerfile 会把 `image/` 目录中的最新客户端复制进容器并启动。

## 主要功能

| 功能 | 说明 |
|---|---|
| 智能组图 | 复杂商品组图工作流 |
| 快速出图 / 图片翻译 | 支持创意出图和合规翻译 |
| 标题生成 | 支持文字、图片或混合输入生成标题 |
| 模板库 | 管理常用出图模板 |
| 提供商设置 | 配置 Gemini / Google 等出图提供商 |
| 项目中心 | 查看历史项目、下载结果和管理任务 |

## 本地启动

进入 `image/` 目录后启动：

```bash
cd image
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

默认访问：`http://localhost:8501`

也可以在 macOS 上双击：

```text
image/start-mac.command
```

## Docker 启动

在仓库根目录执行：

```bash
docker build -t tuflash .
docker run --rm -p 8501:8501 --env-file image/.env tuflash
```

访问：`http://localhost:8501`

## Zeabur 部署

推荐方式：

1. 连接 GitHub 仓库 `iokk/tuflash`。
2. 服务使用根目录构建即可，无需手动设置 Root Directory。
3. Zeabur 会读取根目录 `Dockerfile`，实际运行 `image/app.py`。
4. 在 Zeabur 环境变量中配置 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`。
5. 生成公网域名后访问服务。

## 📁 文件说明

```
.
├── Dockerfile                  # Zeabur / Docker 部署入口
├── README.md                   # 仓库说明
└── image/
    ├── app.py                  # Streamlit 主应用
    ├── requirements.txt        # Python 依赖
    ├── .env.example            # 环境变量示例
    ├── start-local.sh          # 本地启动脚本
    ├── start-mac.command       # macOS 双击启动入口
    └── README.md               # 客户端详细说明
```

## ⚙️ 配置项

| 变量 | 默认值 | 说明 |
|---|---|---|
| `GOOGLE_API_KEY` | - | Google / Gemini API Key |
| `GEMINI_API_KEY` | - | Gemini API Key |
| `PORT` | 8501 | Web 服务端口，Zeabur 会自动注入 |
| `ECOMMERCE_WORKBENCH_DATA_DIR` | `/app/data` | 云端运行数据目录 |
| `FILE_STORAGE_PATH` | `/app/data/files` | 生成文件保存目录 |

## 安全说明

1. 不要提交 `.env`、`data/`、`.venv/`、`.runtime/`、`.release/`。
2. 不要把 API Key、S3 Secret、账号密码写进代码。
3. 云端部署时通过 Zeabur 环境变量配置密钥。
4. 如果密钥已经公开暴露，应立即在对应平台删除并重新生成。

---

核心作者：企鹅 & 小明  
商业订阅：企鹅 & Jerry
