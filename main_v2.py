"""
FastAPI微服务主入口 - 完整集成版本
整合了模块化路由和兼容性端点，按业务模块分类组织
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import date
from decimal import Decimal
import logging

# ==================== 导入模块化路由 ====================
from modules.bank_account.bank_account_web import router as bank_account_router
from modules.capital_entrust.capital_entrust_web import \
    router as capital_entrust_router
from modules.capital_settlement.capital_settlement_web import \
    router as capital_settlement_router
from modules.fund_account.fund_account_web import router as fund_account_router
from modules.fund_product.fund_product_web import router as fund_product_router
from modules.fund_share.fund_share_web import router as fund_share_router
from modules.transaction_confirm.transaction_confirm_web import \
    router as transaction_confirm_router
from modules.transaction_entrust.transaction_entrust_web import \
    router as transaction_entrust_router
from modules.user.user_web import router as user_router
from modules.user_asset.user_asset_web import router as user_asset_router

# ==================== 导入兼容性端点所需的模块 ====================
from models import (
    UserCreateRequest, FundAccountOpenRequest, FundSubscribeRequest, FundRedeemRequest,
    ProductCreateRequest, NavCreateRequest, ResponseModel, User
)
from repository import Repository
from service import FundService
from common.repository import get_repository
from modules.user.user_app import UserApp

# ==================== 配置日志 ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 安全认证 ====================
security = HTTPBearer()

# ==================== 全局数据仓库和服务 ====================
# 使用 common/repository.py 的单例，确保与模块化服务共享数据
common_repo = get_repository()
user_app = UserApp()

# ==================== Repository适配器 ====================
# 创建一个适配器 Repository，桥接 common/repository 和旧版 Repository 接口
class RepositoryAdapter(Repository):
    """适配器：将 common/repository 的单例适配为 Repository 接口"""
    
    def __init__(self, common_repo_instance):
        # 调用父类初始化，创建存储结构
        super().__init__()
        self._common_repo = common_repo_instance
    
    def get_user(self, user_id: str):
        """获取用户（从 common_repo 读取，确保数据共享）"""
        # 从 common_repo 读取用户数据
        user_data = self._common_repo.get("user", user_id)
        if user_data:
            # 转换为 User 模型
            user_id_value = user_data.get('user_id') or user_data.get('id')
            return User(
                user_id=user_id_value,
                user_name=user_data.get('user_name'),
                user_type=user_data.get('user_type', 'PERSONAL'),
                user_status=user_data.get('user_status', 'ACTIVE'),
                identity_no=user_data.get('identity_no'),
                phone=user_data.get('phone'),
                email=user_data.get('email'),
                create_time=user_data.get('create_time'),
                update_time=user_data.get('update_time')
            )
        return None
    
    def create_user(self, user: User) -> User:
        """创建用户（同时写入 common_repo 和旧存储，确保数据共享）"""
        # 先调用父类方法，写入旧存储并初始化余额
        result = super().create_user(user)
        
        # 同时写入 common_repo
        user_data = user.model_dump()
        # 转换为 common_repo 格式（使用 'id' 作为主键）
        common_user_data = {
            'id': user.user_id,
            'user_id': user.user_id,
            'user_name': user.user_name,
            'user_type': user.user_type,
            'user_status': user.user_status,
            'identity_no': user.identity_no,
            'phone': user.phone,
            'email': user.email,
            'create_time': user.create_time,
            'update_time': user.update_time
        }
        try:
            self._common_repo.create("user", common_user_data)
            logger.debug(f"用户已同步到 common_repo: {user.user_id}")
        except Exception as e:
            # 如果 common_repo 中已存在，忽略错误（可能已存在）
            logger.warning(f"写入 common_repo 失败（可能已存在）: {e}")
        
        return result
    
    def create_fund_account(self, account):
        """创建基金账户（同时写入 common_repo 和旧存储）"""
        # 先调用父类方法，写入旧存储
        result = super().create_fund_account(account)
        
        # 同时写入 common_repo
        from datetime import date as date_type
        # 转换为 common_repo 格式
        open_date_value = account.open_date
        if isinstance(open_date_value, date_type):
            open_date_str = open_date_value.isoformat()
        else:
            open_date_str = str(open_date_value)
        
        common_account_data = {
            'id': account.fund_account_id,
            'fund_account_id': account.fund_account_id,
            'user_id': account.user_id,
            'account_no': account.account_no,
            'account_type': account.account_type,
            'open_date': open_date_str,
            'account_status': getattr(account, 'account_status', 'ACTIVE')
        }
        try:
            self._common_repo.create("fund_account", common_account_data)
        except Exception as e:
            # 如果 common_repo 中已存在，忽略错误（可能已存在）
            logger.warning(f"写入 common_repo 失败（可能已存在）: {e}")
        
        return result

# 创建适配器实例（使用 common/repository 的单例）
repository = RepositoryAdapter(common_repo)
fund_service = FundService(repository)

# ==================== FastAPI应用初始化 ====================
app = FastAPI(
    title="基金交易微服务",
    description="开放式基金交易系统微服务API（完整集成版本）",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ==================== CORS配置 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 注册模块化路由 ====================
app.include_router(user_router, tags=["用户管理（模块化）"])
app.include_router(user_asset_router, tags=["用户资产管理（模块化）"])
app.include_router(bank_account_router, tags=["银行账户管理（模块化）"])
app.include_router(capital_entrust_router, tags=["资金委托管理（模块化）"])
app.include_router(capital_settlement_router, tags=["资金清算管理（模块化）"])
app.include_router(fund_account_router, tags=["基金账户管理（模块化）"])
app.include_router(fund_product_router, tags=["基金产品管理（模块化）"])
app.include_router(transaction_entrust_router, tags=["交易委托管理（模块化）"])
app.include_router(transaction_confirm_router, tags=["交易确认管理（模块化）"])
app.include_router(fund_share_router, tags=["基金份额管理（模块化）"])

# ==================== 辅助函数 ====================
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证Token"""
    token = credentials.credentials
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


