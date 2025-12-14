"""
基金份额微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .fund_share_schema import FundShare, FundShareCreateRequest, FundShareResponse
from .fund_share_app import FundShareApp


router = APIRouter(prefix="/api/v1/fund-share", tags=["基金份额"])


def get_fund_share_app() -> FundShareApp:
    """获取基金份额应用服务"""
    return FundShareApp()


@router.post("", response_model=FundShareResponse, status_code=status.HTTP_201_CREATED)
async def create_fund_share(
    request: FundShareCreateRequest,
    app: FundShareApp = Depends(get_fund_share_app)
):
    """创建基金份额"""
    try:
        obj = app.create(request)
        return FundShareResponse(**obj.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建基金份额失败: {str(e)}"
        )


@router.get("/{id}", response_model=FundShareResponse)
async def get_fund_share(
    id: str,
    app: FundShareApp = Depends(get_fund_share_app)
):
    """获取基金份额信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金份额不存在: {id}"
        )
    return FundShareResponse(**obj.dict())
