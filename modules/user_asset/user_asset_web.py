"""
用户资产微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from .user_asset_schema import UserAssetsResponse, UserBalance
from .user_asset_app import UserAssetApp


router = APIRouter(prefix="/api/v1/assets", tags=["用户资产"])


def get_user_asset_app() -> UserAssetApp:
    """获取用户资产应用服务"""
    return UserAssetApp()


@router.get("/{user_id}", response_model=UserAssetsResponse)
async def get_user_assets(
    user_id: str,
    app: UserAssetApp = Depends(get_user_asset_app)
):
    """获取用户资产"""
    try:
        assets = app.calculate_user_assets(user_id)
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"获取用户资产失败: {str(e)}"
        )


@router.get("/{user_id}/balance", response_model=UserBalance)
async def get_user_balance(
    user_id: str,
    app: UserAssetApp = Depends(get_user_asset_app)
):
    """获取用户余额"""
    balance = app.get_user_balance(user_id)
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户余额不存在: {user_id}"
        )
    return balance

