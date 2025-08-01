# AI Agent Web Service - Docker调试指南

本指南介绍如何使用Docker Compose在本机OrbStack环境中模拟K8s集群内网域名访问，方便调试开发。

## 🎯 调试目标

- 在本机Docker环境中模拟K8s集群部署
- 使用与K8s相同的内网域名访问方式
- 保持开发环境与生产环境的一致性

## 🚀 快速启动

### 1. 启动服务
```bash
cd web-service
docker-compose up -d
```

### 2. 验证服务
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f web-service
```

## 🌐 访问方式

### 1. K8s风格内网域名访问（推荐）

在容器内部或其他容器中，可以使用与K8s集群相同的域名：

```bash
# 进入任意容器测试
docker run --rm --network ai-agents curlimages/curl \
  curl http://web-service.ai-agents.svc.cluster.local/health

# 或使用简化域名
docker run --rm --network ai-agents curlimages/curl \
  curl http://web-service/health
```

### 2. 本机访问

```bash
# 通过8080端口访问（避免与nginx冲突）
curl http://localhost:8080/health

# 通过8000端口直接访问
curl http://localhost:8000/health
```

### 3. 添加本机hosts映射（可选）

如果希望在本机也能使用K8s域名，可以添加hosts映射：

```bash
# 编辑 /etc/hosts 文件
sudo vim /etc/hosts

# 添加以下行
127.0.0.1 web-service.ai-agents.svc.cluster.local
127.0.0.1 web-service

# 然后就可以在本机使用K8s域名
curl http://web-service.ai-agents.svc.cluster.local:8080/health
```

## 🔧 配置说明

### 环境变量

Docker Compose配置模拟了K8s的ConfigMap环境变量：

```yaml
environment:
  # 应用配置
  - APP_NAME=AI Agent Web Service
  - VERSION=1.0.0
  - DEBUG=true
  - LOG_LEVEL=DEBUG
  
  # Agent框架配置
  - AGENT_FRAMEWORKS_PATH=/app/agent-frameworks
  - LANGGRAPH_PATH=/app/agent-frameworks/langgraph
  
  # 服务发现配置
  - WEB_SERVICE_HOST=web-service.ai-agents.svc.cluster.local
  - WEB_SERVICE_PORT=80
```

### 网络配置

```yaml
networks:
  ai-agents:
    name: ai-agents
    driver: bridge

# 服务网络别名
networks:
  ai-agents:
    aliases:
      - web-service.ai-agents.svc.cluster.local
      - web-service
```

### 卷挂载

```yaml
volumes:
  # 开发时挂载源码目录
  - ../agent-frameworks:/app/agent-frameworks:ro
  # 日志目录
  - ./logs:/app/logs
  # 原型输出目录（模拟K8s emptyDir）
  - prototype-outputs:/app/agent-frameworks/langgraph/prototype_design/outputs
```

## 🧪 测试验证

### 1. 健康检查
```bash
# 本机访问
curl http://localhost:8080/health

# 容器内网域名访问
docker run --rm --network ai-agents curlimages/curl \
  curl http://web-service.ai-agents.svc.cluster.local/health
```

### 2. API测试
```bash
# 测试PrototypeDesign健康检查
curl http://localhost:8080/api/v1/prototype_design/health

# 容器内网访问
docker run --rm --network ai-agents curlimages/curl \
  curl http://web-service/api/v1/prototype_design/health
```

### 3. 服务发现测试
```bash
# 在ai-agents网络中启动测试容器
docker run -it --rm --network ai-agents alpine sh

# 在容器内测试DNS解析
nslookup web-service.ai-agents.svc.cluster.local
nslookup web-service

# 测试HTTP访问
wget -qO- http://web-service.ai-agents.svc.cluster.local/health
wget -qO- http://web-service/health
```

## 🔄 开发工作流

### 1. 代码修改
```bash
# 修改代码后重新构建
docker-compose build web-service

# 重启服务
docker-compose restart web-service
```

### 2. 查看日志
```bash
# 实时查看日志
docker-compose logs -f web-service

# 查看特定时间的日志
docker-compose logs --since="1h" web-service
```

### 3. 进入容器调试
```bash
# 进入容器
docker-compose exec web-service bash

# 或者启动新的调试容器
docker run -it --rm --network ai-agents \
  --volumes-from web-service \
  ai-agent-web-service:latest bash
```

## 🔧 可选服务

### 启动Redis缓存
```bash
docker-compose --profile with-redis up -d
```

### 启动PostgreSQL数据库
```bash
docker-compose --profile with-database up -d
```

### 启动Nginx反向代理
```bash
docker-compose --profile with-nginx up -d
```

### 启动所有服务
```bash
docker-compose --profile with-redis --profile with-database --profile with-nginx up -d
```

## 🧹 清理资源

### 停止服务
```bash
docker-compose down
```

### 清理卷和网络
```bash
docker-compose down -v --remove-orphans
```

### 清理镜像
```bash
docker-compose down --rmi all
```

## 📊 监控和调试

### 1. 容器状态
```bash
# 查看容器状态
docker-compose ps

# 查看资源使用
docker stats $(docker-compose ps -q)
```

### 2. 网络调试
```bash
# 查看网络信息
docker network inspect ai-agents

# 查看容器网络配置
docker inspect web-service | jq '.[0].NetworkSettings'
```

### 3. 端口映射
```bash
# 查看端口映射
docker port web-service
```

## 🎉 完成

现在你可以在本机Docker环境中使用与K8s集群相同的内网域名访问方式进行调试：

- **容器内访问**: `http://web-service.ai-agents.svc.cluster.local`
- **简化域名**: `http://web-service`
- **本机访问**: `http://localhost:8080`

这样就实现了开发环境与生产环境的访问方式一致性，方便调试和测试！
