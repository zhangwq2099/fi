"""
数据存储层 - 基于内存的数据管理
使用字典存储数据，模拟数据库操作
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
import uuid
from models import (
    User, UserBankCard, FundAccount, FundProduct, FundNetValue,
    UserBalance, FundShare, EntrustBase, FundAccountEntrust,
    FundTransactionEntrust, CapitalChangeEntrust, ConfirmBase,
    UserTotalAsset, UserFundAsset
)


class Repository:
    """数据仓库基类"""
    
    def __init__(self):
        """初始化数据存储"""
        self._storage: Dict[str, Dict[str, Any]] = {
            'users': {},
            'user_bank_cards': {},
            'fund_accounts': {},
            'fund_products': {},
            'fund_net_values': {},
            'user_balances': {},
            'fund_shares': {},
            'entrust_base': {},
            'fund_account_entrusts': {},
            'fund_transaction_entrusts': {},
            'capital_change_entrusts': {},
            'confirm_base': {},
            'user_total_assets': {},
            'user_fund_assets': {}
        }
    
    def _generate_id(self, prefix: str = '') -> str:
        """生成唯一ID"""
        return f"{prefix}{uuid.uuid4().hex[:16]}"
    
    # ==================== 用户相关 ====================
    
    def create_user(self, user: User) -> User:
        """创建用户"""
        if user.user_id in self._storage['users']:
            raise ValueError(f"用户已存在: {user.user_id}")
        self._storage['users'][user.user_id] = user.dict()
        # 初始化用户余额
        balance = UserBalance(
            balance_id=self._generate_id('BAL_'),
            user_id=user.user_id,
            available_balance=Decimal('0'),
            frozen_balance=Decimal('0'),
            total_balance=Decimal('0')
        )
        self._storage['user_balances'][balance.balance_id] = balance.dict()
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        user_data = self._storage['users'].get(user_id)
        if user_data:
            return User(**user_data)
        return None
    
    def list_users(self) -> List[User]:
        """列出所有用户"""
        return [User(**data) for data in self._storage['users'].values()]
    
    # ==================== 基金账户相关 ====================
    
    def create_fund_account(self, account: FundAccount) -> FundAccount:
        """创建基金账户"""
        if account.fund_account_id in self._storage['fund_accounts']:
            raise ValueError(f"基金账户已存在: {account.fund_account_id}")
        self._storage['fund_accounts'][account.fund_account_id] = account.dict()
        return account
    
    def get_fund_account(self, fund_account_id: str) -> Optional[FundAccount]:
        """获取基金账户"""
        account_data = self._storage['fund_accounts'].get(fund_account_id)
        if account_data:
            return FundAccount(**account_data)
        return None
    
    def get_user_fund_accounts(self, user_id: str) -> List[FundAccount]:
        """获取用户的所有基金账户"""
        accounts = []
        for account_data in self._storage['fund_accounts'].values():
            if account_data.get('user_id') == user_id:
                accounts.append(FundAccount(**account_data))
        return accounts
    
    # ==================== 基金产品相关 ====================
    
    def create_fund_product(self, product: FundProduct) -> FundProduct:
        """创建基金产品"""
        if product.product_id in self._storage['fund_products']:
            raise ValueError(f"基金产品已存在: {product.product_id}")
        self._storage['fund_products'][product.product_id] = product.dict()
        return product
    
    def get_fund_product(self, product_id: str) -> Optional[FundProduct]:
        """获取基金产品"""
        product_data = self._storage['fund_products'].get(product_id)
        if product_data:
            return FundProduct(**product_data)
        return None
    
    def list_fund_products(self, product_type: Optional[str] = None) -> List[FundProduct]:
        """列出基金产品"""
        products = []
        for product_data in self._storage['fund_products'].values():
            if product_type is None or product_data.get('product_type') == product_type:
                products.append(FundProduct(**product_data))
        return products
    
    # ==================== 基金净值相关 ====================
    
    def create_fund_net_value(self, nav: FundNetValue) -> FundNetValue:
        """创建基金净值"""
        self._storage['fund_net_values'][nav.nav_id] = nav.dict()
        return nav
    
    def get_latest_nav(self, product_id: str) -> Optional[FundNetValue]:
        """获取最新净值"""
        navs = []
        for nav_data in self._storage['fund_net_values'].values():
            if nav_data.get('product_id') == product_id:
                navs.append(FundNetValue(**nav_data))
        
        if not navs:
            return None
        
        # 按日期排序，返回最新的
        navs.sort(key=lambda x: x.nav_date, reverse=True)
        return navs[0]
    
    def list_navs_by_product(self, product_id: str) -> List[FundNetValue]:
        """获取产品的所有净值记录"""
        navs = []
        for nav_data in self._storage['fund_net_values'].values():
            if nav_data.get('product_id') == product_id:
                navs.append(FundNetValue(**nav_data))
        navs.sort(key=lambda x: x.nav_date, reverse=True)
        return navs
    
    # ==================== 用户余额相关 ====================
    
    def get_user_balance(self, user_id: str) -> Optional[UserBalance]:
        """获取用户余额"""
        for balance_data in self._storage['user_balances'].values():
            if balance_data.get('user_id') == user_id:
                return UserBalance(**balance_data)
        return None
    
    def update_user_balance(self, balance: UserBalance) -> UserBalance:
        """更新用户余额"""
        # 计算总余额
        balance.total_balance = balance.available_balance + balance.frozen_balance
        balance.last_update = datetime.now()
        self._storage['user_balances'][balance.balance_id] = balance.dict()
        return balance
    
    # ==================== 基金份额相关 ====================
    
    def get_fund_share(self, fund_account_id: str, product_id: str) -> Optional[FundShare]:
        """获取基金份额"""
        for share_data in self._storage['fund_shares'].values():
            if (share_data.get('fund_account_id') == fund_account_id and
                share_data.get('product_id') == product_id):
                return FundShare(**share_data)
        return None
    
    def create_or_update_fund_share(self, share: FundShare) -> FundShare:
        """创建或更新基金份额"""
        share.last_update = datetime.now()
        self._storage['fund_shares'][share.share_id] = share.dict()
        return share
    
    def get_account_shares(self, fund_account_id: str) -> List[FundShare]:
        """获取账户的所有份额"""
        shares = []
        for share_data in self._storage['fund_shares'].values():
            if share_data.get('fund_account_id') == fund_account_id:
                shares.append(FundShare(**share_data))
        return shares
    
    # ==================== 委托相关 ====================
    
    def create_entrust(self, entrust: EntrustBase) -> EntrustBase:
        """创建委托"""
        self._storage['entrust_base'][entrust.entrust_id] = entrust.dict()
        return entrust
    
    def get_entrust(self, entrust_id: str) -> Optional[EntrustBase]:
        """获取委托"""
        entrust_data = self._storage['entrust_base'].get(entrust_id)
        if entrust_data:
            return EntrustBase(**entrust_data)
        return None
    
    def update_entrust(self, entrust: EntrustBase) -> EntrustBase:
        """更新委托"""
        self._storage['entrust_base'][entrust.entrust_id] = entrust.dict()
        return entrust
    
    def create_fund_transaction_entrust(self, entrust: FundTransactionEntrust) -> FundTransactionEntrust:
        """创建基金交易委托"""
        self._storage['fund_transaction_entrusts'][entrust.entrust_id] = entrust.dict()
        return entrust
    
    def create_fund_account_entrust(self, entrust: FundAccountEntrust) -> FundAccountEntrust:
        """创建基金账户委托"""
        self._storage['fund_account_entrusts'][entrust.entrust_id] = entrust.dict()
        return entrust
    
    # ==================== 确认相关 ====================
    
    def create_confirm(self, confirm: ConfirmBase) -> ConfirmBase:
        """创建确认"""
        self._storage['confirm_base'][confirm.confirm_id] = confirm.dict()
        return confirm
    
    # ==================== 资产相关 ====================
    
    def create_user_total_asset(self, asset: UserTotalAsset) -> UserTotalAsset:
        """创建用户总资产"""
        self._storage['user_total_assets'][asset.asset_id] = asset.dict()
        return asset
    
    def create_user_fund_asset(self, asset: UserFundAsset) -> UserFundAsset:
        """创建用户基金资产"""
        self._storage['user_fund_assets'][asset.fund_asset_id] = asset.dict()
        return asset
    
    def get_latest_user_total_asset(self, user_id: str) -> Optional[UserTotalAsset]:
        """获取用户最新总资产"""
        assets = []
        for asset_data in self._storage['user_total_assets'].values():
            if asset_data.get('user_id') == user_id:
                assets.append(UserTotalAsset(**asset_data))
        
        if not assets:
            return None
        
        assets.sort(key=lambda x: x.calc_date, reverse=True)
        return assets[0]

