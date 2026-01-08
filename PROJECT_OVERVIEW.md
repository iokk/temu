# TEMU 智能出图系统 V6.5 - 项目总览

> **核心作者: 企鹅**  
> **版本: V6.5 Refactored**  
> **发布日期: 2024-01-08**

## 🎯 项目简介

TEMU 智能出图系统是一个基于 Google Gemini AI 的专业电商图片智能生成工具。本版本经过全面重构，具有清晰的架构、完整的文档和 Docker 原生支持。

## ✨ 核心特性

### 1. 智能图片生成
- 🎨 5种专业图片类型（主图、场景、细节、对比、规格）
- 🤖 AI 自动分析产品特征
- 🎭 可调节的风格强度
- 🚫 完善的内容合规检查

### 2. 企业级管理
- 🔐 多层次访问控制
- 📊 使用量统计追踪
- 👨‍💼 管理员面板
- 💾 数据持久化

### 3. 部署友好
- 🐳 完整的 Docker 支持
- 📝 详细的部署文档
- 🚀 一键启动脚本
- 🔧 灵活的配置管理

## 📂 项目结构

```
temu_refactored/
├── 核心代码
│   ├── app.py              # 主应用（Streamlit UI）
│   ├── config.py           # 配置管理中心
│   ├── rules.py            # 规则引擎（合规检查）
│   ├── gemini_client.py    # Gemini AI 客户端
│   ├── templates.py        # 提示词模板系统
│   └── usage_tracker.py    # 使用量追踪
│
├── 部署相关
│   ├── Dockerfile          # Docker 镜像定义
│   ├── docker-compose.yml  # Docker Compose 配置
│   ├── .env.example        # 环境变量示例
│   ├── requirements.txt    # Python 依赖
│   ├── .dockerignore       # Docker 构建忽略
│   ├── .gitignore          # Git 忽略规则
│   └── start.sh            # 快速启动脚本
│
└── 文档
    ├── README.md           # 完整使用文档
    ├── DEPLOY.md           # 部署指南
    ├── ARCHITECTURE.md     # 架构说明
    ├── CHANGELOG.md        # 变更日志
    ├── LICENSE             # 许可协议
    └── PROJECT_OVERVIEW.md # 本文档
```

## 🚀 快速开始

### 三种部署方式

#### 1️⃣ Docker Compose（推荐）
```bash
# 1. 配置环境
cp .env.example .env
nano .env  # 填入 GEMINI_API_KEY

# 2. 一键启动
./start.sh

# 3. 访问系统
# http://localhost:8501
```

#### 2️⃣ Docker
```bash
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/data:/data \
  -e GEMINI_API_KEY=your_key \
  temu-app
```

#### 3️⃣ 本地运行
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key
streamlit run app.py
```

## 📋 核心模块说明

### 1. config.py - 配置管理
- 统一管理所有配置项
- 环境变量优先
- 配置验证和默认值
- 清晰的配置分类

### 2. app.py - 主应用
- Streamlit Web UI
- 用户认证和权限
- 图片上传和处理
- 生成流程控制
- 结果展示和下载

### 3. rules.py - 规则引擎
- 敏感词自动替换
- 禁用内容检查
- 负向提示词构建
- 内容合规保障

### 4. gemini_client.py - AI 客户端
- Gemini API 封装
- 图片分析功能
- 图生图功能
- 错误处理和重试

### 5. templates.py - 模板系统
- 5种图片类型模板
- 变量动态替换
- 可自定义提示词
- 模板版本管理

### 6. usage_tracker.py - 使用追踪
- 配额管理
- 使用量统计
- 数据持久化
- 管理员统计

## 🔧 配置说明

### 必填配置
```bash
GEMINI_API_KEY=your_api_key  # Gemini API 密钥（必填）
```

### 认证配置
```bash
ACCESS_PASSWORD=temu2024      # 访问密码（默认）
ADMIN_PASSWORD=admin888       # 管理员密码（默认）
ADMIN_PATH=/admin             # 管理路径（可选）
```

### 配额配置
```bash
DAILY_LIMIT=50               # 每日免费额度（默认）
```

### 模型配置
```bash
IMAGE_MODEL=gemini-2.0-flash-exp  # 使用的模型（默认）
API_TIMEOUT=120                    # API 超时（秒）
```

## 📚 文档导航

### 使用文档
- **README.md**: 完整的使用指南
  - 功能介绍
  - 快速开始
  - 配置说明
  - 使用指南
  - 故障排查

### 部署文档
- **DEPLOY.md**: 详细的部署指南
  - 5分钟快速部署
  - 常用命令
  - 生产环境配置
  - 监控和维护
  - 安全加固

### 架构文档
- **ARCHITECTURE.md**: 系统架构说明
  - 整体架构图
  - 模块详解
  - 数据流说明
  - 安全架构
  - 扩展性设计

### 其他文档
- **CHANGELOG.md**: 版本变更记录
- **LICENSE**: 许可协议
- **PROJECT_OVERVIEW.md**: 本项目总览

## 🎓 使用流程

```
1. 登录系统
   ├─ 使用团队密码（有配额）
   └─ 使用个人 API Key（无限额）

