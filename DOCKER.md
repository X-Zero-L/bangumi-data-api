# Docker 部署指南

## 快速部署

### 使用 Docker Compose（推荐）

```bash
# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 直接使用 Docker

```bash
# 构建镜像
docker build -t bangumi-data-api .

# 运行容器
docker run -d \
  --name bangumi-api \
  -p 8000:8000 \
  -e CACHE_TTL=3600 \
  -e LOG_LEVEL=INFO \
  bangumi-data-api
```

## 配置选项

### 环境变量

- `HOST`: 监听地址 (默认: 0.0.0.0)
- `PORT`: 监听端口 (默认: 8000)
- `LOG_LEVEL`: 日志级别 (默认: INFO)
- `CACHE_TTL`: 缓存时间，秒 (默认: 3600)
- `REQUIRE_API_KEY`: 是否需要 API Key (默认: false)
- `API_KEYS`: API 密钥列表，逗号分隔

### 启用 API Key 认证

在 `docker-compose.yml` 中取消注释：

```yaml
environment:
  - REQUIRE_API_KEY=true
  - API_KEYS=your-secret-key-1,your-secret-key-2
```

## 服务访问

- API 服务: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f bangumi-api

# 进入容器
docker-compose exec bangumi-api sh
```

## 反向代理

如果需要使用反向代理（如 Nginx、Traefik、Caddy 等），可以将服务配置在内网端口，然后通过代理访问。

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Traefik 配置示例

```yaml
# docker-compose.yml
services:
  bangumi-api:
    # ... 其他配置
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.bangumi.rule=Host(`your-domain.com`)"
      - "traefik.http.services.bangumi.loadbalancer.server.port=8000"
```

## 生产环境建议

1. **使用环境变量文件**
   ```bash
   # 创建 .env 文件
   CACHE_TTL=7200
   LOG_LEVEL=WARNING
   REQUIRE_API_KEY=true
   API_KEYS=your-production-key
   ```

2. **资源限制**
   ```yaml
   # 在 docker-compose.yml 中添加
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '1.0'
   ```

3. **健康检查和重启策略**
   ```yaml
   restart: unless-stopped
   healthcheck:
     test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

## 故障排除

### 常见问题

1. **端口被占用**: 修改 docker-compose.yml 中的端口映射
2. **内存不足**: 调整 deploy.resources.limits 或增加系统内存
3. **网络连接问题**: 检查防火墙设置和网络配置

### 日志查看

```bash
# 查看实时日志
docker-compose logs -f bangumi-api

# 查看最近的日志
docker-compose logs --tail=50 bangumi-api

# 查看容器状态
docker-compose ps
```