"""
交易确认微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .transaction_confirm_schema import TransactionConfirm, TransactionConfirmCreateRequest, TransactionConfirmResponse
from .transaction_confirm_app import TransactionConfirmApp


router = APIRouter(prefix="/api/v1/transaction-confirm", tags=["交易确认"])


def get_transaction_confirm_app() -> TransactionConfirmApp:
    """获取交易确认应用服务"""
    return TransactionConfirmApp()


@router.post("", response_model=TransactionConfirmResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction_confirm(
    request: TransactionConfirmCreateRequest,
    app: TransactionConfirmApp = Depends(get_transaction_confirm_app)
):
    """创建交易确认"""
    try:
        obj = app.create(request)
        return TransactionConfirmResponse(**obj.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建交易确认失败: {str(e)}"
        )


@router.get("/{id}", response_model=TransactionConfirmResponse)
async def get_transaction_confirm(
    id: str,
    app: TransactionConfirmApp = Depends(get_transaction_confirm_app)
):
    """获取交易确认信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"交易确认不存在: {id}"
        )
    return TransactionConfirmResponse(**obj.model_dump())
