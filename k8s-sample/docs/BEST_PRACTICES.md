# Kubernetes部署最佳实践

本文档总结了Kubernetes应用部署的最佳实践，基于我们的k8s-sample模板。

## 🏗️ 架构设计

### 1. 命名空间隔离

```yaml
# 为不同环境使用不同命名空间
development: my-app-dev
staging: my-app-staging  
production: my-app-prod

# 为不同团队使用不同命名空间
frontend: frontend-team
backend: backend-team
data: data-team
```

### 2. 标签策略

```yaml
# 推荐的标签结构
labels:
  app: my-application           # 应用名称
  component: web-server         # 组件类型
  version: v1.2.3              # 版本号
  environment: production      # 环境
  team: backend               # 负责团队
  tier: frontend              # 应用层级
```

### 3. 资源命名规范

```bash
# 命名规范：<app>-<component>-<type>
my-app-web-deployment
my-app-web-service
my-app-web-configmap
my-app-web-secret

# 避免使用
web-deployment-1
service-for-web
config
```

## 🔒 安全最佳实践

### 1. 容器安全

```yaml
# 使用非root用户
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
    add:
    - NET_BIND_SERVICE  # 仅在需要时添加
```

### 2. 密钥管理

```bash
# 使用外部密钥管理系统
# AWS Secrets Manager
# Azure Key Vault
# Google Secret Manager
# HashiCorp Vault

# 避免在代码中硬编码密钥
# 使用stringData而不是data（开发时）
# 定期轮换密钥
```

### 3. 网络安全

```yaml
# 使用NetworkPolicy限制网络访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 4. RBAC配置

```yaml
# 最小权限原则
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

## 📊 资源管理

### 1. 资源限制

```yaml
# 始终设置资源请求和限制
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# 根据应用类型调整
# CPU密集型：高CPU限制
# 内存密集型：高内存限制
# I/O密集型：适中的CPU和内存
```

### 2. 质量服务等级(QoS)

```yaml
# Guaranteed QoS（推荐生产环境）
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "1Gi"    # 与requests相同
    cpu: "500m"      # 与requests相同

# Burstable QoS（开发/测试环境）
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"    # 大于requests
    cpu: "1000m"     # 大于requests
```

### 3. 水平扩缩容

```yaml
# HPA配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2      # 最小副本数
  maxReplicas: 10     # 最大副本数
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # CPU使用率阈值
```

## 🔄 部署策略

### 1. 滚动更新

```yaml
# 推荐的滚动更新策略
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1      # 最多1个Pod不可用
    maxSurge: 1           # 最多额外1个Pod
```

### 2. 就绪和存活探针

```yaml
# 存活探针 - 检测容器是否健康
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30  # 给应用足够启动时间
  periodSeconds: 30        # 检查间隔
  timeoutSeconds: 10       # 超时时间
  failureThreshold: 3      # 失败次数阈值

# 就绪探针 - 检测容器是否准备好接收流量
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

# 启动探针 - 用于慢启动应用
startupProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 30     # 给慢启动应用更多时间
```

### 3. 中断预算

```yaml
# 确保服务可用性
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
spec:
  minAvailable: 1          # 至少保持1个Pod可用
  # 或者使用百分比
  # minAvailable: 50%
  selector:
    matchLabels:
      app: my-app
```

## 📈 监控和日志

### 1. 健康检查端点

```go
// 示例健康检查端点
func healthHandler(w http.ResponseWriter, r *http.Request) {
    // 检查数据库连接
    if !checkDatabase() {
        w.WriteHeader(http.StatusServiceUnavailable)
        return
    }
    
    // 检查外部依赖
    if !checkExternalServices() {
        w.WriteHeader(http.StatusServiceUnavailable)
        return
    }
    
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{
        "status": "healthy",
        "timestamp": time.Now().Format(time.RFC3339),
    })
}
```

### 2. 结构化日志

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "my-app",
  "version": "v1.2.3",
  "message": "Request processed",
  "request_id": "req-123",
  "user_id": "user-456",
  "duration_ms": 150
}
```

### 3. Prometheus指标

```yaml
# ServiceMonitor配置
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app-metrics
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

