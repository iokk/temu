# TEMU 智能出图系统 - 快速部署指南

> 核心作者: 企鹅  
> 版本: V6.5

## 🎯 5分钟快速部署

### 前置要求

- Docker 和 Docker Compose
- Gemini API Key ([获取地址](https://aistudio.google.com/apikey))

### 部署步骤

#### 1️⃣ 下载代码

```bash
# 如果有 Git
git clone <repository-url>
cd temu_refactored

# 或直接下载 ZIP 并解压
```

#### 2️⃣ 配置环境

```bash
# 使用快速启动脚本（推荐）
./start.sh

# 或手动配置
cp .env.example .env
nano .env  # 填入 GEMINI_API_KEY
```

#### 3️⃣ 启动服务

```bash
# 使用脚本启动
./start.sh
# 选择 1) 启动服务

# 或直接启动
docker-compose up -d
```

#### 4️⃣ 访问系统

```
浏览器打开: http://localhost:8501
默认密码: temu2024
管理员密码: admin888
```

## 🔧 常用命令

### 使用启动脚本

```bash
./start.sh
# 然后选择对应操作：
# 1) 启动服务
# 2) 停止服务
# 3) 重启服务
# 4) 查看日志
# 5) 查看状态
# 6) 清理数据
```

### 手动操作

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps

# 进入容器
docker exec -it temu-image-generator bash
```

## 🌐 生产环境部署

### 1. 域名绑定

修改 Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 2. HTTPS 配置

```bash
# 使用 Let's Encrypt
certbot --nginx -d your-domain.com
```

### 3. 修改默认密码

```bash
# 编辑 .env 文件
ACCESS_PASSWORD=your_secure_password
ADMIN_PASSWORD=your_admin_password

# 重启服务
docker-compose restart
```

### 4. 调整配额

```bash
# 编辑 .env 文件
DAILY_LIMIT=100  # 每日限额改为100

# 重启服务
docker-compose restart
```

## 📊 监控与维护

### 查看使用统计

1. 使用管理员密码登录
2. 点击侧边栏"查看使用统计"

### 数据备份

```bash
# 备份数据目录
tar -czf temu-backup-$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf temu-backup-YYYYMMDD.tar.gz
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f

# 导出日志
docker-compose logs > temu-logs.txt

# 清理旧日志
docker-compose logs --tail=1000 > recent-logs.txt
```

## 🔍 故障排查

### 问题1: 容器无法启动

```bash
# 检查日志
docker-compose logs

# 常见原因：
# - 端口8501已被占用
# - .env 配置错误
# - Docker 资源不足
```

### 问题2: API 调用失败

```bash
# 检查 API Key
docker-compose exec temu-app env | grep GEMINI

# 测试网络连接
docker-compose exec temu-app ping -c 3 google.com
```

### 问题3: 数据丢失

```bash
# 检查数据目录挂载
docker-compose exec temu-app ls -la /data

# 确保 docker-compose.yml 中有：
# volumes:
#   - ./data:/data
```

## 🚀 性能优化

### 1. 增加资源限制

编辑 `docker-compose.yml`：

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

### 2. 启用缓存

系统已自动使用 `@st.cache_resource` 缓存

### 3. 调整并发

根据服务器配置调整 `API_TIMEOUT`：

```bash
# .env
API_TIMEOUT=180  # 增加到3分钟
```

## 🔒 安全加固

### 1. 防火墙设置

```bash
# 仅允许特定IP访问
ufw allow from YOUR_IP to any port 8501
```

### 2. 反向代理认证

在 Nginx 中添加基础认证：

```nginx
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8501;
}
```

### 3. 定期更新

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```

## 📞 获取帮助

- **文档**: 查看 README.md
- **变更日志**: 查看 CHANGELOG.md
- **核心作者**: 企鹅

---

**部署愉快！** 🎉