# ============================================================================
# ==================== API端点 - 按业务模块分类 ====================
# ============================================================================

# ==================== 1. 系统管理 ====================
@app.get("/", tags=["系统管理"])
async def root():
    """根端点 - 服务信息"""
    return {
        "service": "基金交易微服务",
        "version": "2.0.0",
        "status": "运行中",
        "modules": [
            "user",
            "user_asset",
            "bank_account",
            "capital_entrust",
            "capital_settlement",
            "fund_account",
            "fund_product",
            "transaction_entrust",
            "transaction_confirm",
            "fund_share"
        ]
    }


@app.get("/api/v1/health", tags=["系统管理"])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": str(date.today())}


# ==================== 2. 用户管理 ====================
@app.post("/api/v1/users", response_model=ResponseModel, tags=["用户管理"])
async def create_user(
    request: UserCreateRequest,
    token: str = Depends(verify_token)
):
    """创建用户（兼容性端点）"""
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


@app.get("/api/v1/users/{user_id}", response_model=ResponseModel, tags=["用户管理"])
async def get_user(
    user_id: str,
    token: str = Depends(verify_token)
):
    """获取用户信息（兼容性端点）"""
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


# ==================== 3. 基金账户管理 ====================
@app.post("/api/v1/accounts/open", response_model=ResponseModel, tags=["基金账户管理"])
async def open_fund_account(
    request: FundAccountOpenRequest,
    token: str = Depends(verify_token)
):
    """开通基金账户（兼容性端点）"""
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


# ==================== 4. 基金产品管理 ====================
@app.get("/api/v1/products", response_model=ResponseModel, tags=["基金产品管理"])
async def get_products(
    product_type: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """获取基金产品列表（兼容性端点）"""
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


@app.post("/api/v1/products", response_model=ResponseModel, tags=["基金产品管理"])
async def create_product(
    request: ProductCreateRequest,
    token: str = Depends(verify_token)
):
    """创建基金产品（兼容性端点）"""
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


# ==================== 5. 基金净值管理 ====================
@app.post("/api/v1/nav", response_model=ResponseModel, tags=["基金净值管理"])
async def create_nav(
    request: NavCreateRequest,
    token: str = Depends(verify_token)
):
    """创建基金净值（兼容性端点）"""
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


# ==================== 6. 基金交易 ====================
@app.post("/api/v1/funds/subscribe", response_model=ResponseModel, tags=["基金交易"])
async def subscribe_fund(
    request: FundSubscribeRequest,
    token: str = Depends(verify_token)
):
    """申购基金（兼容性端点）"""
    try:
        result = fund_service.subscribe_fund(
            request.fund_account_id,
            request.product_id,
            request.amount
        )
        logger.info(f"基金申购成功: {result.get('entrust_id')}")
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        handle_exception(e, "申购基金")


@app.post("/api/v1/funds/redeem", response_model=ResponseModel, tags=["基金交易"])
async def redeem_fund(
    request: FundRedeemRequest,
    token: str = Depends(verify_token)
):
    """赎回基金（兼容性端点）"""
    try:
        result = fund_service.redeem_fund(
            request.fund_account_id,
            request.product_id,
            request.share
        )
        logger.info(f"基金赎回成功: {result.get('entrust_id')}")
        return ResponseModel(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        handle_exception(e, "赎回基金")


# ==================== 7. 用户资产管理 ====================
@app.get("/api/v1/assets/{user_id}", response_model=ResponseModel, tags=["用户资产管理"])
async def get_user_assets(
    user_id: str,
    token: str = Depends(verify_token)
):
    """获取用户资产（兼容性端点）"""
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


# ============================================================================
# ==================== 启动配置 ====================
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
