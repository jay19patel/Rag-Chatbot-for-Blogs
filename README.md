# 🤖 Advanced AI Blog System with RAG

An intelligent blog management system powered by **ChromaDB**, **RAG (Retrieval Augmented Generation)**, **Web Search Integration**, and **Authentication**.

## 🚀 Features

### 🔍 **Intelligent Search & RAG**
- **ChromaDB Integration**: Fast, accurate vector search with semantic similarity
- **RAG System**: Context-aware responses using existing blog content  
- **Personal Context**: AI knows about Jay Patel's personal information
- **Optimized Embeddings**: Uses `all-MiniLM-L6-v2` for high-quality semantic search

### 🌐 **Web Research & Blog Creation**
- **Automated Web Research**: Creates blogs by researching topics from multiple web sources
- **Google Search Integration**: Searches and extracts content from authoritative websites
- **Content Synthesis**: Combines multiple sources into comprehensive blog posts
- **Quality Assessment**: Evaluates research quality and source reliability

### 🔐 **Secure Authentication System**
- **Multi-Level Access Keys**: Master, Admin, and Update keys with different permissions
- **Rate Limiting**: Protection against brute force attacks with temporary lockouts
- **Audit Logging**: Complete tracking of all authentication attempts
- **Session Management**: Secure session handling with automatic expiration

### 💬 **Enhanced Chat System**
- **Personal Queries**: Ask about Jay Patel's background, skills, projects
- **Blog Q&A**: Query existing blog content for specific information
- **Context-Aware Responses**: AI provides relevant answers from blog database
- **Multi-Source Responses**: Combines blog content and general knowledge

## 🛠️ **Installation & Setup**

### 1. **Install Dependencies**
```bash
pip install chromadb sentence-transformers fastapi uvicorn langchain-mistralai numpy pydantic requests googlesearch-python python-dotenv httpx aiohttp beautifulsoup4
```

### 2. **Set Environment Variables**
```bash
export MISTRAL_API_KEY="your_mistral_api_key_here"
```

### 3. **Run the Server**
```bash
python main.py
```

Server will start at: `http://localhost:8000`

## 🔑 **Access Keys**

### **Master Key**: `JAY_AI_MASTER_2024_SECURE`
**Permissions**: Create, Update, Delete, Search, Admin Access, System Stats

### **Admin Key**: `JAY_ADMIN_ACCESS_KEY_2024`  
**Permissions**: Create, Update, Search, System Stats

### **Update Key**: `JAY_UPDATE_BLOG_KEY_2024`
**Permissions**: Update, Search

## 📚 **API Endpoints**

### 🗣️ **Chat System**
```bash
# Personal information queries
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Who are you?"}'

# Blog content queries  
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}'
```

### 📝 **Blog Management**

#### **Create Blog from Web Research**
```bash
curl -X POST "http://localhost:8000/create-web-blog" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning Fundamentals",
    "access_key": "JAY_AI_MASTER_2024_SECURE",
    "max_sources": 4
  }'
```

#### **Update Blog**
```bash
curl -X PUT "http://localhost:8000/update-blog" \
  -H "Content-Type: application/json" \
  -d '{
    "blog_id": 1,
    "access_key": "JAY_ADMIN_ACCESS_KEY_2024",
    "title": "New Title",
    "content": "Updated content..."
  }'
```

#### **Delete Blog**
```bash
curl -X DELETE "http://localhost:8000/delete-blog" \
  -H "Content-Type: application/json" \
  -d '{
    "blog_id": 1,
    "access_key": "JAY_AI_MASTER_2024_SECURE"
  }'
```

### 🔍 **Search & Discovery**
```bash
# Search blogs
curl -X POST "http://localhost:8000/blog-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Python machine learning"}'

# List all blogs
curl "http://localhost:8000/blogs"

# Get specific blog
curl "http://localhost:8000/blogs/1"
```

