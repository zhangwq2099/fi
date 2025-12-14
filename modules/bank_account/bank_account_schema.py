"""
银行账户数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class BankAccount(BaseModel):
    """银行账户模型"""
    # TODO: 根据表结构定义字段
    pass


class BankAccountCreateRequest(BaseModel):
    """银行账户创建请求"""
    # TODO: 定义创建请求字段
    pass


class BankAccountResponse(BaseModel):
    """银行账户响应"""
    # TODO: 定义响应字段
    pass
