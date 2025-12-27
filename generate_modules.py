"""
批量生成模块基础结构
"""
import os

# 模块定义
modules = [
    {
        'name': 'bank_account',
        'description': '银行账户',
        'table': 'user_bank_card',
        'class_name': 'BankAccount'
    },
    {
        'name': 'capital_entrust',
        'description': '资金委托',
        'table': 'capital_change_entrust',
        'class_name': 'CapitalEntrust'
    },
    {
        'name': 'capital_settlement',
        'description': '资金清算',
        'table': 'capital_settlement',
        'class_name': 'CapitalSettlement'
    },
    {
        'name': 'fund_account',
        'description': '基金账户',
        'table': 'fund_account',
        'class_name': 'FundAccount'
    },
    {
        'name': 'fund_product',
        'description': '基金产品',
        'table': 'fund_product',
        'class_name': 'FundProduct'
    },
    {
        'name': 'transaction_entrust',
        'description': '交易委托',
        'table': 'fund_transaction_entrust',
        'class_name': 'TransactionEntrust'
    },
    {
        'name': 'transaction_confirm',
        'description': '交易确认',
        'table': 'fund_transaction_confirm',
        'class_name': 'TransactionConfirm'
    },
    {
        'name': 'fund_share',
        'description': '基金份额',
        'table': 'fund_share',
        'class_name': 'FundShare'
    },
]

# Schema模板
schema_template = '''"""
{description}数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from common.enums import *


class {class_name}(BaseModel):
    """{description}模型"""
    # TODO: 根据表结构定义字段
    pass


class {class_name}CreateRequest(BaseModel):
    """{description}创建请求"""
    # TODO: 定义创建请求字段
    pass


class {class_name}Response(BaseModel):
    """{description}响应"""
    # TODO: 定义响应字段
    pass
'''

# App模板
app_template = '''"""
{description}应用服务层
"""
from typing import Optional, List
from datetime import datetime
from common.repository import get_repository
from .{module_name}_schema import {class_name}, {class_name}CreateRequest


class {class_name}App:
    """{description}应用服务"""
    
    def __init__(self):
        self.repo = get_repository()
        self.table_name = "{table}"
    
    def _generate_id(self) -> str:
        """生成ID"""
        import uuid
        return f"{prefix}_{{uuid.uuid4().hex[:16]}}"
    
    def create(self, request: {class_name}CreateRequest) -> {class_name}:
        """创建{description}"""
        # TODO: 实现创建逻辑
        pass
    
    def get(self, id: str) -> Optional[{class_name}]:
        """获取{description}"""
        # TODO: 实现获取逻辑
        pass
    
    def list(self, filters: Optional[dict] = None) -> List[{class_name}]:
        """列出{description}"""
        # TODO: 实现列表逻辑
        pass
'''

# Web模板
web_template = '''"""
{description}微服务API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .{module_name}_schema import {class_name}, {class_name}CreateRequest, {class_name}Response
from .{module_name}_app import {class_name}App


router = APIRouter(prefix="/api/v1/{api_prefix}", tags=["{description}"])


def get_{module_name}_app() -> {class_name}App:
    """获取{description}应用服务"""
    return {class_name}App()


@router.post("", response_model={class_name}Response, status_code=status.HTTP_201_CREATED)
async def create_{module_name}(
    request: {class_name}CreateRequest,
    app: {class_name}App = Depends(get_{module_name}_app)
):
    """创建{description}"""
    try:
        obj = app.create(request)
        return {class_name}Response(**obj.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建{description}失败: {{str(e)}}"
        )


@router.get("/{{id}}", response_model={class_name}Response)
async def get_{module_name}(
    id: str,
    app: {class_name}App = Depends(get_{module_name}_app)
):
    """获取{description}信息"""
    obj = app.get(id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{description}不存在: {{id}}"
        )
    return {class_name}Response(**obj.model_dump())
'''

# API模板
api_template = '''"""
{description}客户端API
"""
import requests
from typing import List, Dict, Any
from .{module_name}_schema import {class_name}CreateRequest, {class_name}Response


class {class_name}API:
    """{description}客户端API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = "demo_token_2025"):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {{
            "Authorization": f"Bearer {{token}}",
            "Content-Type": "application/json"
        }}
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{{self.base_url}}{{endpoint}}"
        response = requests.request(method=method, url=url, headers=self.headers, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get('detail', '未知错误')
            raise Exception(f"HTTP错误 {{response.status_code}}: {{error_detail}}")
    
    def create(self, request: {class_name}CreateRequest) -> {class_name}Response:
        """创建{description}"""
        result = self._request("POST", "/api/v1/{api_prefix}", json=request.model_dump())
        return {class_name}Response(**result)
    
    def get(self, id: str) -> {class_name}Response:
        """获取{description}"""
        result = self._request("GET", f"/api/v1/{api_prefix}/{{id}}")
        return {class_name}Response(**result)
'''

# 生成文件
for module in modules:
    module_name = module['name']
    module_dir = f"modules/{module_name}"
    
    # 确保目录存在
    os.makedirs(module_dir, exist_ok=True)
    
    # 生成__init__.py
    init_file = f"{module_dir}/__init__.py"
    if not os.path.exists(init_file):
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'"""{module["description"]}模块"""\n')
    
    # 生成schema文件
    schema_file = f"{module_dir}/{module_name}_schema.py"
    if not os.path.exists(schema_file):
        prefix = module_name.upper().replace('_', '')[:4]
        content = schema_template.format(
            description=module['description'],
            class_name=module['class_name'],
            module_name=module_name
        )
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 创建: {schema_file}")
    
    # 生成app文件
    app_file = f"{module_dir}/{module_name}_app.py"
    if not os.path.exists(app_file):
        prefix = module_name.upper().replace('_', '')[:4]
        content = app_template.format(
            description=module['description'],
            class_name=module['class_name'],
            module_name=module_name,
            table=module['table'],
            prefix=prefix
        )
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 创建: {app_file}")
    
    # 生成web文件
    web_file = f"{module_dir}/{module_name}_web.py"
    if not os.path.exists(web_file):
        api_prefix = module_name.replace('_', '-')
        content = web_template.format(
            description=module['description'],
            class_name=module['class_name'],
            module_name=module_name,
            api_prefix=api_prefix
        )
        with open(web_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 创建: {web_file}")
    
    # 生成api文件
    api_file = f"{module_dir}/{module_name}_api.py"
    if not os.path.exists(api_file):
        api_prefix = module_name.replace('_', '-')
        content = api_template.format(
            description=module['description'],
            class_name=module['class_name'],
            module_name=module_name,
            api_prefix=api_prefix
        )
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 创建: {api_file}")

print("\n所有模块基础结构已生成！")
print("请根据实际需求完善各模块的实现。")


