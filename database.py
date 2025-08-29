import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np

class BlogDatabase:
    def __init__(self, db_path: str = "blogs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create blogs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                topic TEXT,
                tags TEXT,
                created_at TEXT,
                embedding BLOB
            )
        ''')
        
        # Create blog_chunks table for RAG
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_id INTEGER,
                chunk_text TEXT NOT NULL,
                chunk_embedding BLOB,
                FOREIGN KEY (blog_id) REFERENCES blogs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_blog(self, title: str, content: str, topic: str = "", 
                  tags: List[str] = None, embedding: np.ndarray = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_str = json.dumps(tags or [])
        embedding_blob = embedding.tobytes() if embedding is not None else None
        
        cursor.execute('''
            INSERT INTO blogs (title, content, topic, tags, created_at, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, topic, tags_str, datetime.now().isoformat(), embedding_blob))
        
        blog_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return blog_id
    
    def save_blog_chunks(self, blog_id: int, chunks: List[Dict[str, Any]]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for chunk in chunks:
            embedding_blob = chunk['embedding'].tobytes() if chunk.get('embedding') is not None else None
            cursor.execute('''
                INSERT INTO blog_chunks (blog_id, chunk_text, chunk_embedding)
                VALUES (?, ?, ?)
            ''', (blog_id, chunk['text'], embedding_blob))
        
        conn.commit()
        conn.close()
    
    def get_all_blogs(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title, content, topic, tags, created_at FROM blogs')
        rows = cursor.fetchall()
        
        blogs = []
        for row in rows:
            blogs.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'topic': row[3],
                'tags': json.loads(row[4]),
                'created_at': row[5]
            })
        
        conn.close()
        return blogs
    
    def delete_blog(self, blog_id: int) -> bool:
        """Delete a blog and its chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete blog chunks first (foreign key constraint)
            cursor.execute('DELETE FROM blog_chunks WHERE blog_id = ?', (blog_id,))
            
            # Delete the blog
            cursor.execute('DELETE FROM blogs WHERE id = ?', (blog_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return deleted
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def update_blog(self, blog_id: int, title: str = None, content: str = None, 
                   topic: str = None, tags: List[str] = None) -> bool:
        """Update an existing blog"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
                
            if content is not None:
                updates.append("content = ?")
                params.append(content)
                
            if topic is not None:
                updates.append("topic = ?")
                params.append(topic)
                
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if updates:
                params.append(blog_id)
                query = f"UPDATE blogs SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                
                updated = cursor.rowcount > 0
                conn.commit()
                conn.close()
                return updated
            else:
                conn.close()
                return False
                
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def get_blog_by_id(self, blog_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific blog by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title, content, topic, tags, created_at FROM blogs WHERE id = ?', (blog_id,))
        row = cursor.fetchone()
        
        if row:
            blog = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'topic': row[3],
                'tags': json.loads(row[4]),
                'created_at': row[5]
            }
            conn.close()
            return blog
        else:
            conn.close()
            return None
    
    def get_blogs_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get all blogs for a specific topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id, title, content, topic, tags, created_at 
                         FROM blogs WHERE topic LIKE ?''', (f'%{topic}%',))
        rows = cursor.fetchall()
        
        blogs = []
        for row in rows:
            blogs.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'topic': row[3],
                'tags': json.loads(row[4]),
                'created_at': row[5]
            })
        
        conn.close()
        return blogs
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get blog count
        cursor.execute('SELECT COUNT(*) FROM blogs')
        blog_count = cursor.fetchone()[0]
        
        # Get chunk count
        cursor.execute('SELECT COUNT(*) FROM blog_chunks')
        chunk_count = cursor.fetchone()[0]
        
        # Get latest blog
        cursor.execute('SELECT title, created_at FROM blogs ORDER BY created_at DESC LIMIT 1')
        latest_blog = cursor.fetchone()
        
        # Get unique topics
        cursor.execute('SELECT DISTINCT topic FROM blogs WHERE topic IS NOT NULL AND topic != ""')
        topics = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_blogs': blog_count,
            'total_chunks': chunk_count,
            'latest_blog': {'title': latest_blog[0], 'created_at': latest_blog[1]} if latest_blog else None,
            'unique_topics': topics,
            'topics_count': len(topics)
        }
    
    def get_blog_chunks_with_embeddings(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bc.chunk_text, bc.chunk_embedding, b.title, b.id 
            FROM blog_chunks bc 
            JOIN blogs b ON bc.blog_id = b.id
            WHERE bc.chunk_embedding IS NOT NULL
        ''')
        
        rows = cursor.fetchall()
        chunks = []
        
        for row in rows:
            embedding = np.frombuffer(row[1], dtype=np.float32) if row[1] else None
            chunks.append({
                'text': row[0],
                'embedding': embedding,
                'blog_title': row[2],
                'blog_id': row[3]
            })
        
        conn.close()
        return chunks
    
    def search_blogs_by_text(self, query: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, topic, tags, created_at 
            FROM blogs 
            WHERE title LIKE ? OR content LIKE ? OR topic LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        blogs = []
        
        for row in rows:
            blogs.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'topic': row[3],
                'tags': json.loads(row[4]),
                'created_at': row[5]
            })
        
        conn.close()
        return blogs
    
    def delete_blog(self, blog_id: int) -> bool:
        """Delete a blog and its chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete blog chunks first (foreign key constraint)
            cursor.execute('DELETE FROM blog_chunks WHERE blog_id = ?', (blog_id,))
            
            # Delete the blog
            cursor.execute('DELETE FROM blogs WHERE id = ?', (blog_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return deleted
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def update_blog(self, blog_id: int, title: str = None, content: str = None, 
                   topic: str = None, tags: List[str] = None) -> bool:
        """Update an existing blog"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
                
            if content is not None:
                updates.append("content = ?")
                params.append(content)
                
            if topic is not None:
                updates.append("topic = ?")
                params.append(topic)
                
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if updates:
                params.append(blog_id)
                query = f"UPDATE blogs SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                
                updated = cursor.rowcount > 0
                conn.commit()
                conn.close()
                return updated
            else:
                conn.close()
                return False
                
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def get_blog_by_id(self, blog_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific blog by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title, content, topic, tags, created_at FROM blogs WHERE id = ?', (blog_id,))
        row = cursor.fetchone()
        
        if row:
            blog = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'topic': row[3],
                'tags': json.loads(row[4]),
                'created_at': row[5]
            }
            conn.close()
            return blog
        else:
            conn.close()
            return None
    
    def get_blogs_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get all blogs for a specific topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id, title, content, topic, tags, created_at 
                         FROM blogs WHERE topic LIKE ?''', (f'%{topic}%',))
        rows = cursor.fetchall()
        
        blogs = []
        for row in rows:
            blogs.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'topic': row[3],
                'tags': json.loads(row[4]),
                'created_at': row[5]
            })
        
        conn.close()
        return blogs
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get blog count
        cursor.execute('SELECT COUNT(*) FROM blogs')
        blog_count = cursor.fetchone()[0]
        
        # Get chunk count
        cursor.execute('SELECT COUNT(*) FROM blog_chunks')
        chunk_count = cursor.fetchone()[0]
        
        # Get latest blog
        cursor.execute('SELECT title, created_at FROM blogs ORDER BY created_at DESC LIMIT 1')
        latest_blog = cursor.fetchone()
        
        # Get unique topics
        cursor.execute('SELECT DISTINCT topic FROM blogs WHERE topic IS NOT NULL AND topic != ""')
        topics = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_blogs': blog_count,
            'total_chunks': chunk_count,
            'latest_blog': {'title': latest_blog[0], 'created_at': latest_blog[1]} if latest_blog else None,
            'unique_topics': topics,
            'topics_count': len(topics)
        }