## 🗂️ 配置管理

### 1. ConfigMap vs Secret

```yaml
# ConfigMap - 非敏感配置
apiVersion: v1
kind: ConfigMap
data:
  database_host: "postgres.example.com"
  log_level: "INFO"
  feature_flags: '{"new_ui": true}'

# Secret - 敏感信息
apiVersion: v1
kind: Secret
type: Opaque
stringData:
  database_password: "secret-password"
  api_key: "secret-api-key"
```

### 2. 环境特定配置

```bash
# 使用不同的ConfigMap/Secret名称
development: my-app-config-dev
staging: my-app-config-staging
production: my-app-config-prod
```

### 3. 配置热更新

```yaml
# 使用卷挂载实现配置热更新
volumeMounts:
- name: config
  mountPath: /etc/config
  readOnly: true
volumes:
- name: config
  configMap:
    name: my-app-config
```

## 🌐 网络最佳实践

### 1. Service类型选择

```yaml
# ClusterIP - 集群内访问（推荐）
type: ClusterIP

# NodePort - 测试环境外部访问
type: NodePort

# LoadBalancer - 生产环境外部访问
type: LoadBalancer

# ExternalName - 外部服务映射
type: ExternalName
```

### 2. Ingress配置

```yaml
# 使用TLS
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls-secret
  
  # 配置路径路由
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### 3. DNS配置

```yaml
# 优化DNS配置
dnsPolicy: ClusterFirst
dnsConfig:
  options:
  - name: ndots
    value: "2"
  - name: edns0
```

## 💾 存储最佳实践

### 1. 存储类型选择

```yaml
# emptyDir - 临时存储
volumes:
- name: tmp
  emptyDir: {}

# PersistentVolume - 持久存储
volumes:
- name: data
  persistentVolumeClaim:
    claimName: my-app-data

# ConfigMap/Secret - 配置文件
volumes:
- name: config
  configMap:
    name: my-app-config
```

### 2. 存储类配置

```yaml
# 高性能存储类
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
```

## 🔧 运维最佳实践

### 1. 版本管理

```bash
# 使用语义化版本
v1.2.3
v1.2.3-rc.1
v1.2.3-beta.1

# 镜像标签策略
my-app:v1.2.3          # 生产环境
my-app:v1.2.3-staging  # 测试环境
my-app:latest          # 开发环境（谨慎使用）
```

### 2. 备份策略

```bash
# 定期备份
# - 配置文件
# - 密钥
# - 持久卷数据
# - 数据库

# 使用Velero进行集群备份
velero backup create my-app-backup \
  --include-namespaces my-app-prod
```

### 3. 灾难恢复

```yaml
# 多可用区部署
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - my-app
      topologyKey: topology.kubernetes.io/zone
```

## 📋 检查清单

### 部署前检查

- [ ] 资源请求和限制已设置
- [ ] 健康检查已配置
- [ ] 安全上下文已设置
- [ ] 标签和注解完整
- [ ] 密钥已正确配置
- [ ] 网络策略已定义
- [ ] 监控已配置

### 部署后验证

- [ ] Pod状态正常
- [ ] 服务可访问
- [ ] 健康检查通过
- [ ] 日志正常输出
- [ ] 指标正常收集
- [ ] 备份策略生效

## 🚨 常见陷阱

### 1. 避免的做法

```yaml
# ❌ 不要使用latest标签在生产环境
image: my-app:latest

# ❌ 不要忽略资源限制
# resources: {}

# ❌ 不要使用默认ServiceAccount
# serviceAccountName: default

# ❌ 不要在容器中运行为root
# securityContext: {}
```

### 2. 推荐的做法

```yaml
# ✅ 使用具体版本标签
image: my-app:v1.2.3

# ✅ 设置适当的资源限制
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# ✅ 使用专用ServiceAccount
serviceAccountName: my-app-sa

# ✅ 使用非root用户
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
```

## 📚 参考资源

- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [12-Factor App](https://12factor.net/)
- [CNCF Cloud Native Trail Map](https://github.com/cncf/trailmap)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Production-Grade Container Orchestration](https://kubernetes.io/docs/setup/production-environment/)
