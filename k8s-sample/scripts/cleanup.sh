#!/bin/bash

# Kubernetes资源清理脚本模板
# 用法：./cleanup.sh [选项] [命名空间]

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 默认配置
DEFAULT_NAMESPACE=""
FORCE_DELETE=false
DELETE_NAMESPACE=false
DELETE_PVC=false
DELETE_SECRETS=false
DRY_RUN=false

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
Kubernetes资源清理脚本

用法:
    $0 [选项] [命名空间]

选项:
    -h, --help              显示帮助信息
    -f, --force             强制删除，不询问确认
    -n, --delete-namespace  删除命名空间
    -p, --delete-pvc        删除持久卷声明
    -s, --delete-secrets    删除密钥
    -d, --dry-run          干运行模式，只显示将要删除的资源
    -a, --all              删除所有资源（包括命名空间、PVC、密钥）
    -l, --label LABEL      按标签选择资源
    --timeout SECONDS      设置删除超时时间（默认：300秒）

参数:
    命名空间               要清理的命名空间名称

示例:
    $0 my-app-namespace                    # 清理指定命名空间的基础资源
    $0 -f my-app-namespace                 # 强制清理，不询问确认
    $0 -a my-app-namespace                 # 清理所有资源包括命名空间
    $0 -d my-app-namespace                 # 干运行模式，查看将要删除的资源
    $0 -l app=my-app my-namespace          # 按标签清理资源
    $0 --delete-pvc my-namespace           # 清理资源并删除PVC

注意:
    - 删除操作不可逆，请谨慎使用
    - 建议先使用 --dry-run 查看将要删除的资源
    - 生产环境请务必备份重要数据
EOF
}

# 检查依赖
check_dependencies() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安装"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 确认操作
confirm_action() {
    local message="$1"
    
    if [[ "$FORCE_DELETE" == "true" ]]; then
        log_warning "强制模式：$message"
        return 0
    fi
    
    echo -e "${YELLOW}$message${NC}"
    read -p "确认继续? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        return 1
    fi
    
    return 0
}

# 列出资源
list_resources() {
    local namespace="$1"
    local label_selector="$2"
    
    log_info "扫描命名空间 '$namespace' 中的资源..."
    
    if [[ ! -z "$label_selector" ]]; then
        log_info "使用标签选择器: $label_selector"
    fi
    
    local kubectl_opts="-n $namespace"
    if [[ ! -z "$label_selector" ]]; then
        kubectl_opts="$kubectl_opts -l $label_selector"
    fi
    
    echo
    echo "=== Deployments ==="
    kubectl get deployments $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    
    echo
    echo "=== StatefulSets ==="
    kubectl get statefulsets $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    
    echo
    echo "=== DaemonSets ==="
    kubectl get daemonsets $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    
    echo
    echo "=== Services ==="
    kubectl get services $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    
    echo
    echo "=== Ingress ==="
    kubectl get ingress $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    
    echo
    echo "=== ConfigMaps ==="
    kubectl get configmaps $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    
    if [[ "$DELETE_SECRETS" == "true" ]]; then
        echo
        echo "=== Secrets ==="
        kubectl get secrets $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    fi
    
    if [[ "$DELETE_PVC" == "true" ]]; then
        echo
        echo "=== PersistentVolumeClaims ==="
        kubectl get pvc $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
    fi
    
    echo
    echo "=== Pods ==="
    kubectl get pods $kubectl_opts --no-headers 2>/dev/null | awk '{print $1}' || echo "无"
}

# 删除工作负载
delete_workloads() {
    local namespace="$1"
    local label_selector="$2"
    local timeout="$3"
    
    log_info "删除工作负载..."
    
    local kubectl_opts="-n $namespace --timeout=${timeout}s"
    if [[ ! -z "$label_selector" ]]; then
        kubectl_opts="$kubectl_opts -l $label_selector"
    fi
    
    # 删除Deployments
    local deployments
    deployments=$(kubectl get deployments -n "$namespace" ${label_selector:+-l "$label_selector"} --no-headers 2>/dev/null | awk '{print $1}' || true)
    if [[ ! -z "$deployments" ]]; then
        log_info "删除 Deployments: $deployments"
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "kubectl delete deployments $kubectl_opts"
        else
            kubectl delete deployments $kubectl_opts --ignore-not-found=true
        fi
    fi
    
    # 删除StatefulSets
    local statefulsets
    statefulsets=$(kubectl get statefulsets -n "$namespace" ${label_selector:+-l "$label_selector"} --no-headers 2>/dev/null | awk '{print $1}' || true)
    if [[ ! -z "$statefulsets" ]]; then
        log_info "删除 StatefulSets: $statefulsets"
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "kubectl delete statefulsets $kubectl_opts"
        else
            kubectl delete statefulsets $kubectl_opts --ignore-not-found=true
        fi
    fi
    
    # 删除DaemonSets
    local daemonsets
    daemonsets=$(kubectl get daemonsets -n "$namespace" ${label_selector:+-l "$label_selector"} --no-headers 2>/dev/null | awk '{print $1}' || true)
    if [[ ! -z "$daemonsets" ]]; then
        log_info "删除 DaemonSets: $daemonsets"
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "kubectl delete daemonsets $kubectl_opts"
        else
            kubectl delete daemonsets $kubectl_opts --ignore-not-found=true
        fi
    fi
    
    # 等待Pods终止
    if [[ "$DRY_RUN" != "true" ]]; then
        log_info "等待Pods终止..."
        local max_wait=60
        local wait_count=0
        
        while [[ $wait_count -lt $max_wait ]]; do
            local running_pods
            running_pods=$(kubectl get pods -n "$namespace" ${label_selector:+-l "$label_selector"} --no-headers 2>/dev/null | wc -l || echo "0")
            
            if [[ "$running_pods" -eq 0 ]]; then
                log_success "所有Pods已终止"
                break
            fi
            
            log_info "等待 $running_pods 个Pods终止... ($wait_count/$max_wait)"
            sleep 5
            ((wait_count+=5))
        done
        
        if [[ $wait_count -ge $max_wait ]]; then
            log_warning "部分Pods可能仍在运行"
        fi
    fi
}

