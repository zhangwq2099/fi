# 代码重构指南

## 重构概述

根据需求，已将系统按实体拆分为多个模块，每个模块遵循统一的4层架构设计：

1. **`{module_name}_schema.py`** - 数据模型层
   - 使用Pydantic定义数据模型
   - 包含请求模型（Request）和响应模型（Response）
   - 数据验证和类型检查

2. **`{module_name}_app.py`** - 业务逻辑层
   - 实现核心业务逻辑
   - 调用统一数据存储层（`common/repository.py`）
   - 业务规则验证和处理

3. **`{module_name}_api.py`** - API接口层
   - 定义API接口方法
   - 参数处理和转换
   - 调用业务逻辑层（`*_app.py`）

4. **`{module_name}_web.py`** - Web路由层
   - 定义FastAPI路由和端点
   - 请求/响应处理
   - 通过`main_v2.py`注册到主应用

### 命名规范

- **模块目录**: 使用小写字母和下划线（snake_case），如 `user_asset/`
- **文件名**: 使用小写字母和下划线，如 `user_asset_schema.py`
- **类名**: 使用大驼峰命名（PascalCase），如 `UserApp`
- **函数/变量名**: 使用小写字母和下划线，如 `create_user()`

## 已完成的模块

### 1. 用户模块 (modules/user/)
- ✅ `user_schema.py` - 用户数据模型
- ✅ `user_app.py` - 用户应用服务
- ✅ `user_web.py` - 用户微服务API
- ✅ `user_api.py` - 用户客户端API

### 2. 用户资产模块 (modules/user_asset/)
- ✅ `user_asset_schema.py` - 用户资产数据模型
- ✅ `user_asset_app.py` - 用户资产应用服务
- ✅ `user_asset_web.py` - 用户资产微服务API
- ✅ `user_asset_api.py` - 用户资产客户端API

## 待创建的模块

### 3. 银行账户模块 (modules/bank_account/)
对应表：`user_bank_card`
- ⏳ `bank_account_schema.py`
- ⏳ `bank_account_app.py`
- ⏳ `bank_account_web.py`
- ⏳ `bank_account_api.py`

### 4. 资金委托模块 (modules/capital_entrust/)
对应表：`capital_change_entrust`
- ⏳ `capital_entrust_schema.py`
- ⏳ `capital_entrust_app.py`
- ⏳ `capital_entrust_web.py`
- ⏳ `capital_entrust_api.py`

### 5. 资金清算模块 (modules/capital_settlement/)
对应表：`capital_settlement`
- ⏳ `capital_settlement_schema.py`
- ⏳ `capital_settlement_app.py`
- ⏳ `capital_settlement_web.py`
- ⏳ `capital_settlement_api.py`

### 6. 基金账户模块 (modules/fund_account/)
对应表：`fund_account`, `fund_account_entrust`
- ⏳ `fund_account_schema.py`
- ⏳ `fund_account_app.py`
- ⏳ `fund_account_web.py`
- ⏳ `fund_account_api.py`

### 7. 基金产品模块 (modules/fund_product/)
对应表：`fund_product`, `fund_net_value`
- ⏳ `fund_product_schema.py`
- ⏳ `fund_product_app.py`
- ⏳ `fund_product_web.py`
- ⏳ `fund_product_api.py`

### 8. 交易委托模块 (modules/transaction_entrust/)
对应表：`fund_transaction_entrust`
- ⏳ `transaction_entrust_schema.py`
- ⏳ `transaction_entrust_app.py`
- ⏳ `transaction_entrust_web.py`
- ⏳ `transaction_entrust_api.py`

### 9. 交易确认模块 (modules/transaction_confirm/)
对应表：`fund_transaction_confirm`
- ⏳ `transaction_confirm_schema.py`
- ⏳ `transaction_confirm_app.py`
- ⏳ `transaction_confirm_web.py`
- ⏳ `transaction_confirm_api.py`

### 10. 基金份额模块 (modules/fund_share/)
对应表：`fund_share`
- ⏳ `fund_share_schema.py`
- ⏳ `fund_share_app.py`
- ⏳ `fund_share_web.py`
- ⏳ `fund_share_api.py`

## 模块创建模板

### Schema模板 (示例：bank_account_schema.py)

```python
"""
银行账户数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from common.enums import AccountStatus


class UserBankCard(BaseModel):
    """用户银行卡模型"""
    card_id: str = Field(..., description="银行卡ID")
    user_id: str = Field(..., description="用户ID")
    bank_code: str = Field(..., max_length=20, description="银行代码")
    bank_name: Optional[str] = Field(None, max_length=50, description="银行名称")
    card_no: str = Field(..., max_length=30, description="银行卡号")
    card_type: str = Field("DEBIT", description="卡类型：DEBIT/CREDIT")
    card_status: str = Field("ACTIVE", description="状态")
    bind_time: datetime = Field(default_factory=datetime.now, description="绑定时间")
    is_default: bool = Field(False, description="是否默认卡")


class BankCardCreateRequest(BaseModel):
    """银行卡创建请求"""
    user_id: str
    bank_code: str
    card_no: str
    bank_name: Optional[str] = None
    card_type: str = "DEBIT"
    is_default: bool = False


class BankCardResponse(BaseModel):
    """银行卡响应"""
    card_id: str
    user_id: str
    bank_code: str
    bank_name: Optional[str]
    card_type: str
    card_status: str
    bind_time: datetime
    is_default: bool
```

