# 基金交易系统 - 操作手册

## 目录

1. [系统概述](#系统概述)
2. [快速开始](#快速开始)
3. [用户操作指南](#用户操作指南)
4. [API使用说明](#api使用说明)
5. [交互式客户端使用](#交互式客户端使用)
6. [常见问题](#常见问题)

## 系统概述

基金交易系统是一个基于FastAPI开发的微服务系统，提供以下核心功能：

- 用户注册和管理
- 基金账户开户
- 基金产品查询
- 基金申购和赎回
- 用户资产查询

### 系统访问地址

- **API服务**: http://localhost:8000
- **Swagger文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

## 快速开始

### 前置条件

1. 确保服务已启动（运行 `python run_service.py`）
2. 准备认证Token：`demo_token_2025`

### 使用方式

系统提供三种使用方式：

1. **交互式客户端**（推荐新手使用）
2. **API直接调用**（适合开发集成）
3. **Swagger UI**（适合测试和探索）

## 用户操作指南

### 方式一：使用交互式客户端（推荐）

交互式客户端提供了友好的命令行界面，适合手动操作。

#### 启动客户端

```bash
python interactive_client.py
```

#### 操作流程

**1. 创建用户**

```
请选择操作 (0-10): 1

【创建用户】
------------------------------------------------------------
用户姓名: 张三
身份证号: 320101199001011234
用户类型 [默认: PERSONAL]: 
手机号 [默认: 13800138000]: 
邮箱 [默认: 张三@example.com]: 

【创建成功】
------------------------------------------------------------
  用户ID: user_xxxxx
  用户姓名: 张三
------------------------------------------------------------
```

**2. 开通基金账户**

```
请选择操作 (0-10): 3

【开通基金账户】
------------------------------------------------------------
使用当前用户ID: user_xxxxx
是否使用当前用户? (Y/n): y
账户类型 [默认: INDIVIDUAL]: 

【开户成功】
------------------------------------------------------------
  基金账户ID: account_xxxxx
  用户ID: user_xxxxx
  账户类型: INDIVIDUAL
------------------------------------------------------------
```

**3. 查询基金产品**

```
请选择操作 (0-10): 4

【查询基金产品列表】
------------------------------------------------------------
产品类型筛选（可选，如EQUITY/BOND/MIXED/MONETARY）: 

【找到 1 个产品】
------------------------------------------------------------
  产品 1:
    product_id: prod_xxxxx
    product_name: 测试基金
    product_type: EQUITY
    latest_nav: {'net_value': 1.2345, ...}
------------------------------------------------------------
```

**4. 申购基金**

```
请选择操作 (0-10): 5

【申购基金】
------------------------------------------------------------
使用当前账户ID: account_xxxxx
是否使用当前账户? (Y/n): y
产品ID: prod_xxxxx
申购金额（元）: 10000

【申购成功】
------------------------------------------------------------
  entrust_id: entrust_xxxxx
  share: 8100.00
  amount: 10000.00
  ...
------------------------------------------------------------
```

**5. 查询用户资产**

```
请选择操作 (0-10): 7

【查询用户资产】
------------------------------------------------------------
使用当前用户ID: user_xxxxx
是否使用当前用户? (Y/n): y

【用户资产】
------------------------------------------------------------
  total_asset: 10000.00
  total_fund_asset: 10000.00
  total_balance: 0.00
  fund_assets: [...]
------------------------------------------------------------
```

**6. 赎回基金**

```
请选择操作 (0-10): 6

【赎回基金】
------------------------------------------------------------
使用当前账户ID: account_xxxxx
是否使用当前账户? (Y/n): y
产品ID: prod_xxxxx
赎回份额: 2000

【赎回成功】
------------------------------------------------------------
  entrust_id: entrust_xxxxx
  amount: 2469.00
  share: 2000.00
  ...
------------------------------------------------------------
```

详细操作指南请参考：[交互式客户端使用指南](INTERACTIVE_CLIENT_GUIDE.md)

### 方式二：使用Swagger UI

1. 打开浏览器访问：http://localhost:8000/docs
2. 点击右上角 "Authorize" 按钮
3. 输入Token：`demo_token_2025`
4. 选择要调用的API接口
5. 点击 "Try it out"
6. 填写请求参数
7. 点击 "Execute" 执行

### 方式三：使用API直接调用

#### 使用curl命令

**1. 创建用户**

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer demo_token_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "张三",
    "identity_no": "320101199001011234",
    "user_type": "PERSONAL",
    "phone": "13800138000",
    "email": "zhangsan@example.com"
  }'
```

**2. 开通基金账户**

```bash
curl -X POST "http://localhost:8000/api/v1/accounts/open" \
  -H "Authorization: Bearer demo_token_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_xxxxx",
    "account_type": "INDIVIDUAL"
  }'
```

**3. 查询基金产品**

```bash
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer demo_token_2025"
```

**4. 申购基金**

```bash
curl -X POST "http://localhost:8000/api/v1/funds/subscribe" \
  -H "Authorization: Bearer demo_token_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "fund_account_id": "account_xxxxx",
    "product_id": "prod_xxxxx",
    "amount": 10000.00
  }'
```

**5. 赎回基金**

```bash
curl -X POST "http://localhost:8000/api/v1/funds/redeem" \
  -H "Authorization: Bearer demo_token_2025" \
  -H "Content-Type: application/json" \
  -d '{
    "fund_account_id": "account_xxxxx",
    "product_id": "prod_xxxxx",
    "share": 2000.00
  }'
```

**6. 查询用户资产**

```bash
curl -X GET "http://localhost:8000/api/v1/assets/user_xxxxx" \
  -H "Authorization: Bearer demo_token_2025"
```

#### 使用Python客户端

```python
from client import FundClient

# 创建客户端
client = FundClient(base_url="http://localhost:8000", token="demo_token_2025")

# 创建用户
user_id = client.create_user(
    user_name="张三",
    identity_no="320101199001011234",
    user_type="PERSONAL",
    phone="13800138000",
    email="zhangsan@example.com"
)

# 开通账户
account_id = client.open_fund_account(user_id, "INDIVIDUAL")

# 查询产品
products = client.get_products()
product_id = products[0]['product_id']

# 申购基金
result = client.subscribe_fund(account_id, product_id, 10000.00)
print(f"申购成功，获得份额: {result['share']}")

# 查询资产
assets = client.get_user_assets(user_id)
print(f"总资产: {assets['total_asset']}")

# 赎回基金
redeem_result = client.redeem_fund(account_id, product_id, 2000.00)
print(f"赎回成功，获得金额: {redeem_result['amount']}")
```

## API使用说明

### 认证方式

所有API接口都需要在请求头中包含认证Token：

```
Authorization: Bearer demo_token_2025
```

### 请求格式

- **Content-Type**: `application/json`
- **请求体**: JSON格式

### 响应格式

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 业务数据
  }
}
```

错误响应：

```json
{
  "detail": "错误描述信息"
}
```

### 主要API接口

#### 1. 创建用户

**接口**: `POST /api/v1/users`

**请求参数**:

```json
{
  "user_name": "张三",
  "identity_no": "320101199001011234",
  "user_type": "PERSONAL",
  "phone": "13800138000",
  "email": "zhangsan@example.com"
}
```

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "user_xxxxx",
    "user_name": "张三",
    "user_type": "PERSONAL"
  }
}
```

#### 2. 查询用户信息

**接口**: `GET /api/v1/users/{user_id}`

**路径参数**:
- `user_id`: 用户ID

#### 3. 开通基金账户

**接口**: `POST /api/v1/accounts/open`

**请求参数**:

```json
{
  "user_id": "user_xxxxx",
  "account_type": "INDIVIDUAL"
}
```

**账户类型**:
- `INDIVIDUAL`: 个人账户
- `INSTITUTION`: 机构账户

#### 4. 查询基金产品列表

**接口**: `GET /api/v1/products`

**查询参数**（可选）:
- `product_type`: 产品类型（EQUITY/BOND/MIXED/MONETARY）

#### 5. 申购基金

**接口**: `POST /api/v1/funds/subscribe`

**请求参数**:

```json
{
  "fund_account_id": "account_xxxxx",
  "product_id": "prod_xxxxx",
  "amount": 10000.00
}
```

**说明**:
- `amount`: 申购金额（元），必须大于0

#### 6. 赎回基金

**接口**: `POST /api/v1/funds/redeem`

**请求参数**:

```json
{
  "fund_account_id": "account_xxxxx",
  "product_id": "prod_xxxxx",
  "share": 2000.00
}
```

**说明**:
- `share`: 赎回份额，必须大于0且不超过持有份额

#### 7. 查询用户资产

**接口**: `GET /api/v1/assets/{user_id}`

**路径参数**:
- `user_id`: 用户ID

**响应示例**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_asset": 10000.00,
    "total_fund_asset": 10000.00,
    "total_balance": 0.00,
    "fund_assets": [
      {
        "product_id": "prod_xxxxx",
        "fund_share": 8100.00,
        "fund_value": 10000.00,
        "nav": 1.2345
      }
    ]
  }
}
```

