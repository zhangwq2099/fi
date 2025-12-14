"""
基金产品数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class FundProduct(BaseModel):
    """基金产品模型"""
    # TODO: 根据表结构定义字段
    pass


class FundProductCreateRequest(BaseModel):
    """基金产品创建请求"""
    # TODO: 定义创建请求字段
    pass


class FundProductResponse(BaseModel):
    """基金产品响应"""
    # TODO: 定义响应字段
    pass
