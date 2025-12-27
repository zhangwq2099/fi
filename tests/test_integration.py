"""
集成测试 - 完整的业务流程测试
"""
import sys
import os
# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from decimal import Decimal
from repository import Repository
from service import FundService


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        repo = Repository()
        return FundService(repo)
    
    def test_complete_trading_flow(self, service):
        """测试完整的交易流程"""
        # 1. 创建用户
        user = service.create_user(
            user_name="集成测试用户",
            user_type="PERSONAL",
            identity_no="320101199001011234",
            phone="13800138000",
            email="test@example.com"
        )
        assert user.user_id is not None
        
        # 2. 初始化用户余额
        balance = service.repo.get_user_balance(user.user_id)
        balance.available_balance = Decimal("100000.00")
        balance.total_balance = Decimal("100000.00")
        service.repo.update_user_balance(balance)
        
        # 3. 开通基金账户
        account = service.open_fund_account(user.user_id)
        assert account.fund_account_id is not None
        
        # 4. 创建基金产品
        product = service.create_fund_product(
            product_code="001234",
            product_name="集成测试基金",
            product_type="EQUITY",
            risk_level="R3",
            fund_company="测试基金公司"
        )
        assert product.product_id is not None
        
        # 5. 添加基金净值
        nav = service.create_fund_nav(
            product_id=product.product_id,
            net_value=Decimal("1.2345"),
            accumulated_nav=Decimal("1.5678")
        )
        assert nav.nav_id is not None
        
        # 6. 申购基金
        subscribe_result = service.subscribe_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            amount=Decimal("10000.00")
        )
        assert subscribe_result['entrust_id'] is not None
        assert subscribe_result['share'] > 0
        
        # 7. 验证份额
        share = service.repo.get_fund_share(account.fund_account_id, product.product_id)
        assert share is not None
        assert share.total_share > 0
        
        # 8. 验证余额变化
        updated_balance = service.repo.get_user_balance(user.user_id)
        assert updated_balance.available_balance < balance.available_balance
        
        # 9. 计算资产
        assets = service.calculate_user_assets(user.user_id)
        assert assets['total_asset'] > 0
        assert assets['total_fund_asset'] > 0
        
        # 10. 赎回部分份额
        redeem_share = Decimal(str(subscribe_result['share'])) * Decimal("0.3")
        redeem_result = service.redeem_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            share=redeem_share
        )
        assert redeem_result['entrust_id'] is not None
        assert redeem_result['amount'] > 0
        
        # 11. 验证份额减少
        updated_share = service.repo.get_fund_share(account.fund_account_id, product.product_id)
        assert updated_share.total_share < share.total_share
        
        # 12. 验证余额增加
        final_balance = service.repo.get_user_balance(user.user_id)
        assert final_balance.available_balance > updated_balance.available_balance
        
        # 13. 最终资产计算
        final_assets = service.calculate_user_assets(user.user_id)
        assert final_assets['total_asset'] > 0
        assert final_assets['total_balance'] > 0
        assert final_assets['total_fund_asset'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


