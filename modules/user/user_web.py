"""
用户微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from common.repository import get_repository
from .user_schema import User, UserCreateRequest, UserResponse
from .user_app import UserApp


router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


def get_user_app() -> UserApp:
    """获取用户应用服务"""
    return UserApp()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    app: UserApp = Depends(get_user_app)
):
    """创建用户"""
    try:
        user = app.create_user(request)
        return UserResponse(**user.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建用户失败: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    app: UserApp = Depends(get_user_app)
):
    """获取用户信息"""
    user = app.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户不存在: {user_id}"
        )
    return UserResponse(**user.model_dump())


@router.get("", response_model=List[UserResponse])
async def list_users(
    app: UserApp = Depends(get_user_app)
):
    """列出用户"""
    users = app.list_users()
    return [UserResponse(**user.model_dump()) for user in users]


