"""
交易确认数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class TransactionConfirm(BaseModel):
    """交易确认模型"""
    # TODO: 根据表结构定义字段
    pass


class TransactionConfirmCreateRequest(BaseModel):
    """交易确认创建请求"""
    # TODO: 定义创建请求字段
    pass


class TransactionConfirmResponse(BaseModel):
    """交易确认响应"""
    # TODO: 定义响应字段
    pass
