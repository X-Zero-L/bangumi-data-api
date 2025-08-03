from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
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


@router.get("/items/site/{site_name}", response_model=List[Item])
async def get_items_by_site(
    site_name: str,
    _: bool = Depends(verify_api_key),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="限制返回数量")
):
    """根据站点获取番组"""
    items = await bangumi_service.get_items_by_site(site_name)
    return items[:limit]


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