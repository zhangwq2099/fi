"""
基金账户微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .fund_account_schema import FundAccount, FundAccountCreateRequest, FundAccountResponse
from .fund_account_app import FundAccountApp


router = APIRouter(prefix="/api/v1/fund-account", tags=["基金账户"])


def get_fund_account_app() -> FundAccountApp:
    """获取基金账户应用服务"""
    return FundAccountApp()


@router.post("", response_model=FundAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_fund_account(
    request: FundAccountCreateRequest,
    app: FundAccountApp = Depends(get_fund_account_app)
):
    """创建基金账户"""
    try:
        obj = app.create(request)
        return FundAccountResponse(**obj.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建基金账户失败: {str(e)}"
        )


@router.get("/{id}", response_model=FundAccountResponse)
async def get_fund_account(
    id: str,
    app: FundAccountApp = Depends(get_fund_account_app)
):
    """获取基金账户信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金账户不存在: {id}"
        )
    return FundAccountResponse(**obj.model_dump())
