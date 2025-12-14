"""
测试客户端接口
"""
import pytest
import time
from client import FundClient, FundTradingApp


class TestFundClient:
    """测试基金客户端"""
    
    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        # 注意：需要先启动服务
        return FundClient(base_url="http://localhost:8000")
    
    def test_health_check(self, client):
        """测试健康检查"""
        result = client.health_check()
        assert result['status'] == 'healthy'
    
    def test_create_user(self, client):
        """测试创建用户"""
        user_id = client.create_user(
            user_name="测试用户",
            identity_no="320101199001011234"
        )
        assert user_id is not None
        
        # 获取用户信息
        user = client.get_user(user_id)
        assert user['user_id'] == user_id
    
    def test_open_fund_account(self, client):
        """测试开通基金账户"""
        # 先创建用户
        user_id = client.create_user(
            user_name="测试用户",
            identity_no="320101199001011234"
        )
        
        # 开通账户
        account_id = client.open_fund_account(user_id)
        assert account_id is not None
    
    def test_subscribe_and_redeem(self, client):
        """测试申购和赎回流程"""
        # 创建用户
        user_id = client.create_user(
            user_name="测试用户",
            identity_no="320101199001011234"
        )
        
        # 开通账户
        account_id = client.open_fund_account(user_id)
        
        # 获取产品列表
        products = client.get_products()
        if not products:
            pytest.skip("没有可用的基金产品")
        
        product = products[0]
        product_id = product['product_id']
        
        # 申购
        subscribe_result = client.subscribe_fund(
            fund_account_id=account_id,
            product_id=product_id,
            amount=10000.00
        )
        assert subscribe_result['entrust_id'] is not None
        assert subscribe_result['share'] > 0
        
        # 等待一下
        time.sleep(0.5)
        
        # 赎回部分份额
        redeem_share = subscribe_result['share'] * 0.3
        redeem_result = client.redeem_fund(
            fund_account_id=account_id,
            product_id=product_id,
            share=redeem_share
        )
        assert redeem_result['entrust_id'] is not None
        assert redeem_result['amount'] > 0
        
        # 获取资产
        assets = client.get_user_assets(user_id)
        assert assets['total_asset'] > 0


class TestFundTradingApp:
    """测试基金交易应用"""
    
    @pytest.fixture
    def app(self):
        """创建应用实例"""
        client = FundClient(base_url="http://localhost:8000")
        return FundTradingApp(client)
    
    def test_register_and_login(self, app):
        """测试注册登录"""
        user_id = app.register_and_login(
            user_name="测试用户",
            identity_no="320101199001011234"
        )
        assert user_id is not None
        assert app.current_user_id == user_id
    
    def test_open_account(self, app):
        """测试开通账户"""
        # 先注册
        app.register_and_login("测试用户", "320101199001011234")
        
        # 开通账户
        account_id = app.open_account()
        assert account_id is not None
        assert app.current_account_id == account_id
    
    def test_quick_subscribe(self, app):
        """测试快速申购"""
        # 注册并开通账户
        app.register_and_login("测试用户", "320101199001011234")
        app.open_account()
        
        # 获取产品
        products = app.client.get_products()
        if not products:
            pytest.skip("没有可用的基金产品")
        
        product_id = products[0]['product_id']
        
        # 申购
        result = app.quick_subscribe(product_id, 10000.00)
        assert result['subscribe_result'] is not None
        assert result['current_assets'] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

