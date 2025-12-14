"""
资金清算微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .capital_settlement_schema import CapitalSettlement, CapitalSettlementCreateRequest, CapitalSettlementResponse
from .capital_settlement_app import CapitalSettlementApp


router = APIRouter(prefix="/api/v1/capital-settlement", tags=["资金清算"])


def get_capital_settlement_app() -> CapitalSettlementApp:
    """获取资金清算应用服务"""
    return CapitalSettlementApp()


@router.post("", response_model=CapitalSettlementResponse, status_code=status.HTTP_201_CREATED)
async def create_capital_settlement(
    request: CapitalSettlementCreateRequest,
    app: CapitalSettlementApp = Depends(get_capital_settlement_app)
):
    """创建资金清算"""
    try:
        obj = app.create(request)
        return CapitalSettlementResponse(**obj.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建资金清算失败: {str(e)}"
        )


@router.get("/{id}", response_model=CapitalSettlementResponse)
async def get_capital_settlement(
    id: str,
    app: CapitalSettlementApp = Depends(get_capital_settlement_app)
):
    """获取资金清算信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"资金清算不存在: {id}"
        )
    return CapitalSettlementResponse(**obj.dict())
