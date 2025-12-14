"""
基于Pydantic BaseModel的数据对象模型
定义基金交易系统的所有数据模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ==================== 枚举类型 ====================

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


# ==================== 核心实体模型 ====================

class User(BaseModel):
    """用户模型"""
    user_id: str = Field(..., description="用户ID，全局唯一")
    user_name: Optional[str] = Field(None, max_length=50, description="用户姓名")
    user_type: UserType = Field(UserType.PERSONAL, description="用户类型")
    user_status: UserStatus = Field(UserStatus.ACTIVE, description="用户状态")
    identity_no: Optional[str] = Field(None, max_length=30, description="身份证/机构代码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        use_enum_values = True


class UserBankCard(BaseModel):
    """用户银行卡模型"""
    card_id: str = Field(..., description="银行卡ID")
    user_id: str = Field(..., description="用户ID")
    bank_code: str = Field(..., max_length=20, description="银行代码")
    bank_name: Optional[str] = Field(None, max_length=50, description="银行名称")
    card_no: str = Field(..., max_length=30, description="银行卡号")
    card_type: str = Field("DEBIT", description="卡类型：DEBIT/CREDIT")
    card_status: str = Field("ACTIVE", description="状态")
    bind_time: datetime = Field(default_factory=datetime.now, description="绑定时间")
    is_default: bool = Field(False, description="是否默认卡")


class FundAccount(BaseModel):
    """基金账户模型"""
    fund_account_id: str = Field(..., description="基金账户ID")
    user_id: str = Field(..., description="用户ID")
    account_no: str = Field(..., max_length=30, description="基金账户号")
    account_type: AccountType = Field(AccountType.INDIVIDUAL, description="账户类型")
    account_status: AccountStatus = Field(AccountStatus.ACTIVE, description="账户状态")
    open_date: date = Field(..., description="开户日期")
    close_date: Optional[date] = Field(None, description="销户日期")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")

    class Config:
        use_enum_values = True


class FundProduct(BaseModel):
    """基金产品模型"""
    product_id: str = Field(..., description="产品ID")
    product_code: str = Field(..., max_length=20, description="产品代码")
    product_name: str = Field(..., max_length=100, description="产品名称")
    product_type: ProductType = Field(ProductType.EQUITY, description="产品类型")
    product_status: ProductStatus = Field(ProductStatus.ACTIVE, description="产品状态")
    risk_level: RiskLevel = Field(RiskLevel.R3, description="风险等级")
    fund_company: Optional[str] = Field(None, max_length=50, description="基金公司")
    issue_date: date = Field(..., description="发行日期")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")

    class Config:
        use_enum_values = True


class FundNetValue(BaseModel):
    """基金单位净值模型"""
    nav_id: str = Field(..., description="净值ID")
    product_id: str = Field(..., description="产品ID")
    net_value: Decimal = Field(..., ge=0, description="单位净值")
    accumulated_nav: Optional[Decimal] = Field(None, ge=0, description="累计净值")
    nav_date: date = Field(..., description="净值日期")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")


class UserBalance(BaseModel):
    """用户资金余额模型"""
    balance_id: str = Field(..., description="余额ID")
    user_id: str = Field(..., description="用户ID")
    available_balance: Decimal = Field(0, ge=0, description="可用余额")
    frozen_balance: Decimal = Field(0, ge=0, description="冻结余额")
    total_balance: Decimal = Field(0, ge=0, description="总余额")
    last_update: datetime = Field(default_factory=datetime.now, description="最后更新时间")

    @validator('total_balance', always=True)
    def calculate_total_balance(cls, v, values):
        """计算总余额"""
        if 'available_balance' in values and 'frozen_balance' in values:
            return values['available_balance'] + values['frozen_balance']
        return v


class FundShare(BaseModel):
    """基金份额模型"""
    share_id: str = Field(..., description="份额ID")
    fund_account_id: str = Field(..., description="基金账户ID")
    product_id: str = Field(..., description="产品ID")
    total_share: Decimal = Field(0, ge=0, description="总份额")
    available_share: Decimal = Field(0, ge=0, description="可用份额")
    frozen_share: Decimal = Field(0, ge=0, description="冻结份额")
    last_update: datetime = Field(default_factory=datetime.now, description="最后更新时间")


# ==================== 业务处理模型 ====================

class EntrustBase(BaseModel):
    """委托基础模型"""
    entrust_id: str = Field(..., description="委托ID")
    business_type: BusinessType = Field(..., description="业务类型")
    status: EntrustStatus = Field(EntrustStatus.PENDING, description="状态")
    user_id: str = Field(..., description="用户ID")
    request_data: Optional[Dict[str, Any]] = Field(None, description="请求数据")
    response_data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    process_time: Optional[datetime] = Field(None, description="处理时间")
    complete_time: Optional[datetime] = Field(None, description="完成时间")
    error_msg: Optional[str] = Field(None, description="错误信息")

    class Config:
        use_enum_values = True


class FundAccountEntrust(BaseModel):
    """基金账户委托模型"""
    entrust_id: str = Field(..., description="委托ID")
    account_type: AccountType = Field(AccountType.INDIVIDUAL, description="账户类型")
    source_channel: str = Field("WEB", description="来源渠道：WEB/APP/BANK")

    class Config:
        use_enum_values = True


class FundTransactionEntrust(BaseModel):
    """基金交易委托模型"""
    entrust_id: str = Field(..., description="委托ID")
    fund_account_id: str = Field(..., description="基金账户ID")
    product_id: str = Field(..., description="产品ID")
    transaction_type: TransactionType = Field(..., description="交易类型")
    amount: Optional[Decimal] = Field(None, ge=0, description="交易金额")
    share: Optional[Decimal] = Field(None, ge=0, description="交易份额")
    nav: Optional[Decimal] = Field(None, ge=0, description="交易净值")
    fee: Decimal = Field(0, ge=0, description="手续费")

    class Config:
        use_enum_values = True


class CapitalChangeEntrust(BaseModel):
    """资金变动委托模型"""
    entrust_id: str = Field(..., description="委托ID")
    card_id: str = Field(..., description="银行卡ID")
    change_type: ChangeType = Field(..., description="变动类型")
    amount: Decimal = Field(..., ge=0, description="变动金额")
    third_party_no: Optional[str] = Field(None, max_length=50, description="第三方流水号")

    class Config:
        use_enum_values = True


class ConfirmBase(BaseModel):
    """确认基础模型"""
    confirm_id: str = Field(..., description="确认ID")
    entrust_id: str = Field(..., description="委托ID")
    confirm_type: str = Field(..., description="确认类型")
    result_status: ConfirmResultStatus = Field(..., description="结果状态")
    confirm_data: Optional[Dict[str, Any]] = Field(None, description="确认数据")
    confirm_time: datetime = Field(default_factory=datetime.now, description="确认时间")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    class Config:
        use_enum_values = True


# ==================== 资产汇总模型 ====================

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


# ==================== API请求/响应模型 ====================

class UserCreateRequest(BaseModel):
    """用户创建请求"""
    user_name: str = Field(..., min_length=2, max_length=50)
    user_type: UserType = UserType.PERSONAL
    identity_no: Optional[str] = Field(None, min_length=15, max_length=30)
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        use_enum_values = True


class FundAccountOpenRequest(BaseModel):
    """基金账户开户请求"""
    user_id: str
    account_type: AccountType = AccountType.INDIVIDUAL

    class Config:
        use_enum_values = True


class FundSubscribeRequest(BaseModel):
    """基金申购请求"""
    fund_account_id: str
    product_id: str
    amount: Decimal = Field(..., gt=0, description="申购金额")


class FundRedeemRequest(BaseModel):
    """基金赎回请求"""
    fund_account_id: str
    product_id: str
    share: Decimal = Field(..., gt=0, description="赎回份额")


class ProductCreateRequest(BaseModel):
    """产品创建请求"""
    product_code: str = Field(..., max_length=20)
    product_name: str = Field(..., max_length=100)
    product_type: ProductType = ProductType.EQUITY
    risk_level: RiskLevel = RiskLevel.R3
    fund_company: Optional[str] = None
    issue_date: Optional[date] = None

    class Config:
        use_enum_values = True


class NavCreateRequest(BaseModel):
    """净值创建请求"""
    product_id: str
    net_value: Decimal = Field(..., gt=0)
    accumulated_nav: Optional[Decimal] = Field(None, ge=0)
    nav_date: Optional[date] = None


class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = Field(0, description="响应码，0表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class UserAssetsResponse(BaseModel):
    """用户资产响应"""
    user_id: str
    total_asset: Decimal
    total_fund_asset: Decimal
    total_balance: Decimal
    fund_assets: List[Dict[str, Any]]
    calc_date: date

