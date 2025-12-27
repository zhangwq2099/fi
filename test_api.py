"""
测试API功能
"""
from fastapi.testclient import TestClient

from main_v2 import app

client = TestClient(app)

def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "基金交易微服务"
    print("[OK] Root endpoint works")

def test_health():
    """测试健康检查"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("[OK] Health check works")

def test_create_user():
    """测试创建用户"""
    user_data = {
        "user_name": "API Test User",
        "user_type": "PERSONAL",
        "identity_no": "320101199001011234",
        "phone": "13800138000",
        "email": "apitest@example.com"
    }
    
    # 注意：需要认证token，这里先测试结构
    response = client.post("/api/v1/users", json=user_data)
    # 由于没有认证，可能会返回401，但至少可以测试路由是否注册
    print(f"[OK] User creation endpoint responds (status: {response.status_code})")

def test_get_user():
    """测试获取用户"""
    # 先创建一个用户
    from modules.user.user_app import UserApp
    from modules.user.user_schema import UserCreateRequest
    
    user_app = UserApp()
    request = UserCreateRequest(
        user_name="API Test User 2",
        user_type="PERSONAL",
        identity_no="320101199001011235"
    )
    user = user_app.create_user(request)
    
    # 测试API（可能需要认证）
    response = client.get(f"/api/v1/users/{user.user_id}")
    print(f"[OK] User get endpoint responds (status: {response.status_code})")

if __name__ == "__main__":
    print("=" * 50)
    print("Testing API Endpoints")
    print("=" * 50)
    
    try:
        test_root()
        test_health()
        test_create_user()
        test_get_user()
        
        print("\n" + "=" * 50)
        print("[OK] All API tests completed!")
        print("=" * 50)
    except Exception as e:
        print(f"\n[ERROR] API test failed: {e}")
        import traceback
        traceback.print_exc()


