from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ContentSection(BaseModel):
    type: str  # "section", "note", "code", "table", "link", "video"
    heading: Optional[str] = None
    text: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    note: Optional[str] = None
    table: Optional[Dict[str, Any]] = None
    url: Optional[str] = None


class BlogPost(BaseModel):
    id: str
    slug: str
    title: str
    subtitle: str
    excerpt: str
    content: List[ContentSection]
    author: str
    publishedDate: datetime
    readTime: int
    tags: List[str]
    image: str
    category: str
    featured: bool
    views: int
    likes: int
