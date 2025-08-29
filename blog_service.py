from database import BlogDatabase
from embeddings import EmbeddingSystem
from typing import List, Dict, Any, Optional
import requests
from googlesearch import search
import asyncio
import aiohttp

class BlogService:
    def __init__(self, api_key: str):
        self.db = BlogDatabase()
        self.embedding_system = EmbeddingSystem(api_key)
        self.api_key = api_key
    
    def create_blog(self, title: str, content: str, topic: str = "") -> Dict[str, Any]:
        """Create a new blog with embeddings"""
        try:
            # Create embedding for the full content
            content_embedding = self.embedding_system.create_embedding(content)
            
            # Save blog to database
            blog_id = self.db.save_blog(
                title=title,
                content=content,
                topic=topic,
                embedding=content_embedding
            )
            
            # Create chunks and their embeddings
            chunks = self.embedding_system.chunk_text(content)
            chunk_data = []
            
            for chunk in chunks:
                chunk_embedding = self.embedding_system.create_embedding(chunk)
                chunk_data.append({
                    'text': chunk,
                    'embedding': chunk_embedding
                })
            
            # Save chunks to database
            self.db.save_blog_chunks(blog_id, chunk_data)
            
            return {
                'success': True,
                'blog_id': blog_id,
                'title': title,
                'content': content,
                'chunks_created': len(chunk_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_blogs_rag(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Search blogs using RAG (Retrieval Augmented Generation)"""
        try:
            # Create embedding for the query
            query_embedding = self.embedding_system.create_embedding(query)
            
            # Get all blog chunks with embeddings
            chunk_data = self.db.get_blog_chunks_with_embeddings()
            
            if not chunk_data:
                return {
                    'found_in_blogs': False,
                    'message': "No blogs found in database",
                    'chunks': []
                }
            
            # Find similar chunks
            similar_chunks = self.embedding_system.find_similar_chunks(
                query_embedding, chunk_data, top_k
            )
            
            # Filter chunks with good similarity (threshold)
            relevant_chunks = [chunk for chunk in similar_chunks if chunk['similarity'] > 0.3]
            
            if relevant_chunks:
                return {
                    'found_in_blogs': True,
                    'chunks': relevant_chunks,
                    'source': 'blog_database'
                }
            else:
                return {
                    'found_in_blogs': False,
                    'message': "No relevant content found in blogs",
                    'chunks': []
                }
                
        except Exception as e:
            return {
                'found_in_blogs': False,
                'error': str(e),
                'chunks': []
            }
    
    def google_search_fallback(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Real Google search implementation"""
        try:
            search_results = []
            
            # Perform Google search
            for url in search(query, num_results=num_results, stop=num_results, pause=2):
                search_results.append(url)
            
            if search_results:
                formatted_results = "\n".join([f"• {url}" for url in search_results])
                return {
                    'source': 'google_search',
                    'results': f"🔍 Google search results for '{query}':\n\n{formatted_results}",
                    'raw_urls': search_results,
                    'query': query,
                    'found_results': len(search_results)
                }
            else:
                return {
                    'source': 'google_search', 
                    'results': f"🔍 No Google search results found for '{query}'",
                    'raw_urls': [],
                    'query': query,
                    'found_results': 0
                }
                
        except Exception as e:
            return {
                'source': 'google_search',
                'error': str(e),
                'results': f"❌ Could not perform web search for '{query}': {str(e)}",
                'raw_urls': [],
                'query': query,
                'found_results': 0
            }
    
    def get_all_blogs_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all blogs"""
        blogs = self.db.get_all_blogs()
        summaries = []
        
        for blog in blogs:
            summary = {
                'id': blog['id'],
                'title': blog['title'],
                'topic': blog['topic'],
                'preview': blog['content'][:100] + "..." if len(blog['content']) > 100 else blog['content'],
                'created_at': blog['created_at']
            }
            summaries.append(summary)
        
        return summaries
    
    def delete_blog(self, blog_id: int) -> Dict[str, Any]:
        """Delete a blog and its chunks"""
        try:
            deleted = self.db.delete_blog(blog_id)
            
            if deleted:
                return {
                    'success': True,
                    'message': f"✅ Blog {blog_id} deleted successfully",
                    'blog_id': blog_id
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Blog {blog_id} not found or could not be deleted",
                    'blog_id': blog_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Error deleting blog {blog_id}: {str(e)}"
            }
    
    def update_blog(self, blog_id: int, **kwargs) -> Dict[str, Any]:
        """Update a blog"""
        try:
            updated = self.db.update_blog(blog_id, **kwargs)
            
            if updated:
                return {
                    'success': True,
                    'message': f"✅ Blog {blog_id} updated successfully",
                    'blog_id': blog_id
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Blog {blog_id} not found or no changes made",
                    'blog_id': blog_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Error updating blog {blog_id}: {str(e)}"
            }
    
    def get_blog_by_id(self, blog_id: int) -> Dict[str, Any]:
        """Get a specific blog by ID"""
        try:
            blog = self.db.get_blog_by_id(blog_id)
            
            if blog:
                return {
                    'success': True,
                    'blog': blog,
                    'message': f"📄 Retrieved blog: {blog['title']}"
                }
            else:
                return {
                    'success': False,
                    'message': f"❌ Blog {blog_id} not found",
                    'blog_id': blog_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Error retrieving blog {blog_id}: {str(e)}"
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = self.db.get_database_stats()
            return {
                'success': True,
                'stats': stats,
                'message': f"📊 Database contains {stats['total_blogs']} blogs with {stats['total_chunks']} chunks"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Error getting database stats: {str(e)}"
            }