# TEMU 智能出图系统 - 快速参考

> 核心作者: 企鹅 | 版本: V6.5

## 🚀 一键部署

```bash
# 1. 解压项目
tar -xzf temu_v6.5_refactored.tar.gz
cd temu_refactored

# 2. 配置环境
cp .env.example .env
nano .env  # 填入 GEMINI_API_KEY

# 3. 启动服务
./start.sh  # 选择 1

# 4. 访问系统
# http://localhost:8501
```

## 🔑 默认密码

| 类型 | 密码 | 说明 |
|------|------|------|
| 访问密码 | `temu2024` | 所有用户 |
| 管理员密码 | `admin888` | 管理员 |

## 📁 核心文件

| 文件 | 说明 |
|------|------|
| `app.py` | 主应用 |
| `config.py` | 配置管理 |
| `rules.py` | 规则引擎 |
| `gemini_client.py` | AI 客户端 |
| `templates.py` | 模板系统 |
| `usage_tracker.py` | 使用追踪 |

## 🎨 图片类型

| 代码 | 名称 | 说明 |
|------|------|------|
| C1 | 主卖点图 | 突出产品核心优势 |
| C2 | 场景图 | 展示使用场景 |
| C3 | 细节图 | 展现工艺细节 |
| C4 | 对比图 | 对比产品优势 |
| C5 | 规格图 | 参数信息展示 |

## ⚙️ 环境变量

```bash
# 必填
GEMINI_API_KEY=your_key

# 可选
ACCESS_PASSWORD=temu2024
ADMIN_PASSWORD=admin888
DAILY_LIMIT=50
IMAGE_MODEL=gemini-2.0-flash-exp
```

## 🐳 Docker 命令

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启
docker-compose restart

# 日志
docker-compose logs -f

# 状态
docker-compose ps
```

## 🔧 常用操作

### 修改配额
```bash
nano .env
# DAILY_LIMIT=100
docker-compose restart
```

### 修改密码
```bash
nano .env
# ACCESS_PASSWORD=new_password
docker-compose restart
```

### 备份数据
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

### 查看统计
```
登录 → 使用管理员密码 → 侧边栏 → 查看使用统计
```

## 📖 文档索引

| 文档 | 内容 |
|------|------|
| `README.md` | 完整使用文档 |
| `DEPLOY.md` | 部署详细指南 |
| `ARCHITECTURE.md` | 系统架构说明 |
| `CHANGELOG.md` | 版本变更记录 |
| `PROJECT_OVERVIEW.md` | 项目总览 |

## 🆘 快速故障排查

### 问题: 无法启动
```bash
# 检查配置
docker-compose config

# 查看日志
docker-compose logs
```

### 问题: API 失败
```bash
# 检查 API Key
echo $GEMINI_API_KEY

# 测试网络
curl https://generativelanguage.googleapis.com
```

### 问题: 端口占用
```bash
# 修改端口
nano docker-compose.yml
# ports: - "8502:8501"
```

## 📊 性能建议

| 项目 | 推荐值 |
|------|--------|
| 风格强度 | 0.2 - 0.4 |
| 每日配额 | 50 - 100 |
| API 超时 | 120 秒 |
| 单次图片 | 1 - 5 张 |

## 🔐 安全检查清单

- [ ] 已修改默认访问密码
- [ ] 已修改默认管理员密码
- [ ] 已配置 HTTPS（生产环境）
- [ ] 已设置防火墙规则
- [ ] 已启用日志记录
- [ ] 已配置定期备份

## 🎯 使用技巧

1. **上传高质量原图**: 分辨率 > 1024px
2. **合理风格强度**: 新手使用 0.3
3. **使用预设模板**: 快速生成
4. **批量处理**: 一次上传多张
5. **保存常用设置**: 减少操作

## 📞 获取帮助

```
核心作者: 企鹅
版本: V6.5
更新: 2024-01-08
```

---

**快速参考卡片** | 建议打印或保存