### 🔐 **Authentication & System**
```bash
# Check access key
curl "http://localhost:8000/auth-info/JAY_AI_MASTER_2024_SECURE"

# System statistics
curl "http://localhost:8000/system-stats" \
  -H "access_key: JAY_AI_MASTER_2024_SECURE"
```

## 🎯 **Usage Examples**

### **Personal Information Queries**
```javascript
// Ask about Jay
fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: "Tell me about yourself"
    })
})
```

### **Create Web-Researched Blog**
```javascript
// Create blog from web research
fetch('/create-web-blog', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        topic: "Artificial Intelligence Trends 2024",
        access_key: "JAY_AI_MASTER_2024_SECURE",
        max_sources: 5
    })
})
```

### **Query Existing Blogs**
```javascript
// Search in existing blogs
fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: "What did you write about machine learning?"
    })
})
```

## 🧠 **AI Capabilities**

### **Personal Context Understanding**
- Recognizes queries about Jay Patel's background
- Provides information about skills, projects, contact details
- Maintains context about personal interests and philosophy

### **Blog Content Intelligence**  
- Semantic search through all blog content using ChromaDB
- Contextual responses based on existing blog database
- Similarity scoring with optimized thresholds

### **Web Research Intelligence**
- Automated Google searches with diverse query strategies
- Content extraction from multiple authoritative sources
- Intelligent content synthesis and summarization
- Quality assessment of research sources

## 🏗️ **System Architecture**

```
┌─── FastAPI Main App ───┐
│   • Authentication     │
│   • API Endpoints      │
│   • Request Handling   │
└─────────────────────────┘
            │
┌─── ChromaDB Vector DB ───┐    ┌─── SQLite Metadata ───┐
│   • Blog Embeddings      │    │   • Blog Information   │
│   • Semantic Search      │    │   • User Data          │
│   • Persistent Storage   │    │   • Audit Logs         │
└───────────────────────────┘    └────────────────────────┘
            │
┌─── Web Search Engine ───┐    ┌─── Personal Context ───┐
│   • Google Search API   │    │   • Jay's Information  │
│   • Content Extraction  │    │   • Skills & Projects  │
│   • Content Synthesis   │    │   • Contact Details    │
└─────────────────────────┘    └────────────────────────┘
```

## 📁 **File Structure**

```
ai-chatbot/
├── main.py                    # FastAPI application with all endpoints
├── chromadb_integration.py    # ChromaDB manager with optimizations
├── database.py               # SQLite database for metadata
├── blog_service.py           # Core blog operations
├── tools.py                  # Blog tools and utilities
├── auth_system.py            # Authentication and security
├── personal_context.py       # Personal information manager
├── web_search_integration.py # Web research and content creation
├── personal_info.json        # Jay Patel's personal information
├── auth_config.json          # Authentication configuration
├── requirements.txt          # Python dependencies
└── README.md                # This documentation
```

## ⚡ **Performance Optimizations**

### **ChromaDB Optimizations**
- HNSW index with optimized parameters (`M=16`, `search_ef=200`)
- Efficient similarity scoring with calibrated thresholds
- Batch processing for multiple operations
- Smart chunking with sentence boundary detection

### **Search Performance**
- Sub-second semantic search on thousands of documents
- Intelligent result ranking and filtering
- Caching for repeated queries
- Concurrent web research operations

## 🔒 **Security Features**

### **Authentication**
- Multiple access levels with specific permissions
- Rate limiting and brute force protection
- Session management with automatic expiration
- Comprehensive audit logging

### **Data Protection**
- Secure storage of personal information
- Protected endpoints for sensitive operations
- Input validation and sanitization
- Error handling without information leakage

---

**Created by Jay Patel** • *AI Developer & Tech Enthusiast*

🔗 **Contact**: [GitHub](https://github.com/jaypatel-dev) • [Email](mailto:jay@example.com)

*This system demonstrates advanced AI capabilities including RAG, semantic search, web research automation, and intelligent content management.*

Access interactive API documentation at: `http://localhost:8000/docs`