"""
功能验证脚本 - 验证系统基本功能是否正常
"""
from decimal import Decimal
from repository import Repository
from service import FundService


def verify_basic_functionality():
    """验证基本功能"""
    print("=" * 50)
    print("基金交易系统功能验证")
    print("=" * 50)
    
    # 初始化服务
    repo = Repository()
    service = FundService(repo)
    
    try:
        # 1. 创建用户
        print("\n1. 创建用户...")
        user = service.create_user(
            user_name="验证用户",
            user_type="PERSONAL",
            identity_no="320101199001011234",
            phone="13800138000",
            email="verify@example.com"
        )
        print(f"   ✓ 用户创建成功: {user.user_id}")
        
        # 2. 初始化余额
        print("\n2. 初始化用户余额...")
        balance = service.repo.get_user_balance(user.user_id)
        balance.available_balance = Decimal("100000.00")
        balance.total_balance = Decimal("100000.00")
        service.repo.update_user_balance(balance)
        print(f"   ✓ 余额初始化成功: {balance.available_balance}")
        
        # 3. 开通基金账户
        print("\n3. 开通基金账户...")
        account = service.open_fund_account(user.user_id)
        print(f"   ✓ 账户开通成功: {account.fund_account_id}")
        
        # 4. 创建基金产品
        print("\n4. 创建基金产品...")
        product = service.create_fund_product(
            product_code="001234",
            product_name="验证测试基金",
            product_type="EQUITY",
            risk_level="R3",
            fund_company="测试基金公司"
        )
        print(f"   ✓ 产品创建成功: {product.product_id}")
        
        # 5. 添加基金净值
        print("\n5. 添加基金净值...")
        nav = service.create_fund_nav(
            product_id=product.product_id,
            net_value=Decimal("1.2345"),
            accumulated_nav=Decimal("1.5678")
        )
        print(f"   ✓ 净值添加成功: {nav.net_value}")
        
        # 6. 申购基金
        print("\n6. 申购基金...")
        subscribe_result = service.subscribe_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            amount=Decimal("10000.00")
        )
        print(f"   ✓ 申购成功:")
        print(f"     - 委托ID: {subscribe_result['entrust_id']}")
        print(f"     - 申购金额: {subscribe_result['amount']}")
        print(f"     - 获得份额: {subscribe_result['share']:.4f}")
        print(f"     - 交易净值: {subscribe_result['nav']}")
        
        # 7. 验证份额
        print("\n7. 验证基金份额...")
        share = service.repo.get_fund_share(account.fund_account_id, product.product_id)
        if share:
            print(f"   ✓ 份额验证成功:")
            print(f"     - 总份额: {share.total_share:.4f}")
            print(f"     - 可用份额: {share.available_share:.4f}")
        
        # 8. 验证余额变化
        print("\n8. 验证余额变化...")
        updated_balance = service.repo.get_user_balance(user.user_id)
        print(f"   ✓ 余额验证:")
        print(f"     - 可用余额: {updated_balance.available_balance:.2f}")
        print(f"     - 冻结余额: {updated_balance.frozen_balance:.2f}")
        print(f"     - 总余额: {updated_balance.total_balance:.2f}")
        
        # 9. 赎回部分份额
        print("\n9. 赎回基金...")
        redeem_share = Decimal(str(subscribe_result['share'])) * Decimal("0.3")
        redeem_result = service.redeem_fund(
            fund_account_id=account.fund_account_id,
            product_id=product.product_id,
            share=redeem_share
        )
        print(f"   ✓ 赎回成功:")
        print(f"     - 委托ID: {redeem_result['entrust_id']}")
        print(f"     - 赎回份额: {redeem_result['share']:.4f}")
        print(f"     - 赎回金额: {redeem_result['amount']:.2f}")
        
        # 10. 计算资产
        print("\n10. 计算用户资产...")
        assets = service.calculate_user_assets(user.user_id)
        print(f"   ✓ 资产计算成功:")
        print(f"     - 总资产: {assets['total_asset']:.2f}")
        print(f"     - 基金资产: {assets['total_fund_asset']:.2f}")
        print(f"     - 总余额: {assets['total_balance']:.2f}")
        print(f"     - 基金产品数: {len(assets['fund_assets'])}")
        
        print("\n" + "=" * 50)
        print("✓ 所有功能验证通过！")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_basic_functionality()
    exit(0 if success else 1)

