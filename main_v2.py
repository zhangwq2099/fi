"""
FastAPI微服务主入口 - 模块化版本
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入各模块路由
from modules.user.user_web import router as user_router
from modules.user_asset.user_asset_web import router as user_asset_router
# 其他模块路由将在完善后添加
# from modules.bank_account.bank_account_web import router as bank_account_router
# from modules.capital_entrust.capital_entrust_web import router as capital_entrust_router
# from modules.capital_settlement.capital_settlement_web import router as capital_settlement_router
# from modules.fund_account.fund_account_web import router as fund_account_router
# from modules.fund_product.fund_product_web import router as fund_product_router
# from modules.transaction_entrust.transaction_entrust_web import router as transaction_entrust_router
# from modules.transaction_confirm.transaction_confirm_web import router as transaction_confirm_router
# from modules.fund_share.fund_share_web import router as fund_share_router

app = FastAPI(
    title="基金交易微服务",
    description="开放式基金交易系统微服务API（模块化版本）",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user_router)
app.include_router(user_asset_router)
# 其他模块路由将在完善后添加
# app.include_router(bank_account_router)
# app.include_router(capital_entrust_router)
# app.include_router(capital_settlement_router)
# app.include_router(fund_account_router)
# app.include_router(fund_product_router)
# app.include_router(transaction_entrust_router)
# app.include_router(transaction_confirm_router)
# app.include_router(fund_share_router)

@app.get("/")
async def root():
    return {
        "service": "基金交易微服务",
        "version": "2.0.0",
        "status": "运行中",
        "modules": [
            "user",
            "user_asset",
            # 其他模块将在完善后添加
        ]
    }

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_v2:app", host="0.0.0.0", port=8000, reload=True)

