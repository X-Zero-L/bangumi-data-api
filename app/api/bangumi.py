from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from app.core.auth import verify_api_key
from app.models.bangumi import Item, SiteMeta
from app.services.bangumi_service import bangumi_service


router = APIRouter()


@router.get("/items", response_model=List[Item])
async def get_all_items(
    _: bool = Depends(verify_api_key),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="限制返回数量"),
    offset: Optional[int] = Query(0, ge=0, description="偏移量")
):
    """获取所有番组"""
    items = await bangumi_service.get_all_items()
    
    if offset:
        items = items[offset:]
    if limit:
        items = items[:limit]
        
    return items


@router.get("/items/bgm/batch", response_model=Dict[str, Optional[Item]])
async def get_items_by_bgm_ids_query(
    _: bool = Depends(verify_api_key),
    ids: str = Query(..., description="BGM ID列表，用逗号分隔，例如: 123,456,789")
):
    """根据多个BGM ID批量获取番组（GET方式）"""
    bgm_ids = [id.strip() for id in ids.split(",") if id.strip()]
    
    if len(bgm_ids) > 100:
        raise HTTPException(status_code=400, detail="Too many IDs. Maximum 100 IDs per request")
    
    result = {}
    for bgm_id in bgm_ids:
        item = await bangumi_service.get_item_by_bgm_id(bgm_id)
        result[bgm_id] = item
    
    return result


@router.get("/items/bgm/{bgm_id}", response_model=Item)
async def get_item_by_bgm_id(
    bgm_id: str,
    _: bool = Depends(verify_api_key)
):
    """根据BGM ID获取番组"""
    item = await bangumi_service.get_item_by_bgm_id(bgm_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items/bgm/batch", response_model=Dict[str, Optional[Item]])
async def get_items_by_bgm_ids_post(
    _: bool = Depends(verify_api_key),
    bgm_ids: List[str] = Body(..., description="BGM ID数组", example=["123", "456", "789"])
):
    """根据多个BGM ID批量获取番组（POST方式）"""
    if len(bgm_ids) > 100:
        raise HTTPException(status_code=400, detail="Too many IDs. Maximum 100 IDs per request")
    
    result = {}
    for bgm_id in bgm_ids:
        item = await bangumi_service.get_item_by_bgm_id(bgm_id)
        result[bgm_id] = item
    
    return result


@router.get("/items/search", response_model=List[Item])
async def search_items(
    _: bool = Depends(verify_api_key),
    title: Optional[str] = Query(None, description="标题搜索"),
    type: Optional[str] = Query(None, description="类型过滤 (tv, web, movie, ova)"),
    lang: Optional[str] = Query(None, description="语言过滤 (ja, en, zh-Hans, zh-Hant)"),
    year: Optional[int] = Query(None, ge=1900, le=2100, description="年份过滤"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="限制返回数量")
):
    """搜索番组"""
    items = await bangumi_service.search_items(
        title=title,
        type_filter=type,
        lang=lang,
        year=year
    )
    return items[:limit]


@router.post("/items/search/batch", response_model=List[Item])
async def search_items_batch(
    _: bool = Depends(verify_api_key),
    search_params: Dict[str, Any] = Body(
        ..., 
        description="批量搜索参数",
        example={
            "queries": [
                {"title": "进击", "type": "tv"},
                {"year": 2023, "lang": "ja"}
            ],
            "limit": 50
        }
    )
):
    """批量搜索番组"""
    queries = search_params.get("queries", [])
    limit = search_params.get("limit", 100)
    
    if len(queries) > 10:
        raise HTTPException(status_code=400, detail="Too many queries. Maximum 10 queries per request")
    
    all_results = []
    seen_titles = set()
    
    for query in queries:
        items = await bangumi_service.search_items(
            title=query.get("title"),
            type_filter=query.get("type"),
            lang=query.get("lang"),
            year=query.get("year")
        )
        
        # 去重
        for item in items:
            if item.title not in seen_titles:
                all_results.append(item)
                seen_titles.add(item.title)
    
    return all_results[:limit]


@router.get("/items/site/{site_name}", response_model=List[Item])
async def get_items_by_site(
    site_name: str,
    _: bool = Depends(verify_api_key),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="限制返回数量")
):
    """根据站点获取番组"""
    items = await bangumi_service.get_items_by_site(site_name)
    return items[:limit]


@router.post("/items/sites/batch", response_model=Dict[str, List[Item]])
async def get_items_by_sites_batch(
    _: bool = Depends(verify_api_key),
    site_names: List[str] = Body(..., description="站点名称数组", example=["bilibili", "netflix"])
):
    """根据多个站点批量获取番组"""
    if len(site_names) > 20:
        raise HTTPException(status_code=400, detail="Too many sites. Maximum 20 sites per request")
    
    result = {}
    for site_name in site_names:
        items = await bangumi_service.get_items_by_site(site_name)
        result[site_name] = items[:100]  # 每个站点最多返回100个
    
    return result


@router.get("/sites", response_model=dict)
async def get_site_meta(
    _: bool = Depends(verify_api_key)
):
    """获取站点元数据"""
    return await bangumi_service.get_site_meta()


@router.post("/refresh")
async def refresh_data(
    _: bool = Depends(verify_api_key)
):
    """强制刷新数据缓存"""
    await bangumi_service.get_data(force_refresh=True)
    return {"message": "Data refreshed successfully"}