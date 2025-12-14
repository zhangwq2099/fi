"""
用户资产应用服务层
"""
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.repository import get_repository
from .user_asset_schema import UserBalance, UserTotalAsset, UserFundAsset, UserAssetsResponse


class UserAssetApp:
    """用户资产应用服务"""
    
    def __init__(self):
        self.repo = get_repository()
        self.balance_table = "user_balance"
        self.total_asset_table = "user_total_asset"
        self.fund_asset_table = "user_fund_asset"
    
    def _generate_id(self, prefix: str = '') -> str:
        """生成ID"""
        import uuid
        return f"{prefix}{uuid.uuid4().hex[:16]}"
    
    def init_user_balance(self, user_id: str) -> UserBalance:
        """初始化用户余额"""
        balance_id = self._generate_id('BAL_')
        balance_data = {
            'id': balance_id,
            'balance_id': balance_id,
            'user_id': user_id,
            'available_balance': Decimal('0'),
            'frozen_balance': Decimal('0'),
            'total_balance': Decimal('0'),
            'last_update': datetime.now()
        }
        self.repo.create(self.balance_table, balance_data)
        return UserBalance(**balance_data)
    
    def get_user_balance(self, user_id: str) -> Optional[UserBalance]:
        """获取用户余额"""
        balances = self.repo.list(self.balance_table, {'user_id': user_id})
        if balances:
            return UserBalance(**balances[0])
        return None
    
    def update_user_balance(self, user_id: str, available_balance: Optional[Decimal] = None,
                           frozen_balance: Optional[Decimal] = None) -> Optional[UserBalance]:
        """更新用户余额"""
        balance = self.get_user_balance(user_id)
        if not balance:
            return None
        
        update_data = {}
        if available_balance is not None:
            update_data['available_balance'] = available_balance
        if frozen_balance is not None:
            update_data['frozen_balance'] = frozen_balance
        
        if update_data:
            update_data['total_balance'] = (
                update_data.get('available_balance', balance.available_balance) +
                update_data.get('frozen_balance', balance.frozen_balance)
            )
            update_data['last_update'] = datetime.now()
            updated = self.repo.update(self.balance_table, balance.balance_id, update_data)
            if updated:
                return UserBalance(**updated)
        return balance
    
    def calculate_user_assets(self, user_id: str) -> UserAssetsResponse:
        """计算用户资产"""
        # 获取用户余额
        balance = self.get_user_balance(user_id)
        if not balance:
            raise ValueError(f"用户余额不存在: {user_id}")
        
        total_balance = balance.total_balance
        
        # 获取用户所有基金账户的份额
        # TODO: 实现获取用户所有份额的逻辑
        # from modules.fund_share.fund_share_app import FundShareApp
        # share_app = FundShareApp()
        # all_shares = share_app.get_user_all_shares(user_id)
        all_shares = []  # 临时占位
        
        # 获取基金产品净值
        # TODO: 实现获取基金产品净值的逻辑
        # from modules.fund_product.fund_product_app import FundProductApp
        # product_app = FundProductApp()
        
        total_fund_value = Decimal('0')
        fund_assets = []
        
        # TODO: 实现基金资产计算逻辑
        # for share_info in all_shares:
        #     # 获取最新净值
        #     nav = product_app.get_latest_nav(share_info['product_id'])
        #     if nav:
        #         # 计算基金价值
        #         fund_value = share_info['total_share'] * nav.net_value
        #         total_fund_value += fund_value
        #         
        #         fund_assets.append({
        #             'product_id': share_info['product_id'],
        #             'share': float(share_info['total_share']),
        #             'nav': float(nav.net_value),
        #             'value': float(fund_value)
        #         })
        
        # 计算总资产
        total_asset = total_balance + total_fund_value
        
        # 保存总资产记录
        asset_id = self._generate_id('ASSET_')
        asset_data = {
            'id': asset_id,
            'asset_id': asset_id,
            'user_id': user_id,
            'total_asset': total_asset,
            'total_fund_asset': total_fund_value,
            'total_balance': total_balance,
            'calc_date': date.today(),
            'create_time': datetime.now()
        }
        self.repo.create(self.total_asset_table, asset_data)
        
        # 保存基金资产明细
        for fund_asset_info in fund_assets:
            fund_asset_id = self._generate_id('FA_')
            fund_asset_data = {
                'id': fund_asset_id,
                'fund_asset_id': fund_asset_id,
                'user_id': user_id,
                'product_id': fund_asset_info['product_id'],
                'fund_share': Decimal(str(fund_asset_info['share'])),
                'fund_value': Decimal(str(fund_asset_info['value'])),
                'nav': Decimal(str(fund_asset_info['nav'])),
                'calc_date': date.today(),
                'create_time': datetime.now()
            }
            self.repo.create(self.fund_asset_table, fund_asset_data)
        
        return UserAssetsResponse(
            user_id=user_id,
            total_asset=total_asset,
            total_fund_asset=total_fund_value,
            total_balance=total_balance,
            fund_assets=fund_assets,
            calc_date=date.today()
        )

