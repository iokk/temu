# 🎨 TEMU 智能出图系统 V6.6

> 基于 Gemini AI 的电商图片智能生成系统  
> **核心作者: 企鹅**

## ✨ 功能特性

- 🖼️ **5种专业图片** - 主图、场景、细节、对比、规格
- 🤖 **AI 智能分析** - 自动识别产品特征和卖点
- 🎨 **可调节风格** - 灵活控制 AI 创意程度
- 📊 **配额管理** - 支持团队共享和个人 API Key
- 🔒 **内容合规** - 自动过滤敏感内容

## 🚀 Zeabur 一键部署

### 步骤 1: Fork 或上传代码

将代码上传到 GitHub 仓库

### 步骤 2: 在 Zeabur 部署

1. 登录 [Zeabur](https://zeabur.com)
2. 创建新项目
3. 选择 "Deploy from GitHub"
4. 选择你的仓库

### 步骤 3: 配置环境变量

在 Zeabur 控制台添加环境变量：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `GEMINI_API_KEY` | ✅ | [获取 API Key](https://aistudio.google.com/apikey) |
| `ACCESS_PASSWORD` | ❌ | 访问密码，默认 `temu2024` |
| `ADMIN_PASSWORD` | ❌ | 管理员密码，默认 `admin888` |
| `DAILY_LIMIT` | ❌ | 每日额度，默认 `50` |

### 步骤 4: 绑定域名

在 Zeabur 控制台绑定域名即可访问

## 📁 项目结构

```
├── app.py              # 主应用
├── config.py           # 配置管理
├── gemini_client.py    # AI 客户端
├── rules.py            # 规则引擎
├── templates.py        # 提示词模板
├── usage_tracker.py    # 使用量追踪
├── requirements.txt    # 依赖清单
├── zbpack.json         # Zeabur 配置
└── .streamlit/
    └── config.toml     # Streamlit 配置
```

## 🔧 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GEMINI_API_KEY=your_key

# 启动
streamlit run app.py
```

## 📝 使用说明

1. **登录** - 输入访问密码
2. **上传图片** - 支持 PNG/JPG/WebP
3. **填写信息** - 商品名称、类型、材质
4. **选择类型** - 主图/场景/细节/对比/规格
5. **调整参数** - 风格强度、禁用词
6. **生成下载** - AI 生成后打包下载

## 🎯 图片类型说明

| 类型 | 用途 |
|------|------|
| 🌟 主卖点图 | 突出产品核心优势 |
| 🏡 场景图 | 展示产品使用场景 |
| 🔍 细节图 | 展现产品工艺细节 |
| ⚖️ 对比图 | 对比展示产品优势 |
| 📐 规格图 | 产品参数信息展示 |

## ❓ 常见问题

### Q: 部署失败？
A: 检查 `GEMINI_API_KEY` 是否正确设置

### Q: 生成失败？
A: 检查 API Key 配额，或稍后重试

### Q: 图片质量不佳？
A: 上传更高清的原图，调整风格强度到 0.2-0.4

---

**核心作者: 企鹅** | TEMU 智能出图系统 V6.6
