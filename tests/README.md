# 测试说明文档

## 测试结构

本项目包含以下测试模块：

1. **test_models.py** - 数据模型测试
   - 测试所有Pydantic模型的创建和验证
   - 验证默认值和枚举类型

2. **test_service.py** - 业务服务层测试
   - 测试用户管理
   - 测试基金账户管理
   - 测试基金申购和赎回
   - 测试资产计算

3. **test_client.py** - 客户端接口测试
   - 测试HTTP客户端调用
   - 测试高级封装应用
   - 需要先启动微服务

4. **test_integration.py** - 集成测试
   - 测试完整的业务流程
   - 端到端测试

## 运行测试

### 前置条件

1. 安装测试依赖：
```bash
pip install pytest pytest-cov
```

2. 对于客户端测试，需要先启动微服务：
```bash
python main.py
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py

# 运行特定测试类
pytest tests/test_service.py::TestFundService

# 运行特定测试方法
pytest tests/test_service.py::TestFundService::test_create_user
```

### 带覆盖率运行

```bash
pytest --cov=. --cov-report=html
```

### 详细输出

```bash
pytest -v
```

### 跳过需要服务的测试

```bash
pytest -m "not requires_service"
```

## 测试策略

### 单元测试
- 测试单个函数和方法的正确性
- 使用mock隔离依赖
- 快速执行

### 集成测试
- 测试多个组件协同工作
- 验证业务流程完整性
- 使用真实的数据存储

### 端到端测试
- 测试完整的用户场景
- 从API到数据存储的完整流程
- 需要启动完整服务

## 测试数据

测试使用内存存储，每次运行都是干净的环境。测试数据在测试方法中创建，测试结束后自动清理。

## 注意事项

1. 客户端测试需要服务运行在 `http://localhost:8000`
2. 某些测试可能因为网络或服务状态而失败
3. 集成测试会创建真实的数据，但使用内存存储，不影响持久化数据


