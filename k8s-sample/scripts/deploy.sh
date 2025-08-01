#!/bin/bash

# Kubernetes部署脚本模板
# 用法：./deploy.sh [环境] [操作]
# 示例：./deploy.sh production deploy

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$PROJECT_ROOT/templates"
CONFIG_DIR="$PROJECT_ROOT/config"

# 默认配置
DEFAULT_ENVIRONMENT="development"
DEFAULT_ACTION="deploy"
DEFAULT_NAMESPACE="default"

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
Kubernetes部署脚本

用法:
    $0 [选项] [环境] [操作]

参数:
    环境        部署环境 (development|staging|production)
    操作        执行操作 (deploy|delete|status|logs)

选项:
    -h, --help              显示帮助信息
    -n, --namespace NAME    指定命名空间
    -c, --config FILE       指定配置文件
    -d, --dry-run          干运行模式
    -v, --verbose          详细输出
    --skip-build           跳过镜像构建
    --skip-push            跳过镜像推送

示例:
    $0 production deploy                    # 部署到生产环境
    $0 staging delete                       # 删除staging环境
    $0 development status                   # 查看开发环境状态
    $0 -n my-app production deploy          # 部署到指定命名空间
    $0 --dry-run production deploy          # 干运行模式

环境配置文件:
    config/development.env                  # 开发环境配置
    config/staging.env                      # 测试环境配置
    config/production.env                   # 生产环境配置
EOF
}

