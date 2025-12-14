"""
基金产品微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .fund_product_schema import FundProduct, FundProductCreateRequest, FundProductResponse
from .fund_product_app import FundProductApp


router = APIRouter(prefix="/api/v1/fund-product", tags=["基金产品"])


def get_fund_product_app() -> FundProductApp:
    """获取基金产品应用服务"""
    return FundProductApp()


@router.post("", response_model=FundProductResponse, status_code=status.HTTP_201_CREATED)
async def create_fund_product(
    request: FundProductCreateRequest,
    app: FundProductApp = Depends(get_fund_product_app)
):
    """创建基金产品"""
    try:
        obj = app.create(request)
        return FundProductResponse(**obj.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建基金产品失败: {str(e)}"
        )


@router.get("/{id}", response_model=FundProductResponse)
async def get_fund_product(
    id: str,
    app: FundProductApp = Depends(get_fund_product_app)
):
    """获取基金产品信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金产品不存在: {id}"
        )
    return FundProductResponse(**obj.dict())
