"""
资金清算数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class CapitalSettlement(BaseModel):
    """资金清算模型"""
    # TODO: 根据表结构定义字段
    pass


class CapitalSettlementCreateRequest(BaseModel):
    """资金清算创建请求"""
    # TODO: 定义创建请求字段
    pass


class CapitalSettlementResponse(BaseModel):
    """资金清算响应"""
    # TODO: 定义响应字段
    pass
