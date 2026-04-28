# 新 Mac 恢复步骤

## 1. 准备环境

1. 安装 Homebrew
2. 安装 Python 3.12

```bash
brew install python@3.12
```

## 2. 解压程序包

把 `电商出图工作台-app-package.zip` 解压到任意目录，例如 `~/Applications/电商出图工作台/`。

## 3. 启动应用

方式一：双击 `start-mac.command`

方式二：

```bash
cd ~/Applications/电商出图工作台
./start-local.sh
```

首次启动会自动：

1. 创建 `.venv`
2. 安装 `requirements.txt`
3. 启动 Streamlit
4. 打开浏览器

## 4. 首次配置

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 填写 `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`
3. 或者启动后在 `提供商设置` 页面手动配置

## 5. 停止应用

```bash
./stop-local.sh
```
