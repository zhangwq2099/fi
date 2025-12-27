"""
资金委托微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .capital_entrust_schema import CapitalEntrust, CapitalEntrustCreateRequest, CapitalEntrustResponse
from .capital_entrust_app import CapitalEntrustApp


router = APIRouter(prefix="/api/v1/capital-entrust", tags=["资金委托"])


def get_capital_entrust_app() -> CapitalEntrustApp:
    """获取资金委托应用服务"""
    return CapitalEntrustApp()


@router.post("", response_model=CapitalEntrustResponse, status_code=status.HTTP_201_CREATED)
async def create_capital_entrust(
    request: CapitalEntrustCreateRequest,
    app: CapitalEntrustApp = Depends(get_capital_entrust_app)
):
    """创建资金委托"""
    try:
        obj = app.create(request)
        return CapitalEntrustResponse(**obj.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建资金委托失败: {str(e)}"
        )


@router.get("/{id}", response_model=CapitalEntrustResponse)
async def get_capital_entrust(
    id: str,
    app: CapitalEntrustApp = Depends(get_capital_entrust_app)
):
    """获取资金委托信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"资金委托不存在: {id}"
        )
    return CapitalEntrustResponse(**obj.model_dump())
