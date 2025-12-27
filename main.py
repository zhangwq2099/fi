"""
FastAPI微服务 - 基金交易系统API服务
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import date
from decimal import Decimal
import logging

from models import (
    UserCreateRequest, FundAccountOpenRequest, FundSubscribeRequest,
    FundRedeemRequest, ProductCreateRequest, NavCreateRequest,
    ResponseModel, UserAssetsResponse
)
from repository import Repository
from service import FundService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastAPI应用
app = FastAPI(
    title="基金交易微服务",
    description="开放式基金交易系统微服务API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()

# 全局数据仓库和服务
repository = Repository()
fund_service = FundService(repository)

# 初始化测试数据
def init_test_data():
    """初始化测试数据"""
    try:
        # 创建测试用户
        user = fund_service.create_user(
            user_name="测试用户",
            user_type="PERSONAL",
            identity_no="320101199001011234",
            phone="13800138000",
            email="test@example.com"
        )
        
        # 创建测试产品
        product = fund_service.create_fund_product(
            product_code="001234",
            product_name="测试基金",
            product_type="EQUITY",
            risk_level="R3",
            fund_company="测试基金公司"
        )
        
        # 添加净值
        fund_service.create_fund_nav(
            product_id=product.product_id,
            net_value=Decimal("1.2345"),
            accumulated_nav=Decimal("1.5678")
        )
        
        # 初始化用户余额
        balance = repository.get_user_balance(user.user_id)
        if balance:
            balance.available_balance = Decimal("100000.00")
            balance.total_balance = Decimal("100000.00")
            repository.update_user_balance(balance)
        
        logger.info(f"测试数据初始化完成: 用户ID={user.user_id}, 产品ID={product.product_id}")
    except Exception as e:
        logger.warning(f"测试数据初始化失败: {e}")

# 启动时初始化测试数据
@app.on_event("startup")
async def startup_event():
    init_test_data()

# 辅助函数
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证Token（简化版）"""
    token = credentials.credentials
    # 简单模拟认证
    if token != "demo_token_2025":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    return token

def handle_exception(e: Exception, operation: str):
    """处理异常"""
    logger.error(f"{operation}失败: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{operation}失败: {str(e)}"
    )

# ==================== API端点 ====================

@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "基金交易微服务",
        "version": "1.0.0",
        "status": "运行中"
    }

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": str(date.today())}

@app.post("/api/v1/users", response_model=ResponseModel)
async def create_user(
    request: UserCreateRequest,
    token: str = Depends(verify_token)
):
    """创建用户"""
    try:
        user = fund_service.create_user(
            user_name=request.user_name,
            user_type=request.user_type,
            identity_no=request.identity_no,
            phone=request.phone,
            email=request.email
        )
        logger.info(f"用户创建成功: {user.user_id}")
        
        return ResponseModel(
            data={
                "user_id": user.user_id,
                "user_name": user.user_name,
                "user_type": user.user_type
            }
        )
    except Exception as e:
        handle_exception(e, "创建用户")

@app.get("/api/v1/users/{user_id}", response_model=ResponseModel)
async def get_user(
    user_id: str,
    token: str = Depends(verify_token)
):
    """获取用户信息"""
    try:
        user = fund_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户不存在: {user_id}"
            )
        return ResponseModel(data=user.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        handle_exception(e, "获取用户信息")

@app.post("/api/v1/accounts/open", response_model=ResponseModel)
async def open_fund_account(
    request: FundAccountOpenRequest,
    token: str = Depends(verify_token)
):
    """开通基金账户"""
    try:
        account = fund_service.open_fund_account(
            request.user_id,
            request.account_type
        )
        logger.info(f"基金账户开通成功: {account.fund_account_id}")
        
        return ResponseModel(
            data={
                "fund_account_id": account.fund_account_id,
                "user_id": account.user_id,
                "account_type": account.account_type,
                "account_no": account.account_no
            }
        )
    except Exception as e:
        handle_exception(e, "开通基金账户")

@app.post("/api/v1/funds/subscribe", response_model=ResponseModel)
async def subscribe_fund(
    request: FundSubscribeRequest,
    token: str = Depends(verify_token)
):
    """申购基金"""
    try:
        result = fund_service.subscribe_fund(
            request.fund_account_id,
            request.product_id,
            Decimal(str(request.amount))
        )
        logger.info(f"基金申购成功: {request.fund_account_id}, 金额: {request.amount}")
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        handle_exception(e, "申购基金")

@app.post("/api/v1/funds/redeem", response_model=ResponseModel)
async def redeem_fund(
    request: FundRedeemRequest,
    token: str = Depends(verify_token)
):
    """赎回基金"""
    try:
        result = fund_service.redeem_fund(
            request.fund_account_id,
            request.product_id,
            Decimal(str(request.share))
        )
        logger.info(f"基金赎回成功: {request.fund_account_id}, 份额: {request.share}")
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        handle_exception(e, "赎回基金")

@app.get("/api/v1/assets/{user_id}", response_model=ResponseModel)
async def get_user_assets(
    user_id: str,
    token: str = Depends(verify_token)
):
    """获取用户资产"""
    try:
        assets = fund_service.get_user_assets(user_id)
        if not assets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户资产不存在: {user_id}"
            )
        return ResponseModel(data=assets)
    except HTTPException:
        raise
    except Exception as e:
        handle_exception(e, "获取用户资产")

@app.get("/api/v1/products", response_model=ResponseModel)
async def get_products(
    product_type: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """获取基金产品列表"""
    try:
        products = fund_service.list_fund_products(product_type)
        result = []
        for product in products:
            product_data = product.model_dump()
            # 获取最新净值
            nav = fund_service.get_latest_nav(product.product_id)
            if nav:
                product_data['latest_nav'] = {
                    'net_value': float(nav.net_value),
                    'accumulated_nav': float(nav.accumulated_nav) if nav.accumulated_nav else None,
                    'nav_date': nav.nav_date.isoformat()
                }
            result.append(product_data)
        return ResponseModel(data=result)
    except Exception as e:
        handle_exception(e, "获取基金产品")

@app.post("/api/v1/products", response_model=ResponseModel)
async def create_product(
    request: ProductCreateRequest,
    token: str = Depends(verify_token)
):
    """创建基金产品"""
    try:
        product = fund_service.create_fund_product(
            product_code=request.product_code,
            product_name=request.product_name,
            product_type=request.product_type,
            risk_level=request.risk_level,
            fund_company=request.fund_company,
            issue_date=request.issue_date
        )
        logger.info(f"基金产品创建成功: {product.product_id}")
        
        return ResponseModel(
            data={
                "product_id": product.product_id,
                "product_name": product.product_name,
                "product_type": product.product_type
            }
        )
    except Exception as e:
        handle_exception(e, "创建基金产品")

@app.post("/api/v1/nav", response_model=ResponseModel)
async def create_nav(
    request: NavCreateRequest,
    token: str = Depends(verify_token)
):
    """创建基金净值"""
    try:
        nav = fund_service.create_fund_nav(
            product_id=request.product_id,
            net_value=Decimal(str(request.net_value)),
            accumulated_nav=Decimal(str(request.accumulated_nav)) if request.accumulated_nav else None,
            nav_date=request.nav_date
        )
        logger.info(f"基金净值创建成功: {nav.nav_id}")
        
        return ResponseModel(
            data={
                "nav_id": nav.nav_id,
                "product_id": nav.product_id,
                "net_value": float(nav.net_value),
                "nav_date": nav.nav_date.isoformat()
            }
        )
    except Exception as e:
        handle_exception(e, "创建基金净值")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


