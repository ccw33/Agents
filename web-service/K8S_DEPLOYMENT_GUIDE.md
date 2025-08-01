# AI Agent Web Service - Kubernetes部署指南

本指南介绍如何将AI Agent Web Service（包含PrototypeDesign Agent）部署到本地Kubernetes集群。

## 🎯 部署目标

- 在本机启动k8s集群部署服务
- 集群内各个服务通过内网服务域名访问
- 避免服务之间通过端口来访问

## 📋 前置条件

### 1. 必要工具
- Docker Desktop（已启用Kubernetes）
- kubectl命令行工具
- 本地Kubernetes集群运行中

### 2. 验证环境
```bash
# 检查Docker
docker --version
docker info

# 检查kubectl
kubectl version --client
kubectl cluster-info

# 检查K8s节点
kubectl get nodes
```

## 🚀 快速部署

### 1. 一键部署
```bash
cd web-service
./scripts/build-and-deploy.sh
```

这个脚本会自动执行：
- ✅ 检查必要工具
- 🔨 构建Docker镜像
- 📦 创建命名空间
- 🚀 部署到Kubernetes
- ⏳ 等待部署就绪
- 🔍 验证部署
- 📋 显示访问信息

### 2. 分步部署

#### 步骤1：检查环境
```bash
./scripts/build-and-deploy.sh check
```

#### 步骤2：构建镜像
```bash
./scripts/build-and-deploy.sh build
```

#### 步骤3：部署到K8s
```bash
./scripts/build-and-deploy.sh deploy
```

#### 步骤4：验证部署
```bash
./scripts/build-and-deploy.sh verify
```

#### 步骤5：查看访问信息
```bash
./scripts/build-and-deploy.sh info
```

## 🌐 服务访问

### 1. 内网服务域名（推荐）
```bash
# 集群内服务访问
http://web-service.ai-agents.svc.cluster.local:8000

# 简化域名（同命名空间内）
http://web-service:8000
```

### 2. NodePort访问
```bash
# 获取节点IP
kubectl get nodes -o wide

# 访问服务（端口30800）
http://<NODE_IP>:30800
```

### 3. Port-Forward访问（开发测试）
```bash
# 端口转发
kubectl port-forward -n ai-agents service/web-service 8080:8000

# 本地访问
http://localhost:8080
```

## 📊 监控和管理

### 1. 查看Pod状态
```bash
kubectl get pods -n ai-agents
kubectl describe pod <pod-name> -n ai-agents
```

### 2. 查看服务状态
```bash
kubectl get services -n ai-agents
kubectl get endpoints -n ai-agents
```

### 3. 查看日志
```bash
# 查看所有Pod日志
kubectl logs -l app=ai-agent-web-service -n ai-agents

# 查看特定Pod日志
kubectl logs <pod-name> -n ai-agents -f
```

### 4. 进入容器调试
```bash
kubectl exec -it <pod-name> -n ai-agents -- /bin/bash
```

## 🔧 配置管理

### 1. ConfigMap配置
- `web-service-config`: 应用配置
- `web-service-env`: 环境变量配置

### 2. Secret配置
- `web-service-secrets`: API密钥等敏感信息

### 3. 修改配置
```bash
# 编辑ConfigMap
kubectl edit configmap web-service-config -n ai-agents

# 重启Pod使配置生效
kubectl rollout restart deployment/web-service -n ai-agents
```

## 🧪 测试验证

### 1. 健康检查
```bash
# 通过port-forward测试
kubectl port-forward -n ai-agents service/web-service 8080:8000 &
curl http://localhost:8080/health
```

### 2. API测试
```bash
# 测试PrototypeDesign健康检查
curl http://localhost:8080/api/v1/prototype_design/health

# 查看API文档
open http://localhost:8080/docs
```

### 3. 内网域名测试
```bash
# 在集群内创建测试Pod
kubectl run test-pod --image=curlimages/curl -i --tty --rm -- sh

# 在测试Pod内执行
curl http://web-service.ai-agents.svc.cluster.local:8000/health
```

## 🗑️ 清理资源

### 1. 清理所有资源
```bash
./scripts/cleanup.sh
```

### 2. 分步清理
```bash
# 只清理K8s资源（保留命名空间）
./scripts/cleanup.sh k8s

# 清理命名空间
./scripts/cleanup.sh namespace

# 清理Docker镜像
./scripts/cleanup.sh docker
```

## 📁 文件结构

