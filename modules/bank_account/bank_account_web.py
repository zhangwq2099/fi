"""
银行账户微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .bank_account_schema import BankAccount, BankAccountCreateRequest, BankAccountResponse
from .bank_account_app import BankAccountApp


router = APIRouter(prefix="/api/v1/bank-account", tags=["银行账户"])


def get_bank_account_app() -> BankAccountApp:
    """获取银行账户应用服务"""
    return BankAccountApp()


@router.post("", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    request: BankAccountCreateRequest,
    app: BankAccountApp = Depends(get_bank_account_app)
):
    """创建银行账户"""
    try:
        obj = app.create(request)
        return BankAccountResponse(**obj.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建银行账户失败: {str(e)}"
        )


@router.get("/{id}", response_model=BankAccountResponse)
async def get_bank_account(
    id: str,
    app: BankAccountApp = Depends(get_bank_account_app)
):
    """获取银行账户信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"银行账户不存在: {id}"
        )
    return BankAccountResponse(**obj.dict())