### App模板 (示例：bank_account_app.py)

```python
"""
银行账户应用服务层
"""
from typing import Optional, List
from datetime import datetime
from common.repository import get_repository
from .bank_account_schema import UserBankCard, BankCardCreateRequest


class BankAccountApp:
    """银行账户应用服务"""
    
    def __init__(self):
        self.repo = get_repository()
        self.table_name = "user_bank_card"
    
    def _generate_id(self) -> str:
        """生成银行卡ID"""
        import uuid
        return f"CARD_{uuid.uuid4().hex[:16]}"
    
    def create_bank_card(self, request: BankCardCreateRequest) -> UserBankCard:
        """创建银行卡"""
        card_id = self._generate_id()
        
        card_data = {
            'id': card_id,
            'card_id': card_id,
            'user_id': request.user_id,
            'bank_code': request.bank_code,
            'bank_name': request.bank_name,
            'card_no': request.card_no,
            'card_type': request.card_type,
            'card_status': 'ACTIVE',
            'bind_time': datetime.now(),
            'is_default': request.is_default
        }
        
        self.repo.create(self.table_name, card_data)
        return UserBankCard(**card_data)
    
    def get_bank_card(self, card_id: str) -> Optional[UserBankCard]:
        """获取银行卡"""
        card_data = self.repo.get(self.table_name, card_id)
        if card_data:
            return UserBankCard(**card_data)
        return None
    
    def get_user_bank_cards(self, user_id: str) -> List[UserBankCard]:
        """获取用户的所有银行卡"""
        cards_data = self.repo.list(self.table_name, {'user_id': user_id})
        return [UserBankCard(**data) for data in cards_data]
```

### Web模板 (示例：bank_account_web.py)

```python
"""
银行账户微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .bank_account_schema import UserBankCard, BankCardCreateRequest, BankCardResponse
from .bank_account_app import BankAccountApp


router = APIRouter(prefix="/api/v1/bank-cards", tags=["银行账户"])


def get_bank_account_app() -> BankAccountApp:
    """获取银行账户应用服务"""
    return BankAccountApp()


@router.post("", response_model=BankCardResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_card(
    request: BankCardCreateRequest,
    app: BankAccountApp = Depends(get_bank_account_app)
):
    """创建银行卡"""
    try:
        card = app.create_bank_card(request)
        return BankCardResponse(**card.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建银行卡失败: {str(e)}"
        )


@router.get("/{card_id}", response_model=BankCardResponse)
async def get_bank_card(
    card_id: str,
    app: BankAccountApp = Depends(get_bank_account_app)
):
    """获取银行卡信息"""
    card = app.get_bank_card(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"银行卡不存在: {card_id}"
        )
    return BankCardResponse(**card.dict())


@router.get("/user/{user_id}", response_model=List[BankCardResponse])
async def get_user_bank_cards(
    user_id: str,
    app: BankAccountApp = Depends(get_bank_account_app)
):
    """获取用户的所有银行卡"""
    cards = app.get_user_bank_cards(user_id)
    return [BankCardResponse(**card.dict()) for card in cards]
```

### API模板 (示例：bank_account_api.py)

```python
"""
银行账户客户端API
"""
import requests
from typing import List, Dict, Any
from .bank_account_schema import BankCardCreateRequest, BankCardResponse


class BankAccountAPI:
    """银行账户客户端API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = "demo_token_2025"):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method=method, url=url, headers=self.headers, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get('detail', '未知错误')
            raise Exception(f"HTTP错误 {response.status_code}: {error_detail}")
    
    def create_bank_card(self, request: BankCardCreateRequest) -> BankCardResponse:
        """创建银行卡"""
        result = self._request("POST", "/api/v1/bank-cards", json=request.dict())
        return BankCardResponse(**result)
    
    def get_bank_card(self, card_id: str) -> BankCardResponse:
        """获取银行卡"""
        result = self._request("GET", f"/api/v1/bank-cards/{card_id}")
        return BankCardResponse(**result)
    
    def get_user_bank_cards(self, user_id: str) -> List[BankCardResponse]:
        """获取用户的所有银行卡"""
        result = self._request("GET", f"/api/v1/bank-cards/user/{user_id}")
        return [BankCardResponse(**item) for item in result]
```

## 主入口文件更新

需要创建新的 `main.py` 来整合所有模块：

```python
"""
FastAPI微服务主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入各模块路由
from modules.user.user_web import router as user_router
from modules.user_asset.user_asset_web import router as user_asset_router
# ... 其他模块路由

app = FastAPI(
    title="基金交易微服务",
    description="开放式基金交易系统微服务API",
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
# ... 其他模块路由

@app.get("/")
async def root():
    return {
        "service": "基金交易微服务",
        "version": "2.0.0",
        "status": "运行中"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

## 注意事项

1. 所有模块使用统一的 `common/repository.py` 进行数据存储
2. 所有枚举定义在 `common/enums.py`
3. 模块间通过应用服务层调用，避免直接访问数据层
4. 每个模块的 `__init__.py` 需要导出主要类
5. 测试文件也需要相应拆分到各模块下

## 下一步

1. 按照模板创建剩余模块
2. 更新主入口文件整合所有路由
3. 更新测试文件
4. 更新文档


