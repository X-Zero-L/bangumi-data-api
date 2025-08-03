import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx
from app.models.bangumi import BangumiData, Item, SiteMeta


class BangumiDataService:
    """Bangumi数据服务"""
    
    def __init__(self, cache_ttl: int = 3600):
        self.data_url = "https://unpkg.com/bangumi-data@0.3/dist/data.json"
        self.cache_ttl = cache_ttl
        self._cached_data: Optional[BangumiData] = None
        self._cache_time: Optional[datetime] = None
        self._bgm_index: Dict[str, Item] = {}
        
    async def _fetch_data(self) -> BangumiData:
        """从远程获取数据"""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(self.data_url)
            response.raise_for_status()
            data = response.json()
            return BangumiData(**data)
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._cached_data is None or self._cache_time is None:
            return False
        return datetime.now() - self._cache_time < timedelta(seconds=self.cache_ttl)
    
    def _build_bgm_index(self, data: BangumiData):
        """构建BGM ID索引"""
        self._bgm_index = {}
        for item in data.items:
            for site in item.sites:
                if hasattr(site, 'site') and site.site == 'bangumi':
                    self._bgm_index[site.id] = item
                    break
    
    async def get_data(self, force_refresh: bool = False) -> BangumiData:
        """获取bangumi数据"""
        if force_refresh or not self._is_cache_valid():
            self._cached_data = await self._fetch_data()
            self._cache_time = datetime.now()
            self._build_bgm_index(self._cached_data)
        return self._cached_data
    
    async def get_all_items(self) -> List[Item]:
        """获取所有番组"""
        data = await self.get_data()
        return data.items
    
    async def get_item_by_bgm_id(self, bgm_id: str) -> Optional[Item]:
        """根据BGM ID获取番组"""
        await self.get_data()
        return self._bgm_index.get(bgm_id)
    
    async def search_items(
        self, 
        title: Optional[str] = None,
        type_filter: Optional[str] = None,
        lang: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Item]:
        """搜索番组"""
        items = await self.get_all_items()
        results = []
        
        for item in items:
            # 标题搜索
            if title:
                title_match = title.lower() in item.title.lower()
                translate_match = any(
                    title.lower() in trans.lower()
                    for trans_list in item.title_translate.values()
                    for trans in trans_list
                )
                if not (title_match or translate_match):
                    continue
            
            # 类型过滤
            if type_filter and item.type != type_filter:
                continue
                
            # 语言过滤
            if lang and item.lang != lang:
                continue
                
            # 年份过滤
            if year:
                try:
                    item_year = int(item.begin[:4])
                    if item_year != year:
                        continue
                except (ValueError, IndexError):
                    continue
                    
            results.append(item)
        
        return results
    
    async def get_items_by_site(self, site_name: str) -> List[Item]:
        """根据站点获取番组"""
        items = await self.get_all_items()
        results = []
        
        for item in items:
            for site in item.sites:
                if hasattr(site, 'site') and site.site == site_name:
                    results.append(item)
                    break
        
        return results
    
    async def get_site_meta(self) -> Dict[str, SiteMeta]:
        """获取站点元数据"""
        data = await self.get_data()
        return data.site_meta


# 全局服务实例
bangumi_service = BangumiDataService()