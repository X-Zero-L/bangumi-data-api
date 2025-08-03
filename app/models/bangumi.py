from typing import Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field


SiteType = Literal["info", "onair", "resource"]
Language = Literal["ja", "en", "zh-Hans", "zh-Hant"]
ItemType = Literal["tv", "web", "movie", "ova"]
SiteList = Literal[
    "bangumi", "acfun", "bilibili", "bilibili_hk_mo_tw", "bilibili_hk_mo", 
    "bilibili_tw", "youku", "qq", "iqiyi", "letv", "mgtv", "nicovideo", 
    "netflix", "gamer", "gamer_hk", "muse_hk", "muse_tw", "ani_one", 
    "ani_one_asia", "viu", "mytv", "disneyplus", "abema", "unext", 
    "tropics", "prime", "dmhy", "mikan", "bangumi_moe", "crunchyroll",
    "danime", "youtube"
]


class SiteMeta(BaseModel):
    """站点元数据"""
    title: str = Field(..., description="站点名称")
    url_template: str = Field(..., alias="urlTemplate", description="站点 url 模板")
    regions: Optional[List[str]] = Field(None, description="站点区域限制")
    type: SiteType = Field(..., description="站点类型: info, onair, resource")


class OnairSite(BaseModel):
    """放送站点"""
    site: str = Field(..., description="站点 name")
    id: Optional[str] = Field(None, description="站点 id")
    url: Optional[str] = Field(None, description="url，优先级高于id")
    begin: str = Field(..., description="放送开始时间")
    broadcast: Optional[str] = Field(None, description="放送周期")
    end: Optional[str] = Field(None, description="放送结束时间")
    comment: Optional[str] = Field(None, description="备注")
    regions: List[str] = Field(default_factory=list, description="番剧放送站点区域限制")


class InfoSite(BaseModel):
    """资讯站点"""
    site: str = Field(..., description="站点 name")
    id: Optional[str] = Field(None, description="站点 id")


class ResourceSite(BaseModel):
    """资源（下载）站点"""
    site: str = Field(..., description="站点 name")
    id: Optional[str] = Field(None, description="下载关键词")


Site = Union[OnairSite, InfoSite, ResourceSite]


class Item(BaseModel):
    """番组数据"""
    title: str = Field(..., description="番组原始标题")
    title_translate: Dict[Language, List[str]] = Field(
        ..., alias="titleTranslate", description="番组标题翻译"
    )
    type: ItemType = Field(..., description="番组类型")
    lang: Language = Field(..., description="番组语言")
    official_site: str = Field(..., alias="officialSite", description="官网")
    begin: str = Field(..., description="开始时间")
    broadcast: Optional[str] = Field(None, description="放送周期")
    end: str = Field(..., description="结束时间")
    comment: Optional[str] = Field(None, description="备注")
    sites: List[Site] = Field(..., description="站点列表")


class BangumiData(BaseModel):
    """完整的bangumi数据"""
    site_meta: Dict[str, SiteMeta] = Field(..., alias="siteMeta")
    items: List[Item] = Field(...)