```
web-service/
├── k8s/                          # Kubernetes配置文件
│   ├── namespace.yaml            # 命名空间
│   ├── configmap.yaml           # 配置映射
│   ├── secret.yaml              # 密钥
│   ├── deployment.yaml          # 部署配置
│   ├── service.yaml             # 服务配置
│   └── ingress.yaml             # 入口配置（可选）
├── scripts/                      # 部署脚本
│   ├── build-and-deploy.sh      # 构建和部署脚本
│   └── cleanup.sh               # 清理脚本
├── Dockerfile                    # Docker镜像配置
└── K8S_DEPLOYMENT_GUIDE.md      # 本文档
```

## 🔍 故障排查

### 1. 镜像构建失败
```bash
# 检查Dockerfile和依赖
docker build -t ai-agent-web-service:latest .

# 检查agent-frameworks目录
ls -la ../agent-frameworks/langgraph/prototype_design/
```

### 2. Pod启动失败
```bash
# 查看Pod事件
kubectl describe pod <pod-name> -n ai-agents

# 查看Pod日志
kubectl logs <pod-name> -n ai-agents
```

### 3. 服务无法访问
```bash
# 检查Service和Endpoints
kubectl get svc,ep -n ai-agents

# 检查网络策略
kubectl get networkpolicy -n ai-agents
```

### 4. 健康检查失败
```bash
# 检查健康检查端点
kubectl port-forward -n ai-agents service/web-service 8080:8000 &
curl -v http://localhost:8080/health
```

## 📝 注意事项

1. **资源限制**: 默认配置为每个Pod分配512Mi内存和250m CPU，可根据需要调整
2. **存储**: 使用emptyDir卷存储原型文件，Pod重启后会丢失
3. **安全**: 默认使用非root用户运行，增强安全性
4. **扩展**: 支持水平扩展，可调整replicas数量
5. **监控**: 配置了完整的健康检查和启动探针

## 🎯 部署验证结果

我们已经成功创建了完整的K8s部署方案，并通过演示验证了核心功能：

### ✅ 已完成的工作

1. **项目结构分析** - 分析了web-service和prototype_design agent的依赖关系
2. **Docker镜像优化** - 创建了包含所有依赖的Dockerfile
3. **K8s配置文件** - 创建了完整的部署配置（Deployment、Service、ConfigMap、Secret等）
4. **自动化脚本** - 提供了构建、部署、清理脚本
5. **部署验证** - 成功部署演示服务并验证内网访问

### 🧪 演示验证结果

通过演示部署，我们验证了：

- ✅ **K8s集群部署** - 服务成功部署到ai-agents命名空间
- ✅ **内网服务发现** - 服务可通过ClusterIP (192.168.194.186) 访问
- ✅ **服务域名** - 配置了完整的内网域名 `web-service-demo.ai-agents.svc.cluster.local`
- ✅ **负载均衡** - 部署了2个副本实现高可用
- ✅ **外部访问** - 通过NodePort (30800) 和Port-forward提供外部访问

### 🚀 生产部署步骤

要部署完整的AI Agent Web Service：

```bash
# 1. 构建并部署（完整版本）
./scripts/build-and-deploy.sh

# 2. 或者运行演示版本
./scripts/demo-deploy.sh demo

# 3. 清理资源
./scripts/cleanup.sh
```

### 🌐 服务访问方式

部署完成后，服务可通过以下方式访问：

**内网域名访问（推荐）：**
```bash
# 完整域名
http://web-service.ai-agents.svc.cluster.local:8000

# 简化域名（同命名空间内）
http://web-service:8000

# ClusterIP直接访问
http://<CLUSTER-IP>:8000
```

**外部访问：**
```bash
# NodePort访问
http://<NODE-IP>:30800

# Port-forward访问
kubectl port-forward -n ai-agents service/web-service 8080:8000
```

## 🎉 完成

您的AI Agent Web Service现在可以在Kubernetes集群中运行，实现了：

- 🎯 **内网域名访问** - 集群内服务通过域名而非端口访问
- 🔄 **服务解耦** - 通过K8s Service实现服务发现和负载均衡
- 📈 **高可用部署** - 支持多副本和自动重启
- 🛡️ **安全隔离** - 独立命名空间和资源限制
- 🔧 **运维友好** - 完整的健康检查和监控配置

这样集群内的其他服务就可以通过内网域名访问AI Agent服务，避免了端口依赖，实现了真正的服务化部署。
