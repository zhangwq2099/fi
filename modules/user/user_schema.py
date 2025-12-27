"""
用户数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from common.enums import UserType, UserStatus


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


class UserCreateRequest(BaseModel):
    """用户创建请求"""
    user_name: str = Field(..., min_length=2, max_length=50)
    user_type: UserType = UserType.PERSONAL
    identity_no: Optional[str] = Field(None, min_length=15, max_length=30)
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        use_enum_values = True


class UserResponse(BaseModel):
    """用户响应"""
    user_id: str
    user_name: Optional[str]
    user_type: str
    user_status: str
    identity_no: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    create_time: datetime
    update_time: datetime


