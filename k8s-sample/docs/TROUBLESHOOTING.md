# Kubernetes故障排查指南

本文档提供了常见Kubernetes部署问题的诊断和解决方法。

## 🔍 基础诊断命令

### 1. 集群状态检查

```bash
# 检查集群信息
kubectl cluster-info

# 检查节点状态
kubectl get nodes -o wide

# 检查系统Pod状态
kubectl get pods -n kube-system

# 检查集群事件
kubectl get events --sort-by='.lastTimestamp'
```

### 2. 应用状态检查

```bash
# 检查Pod状态
kubectl get pods -n <namespace> -o wide

# 检查服务状态
kubectl get services -n <namespace>

# 检查Ingress状态
kubectl get ingress -n <namespace>

# 检查部署状态
kubectl get deployments -n <namespace>
```

### 3. 详细信息查看

```bash
# 查看Pod详细信息
kubectl describe pod <pod-name> -n <namespace>

# 查看服务详细信息
kubectl describe service <service-name> -n <namespace>

# 查看部署详细信息
kubectl describe deployment <deployment-name> -n <namespace>
```

## 🚨 常见问题及解决方案

### 1. Pod启动问题

#### 问题：Pod处于Pending状态

**可能原因：**
- 资源不足
- 节点选择器不匹配
- 污点和容忍度问题
- PVC无法绑定

**诊断命令：**
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

**解决方案：**
```bash
# 检查节点资源
kubectl top nodes

# 检查资源配额
kubectl describe resourcequota -n <namespace>

# 调整资源请求
kubectl edit deployment <deployment-name> -n <namespace>
```

#### 问题：Pod处于ImagePullBackOff状态

**可能原因：**
- 镜像不存在
- 镜像仓库认证失败
- 网络问题

**诊断命令：**
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>
```

**解决方案：**
```bash
# 检查镜像是否存在
docker pull <image-name>

# 检查镜像拉取密钥
kubectl get secrets -n <namespace>

# 创建镜像拉取密钥
kubectl create secret docker-registry regcred \
  --docker-server=<registry-url> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> \
  -n <namespace>
```

#### 问题：Pod处于CrashLoopBackOff状态

**可能原因：**
- 应用启动失败
- 配置错误
- 依赖服务不可用
- 健康检查失败

**诊断命令：**
```bash
kubectl logs <pod-name> -n <namespace> --previous
kubectl describe pod <pod-name> -n <namespace>
```

**解决方案：**
```bash
# 查看应用日志
kubectl logs <pod-name> -n <namespace> -f

# 进入容器调试
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# 调整健康检查参数
kubectl edit deployment <deployment-name> -n <namespace>
```

### 2. 网络连接问题

#### 问题：服务无法访问

**可能原因：**
- Service选择器不匹配
- 端口配置错误
- NetworkPolicy阻止访问
- DNS解析问题

**诊断命令：**
```bash
# 检查Service和Endpoints
kubectl get svc,ep -n <namespace>

# 检查Service选择器
kubectl describe service <service-name> -n <namespace>

# 测试DNS解析
kubectl run test-pod --image=busybox -it --rm -- nslookup <service-name>.<namespace>.svc.cluster.local
```

**解决方案：**
```bash
# 检查Pod标签
kubectl get pods -n <namespace> --show-labels

# 修复Service选择器
kubectl edit service <service-name> -n <namespace>

# 测试端口连通性
kubectl run test-pod --image=busybox -it --rm -- telnet <service-name> <port>
```

#### 问题：Ingress无法访问

**可能原因：**
- Ingress Controller未安装
- 域名解析问题
- TLS证书问题
- 后端服务不可用

**诊断命令：**
```bash
# 检查Ingress Controller
kubectl get pods -n ingress-nginx

# 检查Ingress配置
kubectl describe ingress <ingress-name> -n <namespace>

# 检查Ingress Controller日志
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

**解决方案：**
```bash
# 安装Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 检查域名解析
nslookup <domain-name>

# 验证TLS证书
openssl s_client -connect <domain-name>:443 -servername <domain-name>
```

### 3. 存储问题

#### 问题：PVC处于Pending状态

**可能原因：**
- 没有可用的PV
- StorageClass不存在
- 存储资源不足

**诊断命令：**
```bash
kubectl describe pvc <pvc-name> -n <namespace>
kubectl get pv
kubectl get storageclass
```

**解决方案：**
```bash
# 创建PV（如果使用静态供应）
kubectl apply -f pv.yaml

# 检查StorageClass
kubectl describe storageclass <storage-class-name>

# 检查存储节点资源
kubectl describe nodes
```

### 4. 配置问题

#### 问题：ConfigMap或Secret未生效

**可能原因：**
- 配置未正确挂载
- Pod未重启
- 权限问题

**诊断命令：**
```bash
# 检查ConfigMap内容
kubectl get configmap <configmap-name> -n <namespace> -o yaml

# 检查Pod挂载
kubectl describe pod <pod-name> -n <namespace>

# 进入容器检查文件
kubectl exec -it <pod-name> -n <namespace> -- ls -la /etc/config
```

**解决方案：**
```bash
# 重启Pod使配置生效
kubectl rollout restart deployment <deployment-name> -n <namespace>

# 检查挂载路径
kubectl exec -it <pod-name> -n <namespace> -- cat /etc/config/<config-file>
```

### 5. 资源问题

#### 问题：资源配额超限

**可能原因：**
- CPU/内存使用超限
- Pod数量超限
- 存储使用超限

**诊断命令：**
```bash
# 检查资源配额
kubectl describe resourcequota -n <namespace>

# 检查资源使用情况
kubectl top pods -n <namespace>
kubectl top nodes
```

