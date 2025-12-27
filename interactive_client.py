"""
交互式基金交易客户端
支持手工输入参数进行开户、申购、赎回等业务操作
"""
import json
from client import FundClient, FundTradingApp
from typing import Optional, Dict, Any
import sys


class InteractiveClient:
    """交互式客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = "demo_token_2025"):
        """初始化交互式客户端"""
        try:
            self.client = FundClient(base_url=base_url, token=token)
            self.app = FundTradingApp(self.client)
            print("✓ 已连接到基金交易服务")
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            sys.exit(1)
    
    def print_menu(self):
        """打印主菜单"""
        print("\n" + "="*60)
        print("           基金交易系统 - 交互式客户端")
        print("="*60)
        print("1.  创建用户")
        print("2.  查询用户信息")
        print("3.  开通基金账户（开户）")
        print("4.  查询基金产品列表")
        print("5.  申购基金")
        print("6.  赎回基金")
        print("7.  查询用户资产")
        print("8.  创建基金产品（管理员）")
        print("9.  创建基金净值（管理员）")
        print("10. 完整业务流程演示")
        print("0.  退出")
        print("="*60)
    
    def input_with_prompt(self, prompt: str, default: Optional[str] = None, required: bool = True) -> str:
        """带提示的输入"""
        if default:
            full_prompt = f"{prompt} [默认: {default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        while True:
            value = input(full_prompt).strip()
            if value:
                return value
            elif default:
                return default
            elif not required:
                return ""
            else:
                print("  此字段为必填项，请重新输入")
    
    def input_number(self, prompt: str, default: Optional[float] = None, min_val: Optional[float] = None, required: bool = True) -> Optional[float]:
        """输入数字"""
        while True:
            try:
                value_str = self.input_with_prompt(prompt, str(default) if default else None, required=required)
                if not value_str and not required:
                    return None
                value = float(value_str)
                if min_val is not None and value < min_val:
                    print(f"  数值必须 >= {min_val}")
                    continue
                return value
            except ValueError:
                print("  请输入有效的数字")
    
    def print_result(self, title: str, data: Any):
        """打印结果"""
        print(f"\n【{title}】")
        print("-" * 60)
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data, 1):
                print(f"\n  产品 {i}:")
                if isinstance(item, dict):
                    for key, value in item.items():
                        print(f"    {key}: {value}")
                else:
                    print(f"    {item}")
        else:
            print(f"  {data}")
        print("-" * 60)
    
    def create_user(self):
        """创建用户"""
        print("\n【创建用户】")
        print("-" * 60)
        user_name = self.input_with_prompt("用户姓名")
        identity_no = self.input_with_prompt("身份证号")
        user_type = self.input_with_prompt("用户类型", "PERSONAL", required=False) or "PERSONAL"
        phone = self.input_with_prompt("手机号", required=False) or "13800138000"
        email = self.input_with_prompt("邮箱", required=False) or f"{user_name}@example.com"
        
        try:
            user_id = self.client.create_user(
                user_name=user_name,
                identity_no=identity_no,
                user_type=user_type,
                phone=phone,
                email=email
            )
            self.app.current_user_id = user_id
            self.print_result("创建成功", {"用户ID": user_id, "用户姓名": user_name})
            return user_id
        except Exception as e:
            print(f"✗ 创建失败: {e}")
            return None
    
    def get_user(self):
        """查询用户信息"""
        print("\n【查询用户信息】")
        print("-" * 60)
        user_id = self.input_with_prompt("用户ID")
        
        try:
            user_info = self.client.get_user(user_id)
            self.print_result("用户信息", user_info)
            return user_info
        except Exception as e:
            print(f"✗ 查询失败: {e}")
            return None
    
    def open_account(self):
        """开通基金账户"""
        print("\n【开通基金账户】")
        print("-" * 60)
        
        if not self.app.current_user_id:
            user_id = self.input_with_prompt("用户ID")
        else:
            user_id = self.app.current_user_id
            print(f"使用当前用户ID: {user_id}")
            use_current = input("是否使用当前用户? (Y/n): ").strip().lower()
            if use_current != 'n':
                pass
            else:
                user_id = self.input_with_prompt("用户ID")
        
        account_type = self.input_with_prompt("账户类型", "INDIVIDUAL", required=False) or "INDIVIDUAL"
        
        try:
            account_id = self.client.open_fund_account(user_id, account_type)
            self.app.current_account_id = account_id
            self.print_result("开户成功", {
                "基金账户ID": account_id,
                "用户ID": user_id,
                "账户类型": account_type
            })
            return account_id
        except Exception as e:
            print(f"✗ 开户失败: {e}")
            return None
    
    def list_products(self):
        """查询基金产品列表"""
        print("\n【查询基金产品列表】")
        print("-" * 60)
        product_type = self.input_with_prompt("产品类型筛选（可选，如EQUITY/BOND/MIXED/MONETARY）", required=False)
        
        try:
            products = self.client.get_products(product_type if product_type else None)
            if products:
                self.print_result(f"找到 {len(products)} 个产品", products)
            else:
                print("  暂无产品")
            return products
        except Exception as e:
            print(f"✗ 查询失败: {e}")
            return None
    
    def subscribe_fund(self):
        """申购基金"""
        print("\n【申购基金】")
        print("-" * 60)
        
        if not self.app.current_account_id:
            fund_account_id = self.input_with_prompt("基金账户ID")
        else:
            fund_account_id = self.app.current_account_id
            print(f"使用当前账户ID: {fund_account_id}")
            use_current = input("是否使用当前账户? (Y/n): ").strip().lower()
            if use_current != 'n':
                pass
            else:
                fund_account_id = self.input_with_prompt("基金账户ID")
        
        product_id = self.input_with_prompt("产品ID")
        amount = self.input_number("申购金额（元）", min_val=0.01)
        
        try:
            result = self.client.subscribe_fund(fund_account_id, product_id, amount)
            self.print_result("申购成功", result)
            return result
        except Exception as e:
            print(f"✗ 申购失败: {e}")
            return None
    
    def redeem_fund(self):
        """赎回基金"""
        print("\n【赎回基金】")
        print("-" * 60)
        
        if not self.app.current_account_id:
            fund_account_id = self.input_with_prompt("基金账户ID")
        else:
            fund_account_id = self.app.current_account_id
            print(f"使用当前账户ID: {fund_account_id}")
            use_current = input("是否使用当前账户? (Y/n): ").strip().lower()
            if use_current != 'n':
                pass
            else:
                fund_account_id = self.input_with_prompt("基金账户ID")
        
        product_id = self.input_with_prompt("产品ID")
        share = self.input_number("赎回份额", min_val=0.01)
        
        try:
            result = self.client.redeem_fund(fund_account_id, product_id, share)
            self.print_result("赎回成功", result)
            return result
        except Exception as e:
            print(f"✗ 赎回失败: {e}")
            return None
    
    def get_assets(self):
        """查询用户资产"""
        print("\n【查询用户资产】")
        print("-" * 60)
        
        if not self.app.current_user_id:
            user_id = self.input_with_prompt("用户ID")
        else:
            user_id = self.app.current_user_id
            print(f"使用当前用户ID: {user_id}")
            use_current = input("是否使用当前用户? (Y/n): ").strip().lower()
            if use_current != 'n':
                pass
            else:
                user_id = self.input_with_prompt("用户ID")
        
        try:
            assets = self.client.get_user_assets(user_id)
            self.print_result("用户资产", assets)
            return assets
        except Exception as e:
            print(f"✗ 查询失败: {e}")
            return None
    
    def create_product(self):
        """创建基金产品"""
        print("\n【创建基金产品】")
        print("-" * 60)
        product_code = self.input_with_prompt("产品代码")
        product_name = self.input_with_prompt("产品名称")
        product_type = self.input_with_prompt("产品类型（EQUITY/BOND/MIXED/MONETARY）", "EQUITY", required=False) or "EQUITY"
        risk_level = self.input_with_prompt("风险等级（R1-R5）", "R3", required=False) or "R3"
        fund_company = self.input_with_prompt("基金公司", required=False) or "测试基金公司"
        
        try:
            product_id = self.client.create_product(
                product_code=product_code,
                product_name=product_name,
                product_type=product_type,
                risk_level=risk_level,
                fund_company=fund_company
            )
            self.print_result("创建成功", {"产品ID": product_id, "产品名称": product_name})
            return product_id
        except Exception as e:
            print(f"✗ 创建失败: {e}")
            return None
    
    def create_nav(self):
        """创建基金净值"""
        print("\n【创建基金净值】")
        print("-" * 60)
        product_id = self.input_with_prompt("产品ID")
        net_value = self.input_number("单位净值", min_val=0.01)
        accumulated_nav = self.input_number("累计净值（可选，直接回车跳过）", min_val=0.01, required=False)
        
        try:
            nav_data = {"product_id": product_id, "net_value": net_value}
            if accumulated_nav:
                nav_data["accumulated_nav"] = accumulated_nav
            
            nav_id = self.client.create_nav(**nav_data)
            self.print_result("创建成功", {"净值ID": nav_id, "单位净值": net_value})
            return nav_id
        except Exception as e:
            print(f"✗ 创建失败: {e}")
            return None
    
    def demo_workflow(self):
        """完整业务流程演示"""
        print("\n【完整业务流程演示】")
        print("-" * 60)
        print("此功能将演示：创建用户 -> 开户 -> 申购 -> 赎回的完整流程")
        confirm = input("是否继续? (Y/n): ").strip().lower()
        if confirm == 'n':
            return
        
        self.app.demo_trading()
    
    def run(self):
        """运行交互式客户端"""
        print("\n欢迎使用基金交易系统交互式客户端！")
        print("提示：您可以在操作过程中使用当前用户/账户，系统会记住您的选择")
        
        while True:
            try:
                self.print_menu()
                choice = input("\n请选择操作 (0-10): ").strip()
                
                if choice == '0':
                    print("\n感谢使用，再见！")
                    break
                elif choice == '1':
                    self.create_user()
                elif choice == '2':
                    self.get_user()
                elif choice == '3':
                    self.open_account()
                elif choice == '4':
                    self.list_products()
                elif choice == '5':
                    self.subscribe_fund()
                elif choice == '6':
                    self.redeem_fund()
                elif choice == '7':
                    self.get_assets()
                elif choice == '8':
                    self.create_product()
                elif choice == '9':
                    self.create_nav()
                elif choice == '10':
                    self.demo_workflow()
                else:
                    print("无效的选择，请重新输入")
                
                input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n\n操作已取消")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
                input("按回车键继续...")


if __name__ == "__main__":
    # 可以自定义服务地址和token
    import sys
    
    base_url = "http://localhost:8000"
    token = "demo_token_2025"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        token = sys.argv[2]
    
    client = InteractiveClient(base_url=base_url, token=token)
    client.run()

