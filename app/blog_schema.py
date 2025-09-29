from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl
from datetime import date
import uuid

class Link(BaseModel):
    """
    Represents an external resource link related to the blog section.
    """
    text: str
    url: HttpUrl
    description: Optional[str] = None


class SectionBase(BaseModel):
    """
    Base model for a blog section.
    """
    title: str
    type: Literal["text", "bullets", "image", "code", "table", "note", "youtube", "links"]


class TextSection(SectionBase):
    """
    A section containing simple text content.
    """
    content: str


class BulletsSection(SectionBase):
    """
    A section containing a list of bullet points.
    """
    items: List[str]


class ImageSection(SectionBase):
    """
    A section containing an image with optional caption.
    """
    url: HttpUrl
    alt: str
    caption: Optional[str] = None


class CodeSection(SectionBase):
    """
    A section containing code snippet.
    """
    language: str
    content: str


class TableSection(SectionBase):
    """
    A section containing a table with headers and rows.
    """
    headers: List[str]
    rows: List[List[str]]


class NoteSection(SectionBase):
    """
    A section containing a note or tip.
    """
    content: str


class YoutubeSection(SectionBase):
    """
    A section containing an embedded YouTube video.
    """
    videoId: str
    description: Optional[str] = None


class LinksSection(SectionBase):
    """
    A section containing multiple external links.
    """
    links: List[Link]


# Union type for all possible section types
BlogSection = (
    TextSection
    | BulletsSection
    | ImageSection
    | CodeSection
    | TableSection
    | NoteSection
    | YoutubeSection
    | LinksSection
)


class BlogContent(BaseModel):
    """
    Represents the full content of a blog including introduction, sections, and conclusion.
    """
    introduction: str
    sections: List[BlogSection]
    conclusion: str


class Blog(BaseModel):
    """
    Represents a single blog post with metadata and content.
    """
    blog_version: int = 1
    slug: str
    title: str
    subtitle: Optional[str] = None
    excerpt: str
    content: BlogContent
    publishedDate: date
    tags: List[str]
    image: Optional[str] = None
    category: str
    views: int
    likes: int