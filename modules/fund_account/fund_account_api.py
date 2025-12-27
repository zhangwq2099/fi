"""
基金账户客户端API
"""
import requests
from typing import List, Dict, Any
from .fund_account_schema import FundAccountCreateRequest, FundAccountResponse


class FundAccountAPI:
    """基金账户客户端API"""
    
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
    
    def create(self, request: FundAccountCreateRequest) -> FundAccountResponse:
        """创建基金账户"""
        result = self._request("POST", "/api/v1/fund-account", json=request.model_dump())
        return FundAccountResponse(**result)
    
    def get(self, id: str) -> FundAccountResponse:
        """获取基金账户"""
        result = self._request("GET", f"/api/v1/fund-account/{id}")
        return FundAccountResponse(**result)
