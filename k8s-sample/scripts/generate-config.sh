#!/bin/bash

# Kubernetes配置生成脚本模板
# 用法：./generate-config.sh [选项]

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config"
TEMPLATES_DIR="$PROJECT_ROOT/templates"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
Kubernetes配置生成脚本

用法:
    $0 [选项]

选项:
    -h, --help              显示帮助信息
    -e, --environment ENV   指定环境 (development|staging|production)
    -a, --app-name NAME     应用名称
    -n, --namespace NAME    命名空间名称
    -i, --image IMAGE       Docker镜像名称
    -t, --tag TAG           镜像标签
    -d, --domain DOMAIN     域名
    -o, --output DIR        输出目录
    --interactive           交互式配置
    --force                 覆盖已存在的配置文件

示例:
    $0 --interactive                           # 交互式生成配置
    $0 -e production -a my-app -n my-namespace # 快速生成生产环境配置
    $0 -a web-app -i my-registry/web-app -t v1.0.0 # 指定应用和镜像信息

生成的文件:
    config/development.env                     # 开发环境配置
    config/staging.env                         # 测试环境配置
    config/production.env                      # 生产环境配置
    k8s/                                      # 处理后的K8s配置文件
EOF
}

# 创建目录
create_directories() {
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$PROJECT_ROOT/k8s"
    log_success "目录创建完成"
}

# 生成随机密钥
generate_secret() {
    openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 32
}

# Base64编码
base64_encode() {
    echo -n "$1" | base64 | tr -d '\n'
}

# 交互式配置
interactive_config() {
    log_info "开始交互式配置..."
    
    # 基础信息
    read -p "应用名称 [my-app]: " APP_NAME
    APP_NAME=${APP_NAME:-my-app}
    
    read -p "命名空间 [$APP_NAME]: " NAMESPACE_NAME
    NAMESPACE_NAME=${NAMESPACE_NAME:-$APP_NAME}
    
    read -p "应用版本 [1.0.0]: " VERSION
    VERSION=${VERSION:-1.0.0}
    
    read -p "Docker镜像名称 [my-registry/$APP_NAME]: " IMAGE_NAME
    IMAGE_NAME=${IMAGE_NAME:-my-registry/$APP_NAME}
    
    read -p "镜像标签 [latest]: " IMAGE_TAG
    IMAGE_TAG=${IMAGE_TAG:-latest}
    
    read -p "容器端口 [8080]: " CONTAINER_PORT
    CONTAINER_PORT=${CONTAINER_PORT:-8080}
    
    read -p "服务端口 [80]: " SERVICE_PORT
    SERVICE_PORT=${SERVICE_PORT:-80}
    
    read -p "副本数量 [2]: " REPLICAS
    REPLICAS=${REPLICAS:-2}
    
    read -p "域名 [app.example.com]: " DOMAIN_NAME
    DOMAIN_NAME=${DOMAIN_NAME:-app.example.com}
    
    # 资源配置
    read -p "内存请求 [512Mi]: " MEMORY_REQUEST
    MEMORY_REQUEST=${MEMORY_REQUEST:-512Mi}
    
    read -p "内存限制 [2Gi]: " MEMORY_LIMIT
    MEMORY_LIMIT=${MEMORY_LIMIT:-2Gi}
    
    read -p "CPU请求 [250m]: " CPU_REQUEST
    CPU_REQUEST=${CPU_REQUEST:-250m}
    
    read -p "CPU限制 [1000m]: " CPU_LIMIT
    CPU_LIMIT=${CPU_LIMIT:-1000m}
    
    # 数据库配置（可选）
    read -p "是否需要数据库配置? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "数据库主机 [postgres]: " DB_HOST
        DB_HOST=${DB_HOST:-postgres}
        
        read -p "数据库端口 [5432]: " DB_PORT
        DB_PORT=${DB_PORT:-5432}
        
        read -p "数据库名称 [$APP_NAME]: " DB_NAME
        DB_NAME=${DB_NAME:-$APP_NAME}
        
        read -p "数据库用户名 [$APP_NAME]: " DB_USERNAME
        DB_USERNAME=${DB_USERNAME:-$APP_NAME}
        
        read -s -p "数据库密码: " DB_PASSWORD
        echo
        
        USE_DATABASE=true
    else
        USE_DATABASE=false
    fi
    
    # Redis配置（可选）
    read -p "是否需要Redis配置? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Redis主机 [redis]: " REDIS_HOST
        REDIS_HOST=${REDIS_HOST:-redis}
        
        read -p "Redis端口 [6379]: " REDIS_PORT
        REDIS_PORT=${REDIS_PORT:-6379}
        
        read -p "Redis数据库 [0]: " REDIS_DB
        REDIS_DB=${REDIS_DB:-0}
        
        USE_REDIS=true
    else
        USE_REDIS=false
    fi
    
    log_success "交互式配置完成"
}

