"""
基金账户数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class FundAccount(BaseModel):
    """基金账户模型"""
    # TODO: 根据表结构定义字段
    pass


class FundAccountCreateRequest(BaseModel):
    """基金账户创建请求"""
    # TODO: 定义创建请求字段
    pass


class FundAccountResponse(BaseModel):
    """基金账户响应"""
    # TODO: 定义响应字段
    pass
