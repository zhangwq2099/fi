"""
测试客户端接口
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
from datetime import datetime
from pathlib import Path

import pytest

from client import FundClient, FundTradingApp

# ==================== 日志配置 ====================

# 日志文件路径
LOG_DIR = Path(__file__).parent
LOG_FILE = LOG_DIR / "test_client.log"

# 创建自定义控制台处理器，处理编码问题
class SafeConsoleHandler(logging.StreamHandler):
    """安全的控制台处理器，处理 Windows 编码问题"""
    def emit(self, record):
        try:
            msg = self.format(record)
            # 尝试使用 UTF-8 编码，失败则使用 ASCII
            try:
                self.stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # 如果控制台不支持 UTF-8，则使用 ASCII 安全编码
                safe_msg = msg.encode('ascii', 'replace').decode('ascii')
                self.stream.write(safe_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# 清理旧的日志配置（如果存在）
def _cleanup_logging():
    """清理旧的日志配置"""
    root_logger = logging.getLogger()
    # 关闭所有现有的处理器
    for handler in root_logger.handlers[:]:
        try:
            handler.close()
            root_logger.removeHandler(handler)
        except Exception:
            pass

# 清空日志文件（安全方式）
def _clear_log_file():
    """安全地清空日志文件"""
    if LOG_FILE.exists():
        try:
            # 先尝试删除文件
            LOG_FILE.unlink()
        except (PermissionError, OSError) as e:
            # 如果无法删除（文件被占用），则使用 'w' 模式打开会清空内容
            # 这是 Windows 上的常见情况，比如 IDE 正在查看日志文件
            try:
                with open(LOG_FILE, 'w', encoding='utf-8') as f:
                    f.write('')  # 清空文件内容
            except Exception:
                # 如果还是失败，就忽略，让 FileHandler 的 'w' 模式处理
                pass

# 清理旧的日志配置
_cleanup_logging()

# 清空日志文件
_clear_log_file()

# 配置日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 配置根日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        # 文件处理器（UTF-8 编码，'w' 模式会清空文件）
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        # 控制台处理器（安全编码）
        SafeConsoleHandler(sys.stdout)
    ],
    force=True  # 强制重新配置，避免多次调用的问题
)

# 获取测试专用的日志记录器
test_logger = logging.getLogger("test_client")
test_logger.setLevel(logging.DEBUG)

# 记录测试开始
test_logger.info("=" * 80)
test_logger.info(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
test_logger.info(f"日志文件: {LOG_FILE.absolute()}")
test_logger.info("=" * 80)


class TestFundClient:
    """测试基金客户端"""
    
    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        test_logger.info("创建 FundClient 实例")
        # 注意：需要先启动服务
        # test_connection=False 避免在测试初始化时连接服务器
        client = FundClient(base_url="http://localhost:8000", test_connection=False)
        test_logger.debug(f"客户端创建成功，base_url: {client.base_url}")
        return client
    
    def test_health_check(self, client):
        """测试健康检查"""
        test_logger.info("=" * 60)
        test_logger.info("开始测试: test_health_check")
        test_logger.info("=" * 60)
        
        try:
            test_logger.info("调用 health_check()")
            result = client.health_check()
            test_logger.info(f"健康检查结果: {result}")
            assert result['status'] == 'healthy'
            test_logger.info("✓ 健康检查测试通过")
        except Exception as e:
            test_logger.error(f"✗ 健康检查测试失败: {e}", exc_info=True)
            raise
    
    def test_create_user(self, client):
        """测试创建用户"""
        test_logger.info("=" * 60)
        test_logger.info("开始测试: test_create_user")
        test_logger.info("=" * 60)
        
        try:
            test_logger.info("创建用户: 测试用户, 320101199001011234")
            user_id = client.create_user(
                user_name="测试用户",
                identity_no="320101199001011234"
            )
            test_logger.info(f"用户创建成功，user_id: {user_id}")
            assert user_id is not None
            
            # 获取用户信息
            test_logger.info(f"获取用户信息: {user_id}")
            user = client.get_user(user_id)
            test_logger.info(f"用户信息: {user}")
            assert user['user_id'] == user_id
            test_logger.info("✓ 创建用户测试通过")
        except Exception as e:
            test_logger.error(f"✗ 创建用户测试失败: {e}", exc_info=True)
            raise
    
    def test_open_fund_account(self, client):
        """测试开通基金账户"""
        test_logger.info("=" * 60)
        test_logger.info("开始测试: test_open_fund_account")
        test_logger.info("=" * 60)
        
        try:
            # 先创建用户
            test_logger.info("步骤 1: 创建用户")
            user_id = client.create_user(
                user_name="测试用户",
                identity_no="320101199001011234"
            )
            test_logger.info(f"用户创建成功，user_id: {user_id}")
            
            # 开通账户
            test_logger.info(f"步骤 2: 开通基金账户，user_id: {user_id}")
            account_id = client.open_fund_account(user_id)
            test_logger.info(f"基金账户开通成功，account_id: {account_id}")
            assert account_id is not None
            test_logger.info("✓ 开通基金账户测试通过")
        except Exception as e:
            test_logger.error(f"✗ 开通基金账户测试失败: {e}", exc_info=True)
            raise
    
    def test_subscribe_and_redeem(self, client):
        """测试申购和赎回流程"""
        test_logger.info("=" * 60)
        test_logger.info("开始测试: test_subscribe_and_redeem")
        test_logger.info("=" * 60)
        
        try:
            # 创建用户
            test_logger.info("步骤 1: 创建用户")
            user_id = client.create_user(
                user_name="测试用户",
                identity_no="320101199001011234"
            )
            test_logger.info(f"用户创建成功，user_id: {user_id}")
            
            # 开通账户
            test_logger.info("步骤 2: 开通基金账户")
            account_id = client.open_fund_account(user_id)
            test_logger.info(f"基金账户开通成功，account_id: {account_id}")
            
            # 获取产品列表
            test_logger.info("步骤 3: 获取产品列表")
            products = client.get_products()
            test_logger.info(f"获取到 {len(products) if products else 0} 个产品")
            if not products:
                test_logger.warning("没有可用的基金产品，跳过测试")
                pytest.skip("没有可用的基金产品")
            
            product = products[0]
            product_id = product['product_id']
            test_logger.info(f"选择产品: {product_id}, {product.get('product_name', 'N/A')}")
            
            # 申购
            test_logger.info("步骤 4: 申购基金")
            test_logger.info(f"  账户ID: {account_id}")
            test_logger.info(f"  产品ID: {product_id}")
            test_logger.info(f"  申购金额: 10000.00")
            subscribe_result = client.subscribe_fund(
                fund_account_id=account_id,
                product_id=product_id,
                amount=10000.00
            )
            test_logger.info(f"申购结果: {subscribe_result}")
            assert subscribe_result['entrust_id'] is not None
            assert subscribe_result['share'] > 0
            test_logger.info(f"申购成功，委托ID: {subscribe_result['entrust_id']}, 份额: {subscribe_result['share']}")
            
            # 等待一下
            test_logger.info("步骤 5: 等待 0.5 秒")
            time.sleep(0.5)
            
            # 赎回部分份额
            redeem_share = subscribe_result['share'] * 0.3
            test_logger.info("步骤 6: 赎回基金")
            test_logger.info(f"  账户ID: {account_id}")
            test_logger.info(f"  产品ID: {product_id}")
            test_logger.info(f"  赎回份额: {redeem_share}")
            redeem_result = client.redeem_fund(
                fund_account_id=account_id,
                product_id=product_id,
                share=redeem_share
            )
            test_logger.info(f"赎回结果: {redeem_result}")
            assert redeem_result['entrust_id'] is not None
            assert redeem_result['amount'] > 0
            test_logger.info(f"赎回成功，委托ID: {redeem_result['entrust_id']}, 金额: {redeem_result['amount']}")
            
            # 获取资产
            test_logger.info("步骤 7: 获取用户资产")
            assets = client.get_user_assets(user_id)
            test_logger.info(f"用户资产: {assets}")
            assert assets['total_asset'] > 0
            test_logger.info(f"总资产: {assets['total_asset']}")
            test_logger.info("✓ 申购和赎回测试通过")
        except Exception as e:
            test_logger.error(f"✗ 申购和赎回测试失败: {e}", exc_info=True)
            raise


class TestFundTradingApp:
    """测试基金交易应用"""
    
    @pytest.fixture
    def app(self):
        """创建应用实例"""
        test_logger.info("创建 FundTradingApp 实例")
        # test_connection=False 避免在测试初始化时连接服务器
        client = FundClient(base_url="http://localhost:8000", test_connection=False)
        app = FundTradingApp(client)
        test_logger.debug("应用实例创建成功")
        return app
    
    def test_register_and_login(self, app):
        """测试注册登录"""
        test_logger.info("=" * 60)
        test_logger.info("开始测试: test_register_and_login")
        test_logger.info("=" * 60)
        
        try:
            test_logger.info("注册并登录: 测试用户, 320101199001011234")
            user_id = app.register_and_login(
                user_name="测试用户",
                identity_no="320101199001011234"
            )
            test_logger.info(f"注册登录成功，user_id: {user_id}")
            test_logger.info(f"当前用户ID: {app.current_user_id}")
            assert user_id is not None
            assert app.current_user_id == user_id
            test_logger.info("✓ 注册登录测试通过")
        except Exception as e:
            test_logger.error(f"✗ 注册登录测试失败: {e}", exc_info=True)
            raise
    
    def test_open_account(self, app):
        """测试开通账户"""
        test_logger.info("=" * 60)
        test_logger.info("开始测试: test_open_account")
        test_logger.info("=" * 60)
        
        try:
            # 先注册
            test_logger.info("步骤 1: 注册并登录")
            app.register_and_login("测试用户", "320101199001011234")
            test_logger.info(f"当前用户ID: {app.current_user_id}")
            
            # 开通账户
            test_logger.info("步骤 2: 开通账户")
            account_id = app.open_account()
            test_logger.info(f"账户开通成功，account_id: {account_id}")
            test_logger.info(f"当前账户ID: {app.current_account_id}")
            assert account_id is not None
            assert app.current_account_id == account_id
            test_logger.info("✓ 开通账户测试通过")
        except Exception as e:
            test_logger.error(f"✗ 开通账户测试失败: {e}", exc_info=True)
            raise
    
    def test_quick_subscribe(self, app):
        """测试快速申购"""
        test_logger.info("=" * 60)
        test_logger.info("开始测试: test_quick_subscribe")
        test_logger.info("=" * 60)
        
        try:
            # 注册并开通账户
            test_logger.info("步骤 1: 注册并登录")
            app.register_and_login("测试用户", "320101199001011234")
            test_logger.info(f"当前用户ID: {app.current_user_id}")
            
            test_logger.info("步骤 2: 开通账户")
            app.open_account()
            test_logger.info(f"当前账户ID: {app.current_account_id}")
            
            # 获取产品
            test_logger.info("步骤 3: 获取产品列表")
            products = app.client.get_products()
            test_logger.info(f"获取到 {len(products) if products else 0} 个产品")
            if not products:
                test_logger.warning("没有可用的基金产品，跳过测试")
                pytest.skip("没有可用的基金产品")
            
            product_id = products[0]['product_id']
            test_logger.info(f"选择产品: {product_id}")
            
            # 申购
            test_logger.info("步骤 4: 快速申购")
            test_logger.info(f"  产品ID: {product_id}")
            test_logger.info(f"  申购金额: 10000.00")
            result = app.quick_subscribe(product_id, 10000.00)
            test_logger.info(f"快速申购结果: {result}")
            assert result['subscribe_result'] is not None
            assert result['current_assets'] is not None
            test_logger.info(f"申购成功，当前资产: {result['current_assets']}")
            test_logger.info("✓ 快速申购测试通过")
        except Exception as e:
            test_logger.error(f"✗ 快速申购测试失败: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    test_logger.info("=" * 80)
    test_logger.info("启动 pytest 测试")
    test_logger.info("=" * 80)
    
    exit_code = pytest.main([__file__, "-v", "-s"])
    
    test_logger.info("=" * 80)
    test_logger.info(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_logger.info(f"退出代码: {exit_code}")
    test_logger.info(f"日志文件位置: {LOG_FILE.absolute()}")
    test_logger.info("=" * 80)
    
    exit(exit_code)


