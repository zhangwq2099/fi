"""
测试业务服务层
"""
import pytest
from decimal import Decimal
from datetime import date
from repository import Repository
from service import FundService


class TestFundService:
    """测试基金服务"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        repo = Repository()
        return FundService(repo)
    
    def test_create_user(self, service):
        """测试创建用户"""
        user = service.create_user(
            user_name="测试用户",
            user_type="PERSONAL",
            identity_no="320101199001011234"
        )
        assert user.user_id is not None
        assert user.user_name == "测试用户"
        
        # 验证余额已初始化
        balance = service.repo.get_user_balance(user.user_id)
        assert balance is not None
    
    def test_open_fund_account(self, service):
        """测试开通基金账户"""
        # 先创建用户
        user = service.create_user(user_name="测试用户")
        
        # 开通账户
        account = service.open_fund_account(user.user_id)
        assert account.fund_account_id is not None
        assert account.user_id == user.user_id
    
    def test_create_fund_product(self, service):
        """测试创建基金产品"""
        product = service.create_fund_product(
            product_code="001234",
            product_name="测试基金",
            product_type="EQUITY"
        )
        assert product.product_id is not None
        assert product.product_code == "001234"
    
    def test_subscribe_fund(self, service):
        """测试申购基金"""
        # 创建用户
        user = service.create_user(user_name="测试用户")
        
        # 初始化余额
        balance = service.repo.get_user_balance(user.user_id)
        balance.available_balance = Decimal("100000.00")
        balance.total_balance = Decimal("100000.00")
        service.repo.update_user_balance(balance)
        
        # 开通账户
        account = service.open_fund_account(user.user_id)
        
        # 创建产品
        product = service.create_fund_product(
            product_code="001234",
            product_name="测试基金"
        )
        
        # 添加净值
        service.create_fund_nav(
            product_id=product.product_id,
            net_value=Decimal("1.2345")
        )
        
        # 申购
        result = service.subscribe_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            amount=Decimal("10000.00")
        )
        
        assert result['entrust_id'] is not None
        assert result['share'] > 0
        
        # 验证份额已增加
        share = service.repo.get_fund_share(account.fund_account_id, product.product_id)
        assert share is not None
        assert share.total_share > 0
    
    def test_redeem_fund(self, service):
        """测试赎回基金"""
        # 创建用户
        user = service.create_user(user_name="测试用户")
        
        # 初始化余额
        balance = service.repo.get_user_balance(user.user_id)
        balance.available_balance = Decimal("100000.00")
        balance.total_balance = Decimal("100000.00")
        service.repo.update_user_balance(balance)
        
        # 开通账户
        account = service.open_fund_account(user.user_id)
        
        # 创建产品
        product = service.create_fund_product(
            product_code="001234",
            product_name="测试基金"
        )
        
        # 添加净值
        service.create_fund_nav(
            product_id=product.product_id,
            net_value=Decimal("1.2345")
        )
        
        # 先申购
        subscribe_result = service.subscribe_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            amount=Decimal("10000.00")
        )
        
        # 再赎回部分份额
        redeem_share = Decimal(str(subscribe_result['share'])) * Decimal("0.3")
        redeem_result = service.redeem_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            share=redeem_share
        )
        
        assert redeem_result['entrust_id'] is not None
        assert redeem_result['amount'] > 0
    
    def test_calculate_user_assets(self, service):
        """测试计算用户资产"""
        # 创建用户
        user = service.create_user(user_name="测试用户")
        
        # 初始化余额
        balance = service.repo.get_user_balance(user.user_id)
        balance.available_balance = Decimal("50000.00")
        balance.total_balance = Decimal("50000.00")
        service.repo.update_user_balance(balance)
        
        # 开通账户
        account = service.open_fund_account(user.user_id)
        
        # 创建产品
        product = service.create_fund_product(
            product_code="001234",
            product_name="测试基金"
        )
        
        # 添加净值
        service.create_fund_nav(
            product_id=product.product_id,
            net_value=Decimal("1.2345")
        )
        
        # 申购
        service.subscribe_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            amount=Decimal("10000.00")
        )
        
        # 计算资产
        assets = service.calculate_user_assets(user.user_id)
        
        assert assets['total_asset'] > 0
        assert assets['total_balance'] > 0
        assert assets['total_fund_asset'] > 0
        assert len(assets['fund_assets']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

