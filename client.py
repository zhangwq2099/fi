"""
客户端业务接口 - 调用微服务的业务方法封装
"""
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundClient:
    """基金交易客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = "demo_token_2025", test_connection: bool = True):
        """
        初始化客户端
        
        Args:
            base_url: 微服务基础URL
            token: 认证令牌
            test_connection: 是否在初始化时测试连接（默认True，测试时可设为False）
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 测试连接（可选）
        if test_connection:
            self._test_connection()
    
    def _test_connection(self):
        """测试服务连接"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                logger.info(f"连接成功: {response.json()}")
            else:
                logger.warning(f"服务连接异常: {response.status_code}")
        except Exception as e:
            logger.error(f"无法连接到服务: {e}")
            raise
    
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
            
            # 处理成功响应（200-299 都是成功状态码）
            if 200 <= response.status_code < 300:
                result = response.json()
                # 检查是否是包装格式 {'code': 0, 'data': {...}}
                if isinstance(result, dict) and 'code' in result:
                    if result.get('code') == 0:
                        return result.get('data', {})
                    else:
                        raise Exception(f"业务错误: {result.get('message', '未知错误')}")
                # 否则直接返回结果（FastAPI 直接返回对象）
                return result
            else:
                # 处理错误响应
                try:
                    error_detail = response.json().get('detail', '未知错误')
                except:
                    error_detail = response.text or '未知错误'
                raise Exception(f"HTTP错误 {response.status_code}: {error_detail}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"处理响应失败: {e}")
            raise
    
    def create_user(self, user_name: str, identity_no: str, **kwargs) -> str:
        """
        创建用户
        
        Args:
            user_name: 用户姓名
            identity_no: 身份证号
            **kwargs: 其他参数
            
        Returns:
            用户ID
        """
        data = {
            "user_name": user_name,
            "identity_no": identity_no,
            **kwargs
        }
        
        result = self._request("POST", "/api/v1/users", json=data)
        user_id = result.get('user_id')
        logger.info(f"用户创建成功: {user_id}")
        return user_id
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息
        """
        result = self._request("GET", f"/api/v1/users/{user_id}")
        return result
    
    def open_fund_account(self, user_id: str, account_type: str = "INDIVIDUAL") -> str:
        """
        开通基金账户
        
        Args:
            user_id: 用户ID
            account_type: 账户类型
            
        Returns:
            基金账户ID
        """
        data = {
            "user_id": user_id,
            "account_type": account_type
        }
        
        result = self._request("POST", "/api/v1/accounts/open", json=data)
        account_id = result.get('fund_account_id')
        logger.info(f"基金账户开通成功: {account_id}")
        return account_id
    
    def subscribe_fund(self, fund_account_id: str, product_id: str, amount: float) -> Dict[str, Any]:
        """
        申购基金
        
        Args:
            fund_account_id: 基金账户ID
            product_id: 产品ID
            amount: 申购金额
            
        Returns:
            申购结果
        """
        data = {
            "fund_account_id": fund_account_id,
            "product_id": product_id,
            "amount": amount
        }
        
        result = self._request("POST", "/api/v1/funds/subscribe", json=data)
        logger.info(f"基金申购成功: {fund_account_id}, 金额: {amount}")
        return result
    
    def redeem_fund(self, fund_account_id: str, product_id: str, share: float) -> Dict[str, Any]:
        """
        赎回基金
        
        Args:
            fund_account_id: 基金账户ID
            product_id: 产品ID
            share: 赎回份额
            
        Returns:
            赎回结果
        """
        data = {
            "fund_account_id": fund_account_id,
            "product_id": product_id,
            "share": share
        }
        
        result = self._request("POST", "/api/v1/funds/redeem", json=data)
        logger.info(f"基金赎回成功: {fund_account_id}, 份额: {share}")
        return result
    
    def get_user_assets(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户资产
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户资产信息
        """
        result = self._request("GET", f"/api/v1/assets/{user_id}")
        return result
    
    def get_products(self, product_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取基金产品列表
        
        Args:
            product_type: 产品类型筛选
            
        Returns:
            基金产品列表
        """
        params = {}
        if product_type:
            params['product_type'] = product_type
        
        result = self._request("GET", "/api/v1/products", params=params)
        return result
    
    def create_product(self, product_code: str, product_name: str, **kwargs) -> str:
        """
        创建基金产品
        
        Args:
            product_code: 产品代码
            product_name: 产品名称
            **kwargs: 其他参数
            
        Returns:
            产品ID
        """
        data = {
            "product_code": product_code,
            "product_name": product_name,
            **kwargs
        }
        
        result = self._request("POST", "/api/v1/products", json=data)
        product_id = result.get('product_id')
        logger.info(f"基金产品创建成功: {product_id}")
        return product_id
    
    def create_nav(self, product_id: str, net_value: float, **kwargs) -> str:
        """
        创建基金净值
        
        Args:
            product_id: 产品ID
            net_value: 单位净值
            **kwargs: 其他参数
            
        Returns:
            净值ID
        """
        data = {
            "product_id": product_id,
            "net_value": net_value,
            **kwargs
        }
        
        result = self._request("POST", "/api/v1/nav", json=data)
        nav_id = result.get('nav_id')
        logger.info(f"基金净值创建成功: {nav_id}")
        return nav_id
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class FundTradingApp:
    """基金交易应用（高级封装）"""
    
    def __init__(self, client: FundClient):
        """
        初始化交易应用
        
        Args:
            client: 基金客户端
        """
        self.client = client
        self.current_user_id = None
        self.current_account_id = None
    
    def register_and_login(self, user_name: str, identity_no: str) -> str:
        """
        注册并登录用户
        
        Args:
            user_name: 用户姓名
            identity_no: 身份证号
            
        Returns:
            用户ID
        """
        user_id = self.client.create_user(
            user_name=user_name,
            identity_no=identity_no,
            phone="13800138000",
            email=f"{user_name}@example.com"
        )
        
        self.current_user_id = user_id
        logger.info(f"用户注册并登录成功: {user_id}")
        return user_id
    
    def open_account(self, account_type: str = "INDIVIDUAL") -> str:
        """
        开通基金账户
        
        Args:
            account_type: 账户类型
            
        Returns:
            基金账户ID
        """
        if not self.current_user_id:
            raise Exception("请先登录用户")
        
        account_id = self.client.open_fund_account(
            user_id=self.current_user_id,
            account_type=account_type
        )
        
        self.current_account_id = account_id
        logger.info(f"基金账户开通成功: {account_id}")
        return account_id
    
    def quick_subscribe(self, product_id: str, amount: float) -> Dict[str, Any]:
        """
        快速申购（使用当前账户）
        
        Args:
            product_id: 产品ID
            amount: 申购金额
            
        Returns:
            申购结果
        """
        if not self.current_account_id:
            raise Exception("请先开通基金账户")
        
        result = self.client.subscribe_fund(
            fund_account_id=self.current_account_id,
            product_id=product_id,
            amount=amount
        )
        
        # 获取最新资产
        assets = self.client.get_user_assets(self.current_user_id)
        
        return {
            "subscribe_result": result,
            "current_assets": assets
        }
    
    def quick_redeem(self, product_id: str, share: float) -> Dict[str, Any]:
        """
        快速赎回（使用当前账户）
        
        Args:
            product_id: 产品ID
            share: 赎回份额
            
        Returns:
            赎回结果
        """
        if not self.current_account_id:
            raise Exception("请先开通基金账户")
        
        result = self.client.redeem_fund(
            fund_account_id=self.current_account_id,
            product_id=product_id,
            share=share
        )
        
        # 获取最新资产
        assets = self.client.get_user_assets(self.current_user_id)
        
        return {
            "redeem_result": result,
            "current_assets": assets
        }
    
    def get_portfolio(self) -> Dict[str, Any]:
        """
        获取投资组合
        
        Returns:
            投资组合信息
        """
        if not self.current_user_id:
            raise Exception("请先登录用户")
        
        assets = self.client.get_user_assets(self.current_user_id)
        products = self.client.get_products()
        
        # 获取用户持有的产品
        user_products = []
        if assets and 'fund_assets' in assets:
            for fund_asset in assets['fund_assets']:
                product_id = fund_asset['product_id']
                
                # 查找产品详情
                for product in products:
                    if product['product_id'] == product_id:
                        user_products.append({
                            **product,
                            **fund_asset
                        })
                        break
        
        return {
            "user_id": self.current_user_id,
            "total_assets": assets.get('total_asset', 0) if assets else 0,
            "portfolio": user_products
        }
    
    def demo_trading(self):
        """演示交易流程"""
        print("=== 基金交易演示 ===\n")
        
        # 1. 注册用户
        user_id = self.register_and_login("张先生", "320101198001011234")
        print(f"1. 用户注册成功: {user_id}")
        
        # 2. 开通账户
        account_id = self.open_account()
        print(f"2. 基金账户开通成功: {account_id}")
        
        # 3. 查看可用产品
        products = self.client.get_products()
        if products:
            product = products[0]
            product_id = product['product_id']
            product_name = product['product_name']
            print(f"3. 发现基金产品: {product_name} ({product_id})")
            
            # 4. 申购
            print(f"4. 申购基金: 金额=10000元")
            result = self.quick_subscribe(product_id, 10000.00)
            subscribe_result = result['subscribe_result']
            print(f"   申购结果: 获得{subscribe_result.get('share', 0):.2f}份")
            
            # 5. 查看资产
            portfolio = self.get_portfolio()
            print(f"5. 当前资产: 总资产={portfolio['total_assets']:.2f}元")
            
            # 6. 赎回部分份额
            redeem_share = subscribe_result.get('share', 0) * 0.3  # 赎回30%
            print(f"6. 赎回基金: 份额={redeem_share:.2f}份")
            redeem_result = self.quick_redeem(product_id, redeem_share)
            print(f"   赎回结果: 获得{redeem_result['redeem_result'].get('amount', 0):.2f}元")
            
            # 7. 最终资产
            final_portfolio = self.get_portfolio()
            print(f"7. 最终资产: 总资产={final_portfolio['total_assets']:.2f}元")
            
            print("\n=== 演示完成 ===")
        else:
            print("没有可用的基金产品，请先创建产品")


# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = FundClient(base_url="http://localhost:8000")
    
    # 创建交易应用
    app = FundTradingApp(client)
    
    # 演示交易流程
    app.demo_trading()