**解决方案：**
```bash
# 调整资源配额
kubectl edit resourcequota <quota-name> -n <namespace>

# 优化应用资源使用
kubectl edit deployment <deployment-name> -n <namespace>

# 清理不需要的资源
kubectl delete pod <pod-name> -n <namespace>
```

## 🛠️ 调试工具和技巧

### 1. 日志分析

```bash
# 查看实时日志
kubectl logs -f <pod-name> -n <namespace>

# 查看之前容器的日志
kubectl logs <pod-name> -n <namespace> --previous

# 查看多个Pod的日志
kubectl logs -l app=<app-name> -n <namespace>

# 导出日志到文件
kubectl logs <pod-name> -n <namespace> > app.log
```

### 2. 容器调试

```bash
# 进入运行中的容器
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# 在Pod中运行命令
kubectl exec <pod-name> -n <namespace> -- ps aux

# 复制文件到/从容器
kubectl cp <pod-name>:/path/to/file ./local-file -n <namespace>
kubectl cp ./local-file <pod-name>:/path/to/file -n <namespace>
```

### 3. 网络调试

```bash
# 创建调试Pod
kubectl run debug-pod --image=nicolaka/netshoot -it --rm

# 在调试Pod中测试连接
# ping <service-name>.<namespace>.svc.cluster.local
# curl http://<service-name>.<namespace>.svc.cluster.local:<port>
# nslookup <service-name>.<namespace>.svc.cluster.local

# 端口转发调试
kubectl port-forward <pod-name> 8080:80 -n <namespace>
```

### 4. 性能分析

```bash
# 查看资源使用情况
kubectl top pods -n <namespace>
kubectl top nodes

# 查看Pod资源限制
kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Limits\|Requests"

# 监控Pod性能
watch kubectl top pods -n <namespace>
```

## 📊 监控和告警

### 1. 关键指标监控

```yaml
# Prometheus告警规则示例
groups:
- name: kubernetes-pods
  rules:
  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Pod {{ $labels.pod }} is crash looping"

  - alert: PodNotReady
    expr: kube_pod_status_ready{condition="false"} == 1
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "Pod {{ $labels.pod }} has been not ready for more than 10 minutes"
```

### 2. 日志聚合

```yaml
# Fluentd配置示例
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name kubernetes
    </match>
```

## 🔧 自动化故障排查

### 1. 健康检查脚本

```bash
#!/bin/bash
# health-check.sh

NAMESPACE=${1:-default}

echo "=== Checking namespace: $NAMESPACE ==="

# 检查Pod状态
echo "Checking pods..."
kubectl get pods -n $NAMESPACE | grep -v Running | grep -v Completed

# 检查服务状态
echo "Checking services..."
kubectl get svc -n $NAMESPACE

# 检查最近事件
echo "Recent events..."
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

# 检查资源使用
echo "Resource usage..."
kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics server not available"
```

### 2. 故障自愈

```yaml
# 使用livenessProbe实现自动重启
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 30
  failureThreshold: 3

# 使用HPA实现自动扩缩容
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 📋 故障排查检查清单

### 快速诊断步骤

1. **检查Pod状态**
   ```bash
   kubectl get pods -n <namespace>
   ```

2. **查看Pod事件**
   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   ```

3. **检查应用日志**
   ```bash
   kubectl logs <pod-name> -n <namespace>
   ```

4. **验证服务连接**
   ```bash
   kubectl get svc,ep -n <namespace>
   ```

5. **测试网络连通性**
   ```bash
   kubectl run test --image=busybox -it --rm -- wget -qO- http://<service>:<port>
   ```

### 深度分析步骤

1. **检查资源使用**
   ```bash
   kubectl top pods -n <namespace>
   kubectl describe node <node-name>
   ```

2. **分析网络策略**
   ```bash
   kubectl get networkpolicy -n <namespace>
   ```

3. **检查RBAC权限**
   ```bash
   kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<namespace>:<sa-name>
   ```

4. **验证存储状态**
   ```bash
   kubectl get pv,pvc -n <namespace>
   ```

5. **检查集群级别问题**
   ```bash
   kubectl get nodes
   kubectl get events --all-namespaces
   ```

## 🆘 紧急情况处理

### 1. 服务完全不可用

```bash
# 快速回滚到上一个版本
kubectl rollout undo deployment/<deployment-name> -n <namespace>

# 手动扩容增加可用性
kubectl scale deployment <deployment-name> --replicas=5 -n <namespace>

# 临时绕过故障组件
kubectl patch service <service-name> -p '{"spec":{"selector":{"app":"backup-service"}}}' -n <namespace>
```

### 2. 资源耗尽

```bash
# 紧急清理资源
kubectl delete pods --field-selector=status.phase=Failed -n <namespace>
kubectl delete pods --field-selector=status.phase=Succeeded -n <namespace>

# 临时增加资源配额
kubectl patch resourcequota <quota-name> -p '{"spec":{"hard":{"requests.memory":"10Gi"}}}' -n <namespace>
```

### 3. 网络故障

```bash
# 重启网络组件
kubectl delete pods -n kube-system -l k8s-app=kube-dns
kubectl delete pods -n kube-system -l app=calico-node

# 刷新DNS缓存
kubectl delete pods -n kube-system -l k8s-app=kube-dns
```

## 📞 获取帮助

- **Kubernetes官方文档**: https://kubernetes.io/docs/tasks/debug-application-cluster/
- **社区支持**: https://kubernetes.io/community/
- **GitHub Issues**: https://github.com/kubernetes/kubernetes/issues
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/kubernetes