# 删除网络资源
delete_network_resources() {
    local namespace="$1"
    local label_selector="$2"
    
    log_info "删除网络资源..."
    
    local kubectl_opts="-n $namespace"
    if [[ ! -z "$label_selector" ]]; then
        kubectl_opts="$kubectl_opts -l $label_selector"
    fi
    
    # 删除Ingress
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "kubectl delete ingress $kubectl_opts --ignore-not-found=true"
    else
        kubectl delete ingress $kubectl_opts --ignore-not-found=true
    fi
    
    # 删除Services
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "kubectl delete services $kubectl_opts --ignore-not-found=true"
    else
        kubectl delete services $kubectl_opts --ignore-not-found=true
    fi
    
    # 删除NetworkPolicies
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "kubectl delete networkpolicies $kubectl_opts --ignore-not-found=true"
    else
        kubectl delete networkpolicies $kubectl_opts --ignore-not-found=true
    fi
}

# 删除配置资源
delete_config_resources() {
    local namespace="$1"
    local label_selector="$2"
    
    log_info "删除配置资源..."
    
    local kubectl_opts="-n $namespace"
    if [[ ! -z "$label_selector" ]]; then
        kubectl_opts="$kubectl_opts -l $label_selector"
    fi
    
    # 删除ConfigMaps
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "kubectl delete configmaps $kubectl_opts --ignore-not-found=true"
    else
        kubectl delete configmaps $kubectl_opts --ignore-not-found=true
    fi
    
    # 删除Secrets（如果指定）
    if [[ "$DELETE_SECRETS" == "true" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "kubectl delete secrets $kubectl_opts --ignore-not-found=true"
        else
            kubectl delete secrets $kubectl_opts --ignore-not-found=true
        fi
    fi
}

# 删除存储资源
delete_storage_resources() {
    local namespace="$1"
    local label_selector="$2"
    
    if [[ "$DELETE_PVC" != "true" ]]; then
        return
    fi
    
    log_info "删除存储资源..."
    
    local kubectl_opts="-n $namespace"
    if [[ ! -z "$label_selector" ]]; then
        kubectl_opts="$kubectl_opts -l $label_selector"
    fi
    
    # 删除PersistentVolumeClaims
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "kubectl delete pvc $kubectl_opts --ignore-not-found=true"
    else
        kubectl delete pvc $kubectl_opts --ignore-not-found=true
    fi
}

# 删除命名空间
delete_namespace_if_requested() {
    local namespace="$1"
    
    if [[ "$DELETE_NAMESPACE" != "true" ]]; then
        return
    fi
    
    if ! confirm_action "将要删除命名空间 '$namespace' 及其所有资源"; then
        return
    fi
    
    log_info "删除命名空间: $namespace"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "kubectl delete namespace $namespace --ignore-not-found=true"
    else
        kubectl delete namespace "$namespace" --ignore-not-found=true
        
        # 等待命名空间删除完成
        log_info "等待命名空间删除完成..."
        kubectl wait --for=delete namespace/"$namespace" --timeout=300s 2>/dev/null || true
    fi
}

# 主清理函数
cleanup_resources() {
    local namespace="$1"
    local label_selector="$2"
    local timeout="$3"
    
    # 检查命名空间是否存在
    if ! kubectl get namespace "$namespace" &> /dev/null; then
        log_error "命名空间 '$namespace' 不存在"
        exit 1
    fi
    
    # 显示将要删除的资源
    list_resources "$namespace" "$label_selector"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "干运行模式：以上资源将被删除"
        return
    fi
    
    # 确认删除
    if ! confirm_action "将要删除命名空间 '$namespace' 中的资源"; then
        exit 0
    fi
    
    # 按顺序删除资源
    delete_workloads "$namespace" "$label_selector" "$timeout"
    delete_network_resources "$namespace" "$label_selector"
    delete_config_resources "$namespace" "$label_selector"
    delete_storage_resources "$namespace" "$label_selector"
    delete_namespace_if_requested "$namespace"
    
    log_success "清理完成"
}

# 主函数
main() {
    local namespace="$DEFAULT_NAMESPACE"
    local label_selector=""
    local timeout=300
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                FORCE_DELETE=true
                shift
                ;;
            -n|--delete-namespace)
                DELETE_NAMESPACE=true
                shift
                ;;
            -p|--delete-pvc)
                DELETE_PVC=true
                shift
                ;;
            -s|--delete-secrets)
                DELETE_SECRETS=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -a|--all)
                DELETE_NAMESPACE=true
                DELETE_PVC=true
                DELETE_SECRETS=true
                shift
                ;;
            -l|--label)
                label_selector="$2"
                shift 2
                ;;
            --timeout)
                timeout="$2"
                shift 2
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$namespace" ]]; then
                    namespace="$1"
                else
                    log_error "多余的参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 检查必需参数
    if [[ -z "$namespace" ]]; then
        log_error "必须指定命名空间"
        show_help
        exit 1
    fi
    
    # 检查依赖
    check_dependencies
    
    log_info "开始清理命名空间: $namespace"
    if [[ ! -z "$label_selector" ]]; then
        log_info "标签选择器: $label_selector"
    fi
    
    # 执行清理
    cleanup_resources "$namespace" "$label_selector" "$timeout"
}

# 执行主函数
main "$@"
