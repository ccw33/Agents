package main

/*
AI Agent Web Service - Go客户端SDK

用于在Kubernetes集群内调用AI Agent Web Service的Go客户端库。

使用示例:
    client := NewAIAgentClient()
    health, err := client.HealthCheck()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("服务状态: %s\n", health.Status)
*/

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"
)

// AIAgentClient AI Agent服务客户端
type AIAgentClient struct {
	BaseURL string
	Client  *http.Client
}

// HealthResponse 健康检查响应
type HealthResponse struct {
	Status      string `json:"status"`
	Service     string `json:"service"`
	Version     string `json:"version"`
	Timestamp   string `json:"timestamp"`
	Environment string `json:"environment"`
	Deployment  string `json:"deployment"`
}

// ServiceInfoResponse 服务信息响应
type ServiceInfoResponse struct {
	Service     string   `json:"service"`
	Version     string   `json:"version"`
	Deployment  string   `json:"deployment"`
	Namespace   string   `json:"namespace"`
	InternalURL string   `json:"internal_url"`
	Features    []string `json:"features"`
	Endpoints   []string `json:"endpoints"`
}

// AgentHealthResponse Agent健康检查响应
type AgentHealthResponse struct {
	Status         string `json:"status"`
	Message        string `json:"message"`
	AgentAvailable bool   `json:"agent_available"`
	Note           string `json:"note"`
}

// DesignRequest 设计请求
type DesignRequest struct {
	Requirement string `json:"requirement"`
	Style       string `json:"style"`
}

// DesignResponse 设计响应
type DesignResponse struct {
	Status         string   `json:"status"`
	Success        bool     `json:"success"`
	Message        string   `json:"message"`
	PrototypeURL   string   `json:"prototype_url,omitempty"`
	InternalDomain string   `json:"internal_domain,omitempty"`
	Features       []string `json:"features,omitempty"`
}

// ErrorResponse 错误响应
type ErrorResponse struct {
	Error     string `json:"error"`
	Message   string `json:"message"`
	Code      int    `json:"code,omitempty"`
	Timestamp string `json:"timestamp,omitempty"`
}

// NewAIAgentClient 创建新的AI Agent客户端
func NewAIAgentClient() *AIAgentClient {
	return &AIAgentClient{
		BaseURL: "http://web-service.ai-agents.svc.cluster.local:8000",
		Client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// NewAIAgentClientWithConfig 使用自定义配置创建客户端
func NewAIAgentClientWithConfig(baseURL string, timeout time.Duration) *AIAgentClient {
	return &AIAgentClient{
		BaseURL: baseURL,
		Client: &http.Client{
			Timeout: timeout,
		},
	}
}

// makeRequest 发送HTTP请求
func (c *AIAgentClient) makeRequest(method, endpoint string, body interface{}) ([]byte, error) {
	url := c.BaseURL + endpoint
	
	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("JSON序列化失败: %w", err)
		}
		reqBody = bytes.NewBuffer(jsonData)
	}
	
	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %w", err)
	}
	
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("请求失败: %w", err)
	}
	defer resp.Body.Close()
	
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %w", err)
	}
	
	if resp.StatusCode >= 400 {
		var errResp ErrorResponse
		if err := json.Unmarshal(respBody, &errResp); err == nil {
			return nil, fmt.Errorf("API错误 [%d]: %s", resp.StatusCode, errResp.Message)
		}
		return nil, fmt.Errorf("HTTP错误 [%d]: %s", resp.StatusCode, string(respBody))
	}
	
	return respBody, nil
}

// HealthCheck 健康检查
func (c *AIAgentClient) HealthCheck() (*HealthResponse, error) {
	respBody, err := c.makeRequest("GET", "/health", nil)
	if err != nil {
		return nil, err
	}
	
	var health HealthResponse
	if err := json.Unmarshal(respBody, &health); err != nil {
		return nil, fmt.Errorf("解析健康检查响应失败: %w", err)
	}
	
	return &health, nil
}

