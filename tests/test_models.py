"""
测试数据模型
"""
import pytest
from datetime import date, datetime
from decimal import Decimal
from models import (
    User, FundAccount, FundProduct, FundNetValue, UserBalance, FundShare,
    EntrustBase, FundTransactionEntrust, UserTotalAsset,
    UserType, UserStatus, BusinessType, EntrustStatus, TransactionType
)


class TestUser:
    """测试用户模型"""
    
    def test_create_user(self):
        """测试创建用户"""
        user = User(
            user_id="USER_001",
            user_name="测试用户",
            user_type=UserType.PERSONAL,
            user_status=UserStatus.ACTIVE,
            identity_no="320101199001011234",
            phone="13800138000",
            email="test@example.com"
        )
        assert user.user_id == "USER_001"
        assert user.user_name == "测试用户"
        assert user.user_type == UserType.PERSONAL
    
    def test_user_defaults(self):
        """测试用户默认值"""
        user = User(user_id="USER_002")
        assert user.user_type == UserType.PERSONAL
        assert user.user_status == UserStatus.ACTIVE


class TestFundAccount:
    """测试基金账户模型"""
    
    def test_create_fund_account(self):
        """测试创建基金账户"""
        account = FundAccount(
            fund_account_id="ACC_001",
            user_id="USER_001",
            account_no="F20250101001",
            account_type="INDIVIDUAL",
            open_date=date.today()
        )
        assert account.fund_account_id == "ACC_001"
        assert account.account_status == "ACTIVE"


class TestFundProduct:
    """测试基金产品模型"""
    
    def test_create_fund_product(self):
        """测试创建基金产品"""
        product = FundProduct(
            product_id="PROD_001",
            product_code="001234",
            product_name="测试基金",
            product_type="EQUITY",
            issue_date=date.today()
        )
        assert product.product_id == "PROD_001"
        assert product.product_status == "ACTIVE"


class TestUserBalance:
    """测试用户余额模型"""
    
    def test_create_user_balance(self):
        """测试创建用户余额"""
        balance = UserBalance(
            balance_id="BAL_001",
            user_id="USER_001",
            available_balance=Decimal("10000.00"),
            frozen_balance=Decimal("1000.00")
        )
        assert balance.available_balance == Decimal("10000.00")
        assert balance.total_balance == Decimal("11000.00")


class TestFundShare:
    """测试基金份额模型"""
    
    def test_create_fund_share(self):
        """测试创建基金份额"""
        share = FundShare(
            share_id="SHARE_001",
            fund_account_id="ACC_001",
            product_id="PROD_001",
            total_share=Decimal("1000.00"),
            available_share=Decimal("800.00"),
            frozen_share=Decimal("200.00")
        )
        assert share.total_share == Decimal("1000.00")
        assert share.available_share == Decimal("800.00")


class TestEntrustBase:
    """测试委托基础模型"""
    
    def test_create_entrust(self):
        """测试创建委托"""
        entrust = EntrustBase(
            entrust_id="ENT_001",
            business_type=BusinessType.FUND_SUBSCRIBE,
            status=EntrustStatus.PENDING,
            user_id="USER_001",
            request_data={"amount": 10000}
        )
        assert entrust.business_type == BusinessType.FUND_SUBSCRIBE
        assert entrust.status == EntrustStatus.PENDING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

