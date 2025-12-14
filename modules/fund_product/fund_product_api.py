"""
基金产品客户端API
"""
import requests
from typing import List, Dict, Any
from .fund_product_schema import FundProductCreateRequest, FundProductResponse


class FundProductAPI:
    """基金产品客户端API"""
    
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
    
    def create(self, request: FundProductCreateRequest) -> FundProductResponse:
        """创建基金产品"""
        result = self._request("POST", "/api/v1/fund-product", json=request.dict())
        return FundProductResponse(**result)
    
    def get(self, id: str) -> FundProductResponse:
        """获取基金产品"""
        result = self._request("GET", f"/api/v1/fund-product/{id}")
        return FundProductResponse(**result)
