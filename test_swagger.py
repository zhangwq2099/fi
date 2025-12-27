"""
测试 Swagger UI 和 OpenAPI schema 是否正常工作
"""
import requests
import json

def test_swagger():
    """测试 Swagger UI 相关端点"""
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("测试 Swagger UI 和 OpenAPI")
    print("=" * 50)
    
    # 测试根路径
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ 根路径访问成功: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"✗ 根路径访问失败: {e}")
        return
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"✓ 健康检查成功: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
    
    # 测试 OpenAPI JSON
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            print(f"✓ OpenAPI JSON 访问成功")
            print(f"  OpenAPI 版本: {schema.get('openapi')}")
            print(f"  标题: {schema.get('info', {}).get('title')}")
            print(f"  路径数量: {len(schema.get('paths', {}))}")
            print(f"  路径列表: {list(schema.get('paths', {}).keys())[:5]}")
        else:
            print(f"✗ OpenAPI JSON 访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ OpenAPI JSON 访问失败: {e}")
    
    # 测试 Swagger UI HTML
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print(f"✓ Swagger UI HTML 访问成功: {response.status_code}")
            print(f"  HTML 长度: {len(response.text)} 字符")
            if "swagger" in response.text.lower() or "openapi" in response.text.lower():
                print("  ✓ 包含 Swagger/OpenAPI 内容")
            else:
                print("  ⚠ 可能不包含 Swagger 内容")
        else:
            print(f"✗ Swagger UI HTML 访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ Swagger UI HTML 访问失败: {e}")
    
    # 测试 ReDoc
    try:
        response = requests.get(f"{base_url}/redoc")
        if response.status_code == 200:
            print(f"✓ ReDoc 访问成功: {response.status_code}")
        else:
            print(f"✗ ReDoc 访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ ReDoc 访问失败: {e}")
    
    print("=" * 50)
    print("测试完成")
    print("=" * 50)
    print("\n如果 Swagger UI 页面空白，请尝试：")
    print("1. 清除浏览器缓存（Ctrl+Shift+Delete）")
    print("2. 使用无痕模式访问")
    print("3. 检查浏览器控制台是否有错误（F12）")
    print("4. 尝试访问: http://localhost:8000/openapi.json")
    print("5. 确保服务正在运行: python main_v2.py")

if __name__ == "__main__":
    test_swagger()

