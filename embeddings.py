import numpy as np
from typing import List, Dict, Any
import requests
import json
from langchain_mistralai import MistralAIEmbeddings

class EmbeddingSystem:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.embeddings = MistralAIEmbeddings(
            model="mistral-embed",
            mistral_api_key=api_key
        )
    
    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding for a single text"""
        try:
            embedding = self.embeddings.embed_query(text)
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            print(f"Error creating embedding: {e}")
            # Fallback to simple word count vector
            return self._simple_embedding(text)
    
    def create_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Create embeddings for multiple texts"""
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return [np.array(emb, dtype=np.float32) for emb in embeddings]
        except Exception as e:
            print(f"Error creating batch embeddings: {e}")
            return [self._simple_embedding(text) for text in texts]
    
    def _simple_embedding(self, text: str, dim: int = 384) -> np.ndarray:
        """Fallback simple embedding based on text characteristics"""
        words = text.lower().split()
        
        # Simple hash-based embedding
        embedding = np.zeros(dim, dtype=np.float32)
        
        for i, word in enumerate(words[:dim]):
            hash_val = hash(word) % dim
            embedding[hash_val] += 1.0 / (i + 1)  # Diminishing weight for later words
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def chunk_text(self, text: str, chunk_size: int = 300) -> List[str]:
        """Split text into chunks for better RAG performance"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def find_similar_chunks(self, query_embedding: np.ndarray, 
                           chunk_embeddings: List[Dict[str, Any]], 
                           top_k: int = 3) -> List[Dict[str, Any]]:
        """Find most similar chunks to query"""
        similarities = []
        
        for chunk_data in chunk_embeddings:
            similarity = self.cosine_similarity(query_embedding, chunk_data['embedding'])
            similarities.append({
                'text': chunk_data['text'],
                'blog_title': chunk_data['blog_title'],
                'blog_id': chunk_data['blog_id'],
                'similarity': similarity
            })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]