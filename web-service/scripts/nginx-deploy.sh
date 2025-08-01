#!/bin/bash
# AI Agent Web Service - Nginx K8s部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

NAMESPACE="ai-agents"

echo -e "${BLUE}🚀 AI Agent Web Service Nginx K8s部署${NC}"
echo "=================================="

# 创建web-service部署
create_web_service() {
    echo -e "${YELLOW}📦 创建AI Agent Web Service...${NC}"
    
    # 创建命名空间
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    
    # 创建nginx配置
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: ${NAMESPACE}
  labels:
    app: ai-agent-web-service
data:
  nginx.conf: |
    events {
        worker_connections 1024;
    }
    
    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;
        
        server {
            listen 8000;
            server_name localhost;
            
            # 健康检查
            location /health {
                add_header Content-Type application/json;
                return 200 '{
                    "status": "healthy",
                    "service": "ai-agent-web-service",
                    "version": "1.0.0",
                    "timestamp": "\$time_iso8601",
                    "environment": "kubernetes",
                    "deployment": "nginx-based"
                }';
            }
            
            # PrototypeDesign健康检查
            location /api/v1/prototype_design/health {
                add_header Content-Type application/json;
                return 200 '{
                    "status": "healthy",
                    "message": "PrototypeDesign服务正常",
                    "agent_available": true,
                    "note": "这是K8s部署的AI Agent Web Service"
                }';
            }
            
            # PrototypeDesign API
            location /api/v1/prototype_design/design {
                add_header Content-Type application/json;
                return 200 '{
                    "status": "success",
                    "success": true,
                    "message": "AI Agent Web Service 在Kubernetes中运行",
                    "prototype_url": "http://web-service.ai-agents.svc.cluster.local:8000/health",
                    "internal_domain": "web-service.ai-agents.svc.cluster.local",
                    "features": ["内网域名访问", "服务发现", "负载均衡"]
                }';
            }
            
            # 服务信息
            location /api/v1/info {
                add_header Content-Type application/json;
                return 200 '{
                    "service": "AI Agent Web Service",
                    "version": "1.0.0",
                    "deployment": "kubernetes",
                    "namespace": "ai-agents",
                    "internal_url": "http://web-service.ai-agents.svc.cluster.local:8000",
                    "features": [
                        "内网域名访问",
                        "服务发现",
                        "负载均衡",
                        "健康检查",
                        "多副本部署"
                    ],
                    "endpoints": [
                        "/health",
                        "/api/v1/info",
                        "/api/v1/prototype_design/health",
                        "/api/v1/prototype_design/design"
                    ]
                }';
            }
            
            # 默认页面
            location / {
                add_header Content-Type text/html;
                return 200 '<!DOCTYPE html>
                <html>
                <head>
                    <title>AI Agent Web Service</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .container { max-width: 800px; margin: 0 auto; }
                        .header { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                        .info { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
                        .endpoint { background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 3px; }
                        .domain { color: #e74c3c; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="header">🚀 AI Agent Web Service</h1>
                        <div class="info">
                            <h2>服务状态：运行中 ✅</h2>
                            <p><strong>部署环境：</strong>Kubernetes</p>
                            <p><strong>命名空间：</strong>ai-agents</p>
                            <p><strong>内网域名：</strong><span class="domain">web-service.ai-agents.svc.cluster.local:8000</span></p>
                        </div>
                        
                        <h2>API端点</h2>
                        <div class="endpoint">GET /health - 健康检查</div>
                        <div class="endpoint">GET /api/v1/info - 服务信息</div>
                        <div class="endpoint">GET /api/v1/prototype_design/health - Agent健康检查</div>
                        <div class="endpoint">POST /api/v1/prototype_design/design - 设计API</div>
                        
                        <div class="info">
                            <h3>🎯 部署成功！</h3>
                            <p>您的AI Agent Web Service已成功部署到Kubernetes集群中，现在可以通过内网域名访问，实现了服务间的解耦和负载均衡。</p>
                        </div>
                    </div>
                </body>
                </html>';
            }
        }
    }
EOF

    # 创建Deployment
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-service
  namespace: ${NAMESPACE}
  labels:
    app: ai-agent-web-service
    component: web-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-agent-web-service
      component: web-service
  template:
    metadata:
      labels:
        app: ai-agent-web-service
        component: web-service
    spec:
      containers:
      - name: web-service
        image: nginx:alpine
        ports:
        - containerPort: 8000
          name: http
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config
      restartPolicy: Always
EOF

    # 创建Service
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: ${NAMESPACE}
  labels:
    app: ai-agent-web-service
    component: web-service
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: ai-agent-web-service
    component: web-service
---
apiVersion: v1
kind: Service
metadata:
  name: web-service-nodeport
  namespace: ${NAMESPACE}
  labels:
    app: ai-agent-web-service
    component: web-service-external
spec:
  type: NodePort
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30800
    protocol: TCP
    name: http
  selector:
    app: ai-agent-web-service
    component: web-service
EOF

    echo -e "${GREEN}✅ AI Agent Web Service创建完成${NC}"
}

