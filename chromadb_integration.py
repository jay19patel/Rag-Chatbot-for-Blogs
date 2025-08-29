import chromadb
from typing import List, Dict, Any, Optional
import numpy as np
import os
from datetime import datetime
import uuid
import logging

class ChromaDBManager:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "blog_embeddings"):
        """
        Initialize ChromaDB with persistent storage and optimizations
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create directory if not exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Create optimized persistent client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection with optimized settings
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2",
                    device="cpu"  # Explicit device for consistency
                )
            )
            self.logger.info(f"📚 Loaded existing ChromaDB collection: {collection_name}")
        except Exception as e:
            self.logger.info(f"Creating new collection: {e}")
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2",
                    device="cpu"
                ),
                metadata={
                    "hnsw:space": "cosine",
                    "hnsw:search_ef": 200,  # Higher for better accuracy
                    "hnsw:construction_ef": 200,
                    "hnsw:M": 16  # Good balance of accuracy and speed
                }
            )
            self.logger.info(f"🆕 Created optimized ChromaDB collection: {collection_name}")
    
    def add_blog_chunks(self, blog_id: int, blog_title: str, blog_content: str, 
                       topic: str = "", chunk_size: int = 300) -> int:
        """
        Add blog content as chunks to ChromaDB with proper metadata mapping
        """
        chunks = self._chunk_text(blog_content, chunk_size)
        
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"blog_{blog_id}_chunk_{i}"
            
            documents.append(chunk)
            metadatas.append({
                "blog_id": blog_id,
                "blog_title": blog_title,
                "topic": topic,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "created_at": datetime.now().isoformat(),
                "content_length": len(chunk),
                "blog_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
            })
            ids.append(chunk_id)
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(chunks)} chunks for blog '{blog_title}' to ChromaDB")
        return len(chunks)
    
    def search_similar_content(self, query: str, top_k: int = 5, 
                              blog_id_filter: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Optimized search for similar content using ChromaDB's similarity search
        """
        try:
            # Build where clause for filtering
            where_clause = {}
            if blog_id_filter:
                where_clause["blog_id"] = blog_id_filter
            
            # Optimized search parameters
            search_params = {
                "query_texts": [query],
                "n_results": min(top_k * 2, 20),  # Get more results for better filtering
                "include": ["documents", "metadatas", "distances"]
            }
            
            if where_clause:
                search_params["where"] = where_clause
            
            # Search in ChromaDB with timing
            start_time = datetime.now()
            results = self.collection.query(**search_params)
            search_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"🔍 ChromaDB search completed in {search_time:.3f}s")
            
            # Format and rank results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    # ChromaDB returns cosine distances (lower = more similar)
                    distance = results['distances'][0][i]
                    
                    # Convert to similarity score with better calibration
                    if distance <= 0.5:  # Very similar
                        similarity = 0.9 + (0.5 - distance) * 0.2  # 0.9-1.0
                    elif distance <= 1.0:  # Moderately similar
                        similarity = 0.5 + (1.0 - distance) * 0.8  # 0.5-0.9
                    else:  # Less similar
                        similarity = max(0, 0.5 - (distance - 1.0) * 0.5)  # 0-0.5
                    
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'blog_id': results['metadatas'][0][i]['blog_id'],
                        'blog_title': results['metadatas'][0][i]['blog_title'],
                        'topic': results['metadatas'][0][i].get('topic', ''),
                        'similarity': float(similarity),
                        'distance': float(distance),
                        'chunk_index': results['metadatas'][0][i]['chunk_index'],
                        'created_at': results['metadatas'][0][i]['created_at'],
                        'content_length': results['metadatas'][0][i].get('content_length', 0)
                    })
            
            # Sort by similarity and return top_k
            formatted_results.sort(key=lambda x: x['similarity'], reverse=True)
            return formatted_results[:top_k]
            
        except Exception as e:
            self.logger.error(f"❌ ChromaDB search error: {e}")
            return []
    
    def get_blog_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about stored blogs
        """
        try:
            # Get all documents to analyze
            all_data = self.collection.get(include=["metadatas"])
            
            if not all_data['metadatas']:
                return {
                    "total_chunks": 0,
                    "unique_blogs": 0,
                    "topics": [],
                    "latest_blog": None,
                    "storage_info": {
                        "collection_name": self.collection_name,
                        "persist_directory": self.persist_directory
                    }
                }
            
            # Analyze metadata
            blog_ids = set()
            topics = set()
            latest_date = None
            
            for metadata in all_data['metadatas']:
                blog_ids.add(metadata['blog_id'])
                if metadata.get('topic'):
                    topics.add(metadata['topic'])
                
                created_at = metadata.get('created_at')
                if created_at:
                    if not latest_date or created_at > latest_date:
                        latest_date = created_at
            
            return {
                "total_chunks": len(all_data['metadatas']),
                "unique_blogs": len(blog_ids),
                "topics": list(topics),
                "latest_blog": latest_date,
                "blog_ids": list(blog_ids),
                "storage_info": {
                    "collection_name": self.collection_name,
                    "persist_directory": self.persist_directory,
                    "embedding_model": "all-MiniLM-L6-v2"
                }
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {"error": str(e)}
    
    def delete_blog(self, blog_id: int) -> bool:
        """
        Delete all chunks for a specific blog
        """
        try:
            # Get all chunk IDs for this blog
            results = self.collection.get(
                where={"blog_id": blog_id},
                include=["metadatas"]
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"🗑️ Deleted {len(results['ids'])} chunks for blog {blog_id}")
                return True
            else:
                print(f"⚠️ No chunks found for blog {blog_id}")
                return False
        except Exception as e:
            print(f"❌ Error deleting blog {blog_id}: {e}")
            return False
    
    def get_blog_content(self, blog_id: int) -> Dict[str, Any]:
        """
        Retrieve all content for a specific blog
        """
        try:
            results = self.collection.get(
                where={"blog_id": blog_id},
                include=["documents", "metadatas"]
            )
            
            if not results['documents']:
                return {"found": False, "message": f"No content found for blog {blog_id}"}
            
            # Sort chunks by index
            chunks_data = []
            for i, doc in enumerate(results['documents']):
                chunks_data.append({
                    "text": doc,
                    "metadata": results['metadatas'][i]
                })
            
            # Sort by chunk_index
            chunks_data.sort(key=lambda x: x['metadata']['chunk_index'])
            
            # Reconstruct blog info
            first_chunk = chunks_data[0]['metadata']
            full_content = " ".join([chunk['text'] for chunk in chunks_data])
            
            return {
                "found": True,
                "blog_id": blog_id,
                "blog_title": first_chunk['blog_title'],
                "topic": first_chunk.get('topic', ''),
                "full_content": full_content,
                "total_chunks": len(chunks_data),
                "created_at": first_chunk['created_at'],
                "chunks": [chunk['text'] for chunk in chunks_data]
            }
        except Exception as e:
            return {"found": False, "error": str(e)}
    
    def _chunk_text(self, text: str, chunk_size: int = 300) -> List[str]:
        """
        Split text into chunks with smart sentence boundary detection
        """
        import re
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed chunk_size, start new chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += (". " if current_chunk else "") + sentence
        
        # Add remaining content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Fallback to word-based chunking if chunks are too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size * 2:  # Allow some flexibility
                final_chunks.append(chunk)
            else:
                # Split large chunks by words
                words = chunk.split()
                for i in range(0, len(words), chunk_size // 5):  # Rough word estimate
                    word_chunk = " ".join(words[i:i + chunk_size // 5])
                    if word_chunk.strip():
                        final_chunks.append(word_chunk.strip())
        
        return final_chunks if final_chunks else [text]  # Fallback to original text
    
    def reset_collection(self) -> bool:
        """
        Delete and recreate the collection (use with caution!)
        """
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                ),
                metadata={"hnsw:space": "cosine"}
            )
            print(f"🔄 Reset ChromaDB collection: {self.collection_name}")
            return True
        except Exception as e:
            print(f"❌ Error resetting collection: {e}")
            return False

def create_chroma_manager(persist_directory: str = "./chroma_db") -> ChromaDBManager:
    """Factory function to create ChromaDB manager instance"""
    return ChromaDBManager(persist_directory=persist_directory)