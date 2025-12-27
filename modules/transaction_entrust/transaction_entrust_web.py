"""
交易委托微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .transaction_entrust_schema import TransactionEntrust, TransactionEntrustCreateRequest, TransactionEntrustResponse
from .transaction_entrust_app import TransactionEntrustApp


router = APIRouter(prefix="/api/v1/transaction-entrust", tags=["交易委托"])


def get_transaction_entrust_app() -> TransactionEntrustApp:
    """获取交易委托应用服务"""
    return TransactionEntrustApp()


@router.post("", response_model=TransactionEntrustResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction_entrust(
    request: TransactionEntrustCreateRequest,
    app: TransactionEntrustApp = Depends(get_transaction_entrust_app)
):
    """创建交易委托"""
    try:
        obj = app.create(request)
        return TransactionEntrustResponse(**obj.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建交易委托失败: {str(e)}"
        )


@router.get("/{id}", response_model=TransactionEntrustResponse)
async def get_transaction_entrust(
    id: str,
    app: TransactionEntrustApp = Depends(get_transaction_entrust_app)
):
    """获取交易委托信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"交易委托不存在: {id}"
        )
    return TransactionEntrustResponse(**obj.model_dump())