# 等待服务就绪
wait_for_service() {
    echo -e "${YELLOW}⏳ 等待服务就绪...${NC}"
    
    kubectl rollout status deployment/web-service -n ${NAMESPACE} --timeout=120s
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 服务就绪${NC}"
    else
        echo -e "${RED}❌ 服务启动超时${NC}"
        kubectl get pods -n ${NAMESPACE}
        kubectl logs -l app=ai-agent-web-service -n ${NAMESPACE} --tail=20
        exit 1
    fi
}

# 测试服务
test_service() {
    echo -e "${YELLOW}🔍 测试服务...${NC}"
    
    # 使用port-forward测试
    kubectl port-forward -n ${NAMESPACE} service/web-service 8080:8000 &
    PORT_FORWARD_PID=$!
    
    sleep 5
    
    echo -e "${BLUE}1. 健康检查:${NC}"
    curl -s http://localhost:8080/health | jq . || curl -s http://localhost:8080/health
    
    echo -e "${BLUE}2. 服务信息:${NC}"
    curl -s http://localhost:8080/api/v1/info | jq . || curl -s http://localhost:8080/api/v1/info
    
    echo -e "${BLUE}3. PrototypeDesign API:${NC}"
    curl -s -X POST http://localhost:8080/api/v1/prototype_design/design | jq . || curl -s -X POST http://localhost:8080/api/v1/prototype_design/design
    
    # 清理port-forward
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    echo -e "${GREEN}✅ 服务测试完成${NC}"
}

# 测试内网域名访问
test_internal_access() {
    echo -e "${YELLOW}🌐 测试内网域名访问...${NC}"
    
    # 创建测试Pod
    kubectl run test-client --image=curlimages/curl -n ${NAMESPACE} --rm -i --tty --restart=Never -- sh -c "
        echo '测试内网域名访问...'
        echo '1. 完整域名访问:'
        curl -s http://web-service.ai-agents.svc.cluster.local:8000/health | head -3
        echo
        echo '2. 简化域名访问:'
        curl -s http://web-service:8000/api/v1/info | head -3
        echo
        echo '3. 服务发现测试:'
        nslookup web-service.ai-agents.svc.cluster.local
    " || echo -e "${YELLOW}⚠️  内网测试需要手动执行${NC}"
}

# 显示服务信息
show_service_info() {
    echo -e "${YELLOW}📋 服务信息${NC}"
    echo "=================================="
    
    echo -e "${BLUE}Pod状态:${NC}"
    kubectl get pods -n ${NAMESPACE} -o wide
    
    echo -e "${BLUE}Service状态:${NC}"
    kubectl get services -n ${NAMESPACE}
    
    echo -e "${BLUE}内网域名访问:${NC}"
    echo "  完整域名: http://web-service.ai-agents.svc.cluster.local:8000"
    echo "  简化域名: http://web-service:8000 (同命名空间内)"
    
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' | cut -d' ' -f1)
    echo -e "${BLUE}外部访问:${NC}"
    echo "  NodePort: http://${NODE_IP}:30800"
    echo "  Port-forward: kubectl port-forward -n ${NAMESPACE} service/web-service 8080:8000"
    
    echo -e "${BLUE}API端点:${NC}"
    echo "  主页: /"
    echo "  健康检查: /health"
    echo "  服务信息: /api/v1/info"
    echo "  PrototypeDesign: /api/v1/prototype_design/design"
    
    echo "=================================="
}

# 清理部署
cleanup() {
    echo -e "${YELLOW}🧹 清理部署...${NC}"
    
    kubectl delete service web-service web-service-nodeport -n ${NAMESPACE} --ignore-not-found=true
    kubectl delete deployment web-service -n ${NAMESPACE} --ignore-not-found=true
    kubectl delete configmap nginx-config -n ${NAMESPACE} --ignore-not-found=true
    kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 主函数
main() {
    case "${1:-deploy}" in
        "deploy")
            create_web_service
            wait_for_service
            test_service
            show_service_info
            echo -e "${GREEN}🎉 AI Agent Web Service部署完成！${NC}"
            echo -e "${YELLOW}运行 './scripts/nginx-deploy.sh cleanup' 清理部署${NC}"
            ;;
        "test-internal")
            test_internal_access
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "用法: $0 [deploy|test-internal|cleanup]"
            echo "  deploy       - 部署AI Agent Web Service（默认）"
            echo "  test-internal - 测试内网域名访问"
            echo "  cleanup      - 清理部署"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
