"""
用户客户端API
"""
import requests
from typing import Optional, List, Dict, Any
from .user_schema import UserCreateRequest, UserResponse


class UserAPI:
    """用户客户端API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = "demo_token_2025"):
        """
        初始化客户端
        
        Args:
            base_url: 微服务基础URL
            token: 认证令牌
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json().get('detail', '未知错误')
                raise Exception(f"HTTP错误 {response.status_code}: {error_detail}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {e}")
    
    def create_user(self, request: UserCreateRequest) -> UserResponse:
        """
        创建用户
        
        Args:
            request: 用户创建请求
            
        Returns:
            用户响应
        """
        result = self._request("POST", "/api/v1/users", json=request.model_dump())
        return UserResponse(**result)
    
    def get_user(self, user_id: str) -> UserResponse:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户响应
        """
        result = self._request("GET", f"/api/v1/users/{user_id}")
        return UserResponse(**result)
    
    def list_users(self) -> List[UserResponse]:
        """
        列出用户
        
        Returns:
            用户列表
        """
        result = self._request("GET", "/api/v1/users")
        return [UserResponse(**item) for item in result]


