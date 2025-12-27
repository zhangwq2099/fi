"""
公共枚举定义
"""
from enum import Enum


class UserType(str, Enum):
    """用户类型"""
    PERSONAL = "PERSONAL"
    INSTITUTION = "INSTITUTION"


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FROZEN = "FROZEN"


class AccountType(str, Enum):
    """账户类型"""
    INDIVIDUAL = "INDIVIDUAL"
    INSTITUTION = "INSTITUTION"


class AccountStatus(str, Enum):
    """账户状态"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FROZEN = "FROZEN"


class ProductType(str, Enum):
    """产品类型"""
    EQUITY = "EQUITY"
    BOND = "BOND"
    MIXED = "MIXED"
    MONETARY = "MONETARY"


class ProductStatus(str, Enum):
    """产品状态"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class RiskLevel(str, Enum):
    """风险等级"""
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"


class BusinessType(str, Enum):
    """业务类型"""
    ACCOUNT_OPEN = "ACCOUNT_OPEN"
    FUND_SUBSCRIBE = "FUND_SUBSCRIBE"
    FUND_REDEEM = "FUND_REDEEM"
    CAPITAL_IN = "CAPITAL_IN"
    CAPITAL_OUT = "CAPITAL_OUT"


class EntrustStatus(str, Enum):
    """委托状态"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TransactionType(str, Enum):
    """交易类型"""
    SUBSCRIBE = "SUBSCRIBE"
    REDEEM = "REDEEM"


class ChangeType(str, Enum):
    """资金变动类型"""
    IN = "IN"
    OUT = "OUT"


class ConfirmResultStatus(str, Enum):
    """确认结果状态"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class SettlementType(str, Enum):
    """清算类型"""
    CAPITAL_IN = "CAPITAL_IN"
    CAPITAL_OUT = "CAPITAL_OUT"


