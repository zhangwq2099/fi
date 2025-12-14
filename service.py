"""
业务服务层 - 实现基金交易系统的核心业务逻辑
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
import uuid
from models import (
    User, FundAccount, FundProduct, FundNetValue, UserBalance, FundShare,
    EntrustBase, FundTransactionEntrust, FundAccountEntrust, ConfirmBase,
    UserTotalAsset, UserFundAsset,
    BusinessType, EntrustStatus, TransactionType, ConfirmResultStatus
)
from repository import Repository


class FundService:
    """基金交易服务"""
    
    def __init__(self, repository: Repository):
        """初始化服务"""
        self.repo = repository
    
    def _generate_id(self, prefix: str = '') -> str:
        """生成唯一ID"""
        return f"{prefix}{uuid.uuid4().hex[:16]}"
    
    # ==================== 用户管理 ====================
    
    def create_user(self, user_name: str, user_type: str = "PERSONAL",
                   identity_no: Optional[str] = None,
                   phone: Optional[str] = None,
                   email: Optional[str] = None) -> User:
        """创建用户"""
        user = User(
            user_id=self._generate_id('USER_'),
            user_name=user_name,
            user_type=user_type,
            identity_no=identity_no,
            phone=phone,
            email=email
        )
        return self.repo.create_user(user)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        return self.repo.get_user(user_id)
    
    # ==================== 基金账户管理 ====================
    
    def open_fund_account(self, user_id: str, account_type: str = "INDIVIDUAL") -> FundAccount:
        """开通基金账户"""
        # 检查用户是否存在
        user = self.repo.get_user(user_id)
        if not user:
            raise ValueError(f"用户不存在: {user_id}")
        
        # 创建基金账户
        account = FundAccount(
            fund_account_id=self._generate_id('ACC_'),
            user_id=user_id,
            account_no=f"F{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}",
            account_type=account_type,
            open_date=date.today()
        )
        
        # 创建开户委托
        entrust = EntrustBase(
            entrust_id=self._generate_id('ENT_'),
            business_type=BusinessType.ACCOUNT_OPEN,
            status=EntrustStatus.SUCCESS,
            user_id=user_id,
            request_data={"account_type": account_type},
            process_time=datetime.now(),
            complete_time=datetime.now()
        )
        self.repo.create_entrust(entrust)
        
        # 创建账户委托详情
        account_entrust = FundAccountEntrust(
            entrust_id=entrust.entrust_id,
            account_type=account_type,
            source_channel="WEB"
        )
        self.repo.create_fund_account_entrust(account_entrust)
        
        return self.repo.create_fund_account(account)
    
    def get_fund_account(self, fund_account_id: str) -> Optional[FundAccount]:
        """获取基金账户"""
        return self.repo.get_fund_account(fund_account_id)
    
    # ==================== 基金产品管理 ====================
    
    def create_fund_product(self, product_code: str, product_name: str,
                           product_type: str = "EQUITY",
                           risk_level: str = "R3",
                           fund_company: Optional[str] = None,
                           issue_date: Optional[date] = None) -> FundProduct:
        """创建基金产品"""
        product = FundProduct(
            product_id=self._generate_id('PROD_'),
            product_code=product_code,
            product_name=product_name,
            product_type=product_type,
            risk_level=risk_level,
            fund_company=fund_company,
            issue_date=issue_date or date.today()
        )
        return self.repo.create_fund_product(product)
    
    def get_fund_product(self, product_id: str) -> Optional[FundProduct]:
        """获取基金产品"""
        return self.repo.get_fund_product(product_id)
    
    def list_fund_products(self, product_type: Optional[str] = None) -> List[FundProduct]:
        """列出基金产品"""
        return self.repo.list_fund_products(product_type)
    
    # ==================== 基金净值管理 ====================
    
    def create_fund_nav(self, product_id: str, net_value: Decimal,
                       accumulated_nav: Optional[Decimal] = None,
                       nav_date: Optional[date] = None) -> FundNetValue:
        """创建基金净值"""
        nav = FundNetValue(
            nav_id=self._generate_id('NAV_'),
            product_id=product_id,
            net_value=net_value,
            accumulated_nav=accumulated_nav or net_value,
            nav_date=nav_date or date.today()
        )
        return self.repo.create_fund_net_value(nav)
    
    def get_latest_nav(self, product_id: str) -> Optional[FundNetValue]:
        """获取最新净值"""
        return self.repo.get_latest_nav(product_id)
    
    # ==================== 基金申购 ====================
    
    def subscribe_fund(self, fund_account_id: str, product_id: str, amount: Decimal) -> Dict[str, Any]:
        """申购基金"""
        # 1. 验证账户
        account = self.repo.get_fund_account(fund_account_id)
        if not account:
            raise ValueError(f"基金账户不存在: {fund_account_id}")
        
        user_id = account.user_id
        
        # 2. 验证产品
        product = self.repo.get_fund_product(product_id)
        if not product:
            raise ValueError(f"基金产品不存在: {product_id}")
        
        # 3. 获取最新净值
        nav = self.repo.get_latest_nav(product_id)
        if not nav:
            raise ValueError(f"基金产品无净值数据: {product_id}")
        
        # 4. 检查用户余额
        balance = self.repo.get_user_balance(user_id)
        if not balance:
            raise ValueError(f"用户余额不存在: {user_id}")
        
        if balance.available_balance < amount:
            raise ValueError(f"余额不足: 可用余额{balance.available_balance}, 申购金额{amount}")
        
        # 5. 计算份额
        share = amount / nav.net_value
        
        # 6. 冻结资金
        balance.available_balance -= amount
        balance.frozen_balance += amount
        self.repo.update_user_balance(balance)
        
        # 7. 创建委托
        entrust = EntrustBase(
            entrust_id=self._generate_id('ENT_'),
            business_type=BusinessType.FUND_SUBSCRIBE,
            status=EntrustStatus.PENDING,
            user_id=user_id,
            request_data={
                "fund_account_id": fund_account_id,
                "product_id": product_id,
                "amount": float(amount)
            },
            process_time=datetime.now()
        )
        self.repo.create_entrust(entrust)
        
        # 8. 创建交易委托详情
        trans_entrust = FundTransactionEntrust(
            entrust_id=entrust.entrust_id,
            fund_account_id=fund_account_id,
            product_id=product_id,
            transaction_type=TransactionType.SUBSCRIBE,
            amount=amount,
            share=share,
            nav=nav.net_value
        )
        self.repo.create_fund_transaction_entrust(trans_entrust)
        
        # 9. 处理确认（模拟立即确认）
        self._process_subscribe_confirmation(entrust.entrust_id, fund_account_id, product_id, share, amount)
        
        return {
            "entrust_id": entrust.entrust_id,
            "fund_account_id": fund_account_id,
            "product_id": product_id,
            "amount": float(amount),
            "share": float(share),
            "nav": float(nav.net_value)
        }
    
    def _process_subscribe_confirmation(self, entrust_id: str, fund_account_id: str,
                                       product_id: str, share: Decimal, amount: Decimal):
        """处理申购确认"""
        # 1. 更新委托状态
        entrust = self.repo.get_entrust(entrust_id)
        if entrust:
            entrust.status = EntrustStatus.SUCCESS
            entrust.complete_time = datetime.now()
            entrust.response_data = {
                "share": float(share),
                "nav": float(entrust.request_data.get('nav', 0))
            }
            self.repo.update_entrust(entrust)
        
        # 2. 创建确认记录
        confirm = ConfirmBase(
            confirm_id=self._generate_id('CFM_'),
            entrust_id=entrust_id,
            confirm_type="FUND_SUBSCRIBE",
            result_status=ConfirmResultStatus.SUCCESS,
            confirm_data={"share": float(share), "amount": float(amount)}
        )
        self.repo.create_confirm(confirm)
        
        # 3. 更新份额
        fund_share = self.repo.get_fund_share(fund_account_id, product_id)
        if fund_share:
            fund_share.total_share += share
            fund_share.available_share += share
        else:
            fund_share = FundShare(
                share_id=self._generate_id('SHARE_'),
                fund_account_id=fund_account_id,
                product_id=product_id,
                total_share=share,
                available_share=share,
                frozen_share=Decimal('0')
            )
        self.repo.create_or_update_fund_share(fund_share)
        
        # 4. 解冻资金并扣除
        account = self.repo.get_fund_account(fund_account_id)
        balance = self.repo.get_user_balance(account.user_id)
        balance.frozen_balance -= amount
        self.repo.update_user_balance(balance)
        
        # 5. 重新计算资产
        self.calculate_user_assets(account.user_id)
    
    # ==================== 基金赎回 ====================
    
    def redeem_fund(self, fund_account_id: str, product_id: str, share: Decimal) -> Dict[str, Any]:
        """赎回基金"""
        # 1. 验证账户
        account = self.repo.get_fund_account(fund_account_id)
        if not account:
            raise ValueError(f"基金账户不存在: {fund_account_id}")
        
        user_id = account.user_id
        
        # 2. 验证产品
        product = self.repo.get_fund_product(product_id)
        if not product:
            raise ValueError(f"基金产品不存在: {product_id}")
        
        # 3. 检查份额
        fund_share = self.repo.get_fund_share(fund_account_id, product_id)
        if not fund_share or fund_share.available_share < share:
            raise ValueError(f"可用份额不足: 请求赎回{share}份")
        
        # 4. 获取最新净值
        nav = self.repo.get_latest_nav(product_id)
        if not nav:
            raise ValueError(f"基金产品无净值数据: {product_id}")
        
        # 5. 计算赎回金额
        amount = share * nav.net_value
        
        # 6. 冻结份额
        fund_share.available_share -= share
        fund_share.frozen_share += share
        self.repo.create_or_update_fund_share(fund_share)
        
        # 7. 创建委托
        entrust = EntrustBase(
            entrust_id=self._generate_id('ENT_'),
            business_type=BusinessType.FUND_REDEEM,
            status=EntrustStatus.PENDING,
            user_id=user_id,
            request_data={
                "fund_account_id": fund_account_id,
                "product_id": product_id,
                "share": float(share)
            },
            process_time=datetime.now()
        )
        self.repo.create_entrust(entrust)
        
        # 8. 创建交易委托详情
        trans_entrust = FundTransactionEntrust(
            entrust_id=entrust.entrust_id,
            fund_account_id=fund_account_id,
            product_id=product_id,
            transaction_type=TransactionType.REDEEM,
            amount=amount,
            share=share,
            nav=nav.net_value
        )
        self.repo.create_fund_transaction_entrust(trans_entrust)
        
        # 9. 处理确认（模拟立即确认）
        self._process_redeem_confirmation(entrust.entrust_id, user_id, fund_account_id, product_id, share, amount)
        
        return {
            "entrust_id": entrust.entrust_id,
            "fund_account_id": fund_account_id,
            "product_id": product_id,
            "share": float(share),
            "amount": float(amount),
            "nav": float(nav.net_value)
        }
    
    def _process_redeem_confirmation(self, entrust_id: str, user_id: str,
                                    fund_account_id: str, product_id: str,
                                    share: Decimal, amount: Decimal):
        """处理赎回确认"""
        # 1. 更新委托状态
        entrust = self.repo.get_entrust(entrust_id)
        if entrust:
            entrust.status = EntrustStatus.SUCCESS
            entrust.complete_time = datetime.now()
            entrust.response_data = {
                "amount": float(amount),
                "nav": float(entrust.request_data.get('nav', 0))
            }
            self.repo.update_entrust(entrust)
        
        # 2. 创建确认记录
        confirm = ConfirmBase(
            confirm_id=self._generate_id('CFM_'),
            entrust_id=entrust_id,
            confirm_type="FUND_REDEEM",
            result_status=ConfirmResultStatus.SUCCESS,
            confirm_data={"amount": float(amount), "share": float(share)}
        )
        self.repo.create_confirm(confirm)
        
        # 3. 更新份额
        fund_share = self.repo.get_fund_share(fund_account_id, product_id)
        if fund_share:
            fund_share.total_share -= share
            fund_share.frozen_share -= share
            self.repo.create_or_update_fund_share(fund_share)
        
        # 4. 增加用户资金
        balance = self.repo.get_user_balance(user_id)
        balance.available_balance += amount
        self.repo.update_user_balance(balance)
        
        # 5. 重新计算资产
        self.calculate_user_assets(user_id)
    
    # ==================== 资产计算 ====================
    
    def calculate_user_assets(self, user_id: str) -> Dict[str, Any]:
        """计算用户资产"""
        # 1. 获取用户余额
        balance = self.repo.get_user_balance(user_id)
        if not balance:
            raise ValueError(f"用户余额不存在: {user_id}")
        
        total_balance = balance.total_balance
        
        # 2. 获取用户所有基金账户
        accounts = self.repo.get_user_fund_accounts(user_id)
        
        total_fund_value = Decimal('0')
        fund_assets = []
        
        # 3. 计算每个产品的基金资产
        for account in accounts:
            shares = self.repo.get_account_shares(account.fund_account_id)
            
            for share in shares:
                # 获取最新净值
                nav = self.repo.get_latest_nav(share.product_id)
                if nav:
                    # 计算基金价值
                    fund_value = share.total_share * nav.net_value
                    total_fund_value += fund_value
                    
                    # 记录基金资产明细
                    fund_assets.append({
                        'product_id': share.product_id,
                        'share': float(share.total_share),
                        'nav': float(nav.net_value),
                        'value': float(fund_value)
                    })
        
        # 4. 计算总资产
        total_asset = total_balance + total_fund_value
        
        # 5. 更新用户总资产表
        asset = UserTotalAsset(
            asset_id=self._generate_id('ASSET_'),
            user_id=user_id,
            total_asset=total_asset,
            total_fund_asset=total_fund_value,
            total_balance=total_balance,
            calc_date=date.today()
        )
        self.repo.create_user_total_asset(asset)
        
        # 6. 更新用户基金资产表
        for fund_asset_info in fund_assets:
            fund_asset = UserFundAsset(
                fund_asset_id=self._generate_id('FA_'),
                user_id=user_id,
                product_id=fund_asset_info['product_id'],
                fund_share=Decimal(str(fund_asset_info['share'])),
                fund_value=Decimal(str(fund_asset_info['value'])),
                nav=Decimal(str(fund_asset_info['nav'])),
                calc_date=date.today()
            )
            self.repo.create_user_fund_asset(fund_asset)
        
        return {
            'user_id': user_id,
            'total_asset': float(total_asset),
            'total_fund_asset': float(total_fund_value),
            'total_balance': float(total_balance),
            'fund_assets': fund_assets,
            'calc_date': date.today().isoformat()
        }
    
    def get_user_assets(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户资产"""
        # 先计算最新资产
        return self.calculate_user_assets(user_id)

