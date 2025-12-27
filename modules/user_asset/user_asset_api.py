"""
用户资产客户端API
"""
import requests
from typing import Dict, Any
from .user_asset_schema import UserAssetsResponse, UserBalance


class UserAssetAPI:
    """用户资产客户端API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = "demo_token_2025"):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method=method, url=url, headers=self.headers, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get('detail', '未知错误')
            raise Exception(f"HTTP错误 {response.status_code}: {error_detail}")
    
    def get_user_assets(self, user_id: str) -> UserAssetsResponse:
        """获取用户资产"""
        result = self._request("GET", f"/api/v1/assets/{user_id}")
        return UserAssetsResponse(**result)
    
    def get_user_balance(self, user_id: str) -> UserBalance:
        """获取用户余额"""
        result = self._request("GET", f"/api/v1/assets/{user_id}/balance")
        return UserBalance(**result)


