# Kubernetes部署指南

本指南提供了使用K8s-sample模板进行应用部署的完整指导。

## 📋 目录结构

```
k8s-sample/
├── templates/              # K8s配置模板
│   ├── namespace.yaml      # 命名空间配置
│   ├── configmap.yaml      # 配置映射
│   ├── secret.yaml         # 密钥配置
│   ├── deployment.yaml     # 部署配置
│   ├── service.yaml        # 服务配置
│   └── ingress.yaml        # 入口配置
├── scripts/                # 部署脚本
│   ├── deploy.sh          # 部署脚本
│   ├── cleanup.sh         # 清理脚本
│   └── generate-config.sh # 配置生成脚本
└── docs/                  # 文档
    ├── DEPLOYMENT_GUIDE.md # 本文档
    ├── BEST_PRACTICES.md   # 最佳实践
    └── TROUBLESHOOTING.md  # 故障排查
```

## 🚀 快速开始

### 1. 准备工作

确保你有以下工具和权限：

```bash
# 检查kubectl
kubectl version --client

# 检查集群连接
kubectl cluster-info

# 检查权限
kubectl auth can-i create deployments --namespace=default
```

### 2. 复制模板

```bash
# 复制模板到你的项目目录
cp -r k8s-sample/templates your-app/k8s/
```

### 3. 配置替换

使用以下方法替换模板中的占位符：

#### 方法一：手动替换
```bash
# 编辑每个文件，将 {{PLACEHOLDER}} 替换为实际值
vim your-app/k8s/namespace.yaml
vim your-app/k8s/configmap.yaml
# ... 其他文件
```

#### 方法二：使用脚本替换
```bash
# 创建配置文件
cat > config.env << EOF
NAMESPACE_NAME=my-app
APP_NAME=my-application
VERSION=1.0.0
ENVIRONMENT=production
# ... 其他配置
EOF

# 使用sed批量替换
for file in your-app/k8s/*.yaml; do
    while IFS='=' read -r key value; do
        sed -i "s/{{$key}}/$value/g" "$file"
    done < config.env
done
```

### 4. 部署应用

```bash
# 创建命名空间
kubectl apply -f your-app/k8s/namespace.yaml

# 部署配置和密钥
kubectl apply -f your-app/k8s/configmap.yaml
kubectl apply -f your-app/k8s/secret.yaml

# 部署应用
kubectl apply -f your-app/k8s/deployment.yaml
kubectl apply -f your-app/k8s/service.yaml

# 可选：部署Ingress
kubectl apply -f your-app/k8s/ingress.yaml
```

## 🔧 配置说明

### 必需配置项

以下是每个模板文件中必须替换的关键占位符：

#### namespace.yaml
- `{{NAMESPACE_NAME}}`: 命名空间名称
- `{{APP_NAME}}`: 应用名称
- `{{ENVIRONMENT}}`: 环境（development/staging/production）
- `{{TEAM_NAME}}`: 团队名称
- `{{DESCRIPTION}}`: 描述信息

#### configmap.yaml
- `{{APP_NAME}}`: 应用名称
- `{{NAMESPACE_NAME}}`: 命名空间名称
- `{{VERSION}}`: 应用版本
- `{{HOST}}`: 监听地址（通常为0.0.0.0）
- `{{PORT}}`: 应用端口
- `{{LOG_LEVEL}}`: 日志级别

#### secret.yaml
- `{{APP_NAME}}`: 应用名称
- `{{NAMESPACE_NAME}}`: 命名空间名称
- `{{SECRET_KEY_BASE64}}`: Base64编码的密钥
- `{{DB_PASSWORD_BASE64}}`: Base64编码的数据库密码

#### deployment.yaml
- `{{APP_NAME}}`: 应用名称
- `{{NAMESPACE_NAME}}`: 命名空间名称
- `{{IMAGE_NAME}}`: 镜像名称
- `{{IMAGE_TAG}}`: 镜像标签
- `{{CONTAINER_PORT}}`: 容器端口
- `{{REPLICAS}}`: 副本数量

#### service.yaml
- `{{SERVICE_NAME}}`: 服务名称
- `{{NAMESPACE_NAME}}`: 命名空间名称
- `{{SERVICE_PORT}}`: 服务端口
- `{{TARGET_PORT}}`: 目标端口

#### ingress.yaml
- `{{INGRESS_NAME}}`: Ingress名称
- `{{NAMESPACE_NAME}}`: 命名空间名称
- `{{DOMAIN_NAME}}`: 域名
- `{{SERVICE_NAME}}`: 后端服务名称