// GetServiceInfo 获取服务信息
func (c *AIAgentClient) GetServiceInfo() (*ServiceInfoResponse, error) {
	respBody, err := c.makeRequest("GET", "/api/v1/info", nil)
	if err != nil {
		return nil, err
	}
	
	var info ServiceInfoResponse
	if err := json.Unmarshal(respBody, &info); err != nil {
		return nil, fmt.Errorf("解析服务信息响应失败: %w", err)
	}
	
	return &info, nil
}

// CheckAgentHealth 检查Agent健康状态
func (c *AIAgentClient) CheckAgentHealth() (*AgentHealthResponse, error) {
	respBody, err := c.makeRequest("GET", "/api/v1/prototype_design/health", nil)
	if err != nil {
		return nil, err
	}
	
	var agentHealth AgentHealthResponse
	if err := json.Unmarshal(respBody, &agentHealth); err != nil {
		return nil, fmt.Errorf("解析Agent健康检查响应失败: %w", err)
	}
	
	return &agentHealth, nil
}

// CreatePrototype 创建原型设计
func (c *AIAgentClient) CreatePrototype(requirement, style string) (*DesignResponse, error) {
	if style == "" {
		style = "现代简约"
	}
	
	reqData := DesignRequest{
		Requirement: requirement,
		Style:       style,
	}
	
	respBody, err := c.makeRequest("POST", "/api/v1/prototype_design/design", reqData)
	if err != nil {
		return nil, err
	}
	
	var result DesignResponse
	if err := json.Unmarshal(respBody, &result); err != nil {
		return nil, fmt.Errorf("解析设计响应失败: %w", err)
	}
	
	return &result, nil
}

// IsHealthy 检查服务是否健康
func (c *AIAgentClient) IsHealthy() bool {
	health, err := c.HealthCheck()
	if err != nil {
		return false
	}
	return health.Status == "healthy"
}

// WaitForService 等待服务就绪
func (c *AIAgentClient) WaitForService(maxAttempts int, interval time.Duration) bool {
	for attempt := 0; attempt < maxAttempts; attempt++ {
		if c.IsHealthy() {
			log.Printf("服务就绪，尝试次数: %d", attempt+1)
			return true
		}
		
		log.Printf("等待服务就绪，尝试 %d/%d", attempt+1, maxAttempts)
		time.Sleep(interval)
	}
	
	log.Printf("服务等待超时，最大尝试次数: %d", maxAttempts)
	return false
}

// 使用示例
func main() {
	// 创建客户端
	client := NewAIAgentClient()
	
	// 等待服务就绪
	fmt.Println("等待服务就绪...")
	if !client.WaitForService(30, 2*time.Second) {
		log.Fatal("❌ 服务等待超时")
	}
	
	// 健康检查
	fmt.Println("\n🔍 健康检查...")
	health, err := client.HealthCheck()
	if err != nil {
		log.Fatalf("❌ 健康检查失败: %v", err)
	}
	fmt.Printf("✅ 服务状态: %s\n", health.Status)
	fmt.Printf("📋 服务版本: %s\n", health.Version)
	
	// 获取服务信息
	fmt.Println("\n📊 获取服务信息...")
	info, err := client.GetServiceInfo()
	if err != nil {
		log.Fatalf("❌ 获取服务信息失败: %v", err)
	}
	fmt.Printf("🏷️  服务名称: %s\n", info.Service)
	fmt.Printf("🌐 内网地址: %s\n", info.InternalURL)
	fmt.Printf("🎯 支持特性: %v\n", info.Features)
	
	// 检查Agent健康状态
	fmt.Println("\n🤖 检查Agent状态...")
	agentHealth, err := client.CheckAgentHealth()
	if err != nil {
		log.Fatalf("❌ Agent健康检查失败: %v", err)
	}
	fmt.Printf("✅ Agent可用: %t\n", agentHealth.AgentAvailable)
	fmt.Printf("💬 状态信息: %s\n", agentHealth.Message)
	
	// 创建原型设计
	fmt.Println("\n🎨 创建原型设计...")
	result, err := client.CreatePrototype("用户管理界面", "现代简约风格")
	if err != nil {
		log.Fatalf("❌ 创建原型失败: %v", err)
	}
	fmt.Printf("✅ 设计状态: %s\n", result.Status)
	fmt.Printf("💡 设计结果: %s\n", result.Message)
	
	fmt.Println("\n🎉 所有测试完成！")
}
