#!/bin/bash
# AI Agent Web Service - K8s清理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

NAMESPACE="ai-agents"

echo -e "${BLUE}🧹 AI Agent Web Service K8s清理脚本${NC}"
echo "=================================="

# 清理K8s资源
cleanup_k8s() {
    echo -e "${YELLOW}🗑️  清理Kubernetes资源...${NC}"
    
    # 删除Ingress
    if kubectl get ingress web-service-ingress -n ${NAMESPACE} &> /dev/null; then
        echo -e "${BLUE}删除Ingress...${NC}"
        kubectl delete -f k8s/ingress.yaml
    fi
    
    # 删除Service
    if kubectl get service web-service -n ${NAMESPACE} &> /dev/null; then
        echo -e "${BLUE}删除Service...${NC}"
        kubectl delete -f k8s/service.yaml
    fi
    
    # 删除Deployment
    if kubectl get deployment web-service -n ${NAMESPACE} &> /dev/null; then
        echo -e "${BLUE}删除Deployment...${NC}"
        kubectl delete -f k8s/deployment.yaml
    fi
    
    # 删除ConfigMap和Secret
    if kubectl get configmap web-service-config -n ${NAMESPACE} &> /dev/null; then
        echo -e "${BLUE}删除ConfigMap...${NC}"
        kubectl delete -f k8s/configmap.yaml
    fi
    
    if kubectl get secret web-service-secrets -n ${NAMESPACE} &> /dev/null; then
        echo -e "${BLUE}删除Secret...${NC}"
        kubectl delete -f k8s/secret.yaml
    fi
    
    echo -e "${GREEN}✅ K8s资源清理完成${NC}"
}

# 清理命名空间
cleanup_namespace() {
    echo -e "${YELLOW}📦 清理命名空间...${NC}"
    
    if kubectl get namespace ${NAMESPACE} &> /dev/null; then
        echo -e "${BLUE}删除命名空间 ${NAMESPACE}...${NC}"
        kubectl delete namespace ${NAMESPACE}
        echo -e "${GREEN}✅ 命名空间清理完成${NC}"
    else
        echo -e "${BLUE}命名空间 ${NAMESPACE} 不存在${NC}"
    fi
}

# 清理Docker镜像
cleanup_docker() {
    echo -e "${YELLOW}🐳 清理Docker镜像...${NC}"
    
    if docker images | grep -q "ai-agent-web-service"; then
        echo -e "${BLUE}删除Docker镜像...${NC}"
        docker rmi ai-agent-web-service:latest || true
        echo -e "${GREEN}✅ Docker镜像清理完成${NC}"
    else
        echo -e "${BLUE}Docker镜像不存在${NC}"
    fi
}

# 主函数
main() {
    case "${1:-all}" in
        "k8s")
            cleanup_k8s
            ;;
        "namespace")
            cleanup_namespace
            ;;
        "docker")
            cleanup_docker
            ;;
        "all")
            cleanup_k8s
            cleanup_namespace
            cleanup_docker
            ;;
        *)
            echo "用法: $0 [k8s|namespace|docker|all]"
            echo "  k8s       - 清理K8s资源（保留命名空间）"
            echo "  namespace - 清理命名空间"
            echo "  docker    - 清理Docker镜像"
            echo "  all       - 清理所有资源（默认）"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}🎉 清理完成${NC}"
}

# 执行主函数
main "$@"
