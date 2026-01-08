# TEMU 智能出图系统 V6.5

> 基于 Gemini AI 的电商图片智能生成系统  
> **核心作者: 企鹅**

## 📖 简介

TEMU 智能出图系统是一个专业的电商图片智能生成工具，基于 Google Gemini AI，可以将普通商品图片智能优化为专业的电商展示图片。

### 核心功能

- 🎨 **5种专业图片类型**
  - C1 主卖点图：突出产品核心优势
  - C2 场景图：展示产品使用场景
  - C3 细节图：展现产品工艺细节
  - C4 对比图：对比展示产品优势
  - C5 规格图：专业参数展示

- 🤖 **AI 智能分析**
  - 自动识别产品特征
  - 提取关键卖点
  - 推荐最佳场景
  - 材质智能识别

- 🔒 **企业级管理**
  - 密码访问控制
  - 每日配额管理
  - 使用统计追踪
  - 管理员面板

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

1. **克隆仓库**
```bash
git clone <repository-url>
cd temu_refactored
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 GEMINI_API_KEY
nano .env
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问系统**
```
打开浏览器访问: http://localhost:8501
默认密码: temu2024
管理员密码: admin888
```

### 方式二：Docker

```bash
# 构建镜像
docker build -t temu-app .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/data:/data \
  -e GEMINI_API_KEY=your_api_key_here \
  -e ACCESS_PASSWORD=temu2024 \
  -e ADMIN_PASSWORD=admin888 \
  --name temu-app \
  temu-app
```

### 方式三：本地运行

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
export GEMINI_API_KEY=your_api_key_here
export ACCESS_PASSWORD=temu2024
export ADMIN_PASSWORD=admin888
```

3. **启动应用**
```bash
streamlit run app.py
```

## 📝 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `GEMINI_API_KEY` | Gemini API 密钥 | - | ✅ |
| `ACCESS_PASSWORD` | 访问密码 | temu2024 | ✅ |
| `ADMIN_PASSWORD` | 管理员密码 | admin888 | ✅ |
| `ADMIN_PATH` | 管理员路径 | /admin | ❌ |
| `DAILY_LIMIT` | 每日免费额度 | 50 | ❌ |
| `IMAGE_MODEL` | Gemini 模型 | gemini-2.0-flash-exp | ❌ |
| `API_TIMEOUT` | API 超时（秒） | 120 | ❌ |
| `DATA_DIR` | 数据目录 | /data | ❌ |
| `DEBUG` | 调试模式 | false | ❌ |

### 获取 Gemini API Key

1. 访问 [Google AI Studio](https://aistudio.google.com/apikey)
2. 登录 Google 账号
3. 创建或复制 API Key
4. 将 API Key 填入环境变量

## 📋 使用指南

### 1. 登录系统

- 使用团队密码登录（共享配额）
- 或使用个人 API Key 登录（无限配额）

### 2. 上传图片

- 支持 PNG、JPG 格式
- 建议上传高质量原图
- 可一次上传多张

### 3. 填写商品信息

- 商品名称（必填）
- 商品类型（选填）
- 材质（选填，AI 会自动识别）
- 输出尺寸（多种预设）

### 4. 选择图片类型

- 可多选
- 每种类型可设置生成数量
- 自动显示所需总额度

### 5. 调整参数

- **风格强度**：控制 AI 创意程度
  - 0.0-0.2：高度保留原图
  - 0.2-0.4：推荐范围
  - 0.4-0.6：平衡创意
  - 0.6-1.0：大幅创意

- **禁用词预设**：
  - 标准：适合大多数场景
  - 严格：更多限制
  - 宽松：基础限制
  - 自定义：自由选择

### 6. 生成与下载

- 点击"开始生成"
- 等待 AI 处理
- 预览生成结果
- 打包下载 ZIP

## 🔧 高级功能

### 自定义提示词

在"高级：自定义提示词"中可以：
- 修改默认提示词模板
- 使用变量动态替换
- 针对特定需求优化

支持的变量：
- `{product_name}` - 商品名称
- `{product_type}` - 商品类型
- `{material}` - 材质
- `{selling_points}` - 卖点列表
- `{scene}` - 使用场景
- `{title}` - 标题文字

### 管理员功能

使用管理员密码登录后可以：
- 查看使用统计
- 查看活跃用户数
- 查看用户明细
- 清空今日数据

## 🐳 Docker 部署最佳实践

### 持久化数据

```yaml
volumes:
  - ./data:/data  # 使用量数据
```

### 反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name temu.example.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 资源限制

```yaml
services:
  temu-app:
    # ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 📊 系统架构

```
temu_refactored/
├── app.py              # 主应用（Streamlit UI）
├── config.py           # 配置管理
├── rules.py            # 规则引擎（敏感词、禁用词）
├── gemini_client.py    # Gemini AI 客户端
├── templates.py        # 提示词模板系统
├── usage_tracker.py    # 使用量追踪
├── requirements.txt    # Python 依赖
├── Dockerfile          # Docker 镜像
├── docker-compose.yml  # Docker Compose 配置
├── .env.example        # 环境变量示例
└── README.md          # 本文档
```

## 🛡️ 安全建议

1. **修改默认密码**
   ```bash
   ACCESS_PASSWORD=your_strong_password
   ADMIN_PASSWORD=your_admin_password
   ```

2. **保护 API Key**
   - 不要将 `.env` 文件提交到代码仓库
   - 使用环境变量或密钥管理服务
   - 定期轮换 API Key

3. **网络安全**
   - 使用 HTTPS（配置 SSL 证书）
   - 配置防火墙规则
   - 限制访问 IP（可选）

4. **数据备份**
   ```bash
   # 备份使用数据
   docker cp temu-app:/data ./backup/
   ```

## 📈 性能优化

### 1. 调整并发限制

在 `streamlit` 配置中：
```toml
[server]
maxUploadSize = 200
maxMessageSize = 200
```

### 2. 缓存优化

使用 `@st.cache_resource` 缓存客户端实例

### 3. 批量处理

一次上传多张图片，减少 API 调用次数

## 🔍 故障排查

### 问题：无法连接到服务

```bash
# 检查容器状态
docker ps

# 查看日志
docker logs temu-app

# 检查端口占用
netstat -tunlp | grep 8501
```

### 问题：API 调用失败

1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看 API 配额是否用尽
4. 检查模型名称是否正确

### 问题：生成图片质量不佳

1. 提高原图质量
2. 调整风格强度
3. 自定义提示词
4. 添加更多禁用词

## 📞 支持与反馈

如有问题或建议，请联系：

- **核心作者**: 企鹅
- **版本**: V6.5
- **更新日期**: 2024

## 📄 许可证

本项目仅供内部使用，未经授权不得外传或商用。

---

**核心作者: 企鹅** | TEMU 智能出图系统 V6.5
