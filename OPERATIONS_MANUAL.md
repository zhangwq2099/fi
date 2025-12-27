# 基金交易系统 - 运维文档

## 目录

1. [系统概述](#系统概述)
2. [环境要求](#环境要求)
3. [部署指南](#部署指南)
4. [配置说明](#配置说明)
5. [服务管理](#服务管理)
6. [监控与日志](#监控与日志)
7. [故障处理](#故障处理)
8. [性能优化](#性能优化)
9. [安全建议](#安全建议)
10. [备份与恢复](#备份与恢复)

## 系统概述

基金交易系统是一个基于FastAPI的微服务应用，提供基金交易相关的RESTful API服务。

### 系统架构

- **Web框架**: FastAPI
- **ASGI服务器**: Uvicorn
- **数据存储**: 内存（当前版本）
- **认证方式**: Bearer Token

### 服务端口

- **默认端口**: 8000
- **健康检查**: `/api/v1/health`

## 环境要求

### 系统要求

- **操作系统**: Linux / Windows / macOS
- **Python版本**: 3.8+
- **内存**: 最低512MB，推荐1GB+
- **磁盘空间**: 最低100MB

### 依赖软件

- Python 3.8+
- pip
- （可选）虚拟环境工具：venv / virtualenv

## 部署指南

### 方式一：开发环境部署

#### 1. 克隆或获取代码

```bash
# 进入项目目录
cd /path/to/fi
```

#### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 启动服务

```bash
# 使用启动脚本（推荐）
python run_service.py

# 或直接运行
python main_v2.py

# 或使用uvicorn
uvicorn main_v2:app --host 0.0.0.0 --port 8000 --reload
```

#### 5. 验证服务

```bash
# 检查健康状态
curl http://localhost:8000/api/v1/health

# 或访问浏览器
# http://localhost:8000/docs
```

### 方式二：生产环境部署

#### 1. 使用systemd（Linux）

创建服务文件 `/etc/systemd/system/fund-trading.service`:

```ini
[Unit]
Description=Fund Trading Microservice
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/fund-trading
Environment="PATH=/opt/fund-trading/venv/bin"
ExecStart=/opt/fund-trading/venv/bin/uvicorn main_v2:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start fund-trading

# 设置开机自启
sudo systemctl enable fund-trading

# 查看状态
sudo systemctl status fund-trading
```

#### 2. 使用Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main_v2:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
# 构建镜像
docker build -t fund-trading:latest .

# 运行容器
docker run -d -p 8000:8000 --name fund-trading fund-trading:latest

# 查看日志
docker logs -f fund-trading
```

#### 3. 使用Nginx反向代理

创建Nginx配置 `/etc/nginx/sites-available/fund-trading`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/fund-trading /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 配置说明

### 服务配置

#### 端口配置

修改 `run_service.py` 或启动命令中的端口：

```python
uvicorn.run(
    "main_v2:app",
    host="0.0.0.0",
    port=8000,  # 修改端口
    reload=True,
    log_level="info"
)
```

#### 认证Token配置

当前版本使用固定Token，修改 `main.py` 中的验证逻辑：

```python
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != "demo_token_2025":  # 修改Token
        raise HTTPException(...)
    return token
```

**生产环境建议**：
- 使用JWT Token
- 实现Token刷新机制
- 配置Token过期时间

#### CORS配置

修改 `main_v2.py` 中的CORS设置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 环境变量配置

创建 `.env` 文件（需要安装python-dotenv）：

```bash
# 服务配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# 认证配置
AUTH_TOKEN=demo_token_2025

# 数据库配置（未来扩展）
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

在代码中读取：

```python
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
```

## 服务管理

### 启动服务

```bash
# 开发环境
python run_service.py

# 生产环境（后台运行）
nohup uvicorn main_v2:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

# 使用systemd
sudo systemctl start fund-trading
```

### 停止服务

```bash
# 查找进程
ps aux | grep uvicorn

# 停止进程
kill <PID>

# 使用systemd
sudo systemctl stop fund-trading
```

### 重启服务

```bash
# 使用systemd
sudo systemctl restart fund-trading

# 手动重启
kill <PID>
python run_service.py
```

### 查看服务状态

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 查看进程
ps aux | grep uvicorn

# 查看端口
netstat -tlnp | grep 8000
# 或
lsof -i :8000

# 使用systemd
sudo systemctl status fund-trading
```

## 监控与日志

### 日志配置

#### 应用日志

FastAPI默认使用Uvicorn的日志，可以通过环境变量或启动参数配置：

```bash
# 设置日志级别
uvicorn main_v2:app --log-level info

# 日志级别选项：critical, error, warning, info, debug, trace
```

#### 自定义日志

在代码中配置日志：

```python
import logging
import sys

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
```

### 监控指标

#### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:8000/api/v1/health

# 预期响应
{"status": "healthy"}
```

#### 性能监控

建议集成监控工具：

1. **Prometheus + Grafana**
   - 监控请求量、响应时间、错误率
   - 配置告警规则

2. **APM工具**
   - New Relic
   - Datadog
   - Elastic APM

3. **日志聚合**
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Loki + Grafana

### 日志查看

```bash
# 查看实时日志
tail -f app.log

# 查看最近100行
tail -n 100 app.log

# 搜索错误日志
grep ERROR app.log

# 使用systemd查看日志
sudo journalctl -u fund-trading -f
```

## 故障处理

### 常见问题

#### 1. 服务无法启动

**症状**: 启动命令执行后立即退出

**排查步骤**:
```bash
# 检查Python版本
python --version

# 检查依赖是否安装
pip list | grep fastapi
pip list | grep uvicorn

# 检查端口是否被占用
netstat -tlnp | grep 8000
lsof -i :8000

# 查看错误日志
python run_service.py 2>&1 | tee error.log
```

**解决方案**:
- 确保Python版本 >= 3.8
- 重新安装依赖：`pip install -r requirements.txt`
- 更换端口或停止占用端口的进程
- 检查代码语法错误

#### 2. 服务启动但无法访问

**症状**: 服务启动成功，但无法通过HTTP访问

**排查步骤**:
```bash
# 检查服务是否监听
netstat -tlnp | grep 8000

# 检查防火墙
sudo ufw status
sudo iptables -L

# 检查本地连接
curl http://localhost:8000/api/v1/health

# 检查外部连接
curl http://<server-ip>:8000/api/v1/health
```

**解决方案**:
- 确保服务监听 `0.0.0.0` 而不是 `127.0.0.1`
- 开放防火墙端口：`sudo ufw allow 8000`
- 检查网络配置

#### 3. API返回401认证错误

**症状**: 请求API返回401 Unauthorized

**排查步骤**:
```bash
# 检查请求头
curl -v -H "Authorization: Bearer demo_token_2025" http://localhost:8000/api/v1/health

# 检查Token配置
grep -r "demo_token_2025" main*.py
```

**解决方案**:
- 确保请求头包含正确的Token
- 检查服务端Token配置
- 验证Token格式：`Bearer <token>`

#### 4. 内存占用过高

**症状**: 服务运行一段时间后内存占用持续增长

**排查步骤**:
```bash
# 查看内存使用
ps aux | grep uvicorn
top -p <PID>

# 查看内存详情
cat /proc/<PID>/status | grep VmRSS
```

**解决方案**:
- 当前版本使用内存存储，数据会持续增长
- 建议定期重启服务（如果数据可丢失）
- 生产环境应使用数据库持久化
- 配置内存限制和自动重启

#### 5. 响应时间过长

**症状**: API响应时间超过预期

**排查步骤**:
```bash
# 测试响应时间
time curl http://localhost:8000/api/v1/health

# 查看系统负载
top
htop

# 检查网络延迟
ping localhost
```

**解决方案**:
- 优化业务逻辑
- 增加服务器资源
- 使用缓存（Redis）
- 数据库查询优化（如果使用数据库）

### 紧急处理流程

1. **服务完全不可用**
   ```bash
   # 立即重启服务
   sudo systemctl restart fund-trading
   
   # 或手动重启
   pkill -f uvicorn
   python run_service.py
   ```

2. **数据异常**
   - 检查日志文件
   - 验证数据一致性
   - 必要时回滚到备份

3. **安全事件**
   - 立即停止服务
   - 检查访问日志
   - 更换认证Token
   - 通知安全团队

## 性能优化

### 1. 服务器配置

- **多进程运行**:
```bash
uvicorn main_v2:app --workers 4 --host 0.0.0.0 --port 8000
```

- **使用Gunicorn + Uvicorn**:
```bash
gunicorn main_v2:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 应用优化

- 启用异步处理
- 使用连接池（数据库）
- 实现缓存机制
- 优化数据库查询

### 3. 负载均衡

使用Nginx或HAProxy进行负载均衡：

```nginx
upstream fund_trading {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://fund_trading;
    }
}
```

## 安全建议

### 1. 认证安全

- ✅ 使用强密码策略
- ✅ 实现JWT Token认证
- ✅ 配置Token过期时间
- ✅ 实现Token刷新机制
- ✅ 使用HTTPS传输

### 2. 网络安全

- ✅ 配置防火墙规则
- ✅ 限制访问IP（如需要）
- ✅ 使用反向代理（Nginx）
- ✅ 启用HTTPS/SSL

### 3. 数据安全

- ✅ 敏感数据加密存储
- ✅ 定期备份数据
- ✅ 实现数据访问审计
- ✅ 配置数据保留策略

### 4. 应用安全

- ✅ 输入验证和过滤
- ✅ SQL注入防护（如使用数据库）
- ✅ XSS防护
- ✅ CSRF防护
- ✅ 请求限流

### 5. 运维安全

- ✅ 最小权限原则
- ✅ 定期更新依赖
- ✅ 安全日志监控
- ✅ 漏洞扫描

## 备份与恢复

### 数据备份

#### 当前版本（内存存储）

当前版本使用内存存储，服务重启后数据会丢失。建议：

1. **定期导出数据**（如果实现导出功能）
2. **日志记录**：记录所有关键操作
3. **快照备份**：定期保存服务状态

#### 未来版本（数据库）

如果迁移到数据库，建议：

1. **数据库备份**:
```bash
# PostgreSQL
pg_dump -U user -d dbname > backup.sql

# MySQL
mysqldump -u user -p dbname > backup.sql
```

2. **定期备份**:
```bash
# 添加到crontab
0 2 * * * /path/to/backup.sh
```

3. **备份验证**:
```bash
# 测试恢复
psql -U user -d dbname < backup.sql
```

### 恢复流程

1. **停止服务**
2. **恢复数据**（如果使用数据库）
3. **验证数据完整性**
4. **重启服务**
5. **验证服务功能**

## 升级指南

### 版本升级

1. **备份当前版本**
2. **停止服务**
3. **更新代码**
4. **更新依赖**: `pip install -r requirements.txt --upgrade`
5. **运行测试**: `pytest`
6. **启动服务**
7. **验证功能**

### 回滚流程

1. **停止当前服务**
2. **恢复备份版本**
3. **重启服务**
4. **验证功能**

## 附录

### 常用命令

```bash
# 服务管理
systemctl start fund-trading
systemctl stop fund-trading
systemctl restart fund-trading
systemctl status fund-trading

# 日志查看
journalctl -u fund-trading -f
tail -f /var/log/fund-trading/app.log

# 进程管理
ps aux | grep uvicorn
kill <PID>
pkill -f uvicorn

# 端口检查
netstat -tlnp | grep 8000
lsof -i :8000

# 健康检查
curl http://localhost:8000/api/v1/health
```

### 联系信息

- **技术支持**: [联系邮箱]
- **紧急联系**: [紧急电话]
- **文档更新**: 2025-12-14

---

**文档版本**: 1.0.0  
**最后更新**: 2025-12-14

