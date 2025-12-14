"""
基金份额数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class FundShare(BaseModel):
    """基金份额模型"""
    # TODO: 根据表结构定义字段
    pass


class FundShareCreateRequest(BaseModel):
    """基金份额创建请求"""
    # TODO: 定义创建请求字段
    pass


class FundShareResponse(BaseModel):
    """基金份额响应"""
    # TODO: 定义响应字段
    pass
