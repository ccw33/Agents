#!/bin/bash
# AI Agent服务启动脚本

set -e

# 颜色定义
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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查Docker（如果使用Docker模式）
    if [ "$1" = "docker" ]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker 未安装"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            log_error "Docker Compose 未安装"
            exit 1
        fi
    fi
    
    log_success "依赖检查通过"
}

# 启动开发模式
start_dev() {
    log_info "启动开发模式..."
    
    cd web-service
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        log_error "虚拟环境不存在，请先运行 ./scripts/setup.sh"
        exit 1
    fi
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        log_warning ".env文件不存在，使用默认配置"
        cp .env.example .env
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 设置开发环境变量
    export DEBUG=true
    export LOG_LEVEL=DEBUG
    
    log_info "启动FastAPI开发服务器..."
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# 启动生产模式
start_prod() {
    log_info "启动生产模式..."
    
    cd web-service
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        log_error ".env文件不存在，请先配置环境变量"
        exit 1
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 设置生产环境变量
    export DEBUG=false
    export LOG_LEVEL=INFO
    
    log_info "启动FastAPI生产服务器..."
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
}

# 启动Docker模式
start_docker() {
    log_info "启动Docker模式..."
    
    cd web-service
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        log_warning ".env文件不存在，使用默认配置"
        cp .env.example .env
    fi
    
    # 构建并启动服务
    log_info "构建Docker镜像..."
    docker-compose build
    
    log_info "启动Docker服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_success "Docker服务启动成功"
        log_info "服务地址: http://localhost:8000"
        log_info "API文档: http://localhost:8000/docs"
        log_info "查看日志: docker-compose logs -f"
        log_info "停止服务: docker-compose down"
    else
        log_error "Docker服务启动失败"
        docker-compose logs
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    cd web-service
    
    # 停止Docker服务
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        log_success "Docker服务已停止"
    fi
    
    # 停止本地进程
    pkill -f "uvicorn app.main:app" || true
    log_success "本地服务已停止"
}

# 显示帮助信息
show_help() {
    echo "AI Agent服务启动脚本"
    echo ""
    echo "用法: $0 [模式]"
    echo ""
    echo "模式:"
    echo "  dev     - 开发模式 (默认)"
    echo "  prod    - 生产模式"
    echo "  docker  - Docker模式"
    echo "  stop    - 停止所有服务"
    echo "  help    - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev     # 启动开发模式"
    echo "  $0 docker  # 使用Docker启动"
    echo "  $0 stop    # 停止所有服务"
}

# 主函数
main() {
    local mode=${1:-dev}
    
    case $mode in
        dev)
            check_dependencies
            start_dev
            ;;
        prod)
            check_dependencies
            start_prod
            ;;
        docker)
            check_dependencies docker
            start_docker
            ;;
        stop)
            stop_services
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知模式: $mode"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
