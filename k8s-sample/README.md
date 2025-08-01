# Kubernetes部署模板集合 (K8s-Sample)

这是一个完整的Kubernetes应用部署模板集合，提供了生产级别的配置模板、自动化脚本和最佳实践指南。

## 🎯 项目目标

- 提供标准化的Kubernetes部署模板
- 简化应用部署流程
- 确保部署的一致性和可靠性
- 遵循Kubernetes最佳实践
- 支持多环境部署（开发/测试/生产）

## 📁 项目结构

```
k8s-sample/
├── templates/                  # Kubernetes配置模板
│   ├── namespace.yaml         # 命名空间配置模板
│   ├── configmap.yaml         # 配置映射模板
│   ├── secret.yaml            # 密钥配置模板
│   ├── deployment.yaml        # 部署配置模板
│   ├── service.yaml           # 服务配置模板
│   └── ingress.yaml           # 入口配置模板
├── scripts/                   # 自动化脚本
│   ├── deploy.sh             # 部署脚本
│   ├── cleanup.sh            # 清理脚本
│   └── generate-config.sh    # 配置生成脚本
├── docs/                     # 文档
│   ├── DEPLOYMENT_GUIDE.md   # 部署指南
│   ├── BEST_PRACTICES.md     # 最佳实践
│   └── TROUBLESHOOTING.md    # 故障排查
└── README.md                 # 本文件
```

## 🚀 快速开始

### 1. 复制模板到你的项目

```bash
# 复制整个k8s-sample目录到你的项目
cp -r k8s-sample your-project/

# 或者只复制模板文件
cp -r k8s-sample/templates your-project/k8s/
```

### 2. 生成配置文件

```bash
cd your-project/k8s-sample

# 交互式生成配置
./scripts/generate-config.sh --interactive

# 或者快速生成
./scripts/generate-config.sh \
  --app-name my-app \
  --namespace my-namespace \
  --image my-registry/my-app \
  --tag v1.0.0 \
  --domain app.example.com
```

### 3. 部署应用

```bash
# 部署到开发环境
./scripts/deploy.sh development deploy

# 部署到生产环境
./scripts/deploy.sh production deploy
```

### 4. 验证部署

```bash
# 查看应用状态
./scripts/deploy.sh production status

# 查看应用日志
./scripts/deploy.sh production logs
```

## 📋 模板特性

### 🏗️ 完整的资源模板

- **Namespace**: 命名空间隔离，支持资源配额和限制
- **ConfigMap**: 应用配置、环境变量、配置文件
- **Secret**: 密钥管理，支持多种类型（Opaque、TLS、Docker Registry等）
- **Deployment**: 部署配置，包含最佳实践设置
- **Service**: 服务配置，支持ClusterIP、NodePort、LoadBalancer
- **Ingress**: 入口配置，支持TLS、多域名、路径路由

### 🔧 高级功能

- **自动扩缩容**: HorizontalPodAutoscaler配置
- **中断预算**: PodDisruptionBudget确保服务可用性
- **健康检查**: 完整的存活、就绪、启动探针配置
- **安全配置**: SecurityContext、RBAC、NetworkPolicy
- **监控集成**: ServiceMonitor、Prometheus指标
- **存储管理**: PVC、StorageClass配置

### 🛡️ 安全最佳实践

- 非root用户运行
- 只读根文件系统
- 最小权限原则
- 网络策略隔离
- 密钥管理
- 镜像安全扫描

## 🔧 配置说明

### 必需配置项

每个模板都使用`{{PLACEHOLDER}}`格式的占位符，需要替换为实际值：

| 占位符 | 描述 | 示例 |
|--------|------|------|
| `{{APP_NAME}}` | 应用名称 | `my-web-app` |
| `{{NAMESPACE_NAME}}` | 命名空间 | `my-namespace` |
| `{{IMAGE_NAME}}` | 镜像名称 | `my-registry/app` |
| `{{IMAGE_TAG}}` | 镜像标签 | `v1.0.0` |
| `{{DOMAIN_NAME}}` | 域名 | `app.example.com` |

### 环境特定配置

支持多环境部署，每个环境有独立的配置文件：

- `config/development.env` - 开发环境
- `config/staging.env` - 测试环境  
- `config/production.env` - 生产环境

