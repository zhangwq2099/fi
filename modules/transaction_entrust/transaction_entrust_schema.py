"""
交易委托数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class TransactionEntrust(BaseModel):
    """交易委托模型"""
    # TODO: 根据表结构定义字段
    pass


class TransactionEntrustCreateRequest(BaseModel):
    """交易委托创建请求"""
    # TODO: 定义创建请求字段
    pass


class TransactionEntrustResponse(BaseModel):
    """交易委托响应"""
    # TODO: 定义响应字段
    pass
