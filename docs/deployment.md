# AI Agent Web Service 部署文档

## 概述

本文档介绍如何部署AI Agent Web Service，支持开发环境、生产环境和Docker部署。

## 系统要求

### 最低要求

- **操作系统**: Linux, macOS, Windows
- **Python**: 3.10+
- **内存**: 2GB RAM
- **存储**: 5GB 可用空间
- **网络**: 互联网连接（用于下载依赖和API调用）

### 推荐配置

- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 20GB SSD
- **网络**: 稳定的互联网连接

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd Agents
```

### 2. 运行初始化脚本

```bash
./scripts/setup.sh
```

### 3. 配置环境变量

```bash
cd web-service
cp .env.example .env
# 编辑.env文件，配置必要的参数
```

### 4. 启动服务

```bash
# 开发模式
./scripts/start_services.sh dev

# 或者Docker模式
./scripts/start_services.sh docker
```

## 详细部署步骤

### 开发环境部署

#### 1. 环境准备

```bash
# 检查Python版本
python3 --version  # 应该是3.10+

# 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install python3-pip python3-venv git curl

# 安装系统依赖（CentOS/RHEL）
sudo yum install python3-pip python3-venv git curl

# 安装系统依赖（macOS）
brew install python git curl
```

#### 2. 项目设置

```bash
# 运行初始化脚本
./scripts/setup.sh

# 手动设置（如果脚本失败）
cd web-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. 配置文件

编辑 `web-service/.env` 文件：

```bash
# 基础配置
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 框架路径
LANGGRAPH_PATH=../agent-frameworks/langgraph
AUTOGEN_PATH=../agent-frameworks/autogen
CREWAI_PATH=../agent-frameworks/crewai

# API密钥（如果需要）
OPENAI_API_KEY=your-openai-api-key
```

#### 4. 启动服务

```bash
# 使用启动脚本
./scripts/start_services.sh dev

# 或者手动启动
cd web-service
source venv/bin/activate
python app/main.py
```

### 生产环境部署

#### 1. 服务器准备

```bash
# 创建专用用户
sudo useradd -m -s /bin/bash aiagent
sudo usermod -aG sudo aiagent

# 切换到专用用户
sudo su - aiagent
```

#### 2. 项目部署

```bash
# 克隆项目到生产目录
git clone <repository-url> /opt/ai-agent
cd /opt/ai-agent

# 运行初始化
./scripts/setup.sh

# 配置生产环境变量
cd web-service
cp .env.example .env
# 编辑.env，设置生产配置
```

#### 3. 生产配置

编辑 `web-service/.env`：

```bash
# 生产环境配置
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# 安全配置
SECRET_KEY=your-production-secret-key
API_KEY=your-api-key

# 性能配置
MAX_CONCURRENT_AGENTS=20
AGENT_TIMEOUT=600
```

#### 4. 系统服务配置

创建systemd服务文件 `/etc/systemd/system/ai-agent.service`：

```ini
[Unit]
Description=AI Agent Web Service
After=network.target

[Service]
Type=simple
User=aiagent
Group=aiagent
WorkingDirectory=/opt/ai-agent/web-service
Environment=PATH=/opt/ai-agent/web-service/venv/bin
ExecStart=/opt/ai-agent/web-service/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-agent
sudo systemctl start ai-agent
sudo systemctl status ai-agent
```

### Docker部署

#### 1. 安装Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 配置环境

```bash
cd web-service
cp .env.example .env
# 编辑.env文件
```

#### 3. 构建和启动

```bash
# 使用启动脚本
./scripts/start_services.sh docker

# 或者手动操作
cd web-service
docker-compose build
docker-compose up -d
```

#### 4. 验证部署

```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试API
curl http://localhost:8000/health
```

## 反向代理配置

### Nginx配置

创建 `/etc/nginx/sites-available/ai-agent`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/ai-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL配置（使用Let's Encrypt）

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 监控和日志

### 日志配置

服务日志位置：
- 开发环境：控制台输出
- 生产环境：`/var/log/ai-agent/`
- Docker：`docker-compose logs`

### 健康检查

```bash
# API健康检查
curl http://localhost:8000/health

# 详细健康检查
curl -X POST http://localhost:8000/api/v1/health \
     -H "Content-Type: application/json" \
     -d '{"check_frameworks": true}'
```

### 性能监控

推荐使用以下工具：
- **Prometheus + Grafana**: 指标监控
- **ELK Stack**: 日志分析
- **Sentry**: 错误追踪

## 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查Python环境
which python3
python3 --version

# 检查依赖
pip list
```

#### 2. Agent执行失败

```bash
# 检查框架路径
ls -la agent-frameworks/

# 检查权限
chmod +x agent-frameworks/*/runner.py

# 查看详细错误
tail -f /var/log/ai-agent/error.log
```

#### 3. Docker问题

```bash
# 重建镜像
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 查看容器日志
docker-compose logs web-service
```

### 性能优化

#### 1. 系统级优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
sysctl -p
```

#### 2. 应用级优化

- 调整worker数量：`--workers 4`
- 配置连接池大小
- 启用缓存（Redis）
- 使用负载均衡

## 安全配置

### 1. 防火墙设置

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### 2. API安全

- 启用API密钥认证
- 配置CORS策略
- 实施请求限流
- 使用HTTPS

### 3. 系统安全

- 定期更新系统
- 使用非root用户运行
- 配置日志审计
- 实施备份策略

## 备份和恢复

### 备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/ai-agent"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz web-service/.env

# 备份Agent代码
tar -czf $BACKUP_DIR/agents_$DATE.tar.gz agent-frameworks/

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 恢复步骤

```bash
# 停止服务
sudo systemctl stop ai-agent

# 恢复配置
tar -xzf config_backup.tar.gz

# 恢复Agent代码
tar -xzf agents_backup.tar.gz

# 重启服务
sudo systemctl start ai-agent
```