## 交互式客户端使用

交互式客户端提供了完整的菜单操作界面，支持所有业务功能。

### 功能菜单

```
============================================================
           基金交易系统 - 交互式客户端
============================================================
1.  创建用户
2.  查询用户信息
3.  开通基金账户（开户）
4.  查询基金产品列表
5.  申购基金
6.  赎回基金
7.  查询用户资产
8.  创建基金产品（管理员）
9.  创建基金净值（管理员）
10. 完整业务流程演示
0.  退出
============================================================
```

### 使用技巧

1. **状态记忆**: 客户端会记住当前用户和账户，方便连续操作
2. **输入验证**: 所有输入都有格式验证，确保数据正确
3. **错误提示**: 操作失败会显示详细错误信息
4. **结果展示**: 操作结果以格式化方式展示，易于阅读

详细使用说明请参考：[交互式客户端使用指南](INTERACTIVE_CLIENT_GUIDE.md)

## 常见问题

### Q1: 如何获取认证Token？

A: 当前系统使用固定的Token：`demo_token_2025`。在生产环境中，需要通过登录接口获取Token。

### Q2: 服务连接失败怎么办？

A: 请检查：
1. 服务是否已启动（运行 `python run_service.py`）
2. 端口是否正确（默认8000）
3. 防火墙是否阻止了连接

