from typing import List, Dict, Any, Optional
from googlesearch import search
from database import BlogDatabase
from blog_service import BlogService

class BlogTools:
    def __init__(self, api_key: str):
        self.blog_service = BlogService(api_key)
        self.db = BlogDatabase()
        self.api_key = api_key

    def create_blog_tool(self, title: str, content: str, topic: str = "", tags: List[str] = None) -> Dict[str, Any]:
        try:
            result = self.blog_service.create_blog(title, content, topic)
            if result['success']:
                return {
                    "status": "success",
                    "message": f"✅ Blog '{title}' created with {result['chunks_created']} chunks",
                    "blog_id": result['blog_id'],
                    "chunks_created": result['chunks_created']
                }
            else:
                return {"status": "error", "message": f"❌ Failed: {result.get('error', 'Unknown error')}"}
        except Exception as e:
            return {"status": "error", "message": f"❌ Error: {str(e)}"}

    def search_blogs_tool(self, query: str, search_type: str = "rag") -> Dict[str, Any]:
        try:
            if search_type == "rag":
                result = self.blog_service.search_blogs_rag(query)
                if result['found_in_blogs']:
                    return {
                        "status": "success",
                        "source": "blog_database",
                        "found_in_blogs": True,
                        "results": result['chunks'],
                        "message": f"📚 Found {len(result['chunks'])} relevant chunks"
                    }
                else:
                    return {
                        "status": "not_found",
                        "source": "blog_database", 
                        "found_in_blogs": False,
                        "message": "🔍 No relevant content found"
                    }
            else:
                blogs = self.db.search_blogs_by_text(query)
                if blogs:
                    return {
                        "status": "success",
                        "source": "text_search",
                        "found_in_blogs": True,
                        "results": blogs,
                        "message": f"📚 Found {len(blogs)} blogs"
                    }
                else:
                    return {
                        "status": "not_found",
                        "source": "text_search",
                        "found_in_blogs": False,
                        "message": "🔍 No blogs found"
                    }
        except Exception as e:
            return {"status": "error", "message": f"❌ Error: {str(e)}"}

    def google_search_tool(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        try:
            search_results = []
            for url in search(query, num_results=num_results, stop=num_results, pause=2):
                search_results.append(url)
            
            if search_results:
                return {
                    "status": "success",
                    "source": "google_search",
                    "results": search_results,
                    "query": query,
                    "message": f"🌐 Found {len(search_results)} results"
                }
            else:
                return {
                    "status": "not_found",
                    "source": "google_search",
                    "message": f"🔍 No results for '{query}'"
                }
        except Exception as e:
            return {
                "status": "error", 
                "source": "google_search",
                "message": f"❌ Search error: {str(e)}"
            }

    def list_blogs_tool(self, limit: Optional[int] = None) -> Dict[str, Any]:
        try:
            blogs = self.blog_service.get_all_blogs_summary()
            
            if limit:
                blogs = blogs[:limit]
            
            if blogs:
                return {
                    "status": "success",
                    "blogs": blogs,
                    "total_count": len(blogs),
                    "message": f"📚 Found {len(blogs)} blogs"
                }
            else:
                return {
                    "status": "empty",
                    "blogs": [],
                    "total_count": 0,
                    "message": "📭 No blogs found"
                }
        except Exception as e:
            return {"status": "error", "message": f"❌ Error: {str(e)}"}

    def get_blog_by_id_tool(self, blog_id: int) -> Dict[str, Any]:
        try:
            blogs = self.db.get_all_blogs()
            blog = next((b for b in blogs if b['id'] == blog_id), None)
            
            if blog:
                return {
                    "status": "success",
                    "blog": blog,
                    "message": f"📄 Retrieved: {blog['title']}"
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"❌ Blog {blog_id} not found"
                }
        except Exception as e:
            return {"status": "error", "message": f"❌ Error: {str(e)}"}

    def delete_blog_tool(self, blog_id: int) -> Dict[str, Any]:
        return {
            "status": "not_implemented",
            "message": "🚧 Blog deletion not implemented"
        }

    def hybrid_search_tool(self, query: str) -> Dict[str, Any]:
        try:
            rag_result = self.search_blogs_tool(query, "rag")
            
            if rag_result["status"] == "success":
                return {
                    "status": "success",
                    "source": "hybrid_blog_found",
                    "primary_source": "blog_database",
                    "blog_results": rag_result["results"],
                    "message": f"📚 Found in your blogs",
                    "suggestion": "Content found in existing blogs"
                }
            else:
                google_result = self.google_search_tool(query)
                
                return {
                    "status": "success",
                    "source": "hybrid_web_search",
                    "primary_source": "google_search",
                    "web_results": google_result.get("results", []),
                    "message": f"🌐 Searched web - not in blogs",
                    "suggestion": f"💡 Create a blog about '{query}'?",
                    "blog_creation_topic": query
                }
        except Exception as e:
            return {"status": "error", "message": f"❌ Error: {str(e)}"}

    def get_search_stats_tool(self) -> Dict[str, Any]:
        """Get comprehensive statistics using ChromaDB integration"""
        try:
            # Get comprehensive stats from blog service
            result = self.blog_service.get_database_stats()
            
            if result['success']:
                stats = result['stats']
                combined_stats = stats.get('combined_stats', {})
                chromadb_stats = stats.get('chromadb_stats', {})
                
                return {
                    "status": "success",
                    "stats": {
                        "total_blogs": combined_stats.get('total_blogs', 0),
                        "chromadb_chunks": combined_stats.get('chromadb_chunks', 0),
                        "sqlite_chunks": combined_stats.get('sqlite_chunks', 0),
                        "topics": combined_stats.get('topics', []),
                        "storage_health": combined_stats.get('storage_health', 'unknown'),
                        "embedding_model": chromadb_stats.get('storage_info', {}).get('embedding_model', 'all-MiniLM-L6-v2'),
                        "chroma_collection": chromadb_stats.get('storage_info', {}).get('collection_name', 'blog_embeddings')
                    },
                    "message": f"📊 {combined_stats.get('total_blogs', 0)} blogs with {combined_stats.get('chromadb_chunks', 0)} ChromaDB chunks",
                    "storage_info": result.get('storage_info', {})
                }
            else:
                return {"status": "error", "message": result.get('message', 'Unknown error')}
        except Exception as e:
            return {"status": "error", "message": f"❌ Error: {str(e)}"}

def create_tools_instance(api_key: str) -> BlogTools:
    return BlogTools(api_key)