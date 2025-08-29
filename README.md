# 🧠 RAG Blog System

Simple RAG-powered blog system with chat interface, embedding search, and SQLite storage.

## 🚀 Quick Start

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test system
python test_system.py

# 4. Start server
uvicorn main:app --reload
```

## 🛠 API Endpoints (Only 4 endpoints)

### 1. `/chat` (POST) - Main Chat Interface
**Everything happens through chat!**

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python programming?"}'
```

**Chat Commands:**
- `"create blog about Python"` - Creates blog with AI
- `"list blogs"` - Shows all blogs
- `"What is machine learning?"` - RAG search + answer
- Regular questions get RAG responses

### 2. `/blogs` (GET) - List All Blogs
```bash
curl "http://localhost:8000/blogs"
```

### 3. `/blogs/{id}` (GET) - Get Blog Details
```bash
curl "http://localhost:8000/blogs/1"
```

### 4. `/blog-search` (POST) - Search with Embeddings
```bash
curl -X POST "http://localhost:8000/blog-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning"}'
```

Returns blog IDs, similarity scores, and text snippets.

## 💬 How It Works

1. **Chat Interface**: Send any message to `/chat`
2. **Smart Routing**: System detects intent (create blog, search, question)
3. **RAG Search**: Uses embeddings to find relevant blog content
4. **AI Response**: Combines retrieved context with AI generation
5. **Google Fallback**: If not found in blogs, suggests creating new blog

## 📋 Example Usage

### Create Blog via Chat
```json
{
  "message": "create blog about artificial intelligence"
}
```

Response includes blog ID and confirmation.

### Ask Questions (RAG)
```json
{
  "message": "What are the benefits of Python?"
}
```

Gets answer from your blogs if available, otherwise general response.

### List Blogs via Chat
```json
{
  "message": "list my blogs"
}
```

### Search Blogs with Embeddings
```json
{
  "query": "machine learning algorithms"
}
```

Returns matching blog IDs with similarity scores.

## 🔧 System Features

- **📚 Automatic Indexing**: Blogs are chunked and embedded
- **🔍 Semantic Search**: Vector similarity matching
- **💬 Natural Chat**: No commands, just natural language
- **🌐 Smart Fallback**: Google search when content not found
- **📊 SQLite Storage**: Efficient local database
- **⚡ FastAPI**: Production-ready with auto docs at `/docs`

## 📁 Files Structure

```
ai-chatbot/
├── main.py           # FastAPI app (4 endpoints only)
├── tools.py          # Blog management utilities
├── database.py       # SQLite operations
├── embeddings.py     # Mistral embeddings
├── blog_service.py   # Core RAG logic
└── test_system.py    # System tests
```

## 🎯 Key Benefits

- **Simple**: Only 4 endpoints needed
- **Smart**: Chat handles everything via natural language  
- **Fast**: Embedding-based search with similarity scores
- **Complete**: Blog creation, search, and retrieval in one system

Access at: http://localhost:8000/docs for interactive API documentation.