# 检查依赖
check_dependencies() {
    local deps=("kubectl" "docker")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "依赖 '$dep' 未安装"
            exit 1
        fi
    done
    
    # 检查kubectl连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 加载配置
load_config() {
    local environment="$1"
    local config_file="$CONFIG_DIR/$environment.env"
    
    if [[ ! -f "$config_file" ]]; then
        log_error "配置文件不存在: $config_file"
        exit 1
    fi
    
    log_info "加载配置文件: $config_file"
    
    # 导出环境变量
    set -a
    source "$config_file"
    set +a
    
    # 验证必需的环境变量
    local required_vars=("APP_NAME" "NAMESPACE_NAME" "IMAGE_NAME" "IMAGE_TAG")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "必需的环境变量未设置: $var"
            exit 1
        fi
    done
    
    log_success "配置加载完成"
}

# 替换模板变量
process_templates() {
    local temp_dir="$1"
    
    log_info "处理模板文件..."
    
    # 复制模板到临时目录
    cp -r "$TEMPLATES_DIR"/* "$temp_dir/"
    
    # 获取所有环境变量
    local env_vars
    env_vars=$(env | grep -E '^[A-Z_]+=' | cut -d= -f1)
    
    # 替换模板中的变量
    for file in "$temp_dir"/*.yaml; do
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
    
    log_success "模板处理完成"
}

# 构建Docker镜像
build_image() {
    if [[ "${SKIP_BUILD:-false}" == "true" ]]; then
        log_info "跳过镜像构建"
        return
    fi
    
    log_info "构建Docker镜像: $IMAGE_NAME:$IMAGE_TAG"
    
    if [[ -f "$PROJECT_ROOT/Dockerfile" ]]; then
        docker build -t "$IMAGE_NAME:$IMAGE_TAG" "$PROJECT_ROOT"
        log_success "镜像构建完成"
    else
        log_warning "Dockerfile不存在，跳过镜像构建"
    fi
}

# 推送Docker镜像
push_image() {
    if [[ "${SKIP_PUSH:-false}" == "true" ]]; then
        log_info "跳过镜像推送"
        return
    fi
    
    log_info "推送Docker镜像: $IMAGE_NAME:$IMAGE_TAG"
    
    docker push "$IMAGE_NAME:$IMAGE_TAG"
    log_success "镜像推送完成"
}

# 部署应用
deploy_app() {
    local temp_dir="$1"
    
    log_info "开始部署应用到命名空间: $NAMESPACE_NAME"
    
    # 创建命名空间（如果不存在）
    if ! kubectl get namespace "$NAMESPACE_NAME" &> /dev/null; then
        log_info "创建命名空间: $NAMESPACE_NAME"
        kubectl apply -f "$temp_dir/namespace.yaml"
    fi
    
    # 按顺序部署资源
    local resources=("configmap" "secret" "deployment" "service" "ingress")
    
    for resource in "${resources[@]}"; do
        local file="$temp_dir/$resource.yaml"
        if [[ -f "$file" ]]; then
            log_info "部署 $resource..."
            
            if [[ "${DRY_RUN:-false}" == "true" ]]; then
                kubectl apply -f "$file" --dry-run=client
            else
                kubectl apply -f "$file"
            fi
        fi
    done
    
    if [[ "${DRY_RUN:-false}" != "true" ]]; then
        # 等待部署完成
        log_info "等待部署完成..."
        kubectl rollout status deployment/"$APP_NAME" -n "$NAMESPACE_NAME" --timeout=300s
        
        log_success "应用部署完成"
        
        # 显示部署信息
        show_deployment_info
    else
        log_info "干运行模式，未实际部署"
    fi
}

# 删除应用
delete_app() {
    log_info "删除应用: $APP_NAME (命名空间: $NAMESPACE_NAME)"
    
    # 确认删除
    read -p "确认删除应用? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "取消删除操作"
        return
    fi
    
    # 删除资源
    local resources=("ingress" "service" "deployment" "secret" "configmap")
    
    for resource in "${resources[@]}"; do
        log_info "删除 $resource..."
        kubectl delete "$resource" -l app="$APP_NAME" -n "$NAMESPACE_NAME" --ignore-not-found=true
    done
    
    # 询问是否删除命名空间
    read -p "是否删除命名空间 $NAMESPACE_NAME? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE_NAME" --ignore-not-found=true
        log_success "命名空间已删除"
    fi
    
    log_success "应用删除完成"
}

# 显示应用状态
show_status() {
    log_info "应用状态: $APP_NAME (命名空间: $NAMESPACE_NAME)"
    
    echo
    echo "=== Pods ==="
    kubectl get pods -l app="$APP_NAME" -n "$NAMESPACE_NAME" -o wide
    
    echo
    echo "=== Services ==="
    kubectl get services -l app="$APP_NAME" -n "$NAMESPACE_NAME"
    
    echo
    echo "=== Ingress ==="
    kubectl get ingress -l app="$APP_NAME" -n "$NAMESPACE_NAME"
    
    echo
    echo "=== Events ==="
    kubectl get events -n "$NAMESPACE_NAME" --sort-by='.lastTimestamp' | tail -10
}

# 显示应用日志
show_logs() {
    log_info "应用日志: $APP_NAME (命名空间: $NAMESPACE_NAME)"
    
    kubectl logs -l app="$APP_NAME" -n "$NAMESPACE_NAME" --tail=100 -f
}

# 显示部署信息
show_deployment_info() {
    echo
    log_success "=== 部署信息 ==="
    echo "应用名称: $APP_NAME"
    echo "命名空间: $NAMESPACE_NAME"
    echo "镜像: $IMAGE_NAME:$IMAGE_TAG"
    echo "环境: ${ENVIRONMENT:-unknown}"
    
    echo
    echo "=== 访问信息 ==="
    
    # 获取服务信息
    local service_info
    service_info=$(kubectl get service "$APP_NAME" -n "$NAMESPACE_NAME" -o jsonpath='{.spec.type}:{.spec.ports[0].port}:{.spec.ports[0].nodePort}' 2>/dev/null || echo "")
    
    if [[ -n "$service_info" ]]; then
        IFS=':' read -r service_type service_port node_port <<< "$service_info"
        
        case "$service_type" in
            "ClusterIP")
                echo "集群内访问: http://$APP_NAME.$NAMESPACE_NAME.svc.cluster.local:$service_port"
                ;;
            "NodePort")
                echo "NodePort访问: http://<NODE-IP>:$node_port"
                ;;
            "LoadBalancer")
                local external_ip
                external_ip=$(kubectl get service "$APP_NAME" -n "$NAMESPACE_NAME" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
                echo "LoadBalancer访问: http://$external_ip:$service_port"
                ;;
        esac
    fi
    
    # 获取Ingress信息
    local ingress_host
    ingress_host=$(kubectl get ingress -l app="$APP_NAME" -n "$NAMESPACE_NAME" -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "")
    
    if [[ -n "$ingress_host" ]]; then
        echo "Ingress访问: http://$ingress_host"
    fi
    
    echo
    echo "=== 有用的命令 ==="
    echo "查看状态: $0 $ENVIRONMENT status"
    echo "查看日志: $0 $ENVIRONMENT logs"
    echo "端口转发: kubectl port-forward service/$APP_NAME 8080:$service_port -n $NAMESPACE_NAME"
}

# 主函数
main() {
    local environment="$DEFAULT_ENVIRONMENT"
    local action="$DEFAULT_ACTION"
    local namespace=""
    local config_file=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -n|--namespace)
                namespace="$2"
                shift 2
                ;;
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            -d|--dry-run)
                export DRY_RUN="true"
                shift
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            --skip-build)
                export SKIP_BUILD="true"
                shift
                ;;
            --skip-push)
                export SKIP_PUSH="true"
                shift
                ;;
            development|staging|production)
                environment="$1"
                shift
                ;;
            deploy|delete|status|logs)
                action="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查依赖
    check_dependencies
    
    # 加载配置
    if [[ -n "$config_file" ]]; then
        source "$config_file"
    else
        load_config "$environment"
    fi
    
    # 设置命名空间
    if [[ -n "$namespace" ]]; then
        export NAMESPACE_NAME="$namespace"
    fi
    
    # 设置环境变量
    export ENVIRONMENT="$environment"
    
    log_info "执行操作: $action (环境: $environment, 命名空间: $NAMESPACE_NAME)"
    
    case "$action" in
        deploy)
            # 创建临时目录
            local temp_dir
            temp_dir=$(mktemp -d)
            trap "rm -rf $temp_dir" EXIT
            
            # 处理模板
            process_templates "$temp_dir"
            
            # 构建和推送镜像
            build_image
            push_image
            
            # 部署应用
            deploy_app "$temp_dir"
            ;;
        delete)
            delete_app
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        *)
            log_error "未知操作: $action"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