# 生成环境配置文件
generate_env_config() {
    local environment="$1"
    local config_file="$CONFIG_DIR/$environment.env"
    
    log_info "生成 $environment 环境配置: $config_file"
    
    # 根据环境调整配置
    local env_replicas="$REPLICAS"
    local env_debug="false"
    local env_log_level="INFO"
    
    case "$environment" in
        development)
            env_replicas=1
            env_debug="true"
            env_log_level="DEBUG"
            ;;
        staging)
            env_replicas=2
            env_debug="false"
            env_log_level="INFO"
            ;;
        production)
            env_replicas=3
            env_debug="false"
            env_log_level="WARNING"
            ;;
    esac
    
    # 生成密钥
    local secret_key
    secret_key=$(generate_secret)
    local jwt_secret
    jwt_secret=$(generate_secret)
    
    cat > "$config_file" << EOF
# $environment 环境配置
# 生成时间: $(date)

# 基础配置
APP_NAME=$APP_NAME
NAMESPACE_NAME=$NAMESPACE_NAME
VERSION=$VERSION
ENVIRONMENT=$environment
COMPONENT_NAME=web-service

# 镜像配置
IMAGE_NAME=$IMAGE_NAME
IMAGE_TAG=$IMAGE_TAG
IMAGE_PULL_POLICY=IfNotPresent

# 容器配置
CONTAINER_NAME=$APP_NAME
CONTAINER_PORT=$CONTAINER_PORT
SERVICE_PORT=$SERVICE_PORT
TARGET_PORT=$CONTAINER_PORT

# 部署配置
REPLICAS=$env_replicas
RESTART_TIMESTAMP=$(date +%s)

# 应用配置
HOST=0.0.0.0
PORT=$CONTAINER_PORT
DEBUG=$env_debug
LOG_LEVEL=$env_log_level
LOG_FORMAT=json

# 资源配置
MEMORY_REQUEST=$MEMORY_REQUEST
MEMORY_LIMIT=$MEMORY_LIMIT
CPU_REQUEST=$CPU_REQUEST
CPU_LIMIT=$CPU_LIMIT

# 健康检查配置
HEALTH_CHECK_PATH=/health
READINESS_CHECK_PATH=/ready
STARTUP_CHECK_PATH=/health
LIVENESS_INITIAL_DELAY=30
LIVENESS_PERIOD=30
LIVENESS_TIMEOUT=10
LIVENESS_FAILURE_THRESHOLD=3
READINESS_INITIAL_DELAY=10
READINESS_PERIOD=10
READINESS_TIMEOUT=5
READINESS_FAILURE_THRESHOLD=3
STARTUP_INITIAL_DELAY=10
STARTUP_PERIOD=10
STARTUP_TIMEOUT=5
STARTUP_FAILURE_THRESHOLD=30

# 网络配置
SERVICE_NAME=$APP_NAME
INGRESS_NAME=$APP_NAME-ingress
DOMAIN_NAME=$DOMAIN_NAME
INGRESS_CLASS=nginx

# 安全配置
RUN_AS_USER=1000
RUN_AS_GROUP=1000
FS_GROUP=1000
POD_RUN_AS_USER=1000
POD_RUN_AS_GROUP=1000
READ_ONLY_ROOT_FS=false

# 密钥配置（Base64编码）
SECRET_KEY_BASE64=$(base64_encode "$secret_key")
JWT_SECRET_BASE64=$(base64_encode "$jwt_secret")

# 其他配置
TIMEZONE=Asia/Shanghai
LANGUAGE=en_US.UTF-8
TERMINATION_GRACE_PERIOD=30
EOF

    # 添加数据库配置
    if [[ "${USE_DATABASE:-false}" == "true" ]]; then
        cat >> "$config_file" << EOF

