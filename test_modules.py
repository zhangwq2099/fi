"""
测试模块功能
"""
import sys

def test_imports():
    """测试模块导入"""
    print("=" * 50)
    print("Testing Module Imports")
    print("=" * 50)
    
    try:
        # 测试公共模块
        print("\n1. Testing common modules...")
        from common.enums import UserType, UserStatus
        from common.repository import get_repository
        print("   ✓ Common modules imported successfully")
        
        # 测试用户模块
        print("\n2. Testing user module...")
        from modules.user.user_schema import User, UserCreateRequest
        from modules.user.user_app import UserApp
        print("   ✓ User module imported successfully")
        
        # 测试用户资产模块
        print("\n3. Testing user_asset module...")
        from modules.user_asset.user_asset_schema import UserBalance, UserAssetsResponse
        from modules.user_asset.user_asset_app import UserAssetApp
        print("   ✓ User asset module imported successfully")
        
        # 测试主应用
        print("\n4. Testing main application...")
        from main_v2 import app
        print("   ✓ Main application imported successfully")
        
        print("\n" + "=" * 50)
        print("All imports successful!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "=" * 50)
    print("Testing Basic Functionality")
    print("=" * 50)
    
    try:
        from modules.user.user_app import UserApp
        from modules.user.user_schema import UserCreateRequest
        from modules.user_asset.user_asset_app import UserAssetApp
        
        # 创建用户
        print("\n1. Creating user...")
        user_app = UserApp()
        request = UserCreateRequest(
            user_name="Test User",
            user_type="PERSONAL",
            identity_no="320101199001011234",
            phone="13800138000",
            email="test@example.com"
        )
        user = user_app.create_user(request)
        print(f"   ✓ User created: {user.user_id}")
        
        # 获取用户
        print("\n2. Getting user...")
        retrieved_user = user_app.get_user(user.user_id)
        if retrieved_user:
            print(f"   ✓ User retrieved: {retrieved_user.user_name}")
        else:
            print("   ✗ User not found")
            return False
        
        # 获取用户余额
        print("\n3. Getting user balance...")
        asset_app = UserAssetApp()
        balance = asset_app.get_user_balance(user.user_id)
        if balance:
            print(f"   ✓ Balance retrieved: {balance.total_balance}")
        else:
            print("   ✗ Balance not found")
            return False
        
        # 计算用户资产
        print("\n4. Calculating user assets...")
        assets = asset_app.calculate_user_assets(user.user_id)
        print(f"   ✓ Assets calculated:")
        print(f"     - Total Asset: {assets.total_asset}")
        print(f"     - Total Balance: {assets.total_balance}")
        print(f"     - Total Fund Asset: {assets.total_fund_asset}")
        
        print("\n" + "=" * 50)
        print("All functionality tests passed!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nStarting Module Tests...\n")
    
    # 测试导入
    import_ok = test_imports()
    
    if import_ok:
        # 测试功能
        func_ok = test_basic_functionality()
        
        if func_ok:
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Functionality tests failed!")
            sys.exit(1)
    else:
        print("\n✗ Import tests failed!")
        sys.exit(1)


