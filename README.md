# Bangumi Data API

一个基于 FastAPI 的 [bangumi-data](https://github.com/bangumi-data/bangumi-data) 包装 API 服务。

## 功能特性

- 🚀 基于 FastAPI 的高性能 API
- 📊 完整的 bangumi-data 数据支持
- 🔍 多种搜索和过滤功能
- 🔐 可选的 API Key 认证
- 💾 自动数据缓存
- 📖 自动生成的 API 文档

## 部署

### 本地开发

```bash
# 启动服务
uv run python main.py
```

### Docker 部署

```bash
# 使用 Docker Compose (推荐)
docker-compose up -d

# 或直接使用 Docker
docker build -t bangumi-data-api .
docker run -d --name bangumi-api -p 8000:8000 bangumi-data-api
```

详细的 Docker 部署说明请参考 [DOCKER.md](./DOCKER.md)

### 配置

复制 `.env.example` 到 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

## API 接口

### 基础接口

- `GET /` - API 信息
- `GET /health` - 健康检查
- `GET /docs` - Swagger 文档
- `GET /redoc` - ReDoc 文档

### 番组接口

#### 获取所有番组
```http
GET /api/v1/items?limit=100&offset=0
```

#### 根据 BGM ID 获取番组
```http
GET /api/v1/items/bgm/{bgm_id}
```

#### 批量获取多个 BGM ID 的番组
```http
# GET方式 - 用逗号分隔ID
GET /api/v1/items/bgm/batch?ids=123,456,789

# POST方式 - 发送JSON数组
POST /api/v1/items/bgm/batch
Content-Type: application/json
["123", "456", "789"]
```

#### 搜索番组
```http
GET /api/v1/items/search?title=进击&type=tv&lang=ja&year=2023&limit=50
```

参数说明：
- `title`: 标题搜索关键词
- `type`: 番组类型 (tv, web, movie, ova)
- `lang`: 语言 (ja, en, zh-Hans, zh-Hant)
- `year`: 年份过滤
- `limit`: 返回数量限制

#### 批量搜索番组
```http
POST /api/v1/items/search/batch
Content-Type: application/json
{
  "queries": [
    {"title": "进击", "type": "tv"},
    {"year": 2023, "lang": "ja"}
  ],
  "limit": 50
}
```

#### 根据站点获取番组
```http
GET /api/v1/items/site/{site_name}?limit=100
```

支持的站点：bilibili, netflix, crunchyroll 等

#### 批量获取多个站点的番组
```http
POST /api/v1/items/sites/batch
Content-Type: application/json
["bilibili", "netflix", "crunchyroll"]
```

#### 获取站点元数据
```http
GET /api/v1/sites
```

#### 刷新数据缓存
```http
POST /api/v1/refresh
```

## API Key 认证

如果启用了 API Key 认证，需要在请求头中包含：

```http
Authorization: Bearer your-api-key
```

## 使用示例

### Python 示例

```python
import httpx

async def get_bangumi_by_bgm_id(bgm_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/api/v1/items/bgm/{bgm_id}")
        return response.json()

# 搜索番组
async def search_bangumi(title: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/items/search",
            params={"title": title, "limit": 10}
        )
        return response.json()
```

### curl 示例

```bash
# 获取指定 BGM ID 的番组
curl "http://localhost:8000/api/v1/items/bgm/88595"

# 搜索包含"进击"的番组
curl "http://localhost:8000/api/v1/items/search?title=進撃&limit=5"

# 获取 bilibili 站点的番组
curl "http://localhost:8000/api/v1/items/site/bilibili?limit=10"
```

## 数据结构

### 番组 (Item)

```json
{
  "title": "番组原始标题",
  "titleTranslate": {
    "zh-Hans": ["中文简体翻译"],
    "zh-Hant": ["中文繁体翻译"],
    "en": ["英文翻译"]
  },
  "type": "tv",
  "lang": "ja",
  "officialSite": "官网URL",
  "begin": "2023-01-01T00:00:00.000Z",
  "end": "2023-03-31T23:59:59.000Z",
  "broadcast": "R/2023-01-01T00:00:00.000Z/P7D",
  "comment": "备注信息",
  "sites": [
    {
      "site": "bilibili",
      "id": "站点ID",
      "url": "直接链接",
      "begin": "放送开始时间",
      "end": "放送结束时间",
      "regions": ["地区限制"]
    }
  ]
}
```

## 环境变量

- `HOST`: 监听地址 (默认: 0.0.0.0)
- `PORT`: 监听端口 (默认: 8000)
- `API_KEYS`: API 密钥 (逗号分隔)
- `REQUIRE_API_KEY`: 是否需要 API 密钥 (默认: false)
- `CACHE_TTL`: 缓存时间 (秒，默认: 3600)
- `LOG_LEVEL`: 日志级别 (默认: INFO)

## 开发

### 项目结构

```
app/
├── api/           # API 路由
├── core/          # 核心配置
├── models/        # 数据模型
├── services/      # 业务逻辑
└── main.py        # 应用入口
```

### 运行测试

```bash
# 基本功能测试
uv run python -c "
import asyncio
from app.services.bangumi_service import bangumi_service

async def test():
    data = await bangumi_service.get_data()
    print(f'获取到 {len(data.items)} 个番组')

asyncio.run(test())
"
```

## 许可证

本项目使用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！