# 数据库配置
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USERNAME_BASE64=$(base64_encode "$DB_USERNAME")
DB_PASSWORD_BASE64=$(base64_encode "$DB_PASSWORD")
DATABASE_URL_BASE64=$(base64_encode "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME")
EOF
    fi
    
    # 添加Redis配置
    if [[ "${USE_REDIS:-false}" == "true" ]]; then
        cat >> "$config_file" << EOF

# Redis配置
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
REDIS_DB=$REDIS_DB
REDIS_URL_BASE64=$(base64_encode "redis://$REDIS_HOST:$REDIS_PORT/$REDIS_DB")
EOF
    fi
    
    log_success "配置文件生成完成: $config_file"
}

# 生成K8s配置文件
generate_k8s_configs() {
    local environment="$1"
    local output_dir="$PROJECT_ROOT/k8s"
    
    log_info "生成K8s配置文件到: $output_dir"
    
    # 加载环境配置
    source "$CONFIG_DIR/$environment.env"
    
    # 复制模板文件
    cp -r "$TEMPLATES_DIR"/* "$output_dir/"
    
    # 获取所有环境变量
    local env_vars
    env_vars=$(env | grep -E '^[A-Z_]+=' | cut -d= -f1)
    
    # 替换模板中的变量
    for file in "$output_dir"/*.yaml; do
        if [[ -f "$file" ]]; then
            log_info "处理文件: $(basename "$file")"
            
            # 替换环境变量
            for var in $env_vars; do
                local value="${!var}"
                # 转义特殊字符
                value=$(printf '%s\n' "$value" | sed 's/[[\.*^$()+?{|]/\\&/g')
                sed -i "s/{{$var}}/$value/g" "$file"
            done
            
            # 检查是否还有未替换的变量
            if grep -q "{{.*}}" "$file"; then
                log_warning "文件 $(basename "$file") 中存在未替换的变量:"
                grep -o "{{[^}]*}}" "$file" | sort -u
            fi
        fi
    done
    
    log_success "K8s配置文件生成完成"
}

# 生成README文件
generate_readme() {
    local readme_file="$PROJECT_ROOT/README.md"
    
    log_info "生成README文件: $readme_file"
    
    cat > "$readme_file" << EOF
# $APP_NAME

## 项目描述

这是一个基于Kubernetes的应用部署项目。

## 目录结构

\`\`\`
.
├── config/                 # 环境配置文件
│   ├── development.env     # 开发环境配置
│   ├── staging.env         # 测试环境配置
│   └── production.env      # 生产环境配置
├── k8s/                    # Kubernetes配置文件
│   ├── namespace.yaml      # 命名空间
│   ├── configmap.yaml      # 配置映射
│   ├── secret.yaml         # 密钥
│   ├── deployment.yaml     # 部署
│   ├── service.yaml        # 服务
│   └── ingress.yaml        # 入口
├── scripts/                # 部署脚本
│   ├── deploy.sh          # 部署脚本
│   ├── cleanup.sh         # 清理脚本
│   └── generate-config.sh # 配置生成脚本
└── README.md              # 本文件
\`\`\`

## 快速开始

### 1. 部署到开发环境

\`\`\`bash
./scripts/deploy.sh development deploy
\`\`\`

### 2. 部署到生产环境

\`\`\`bash
./scripts/deploy.sh production deploy
\`\`\`

### 3. 查看应用状态

\`\`\`bash
./scripts/deploy.sh production status
\`\`\`

### 4. 查看应用日志

\`\`\`bash
./scripts/deploy.sh production logs
\`\`\`

### 5. 清理资源

\`\`\`bash
./scripts/cleanup.sh $NAMESPACE_NAME
\`\`\`

## 配置说明

### 环境变量

主要的环境变量配置在 \`config/\` 目录下的 \`.env\` 文件中：

- \`APP_NAME\`: 应用名称
- \`NAMESPACE_NAME\`: Kubernetes命名空间
- \`IMAGE_NAME\`: Docker镜像名称
- \`IMAGE_TAG\`: 镜像标签
- \`REPLICAS\`: 副本数量

### 访问方式

- **开发环境**: http://$DOMAIN_NAME
- **集群内访问**: http://$APP_NAME.$NAMESPACE_NAME.svc.cluster.local

## 监控和日志

### 健康检查

应用提供以下健康检查端点：

- \`/health\`: 健康检查
- \`/ready\`: 就绪检查

### 日志查看

\`\`\`bash
# 查看实时日志
kubectl logs -f deployment/$APP_NAME -n $NAMESPACE_NAME

# 查看所有Pod日志
kubectl logs -l app=$APP_NAME -n $NAMESPACE_NAME
\`\`\`

## 故障排查

### 常见问题

1. **Pod无法启动**
   \`\`\`bash
   kubectl describe pod <pod-name> -n $NAMESPACE_NAME
   \`\`\`

2. **服务无法访问**
   \`\`\`bash
   kubectl get svc,ep -n $NAMESPACE_NAME
   \`\`\`

3. **镜像拉取失败**
   检查镜像名称和标签是否正确，确保有权限访问镜像仓库。

## 开发指南

### 本地开发

1. 修改代码
2. 构建镜像：\`docker build -t $IMAGE_NAME:$IMAGE_TAG .\`
3. 推送镜像：\`docker push $IMAGE_NAME:$IMAGE_TAG\`
4. 部署更新：\`./scripts/deploy.sh development deploy\`

### 生产部署

1. 确保代码已合并到主分支
2. 创建发布标签
3. 构建生产镜像
4. 部署到生产环境

## 许可证

[添加许可证信息]

## 联系方式

[添加联系方式]
EOF
    
    log_success "README文件生成完成"
}

# 设置脚本权限
set_script_permissions() {
    chmod +x "$PROJECT_ROOT/scripts"/*.sh
    log_success "脚本权限设置完成"
}

# 主函数
main() {
    local environment=""
    local app_name=""
    local namespace=""
    local image_name=""
    local image_tag=""
    local domain=""
    local output_dir=""
    local interactive=false
    local force=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--environment)
                environment="$2"
                shift 2
                ;;
            -a|--app-name)
                app_name="$2"
                shift 2
                ;;
            -n|--namespace)
                namespace="$2"
                shift 2
                ;;
            -i|--image)
                image_name="$2"
                shift 2
                ;;
            -t|--tag)
                image_tag="$2"
                shift 2
                ;;
            -d|--domain)
                domain="$2"
                shift 2
                ;;
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            --interactive)
                interactive=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 创建目录
    create_directories
    
    # 交互式配置或使用命令行参数
    if [[ "$interactive" == "true" ]]; then
        interactive_config
    else
        # 设置默认值
        APP_NAME=${app_name:-my-app}
        NAMESPACE_NAME=${namespace:-$APP_NAME}
        VERSION=${VERSION:-1.0.0}
        IMAGE_NAME=${image_name:-my-registry/$APP_NAME}
        IMAGE_TAG=${image_tag:-latest}
        CONTAINER_PORT=${CONTAINER_PORT:-8080}
        SERVICE_PORT=${SERVICE_PORT:-80}
        REPLICAS=${REPLICAS:-2}
        DOMAIN_NAME=${domain:-app.example.com}
        MEMORY_REQUEST=${MEMORY_REQUEST:-512Mi}
        MEMORY_LIMIT=${MEMORY_LIMIT:-2Gi}
        CPU_REQUEST=${CPU_REQUEST:-250m}
        CPU_LIMIT=${CPU_LIMIT:-1000m}
        USE_DATABASE=${USE_DATABASE:-false}
        USE_REDIS=${USE_REDIS:-false}
    fi
    
    # 生成配置文件
    local environments=("development" "staging" "production")
    
    if [[ -n "$environment" ]]; then
        environments=("$environment")
    fi
    
    for env in "${environments[@]}"; do
        local config_file="$CONFIG_DIR/$env.env"
        
        if [[ -f "$config_file" && "$force" != "true" ]]; then
            log_warning "配置文件已存在: $config_file"
            read -p "是否覆盖? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                continue
            fi
        fi
        
        generate_env_config "$env"
    done
    
    # 生成K8s配置文件
    local target_env=${environment:-development}
    generate_k8s_configs "$target_env"
    
    # 生成README文件
    generate_readme
    
    # 设置脚本权限
    set_script_permissions
    
    log_success "配置生成完成！"
    
    echo
    echo "=== 下一步操作 ==="
    echo "1. 检查生成的配置文件: config/"
    echo "2. 根据需要修改配置"
    echo "3. 部署应用: ./scripts/deploy.sh $target_env deploy"
    echo "4. 查看状态: ./scripts/deploy.sh $target_env status"
}

# 执行主函数
main "$@"
