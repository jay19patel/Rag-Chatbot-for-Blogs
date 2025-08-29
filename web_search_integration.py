import requests
from bs4 import BeautifulSoup
from googlesearch import search
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse
import time
import json

class WebSearchBlogCreator:
    def __init__(self):
        self.session = None
        self.search_cache = {}
        self.max_cache_age = 3600  # 1 hour cache
    
    async def create_session(self):
        """Create async HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
    
    async def close_session(self):
        """Close async HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def google_search_topics(self, topic: str, num_results: int = 8) -> List[str]:
        """Search Google for relevant URLs on a topic"""
        try:
            print(f"🔍 Searching Google for: {topic}")
            urls = []
            
            # Use different search queries to get diverse results
            search_queries = [
                f"{topic} guide tutorial",
                f"{topic} best practices",
                f"{topic} overview explanation",
                f"what is {topic}",
                f"{topic} examples"
            ]
            
            for query in search_queries[:2]:  # Use first 2 queries
                try:
                    for url in search(query, num_results=num_results//2, stop=num_results//2, pause=2):
                        if url and url not in urls:
                            urls.append(url)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"⚠️ Search query failed: {e}")
                    continue
            
            return urls[:num_results]
            
        except Exception as e:
            print(f"❌ Google search failed: {e}")
            return []
    
    async def fetch_content_from_url(self, url: str) -> Dict[str, Any]:
        """Fetch and extract content from a URL"""
        try:
            await self.create_session()
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"url": url, "success": False, "error": f"HTTP {response.status}"}
                
                html_content = await response.text()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else "No Title"
                
                # Extract main content
                content_selectors = [
                    'article', 'main', '.content', '.post-content', '.entry-content',
                    '.article-body', '[role="main"]', '.main-content'
                ]
                
                content_text = ""
                for selector in content_selectors:
                    content_element = soup.select_one(selector)
                    if content_element:
                        content_text = content_element.get_text(separator=' ', strip=True)
                        break
                
                # Fallback to body content if no specific content found
                if not content_text:
                    body = soup.find('body')
                    if body:
                        content_text = body.get_text(separator=' ', strip=True)
                
                # Clean up content
                content_text = self._clean_content(content_text)
                
                return {
                    "url": url,
                    "success": True,
                    "title": title_text,
                    "content": content_text,
                    "word_count": len(content_text.split()),
                    "domain": urlparse(url).netloc
                }
                
        except Exception as e:
            return {"url": url, "success": False, "error": str(e)}
    
    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        # Remove extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove common noise patterns
        noise_patterns = [
            r'Cookie Notice.*?(?=\.|$)',
            r'We use cookies.*?(?=\.|$)',
            r'By continuing to use.*?(?=\.|$)',
            r'Advertisement\s*',
            r'Subscribe.*?newsletter.*?(?=\.|$)',
            r'Share this.*?(?=\.|$)',
        ]
        
        for pattern in noise_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    async def gather_research_content(self, topic: str, max_sources: int = 5) -> List[Dict[str, Any]]:
        """Gather research content from multiple web sources"""
        print(f"📚 Gathering research content for: {topic}")
        
        # Get URLs from Google search
        urls = self.google_search_topics(topic, max_sources * 2)  # Get more URLs than needed
        
        if not urls:
            return []
        
        # Fetch content from URLs concurrently
        tasks = []
        for url in urls[:max_sources]:
            tasks.append(self.fetch_content_from_url(url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = []
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                # Only include results with substantial content
                if result.get("word_count", 0) > 100:
                    successful_results.append(result)
        
        return successful_results
    
    def synthesize_blog_content(self, research_data: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Synthesize research data into blog content"""
        if not research_data:
            return {
                "success": False,
                "error": "No research data available"
            }
        
        # Combine content from all sources
        all_content = []
        sources = []
        total_words = 0
        
        for data in research_data:
            content = data.get("content", "")
            if content and len(content.split()) > 50:  # Minimum content length
                all_content.append(content[:2000])  # Limit each source content
                sources.append({
                    "title": data.get("title", "Unknown"),
                    "url": data.get("url", ""),
                    "domain": data.get("domain", ""),
                    "word_count": data.get("word_count", 0)
                })
                total_words += data.get("word_count", 0)
        
        if not all_content:
            return {
                "success": False,
                "error": "No substantial content found"
            }
        
        # Create structured blog content
        combined_content = "\n\n".join(all_content)
        
        # Generate title
        title = self._generate_title(topic, research_data)
        
        # Create introduction
        introduction = f"This comprehensive guide explores {topic}, synthesized from multiple authoritative sources across the web."
        
        # Structure the content
        structured_content = f"""# {title}

## Introduction
{introduction}

## Overview
{topic} is an important subject that requires understanding from multiple perspectives. Based on research from {len(sources)} authoritative sources, here's what you need to know:

## Key Insights

{combined_content}

## Summary
This guide has covered the essential aspects of {topic} based on comprehensive research from reliable web sources. The information has been synthesized to provide you with actionable insights and comprehensive understanding.

---
*This blog post was created using AI-powered web research and synthesis.*
"""
        
        return {
            "success": True,
            "title": title,
            "content": structured_content,
            "topic": topic,
            "sources": sources,
            "total_sources": len(sources),
            "estimated_word_count": len(structured_content.split()),
            "research_quality": self._assess_research_quality(research_data)
        }
    
    def _generate_title(self, topic: str, research_data: List[Dict[str, Any]]) -> str:
        """Generate an engaging blog title"""
        # Use the best source title as reference
        source_titles = [data.get("title", "") for data in research_data if data.get("title")]
        
        # Create title variations
        title_templates = [
            f"Complete Guide to {topic.title()}",
            f"Everything You Need to Know About {topic.title()}",
            f"Mastering {topic.title()}: A Comprehensive Guide",
            f"The Ultimate {topic.title()} Guide",
            f"Understanding {topic.title()}: From Basics to Advanced"
        ]
        
        # Choose based on topic characteristics
        if len(topic.split()) <= 2:
            return f"Complete Guide to {topic.title()}"
        else:
            return f"Understanding {topic.title()}"
    
    def _assess_research_quality(self, research_data: List[Dict[str, Any]]) -> str:
        """Assess the quality of research data"""
        if not research_data:
            return "poor"
        
        total_words = sum(data.get("word_count", 0) for data in research_data)
        source_count = len(research_data)
        
        if total_words > 5000 and source_count >= 3:
            return "excellent"
        elif total_words > 2000 and source_count >= 2:
            return "good"
        elif total_words > 500:
            return "fair"
        else:
            return "poor"
    
    async def create_blog_from_web_research(self, topic: str, max_sources: int = 4) -> Dict[str, Any]:
        """Main method to create blog from web research"""
        try:
            print(f"🚀 Starting web research for blog creation: {topic}")
            
            # Gather research content
            research_data = await self.gather_research_content(topic, max_sources)
            
            if not research_data:
                return {
                    "success": False,
                    "error": "Unable to gather research content from web sources",
                    "topic": topic
                }
            
            # Synthesize into blog content
            blog_result = self.synthesize_blog_content(research_data, topic)
            
            if blog_result.get("success"):
                print(f"✅ Blog created successfully with {len(research_data)} sources")
                return blog_result
            else:
                return {
                    "success": False,
                    "error": blog_result.get("error", "Unknown error in synthesis"),
                    "topic": topic
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Blog creation failed: {str(e)}",
                "topic": topic
            }
        finally:
            await self.close_session()

# Global web search instance
web_search_creator = WebSearchBlogCreator()