2. 上传图片
   └─ 支持 PNG/JPG，可多张

3. 填写信息
   ├─ 商品名称（必填）
   ├─ 商品类型（选填）
   └─ 材质（可选，AI 会识别）

4. 选择模板
   ├─ C1: 主卖点图
   ├─ C2: 场景图
   ├─ C3: 细节图
   ├─ C4: 对比图
   └─ C5: 规格图

5. 调整参数
   ├─ 风格强度（0.0-1.0）
   └─ 禁用词预设

6. 开始生成
   └─ AI 自动分析和生成

7. 下载结果
   └─ ZIP 打包下载
```

## 🔐 安全特性

### 访问控制
- 密码认证机制
- 管理员权限分离
- Session 隔离

### 内容安全
- 敏感词自动替换
- 禁用内容检查
- 合规性保障

### 数据安全
- 本地数据存储
- 不上传到云端
- 定期数据备份

## 📊 性能特点

### 优化措施
- 客户端单例模式
- 资源缓存机制
- 批量处理支持
- 异步加载（计划中）

### 资源控制
- API 调用频率限制
- 每日配额管理
- Docker 资源限制
- 请求超时控制

## 🛠️ 维护指南

### 日常维护
```bash
# 查看日志
./start.sh  # 选择 4

# 查看状态
docker-compose ps

# 备份数据
tar -czf backup.tar.gz data/
```

### 更新系统
```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build --no-cache

# 重启服务
docker-compose restart
```

### 问题排查
1. 检查日志: `docker-compose logs -f`
2. 检查配置: `docker-compose config`
3. 检查资源: `docker stats`
4. 查看文档: 参考 DEPLOY.md

## 🎯 最佳实践

### 部署建议
1. **使用 Docker Compose**: 最简单可靠
2. **配置持久化存储**: 避免数据丢失
3. **定期备份数据**: 每周至少一次
4. **监控日志**: 及时发现问题
5. **资源限制**: 防止过载

### 使用建议
1. **上传高质量原图**: 提高生成质量
2. **合理设置风格强度**: 0.2-0.4 为推荐范围
3. **使用禁用词预设**: 确保合规性
4. **批量生成**: 提高效率
5. **保存常用配置**: 减少重复操作

### 安全建议
1. **修改默认密码**: 首次部署必做
2. **定期轮换 API Key**: 提高安全性
3. **启用 HTTPS**: 生产环境必须
4. **限制访问 IP**: 可选但推荐
5. **定期更新系统**: 修复安全漏洞

## 📞 技术支持

### 问题反馈
- 核心作者: 企鹅
- 支持方式: 内部技术支持渠道

### 常见问题
1. **API 调用失败**: 检查 API Key 和网络
2. **生成失败**: 查看日志详细信息
3. **配额不足**: 使用个人 API Key
4. **性能问题**: 检查服务器资源

## 🔄 后续规划

### 短期计划
- [ ] 批量处理优化
- [ ] 结果缓存机制
- [ ] 更多图片类型
- [ ] 移动端适配

### 长期计划
- [ ] 分布式部署支持
- [ ] 任务队列系统
- [ ] 多模型支持
- [ ] API 接口开放

## 📝 版本信息

- **当前版本**: V6.5 Refactored
- **核心作者**: 企鹅
- **发布日期**: 2024-01-08
- **技术栈**: Python 3.11, Streamlit, Gemini AI, Docker

## 🎉 项目亮点

### 代码质量
- ✅ 清晰的模块划分
- ✅ 完整的类型注解
- ✅ 详细的代码注释
- ✅ 规范的命名约定

### 文档完善
- ✅ 完整的使用文档
- ✅ 详细的部署指南
- ✅ 清晰的架构说明
- ✅ 丰富的示例代码

### 部署友好
- ✅ Docker 原生支持
- ✅ 一键启动脚本
- ✅ 环境变量配置
- ✅ 数据持久化

### 企业级特性
- ✅ 多层次权限控制
- ✅ 配额管理系统
- ✅ 使用统计功能
- ✅ 管理员面板

---

**核心作者: 企鹅** | TEMU 智能出图系统 V6.5

*感谢使用本系统，祝使用愉快！* 🎉
