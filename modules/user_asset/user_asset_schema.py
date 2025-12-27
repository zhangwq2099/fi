"""
用户资产数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class UserBalance(BaseModel):
    """用户资金余额模型"""
    balance_id: str = Field(..., description="余额ID")
    user_id: str = Field(..., description="用户ID")
    available_balance: Decimal = Field(0, ge=0, description="可用余额")
    frozen_balance: Decimal = Field(0, ge=0, description="冻结余额")
    total_balance: Decimal = Field(0, ge=0, description="总余额")
    last_update: datetime = Field(default_factory=datetime.now, description="最后更新时间")


class UserTotalAsset(BaseModel):
    """用户总资产模型"""
    asset_id: str = Field(..., description="资产ID")
    user_id: str = Field(..., description="用户ID")
    total_asset: Decimal = Field(0, ge=0, description="总资产")
    total_fund_asset: Decimal = Field(0, ge=0, description="基金总资产")
    total_balance: Decimal = Field(0, ge=0, description="总余额")
    calc_date: date = Field(..., description="计算日期")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")


class UserFundAsset(BaseModel):
    """用户基金资产模型"""
    fund_asset_id: str = Field(..., description="基金资产ID")
    user_id: str = Field(..., description="用户ID")
    product_id: str = Field(..., description="产品ID")
    fund_share: Decimal = Field(0, ge=0, description="持有份额")
    fund_value: Decimal = Field(0, ge=0, description="基金价值")
    nav: Decimal = Field(..., ge=0, description="计算净值")
    calc_date: date = Field(..., description="计算日期")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")


class UserAssetsResponse(BaseModel):
    """用户资产响应"""
    user_id: str
    total_asset: Decimal
    total_fund_asset: Decimal
    total_balance: Decimal
    fund_assets: List[Dict[str, Any]]
    calc_date: date


