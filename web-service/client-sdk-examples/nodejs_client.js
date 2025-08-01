#!/usr/bin/env node

/**
 * AI Agent Web Service - Node.js客户端SDK
 * 
 * 用于在Kubernetes集群内调用AI Agent Web Service的Node.js客户端库。
 * 
 * 使用示例:
 *   const { AIAgentClient } = require('./nodejs_client');
 *   
 *   const client = new AIAgentClient();
 *   const health = await client.healthCheck();
 *   console.log(`服务状态: ${health.status}`);
 */

const axios = require('axios');

/**
 * AI Agent客户端异常类
 */
class AIAgentClientError extends Error {
    constructor(message, statusCode = null, response = null) {
        super(message);
        this.name = 'AIAgentClientError';
        this.statusCode = statusCode;
        this.response = response;
    }
}

/**
 * AI Agent Web Service客户端
 */
class AIAgentClient {
    /**
     * 初始化客户端
     * 
     * @param {string} baseURL - 服务基础URL
     * @param {number} timeout - 请求超时时间（毫秒）
     * @param {number} retries - 重试次数
     */
    constructor(
        baseURL = 'http://web-service.ai-agents.svc.cluster.local:8000',
        timeout = 30000,
        retries = 3
    ) {
        this.baseURL = baseURL.replace(/\/$/, '');
        this.timeout = timeout;
        this.retries = retries;
        
        // 创建axios实例
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // 配置重试拦截器
        this._setupRetryInterceptor();
    }
    
    /**
     * 配置重试拦截器
     * @private
     */
    _setupRetryInterceptor() {
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                const config = error.config;
                
                // 如果没有配置重试或已达到最大重试次数
                if (!config || config.__retryCount >= this.retries) {
                    return Promise.reject(error);
                }
                
                // 只对特定错误码重试
                const retryStatusCodes = [429, 500, 502, 503, 504];
                if (!retryStatusCodes.includes(error.response?.status)) {
                    return Promise.reject(error);
                }
                
                // 增加重试计数
                config.__retryCount = config.__retryCount || 0;
                config.__retryCount++;
                
                // 计算延迟时间（指数退避）
                const delay = Math.pow(2, config.__retryCount) * 1000;
                
                console.log(`请求失败，${delay}ms后进行第${config.__retryCount}次重试...`);
                
                // 延迟后重试
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.client(config);
            }
        );
    }
    
    /**
     * 发送HTTP请求
     * @private
     */
    async _makeRequest(method, endpoint, data = null) {
        try {
            const response = await this.client.request({
                method,
                url: endpoint,
                data
            });
            
            return response.data;
            
        } catch (error) {
            if (error.response) {
                // 服务器响应了错误状态码
                const { status, data } = error.response;
                const message = data?.message || data?.error || `HTTP错误 ${status}`;
                throw new AIAgentClientError(message, status, data);
            } else if (error.request) {
                // 请求发送了但没有收到响应
                throw new AIAgentClientError(`网络错误: ${error.message}`);
            } else {
                // 其他错误
                throw new AIAgentClientError(`请求配置错误: ${error.message}`);
            }
        }
    }
    
    /**
     * 健康检查
     * 
     * @returns {Promise<Object>} 健康状态信息
     * 
     * @example
     * const client = new AIAgentClient();
     * const health = await client.healthCheck();
     * console.log(health.status); // 'healthy'
     */
    async healthCheck() {
        return await this._makeRequest('GET', '/health');
    }
    
    /**
     * 获取服务信息
     * 
     * @returns {Promise<Object>} 服务详细信息
     * 
     * @example
     * const client = new AIAgentClient();
     * const info = await client.getServiceInfo();
     * console.log(info.service); // 'AI Agent Web Service'
     */
    async getServiceInfo() {
        return await this._makeRequest('GET', '/api/v1/info');
    }
    
    /**
     * 检查Agent健康状态
     * 
     * @returns {Promise<Object>} Agent健康状态信息
     * 
     * @example
     * const client = new AIAgentClient();
     * const agentHealth = await client.checkAgentHealth();
     * console.log(agentHealth.agent_available); // true
     */
    async checkAgentHealth() {
        return await this._makeRequest('GET', '/api/v1/prototype_design/health');
    }
    
    /**
     * 创建原型设计
     * 
     * @param {string} requirement - 设计需求描述
     * @param {string} style - 设计风格，默认为"现代简约"
     * @returns {Promise<Object>} 设计结果
     * 
     * @example
     * const client = new AIAgentClient();
     * const result = await client.createPrototype('用户登录页面', '简约风格');
     * console.log(result.status); // 'success'
     */
    async createPrototype(requirement, style = '现代简约') {
        const data = {
            requirement,
            style
        };
        
        return await this._makeRequest('POST', '/api/v1/prototype_design/design', data);
    }
    
    /**
     * 检查服务是否健康
     * 
     * @returns {Promise<boolean>} true如果服务健康，false否则
     */
    async isHealthy() {
        try {
            const health = await this.healthCheck();
            return health.status === 'healthy';
        } catch (error) {
            return false;
        }
    }
    
    /**
     * 等待服务就绪
     * 
     * @param {number} maxAttempts - 最大尝试次数
     * @param {number} interval - 检查间隔（毫秒）
     * @returns {Promise<boolean>} true如果服务就绪，false如果超时
     */
    async waitForService(maxAttempts = 30, interval = 2000) {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            if (await this.isHealthy()) {
                console.log(`服务就绪，尝试次数: ${attempt + 1}`);
                return true;
            }
            
            console.log(`等待服务就绪，尝试 ${attempt + 1}/${maxAttempts}`);
            await new Promise(resolve => setTimeout(resolve, interval));
        }
        
        console.warn(`服务等待超时，最大尝试次数: ${maxAttempts}`);
        return false;
    }
}