### Q3: 申购时提示余额不足？

A: 请确保：
1. 用户已开通基金账户
2. 账户有足够的可用余额
3. 申购金额不超过可用余额

### Q4: 赎回时提示份额不足？

A: 请确保：
1. 用户持有该基金产品
2. 赎回份额不超过持有份额
3. 产品ID正确

### Q5: 如何查看所有可用的基金产品？

A: 使用查询产品接口，不传入 `product_type` 参数即可查询所有产品。

### Q6: 数据会持久化保存吗？

A: 当前版本使用内存存储，服务重启后数据会丢失。生产环境需要配置数据库持久化。

### Q7: 如何查看API文档？

A: 访问以下地址：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Q8: 支持哪些产品类型？

A: 支持以下产品类型：
- `EQUITY`: 股票型
- `BOND`: 债券型
- `MIXED`: 混合型
- `MONETARY`: 货币型

### Q9: 如何创建新的基金产品？

A: 使用交互式客户端选择选项8，或调用 `POST /api/v1/products` 接口。

### Q10: 如何设置基金净值？

A: 使用交互式客户端选择选项9，或调用 `POST /api/v1/nav` 接口。

## 技术支持

如有其他问题，请：

1. 查看API文档：http://localhost:8000/docs
2. 查看系统日志
3. 联系技术支持团队

---

**文档版本**: 1.0.0  
**最后更新**: 2025-12-14

