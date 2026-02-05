# Base Skill Connection - Dive Coder v16

**Version:** 1.0.0
**Status:** Production Ready
**Language:** Python 3.11+

## Mục đích

Base Skill Connection cung cấp một nền tảng thống nhất để kết nối Dive Coder với mọi loại API, CLI, và dịch vụ. Skill này cho phép:

- Kết nối với bất kỳ API nào (REST, GraphQL, gRPC)
- Tích hợp CLI commands
- Giao tiếp với các dịch vụ khác
- Tối ưu hóa truyền dữ liệu
- Quản lý lỗi và resilience

## Cấu trúc

```
base-skill-connection/
├── SKILL.md                           # Tài liệu này
├── base_connection.py                 # Core connection module
├── universal_gateway.py               # Universal API Gateway
├── cli_integration.py                 # CLI integration layer
├── transmission_optimizer.py          # Transmission optimization
├── connection_manager.py              # Connection management
└── examples/
    ├── example_rest_api.py
    ├── example_cli_integration.py
    └── example_transmission_opt.py
```

## Các thành phần chính

### 1. Base Connection (base_connection.py)

Cung cấp các lớp cơ bản cho tất cả các kết nối:

```python
from base_skill_connection import BaseConnection, ConnectionConfig

# Tạo kết nối
config = ConnectionConfig(
    provider="api",
    url="https://api.example.com",
    timeout=30,
    retry_max=3
)

connection = BaseConnection(config)
result = connection.execute(method="GET", endpoint="/data")
```

### 2. Universal API Gateway (universal_gateway.py)

Cho phép kết nối với mọi loại API:

```python
from base_skill_connection import UniversalGateway

gateway = UniversalGateway()

# REST API
gateway.register_api("rest_api", type="rest", url="https://api.example.com")

# GraphQL
gateway.register_api("graphql_api", type="graphql", url="https://graphql.example.com")

# gRPC
gateway.register_api("grpc_service", type="grpc", url="grpc://service.example.com")

# Thực thi
result = gateway.call("rest_api", method="GET", endpoint="/users")
```

### 3. CLI Integration (cli_integration.py)

Tích hợp CLI commands vào Dive Coder:

```python
from base_skill_connection import CLIIntegration

cli = CLIIntegration()

# Đăng ký CLI command
cli.register_command("git", "clone", ["url", "path"])
cli.register_command("docker", "run", ["image", "command"])

# Thực thi
result = cli.execute("git", "clone", ["https://github.com/repo.git", "./repo"])
```

### 4. Transmission Optimizer (transmission_optimizer.py)

Tối ưu hóa truyền dữ liệu:

```python
from base_skill_connection import TransmissionOptimizer

optimizer = TransmissionOptimizer()

# Bật compression
optimizer.enable_compression("gzip", level=6)

# Bật batching
optimizer.enable_batching(batch_size=10, batch_timeout=5)

# Bật caching
optimizer.enable_caching(ttl=3600)

# Tối ưu hóa dữ liệu
optimized_data = optimizer.optimize(data)
```

## Cách sử dụng

### Ví dụ 1: Kết nối REST API

```python
from base_skill_connection import UniversalGateway

gateway = UniversalGateway()
gateway.register_api("my_api", type="rest", url="https://api.example.com")

# GET request
result = gateway.call("my_api", method="GET", endpoint="/users/123")

# POST request
result = gateway.call("my_api", method="POST", endpoint="/users", 
                      data={"name": "John", "email": "john@example.com"})
```

### Ví dụ 2: Tích hợp CLI

```python
from base_skill_connection import CLIIntegration

cli = CLIIntegration()
cli.register_command("python", "script.py", ["--arg1", "value1"])

result = cli.execute("python", "script.py", ["--arg1", "value1"])
print(result.stdout)
```

### Ví dụ 3: Tối ưu hóa Truyền dữ liệu

```python
from base_skill_connection import TransmissionOptimizer

optimizer = TransmissionOptimizer()
optimizer.enable_compression("gzip")
optimizer.enable_batching(batch_size=100)
optimizer.enable_caching(ttl=3600)

# Tối ưu hóa dữ liệu lớn
large_data = [{"id": i, "value": f"data_{i}"} for i in range(10000)]
optimized = optimizer.optimize(large_data)

# Kích thước được giảm
print(f"Original size: {len(str(large_data))} bytes")
print(f"Optimized size: {len(optimized)} bytes")
```

## Configuration

### ConnectionConfig

```python
ConnectionConfig(
    provider="api",                    # "api", "cli", "service"
    url="https://api.example.com",     # URL hoặc path
    timeout=30,                        # Timeout in seconds
    retry_max=3,                       # Max retries
    retry_backoff=2.0,                 # Exponential backoff
    headers={},                        # Custom headers
    auth=None,                         # Authentication
    compression="gzip",                # "gzip", "deflate", None
    batching=True,                     # Enable batching
    caching=True,                      # Enable caching
    cache_ttl=3600                     # Cache TTL in seconds
)
```

## Best Practices

1. **Luôn sử dụng Connection Manager** để quản lý lifecycle của connections
2. **Bật Transmission Optimization** cho dữ liệu lớn
3. **Sử dụng Retry Logic** cho các API không ổn định
4. **Monitor Connection Health** để phát hiện sớm các vấn đề
5. **Implement Proper Error Handling** cho tất cả các calls

## Performance Tips

- **Compression:** Giảm kích thước dữ liệu 70-90% cho dữ liệu text
- **Batching:** Giảm số lượng requests lên đến 10x
- **Caching:** Giảm latency 100-1000x cho dữ liệu cached
- **Connection Pooling:** Tái sử dụng connections, giảm overhead

## Troubleshooting

### Connection Timeout
```python
# Tăng timeout
config.timeout = 60
```

### API Rate Limiting
```python
# Bật batching để giảm số requests
optimizer.enable_batching(batch_size=50)
```

### High Memory Usage
```python
# Bật compression
optimizer.enable_compression("gzip", level=9)
```

## Support & Documentation

Để tìm hiểu thêm, xem:
- `examples/` - Các ví dụ chi tiết
- `universal_gateway.py` - Tài liệu API Gateway
- `transmission_optimizer.py` - Tài liệu Transmission Optimization

---

**Tác giả:** Manus AI
**Ngày cập nhật:** 2026-01-31