## 📝 配置示例

### 示例1：简单Web应用

```yaml
# 配置值
NAMESPACE_NAME: web-app
APP_NAME: my-web-app
VERSION: 1.0.0
ENVIRONMENT: production
IMAGE_NAME: my-registry/web-app
IMAGE_TAG: v1.0.0
CONTAINER_PORT: 8080
SERVICE_PORT: 80
REPLICAS: 3
DOMAIN_NAME: app.example.com
```

### 示例2：微服务API

```yaml
# 配置值
NAMESPACE_NAME: api-services
APP_NAME: user-service
VERSION: 2.1.0
ENVIRONMENT: staging
IMAGE_NAME: my-registry/user-service
IMAGE_TAG: v2.1.0
CONTAINER_PORT: 3000
SERVICE_PORT: 80
REPLICAS: 2
DOMAIN_NAME: api.example.com
```

## 🔒 安全配置

### 1. Secret管理

```bash
# 生成Base64编码的密钥
echo -n "your-secret-key" | base64

# 创建TLS证书Secret
kubectl create secret tls my-app-tls \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem \
  --namespace=my-namespace

# 创建Docker Registry Secret
kubectl create secret docker-registry my-registry \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=password \
  --docker-email=user@example.com \
  --namespace=my-namespace
```

### 2. RBAC配置

```yaml
# ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace

---
# Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-namespace
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-binding
  namespace: my-namespace
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: my-namespace
roleRef:
  kind: Role
  name: my-app-role
  apiGroup: rbac.authorization.k8s.io
```

## 📊 监控配置

### 1. 健康检查

确保在deployment.yaml中正确配置健康检查：

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
```

### 2. Prometheus监控

```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app-monitor
  namespace: my-namespace
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

## 🔄 部署策略

### 1. 滚动更新

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

### 2. 蓝绿部署

```bash
# 部署新版本到新的命名空间
kubectl apply -f deployment-v2.yaml -n my-app-v2

# 验证新版本
kubectl get pods -n my-app-v2

# 切换流量
kubectl patch service my-app-service -p '{"spec":{"selector":{"version":"v2"}}}'
```

### 3. 金丝雀部署

使用Ingress注解实现金丝雀部署：

```yaml
annotations:
  nginx.ingress.kubernetes.io/canary: "true"
  nginx.ingress.kubernetes.io/canary-weight: "10"
```

## 🧪 测试验证

### 1. 部署验证

```bash
# 检查Pod状态
kubectl get pods -n my-namespace

# 检查服务
kubectl get services -n my-namespace

# 检查Ingress
kubectl get ingress -n my-namespace

# 查看事件
kubectl get events -n my-namespace --sort-by='.lastTimestamp'
```

### 2. 功能测试

```bash
# 端口转发测试
kubectl port-forward service/my-app-service 8080:80 -n my-namespace

# 健康检查测试
curl http://localhost:8080/health

# 负载测试
kubectl run -i --tty load-test --image=busybox --rm -- sh
# 在容器内执行
wget -qO- http://my-app-service.my-namespace.svc.cluster.local/health
```

## 🗑️ 清理资源

### 1. 删除应用

```bash
# 删除所有资源
kubectl delete -f your-app/k8s/ --recursive

# 或者删除整个命名空间
kubectl delete namespace my-namespace
```

### 2. 清理脚本

```bash
#!/bin/bash
# cleanup.sh

NAMESPACE=${1:-my-namespace}

echo "Cleaning up resources in namespace: $NAMESPACE"

# 删除Ingress
kubectl delete ingress --all -n $NAMESPACE

# 删除服务
kubectl delete services --all -n $NAMESPACE

# 删除部署
kubectl delete deployments --all -n $NAMESPACE

# 删除ConfigMap和Secret
kubectl delete configmaps,secrets --all -n $NAMESPACE

# 删除命名空间
kubectl delete namespace $NAMESPACE

echo "Cleanup completed!"
```

## 📚 相关文档

- [最佳实践指南](BEST_PRACTICES.md)
- [故障排查指南](TROUBLESHOOTING.md)
- [Kubernetes官方文档](https://kubernetes.io/docs/)

## 🆘 获取帮助

如果遇到问题，请：

1. 查看[故障排查指南](TROUBLESHOOTING.md)
2. 检查Pod日志：`kubectl logs <pod-name> -n <namespace>`
3. 查看事件：`kubectl describe pod <pod-name> -n <namespace>`
4. 联系运维团队或提交Issue