## 📖 使用指南

### 1. 新项目部署

```bash
# 1. 生成配置
./scripts/generate-config.sh --interactive

# 2. 检查生成的配置文件
ls config/
ls k8s/

# 3. 根据需要调整配置
vim config/production.env

# 4. 部署应用
./scripts/deploy.sh production deploy
```

### 2. 现有项目迁移

```bash
# 1. 复制模板到现有项目
cp -r k8s-sample/templates existing-project/k8s/

# 2. 手动替换占位符或使用脚本
sed -i 's/{{APP_NAME}}/my-existing-app/g' existing-project/k8s/*.yaml

# 3. 应用配置
kubectl apply -f existing-project/k8s/
```

### 3. 多环境管理

```bash
# 开发环境
./scripts/deploy.sh development deploy

# 测试环境
./scripts/deploy.sh staging deploy

# 生产环境
./scripts/deploy.sh production deploy
```

## 🛠️ 脚本工具

### deploy.sh - 部署脚本

```bash
# 基本用法
./scripts/deploy.sh [环境] [操作]

# 支持的操作
deploy    # 部署应用
delete    # 删除应用
status    # 查看状态
logs      # 查看日志

# 选项
-n, --namespace NAME    # 指定命名空间
-d, --dry-run          # 干运行模式
--skip-build           # 跳过镜像构建
--skip-push            # 跳过镜像推送
```

### cleanup.sh - 清理脚本

```bash
# 基本用法
./scripts/cleanup.sh [选项] [命名空间]

# 选项
-f, --force            # 强制删除
-a, --all              # 删除所有资源
-d, --dry-run          # 干运行模式
-p, --delete-pvc       # 删除持久卷
-s, --delete-secrets   # 删除密钥
```

### generate-config.sh - 配置生成脚本

```bash
# 交互式生成
./scripts/generate-config.sh --interactive

# 命令行生成
./scripts/generate-config.sh \
  --app-name my-app \
  --namespace my-namespace \
  --image my-registry/my-app \
  --tag v1.0.0
```

## 📚 文档资源

- **[部署指南](docs/DEPLOYMENT_GUIDE.md)** - 详细的部署步骤和配置说明
- **[最佳实践](docs/BEST_PRACTICES.md)** - Kubernetes部署最佳实践
- **[故障排查](docs/TROUBLESHOOTING.md)** - 常见问题诊断和解决方案

## 🎯 适用场景

### Web应用

- 前端应用（React、Vue、Angular）
- 后端API（Node.js、Python、Go、Java）
- 全栈应用

### 微服务

- API网关
- 业务服务
- 数据服务
- 消息队列

### 数据应用

- 数据库（PostgreSQL、MySQL、MongoDB）
- 缓存（Redis、Memcached）
- 搜索引擎（Elasticsearch）

## 🔄 版本管理

### 语义化版本

```bash
# 主版本.次版本.修订版本
v1.0.0    # 初始版本
v1.1.0    # 新功能
v1.1.1    # 修复bug
v2.0.0    # 重大更新
```

### 镜像标签策略

```bash
# 生产环境使用具体版本
my-app:v1.2.3

# 测试环境使用预发布版本
my-app:v1.2.3-rc.1

# 开发环境可以使用latest（谨慎）
my-app:latest
```

## 🤝 贡献指南

### 提交模板改进

1. Fork本项目
2. 创建特性分支：`git checkout -b feature/new-template`
3. 提交更改：`git commit -am 'Add new template'`
4. 推送分支：`git push origin feature/new-template`
5. 创建Pull Request

### 报告问题

- 使用GitHub Issues报告bug
- 提供详细的复现步骤
- 包含相关的配置文件和日志

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 🙏 致谢

感谢以下项目和社区的启发：

- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [Helm Charts](https://helm.sh/)
- [Kustomize](https://kustomize.io/)
- [CNCF项目](https://www.cncf.io/)

## 📞 支持

- **文档**: 查看[docs/](docs/)目录下的详细文档
- **Issues**: [GitHub Issues](https://github.com/your-org/k8s-sample/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-org/k8s-sample/discussions)

---

**开始使用K8s-Sample，让Kubernetes部署变得简单可靠！** 🚀
