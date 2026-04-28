# 🍌 TuFlash 电商出图工作台

TuFlash 是一个基于 Streamlit 的电商出图工作台，用于商品素材整理、智能组图、图片翻译和标题生成。

当前仓库已经收敛为单一 Web 应用。产品入口是 `app.py`，本地启动、Mac 双击启动和 Docker/Zeabur 部署都围绕这个入口进行。

支持目标：

1. macOS 本地启动
2. Linux 本地启动
3. Docker / Zeabur 云端部署

## 当前工作流

1. 在本机启动 Streamlit 服务。
2. 进入 `⚙️ 提供商设置` 配置可用提供商。
3. 回到 `🚀 智能组图`、`🎨 快速出图 / 图片翻译` 或 `🏷️ 标题生成` 开始使用。

如果本地 `.env` 中已经填写 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`，并且 `data/providers.json` 还是空的，应用会在首次读取提供商时自动创建一个默认 Gemini 提供商。

## 本地启动

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

默认访问地址：`http://localhost:8501`

建议使用 Python `3.12` 作为本地运行时。

## Docker 启动

仓库包含 `Dockerfile`，可用于容器化部署：

```bash
docker build -t tuflash .
docker run --rm -p 8501:8501 --env-file .env tuflash
```

访问地址：`http://localhost:8501`

容器默认启动命令：

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true
```

## Zeabur 部署

仓库包含 `zbpack.json`，用于 Zeabur 识别 Python/Streamlit 应用。

建议部署方式：

1. 将本仓库推送到 GitHub。
2. 在 Zeabur 新建项目。
3. 选择 GitHub 仓库 `iokk/tuflash`。
4. 设置环境变量，例如 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`。
5. 使用 Zeabur 自动构建并启动服务。

如果使用 Zeabur 本地 CLI 上传部署，构建可能受网络和镜像拉取影响；更推荐 GitHub 仓库部署。

### 更快的启动方式

1. 命令行启动：`./start-local.sh`
2. 停止服务：`./stop-local.sh`
3. Mac 双击启动：直接双击 `start-mac.command`
4. Mac 登录自动启动：`./install-mac-login-launcher.sh`
5. 配置自动更新远端：`./configure-update-remote.sh <repo-url> [branch]`

`start-local.sh` / `start-mac.command` 会自动：

1. 检查或创建 `.venv`
2. 必要时安装依赖
3. 启动心跳守护器
4. 自动检查 Git 更新条件
5. 拉起 Streamlit 并自动打开浏览器

说明：

1. 双击 `start-mac.command` 时，会打开一个 Terminal 窗口并保持服务运行。
2. 心跳守护器会定期检查服务健康，异常退出时自动重启。
3. 启动器会自动识别外层 workspace 仓库；只有当该仓库工作区干净且配置了更新远端时，才会尝试自动更新。
4. 关闭这个 Terminal 窗口，服务也会一起停止。
5. 如果希望登录后自动启动，可执行 `./install-mac-login-launcher.sh`。
6. 如需取消登录自动启动，可执行 `./uninstall-mac-login-launcher.sh`。
7. 如果还没有配置仓库远端，可先执行 `./configure-update-remote.sh <repo-url> [branch]`。

## 程序包迁移

如果你只想备份程序、不备份数据，使用：

```bash
./package-app.sh
```

脚本会生成：

```text
.release/电商出图工作台-app-package.zip
```

这个压缩包只包含程序文件，不包含：

1. `data/`
2. `.venv/`
3. `.runtime/`

换新 Mac 时，直接解压这个压缩包，然后按 [NEW-MAC-SETUP.md](./NEW-MAC-SETUP.md) 操作即可。

建议先编辑 `.env`，至少填入一个可用的 Gemini Key：

```env
GOOGLE_API_KEY=your_gemini_key
```

也可以留空 `.env`，启动后再进入 `提供商设置` 手动添加。

## 页面结构

| 页面 | 当前用途 |
|---|---|
| `🚀 智能组图` | 复杂商品组图工作流，可选同时生成英文 + 目标语言标题，并设置图片文案语言 |
| `🎨 快速出图 / 图片翻译` | 支持 `创意出图` 与 `合规翻译` 两种模式；翻译模式会尽量保留原图结构，只替换目标语言文案 |
| `🏷️ 标题生成` | 单独进行标题生成，支持文字、图片或混合输入，并选择目标语言 |
| `📚 项目中心` | 查看进行中 / 成功 / 失败项目，下载本地 ZIP、打开保存目录、删除历史项目 |
| `⚙️ 提供商设置` | 管理本地个人提供商资料 |

## 目录说明

常用文件如下：

```text
app.py
.env.example
requirements.txt
Dockerfile
zbpack.json
package-app.sh
start-local.sh
start-mac.command
install-mac-login-launcher.sh
uninstall-mac-login-launcher.sh
configure-update-remote.sh
heartbeat_launcher.py
NEW-MAC-SETUP.md
```

说明：

1. `data/` 只保存本地设置和运行时数据，不参与程序包分发。
2. `start-mac.command` 是 Mac 双击启动入口。
3. `package-app.sh` 用来生成可迁移的 Mac 程序压缩包。
4. 桌面客户端代码和部署链路已经从当前主目录移除。

## 当前版本边界

1. 当前产品只保留本地 Streamlit Web 服务。
2. 启动方式以本机直接运行和 Mac 双击启动为主。
3. Docker 和 Zeabur 配置仅服务于 Web 部署，不包含桌面客户端能力。
4. 不再维护 Electron、pywebview、Windows 启动脚本或历史快照目录。

## 安全说明

1. 不要提交 `.env`、`data/`、`.venv/`、`.runtime/`、`.release/` 等本地运行文件。
2. 不要把 API Key、S3 Secret、账号密码等敏感信息写进代码或 README。
3. 云端部署时请通过平台环境变量配置密钥。
4. 如果密钥曾经公开暴露，应立即在对应平台删除并重新生成。