// 使用示例
async function main() {
    try {
        // 创建客户端
        const client = new AIAgentClient();
        
        // 等待服务就绪
        console.log('等待服务就绪...');
        if (!(await client.waitForService())) {
            console.error('❌ 服务等待超时');
            process.exit(1);
        }
        
        // 健康检查
        console.log('\n🔍 健康检查...');
        const health = await client.healthCheck();
        console.log(`✅ 服务状态: ${health.status}`);
        console.log(`📋 服务版本: ${health.version}`);
        
        // 获取服务信息
        console.log('\n📊 获取服务信息...');
        const info = await client.getServiceInfo();
        console.log(`🏷️  服务名称: ${info.service}`);
        console.log(`🌐 内网地址: ${info.internal_url}`);
        console.log(`🎯 支持特性: ${info.features.join(', ')}`);
        
        // 检查Agent健康状态
        console.log('\n🤖 检查Agent状态...');
        const agentHealth = await client.checkAgentHealth();
        console.log(`✅ Agent可用: ${agentHealth.agent_available}`);
        console.log(`💬 状态信息: ${agentHealth.message}`);
        
        // 创建原型设计
        console.log('\n🎨 创建原型设计...');
        const result = await client.createPrototype(
            '用户管理界面',
            '现代简约风格'
        );
        console.log(`✅ 设计状态: ${result.status}`);
        console.log(`💡 设计结果: ${result.message}`);
        
        console.log('\n🎉 所有测试完成！');
        
    } catch (error) {
        if (error instanceof AIAgentClientError) {
            console.error(`❌ 客户端错误: ${error.message}`);
            if (error.statusCode) {
                console.error(`   状态码: ${error.statusCode}`);
            }
        } else {
            console.error(`❌ 未知错误: ${error.message}`);
        }
        process.exit(1);
    }
}

// 导出类和错误类
module.exports = {
    AIAgentClient,
    AIAgentClientError
};

// 如果直接运行此文件，执行示例
if (require.main === module) {
    main();
}
