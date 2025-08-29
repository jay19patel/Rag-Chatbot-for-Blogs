# 🤖 Jay Patel's AI Blog System

**Simple 5-Endpoint AI Blog System** that represents Jay Patel with RAG capabilities, personal context, and secure admin operations.

## 🚀 Quick Start

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Mistral AI API key
export MISTRAL_API_KEY="your_mistral_api_key_here"

# 4. Run the system
python main.py
```

**Access**: `http://localhost:8000` | **Docs**: `http://localhost:8000/docs`

## 🔑 Access Key
**Master Key**: `JAY_AI_MASTER_2024_SECURE` (Required for admin operations)

## 📡 API Endpoints (Only 5)

### 1. `POST /chat` - Main Chat as Jay Patel
Chat with Jay Patel's AI representation using personal context and blog knowledge.

**Input:**
```json
{
    "message": "Who are you?"
}
```

**Output:**
```json
{
    "response": "Hi! I'm Jay Patel. I'm Jay Patel, a passionate developer working on AI-powered applications. I specialize in building intelligent systems using Python, machine learning, and modern web technologies.",
    "source": "personal_context",
    "timestamp": "2024-12-29T10:30:00"
}
```

**Examples:**
- `"Hello"` → Personal greeting as Jay Patel
- `"What are your skills?"` → Personal information from JSON
- `"Tell me about Python"` → RAG search in blog database
- `"What is machine learning?"` → Blog content + general knowledge

---

### 2. `POST /adminchat` - Admin Chat with Authentication
Secure admin operations with 1-hour session timeout.

**Input (No Auth Required):**
```json
{
    "message": "What is artificial intelligence?"
}
```

**Output:**
```json
{
    "response": "Artificial intelligence is a comprehensive field...",
    "source": "enhanced_ai",
    "timestamp": "2024-12-29T10:30:00"
}
```

**Input (Auth Required for CRUD):**
```json
{
    "message": "create blog about Python programming",
    "access_key": "JAY_AI_MASTER_2024_SECURE"
}
```

**Output:**
```json
{
    "response": "✅ Blog created successfully!\n\n**Title:** Complete Guide to Python Programming\n**Blog ID:** 1\n**Sources:** 3 web sources\n\nYou can continue editing with: 'update blog 1'",
    "blog_id": 1,
    "action": "blog_created",
    "timestamp": "2024-12-29T10:30:00"
}
```

**CRUD Commands:**
- `"create blog about [topic]"` + access_key → Create new blog with web research
- `"update blog 1 add more examples"` + access_key → Update existing blog
- `"delete blog 1"` + access_key → Delete blog

---

### 3. `POST /search-blogs` - Semantic Search
Search blogs using ChromaDB embeddings - returns top 5 matches.

**Input:**
```json
{
    "query": "Python machine learning"
}
```

**Output:**
```json
{
    "success": true,
    "query": "Python machine learning",
    "results": [
        {
            "blog_id": 1,
            "title": "Python for Machine Learning",
            "similarity_score": 0.892,
            "preview": "Python is the most popular language for machine learning due to its simplicity and powerful libraries like scikit-learn, TensorFlow, and PyTorch..."
        },
        {
            "blog_id": 3,
            "title": "Data Science with Python",
            "similarity_score": 0.745,
            "preview": "Data science involves extracting insights from data using statistical methods and machine learning algorithms..."
        }
    ],
    "total_found": 2,
    "timestamp": "2024-12-29T10:30:00"
}
```

---

### 4. `GET /blogs` - List All Blogs
Get all blogs with titles and previews.

**Output:**
```json
{
    "success": true,
    "blogs": [
        {
            "id": 1,
            "title": "Python for Machine Learning",
            "topic": "Programming",
            "created_at": "2024-12-29T10:00:00",
            "preview": "Python is the most popular language for machine learning..."
        },
        {
            "id": 2,
            "title": "Web Development with FastAPI",
            "topic": "Web Development",
            "created_at": "2024-12-29T11:00:00",
            "preview": "FastAPI is a modern web framework for building APIs..."
        }
    ],
    "total_count": 2,
    "timestamp": "2024-12-29T10:30:00"
}
```

---

### 5. `GET /blog/{id}` - Get Complete Blog
Get full blog content by ID.

**URL:** `/blog/1`

**Output:**
```json
{
    "success": true,
    "blog": {
        "id": 1,
        "title": "Python for Machine Learning",
        "content": "# Python for Machine Learning\n\nPython has become the de facto language for machine learning...\n\n## Key Libraries\n- scikit-learn\n- TensorFlow\n- PyTorch...",
        "topic": "Programming",
        "tags": ["python", "ml", "programming"],
        "created_at": "2024-12-29T10:00:00",
        "word_count": 1250,
        "author": "Jay Patel"
    },
    "timestamp": "2024-12-29T10:30:00"
}
```

## 🧠 How It Works

### **Chat System (/chat)**
1. **Personal Queries** → Uses `personal_info.json` to respond as Jay Patel
2. **Blog Queries** → RAG search in ChromaDB blog database
3. **General Questions** → AI knowledge + suggests creating blog post
4. **Always responds as Jay Patel in first person**

### **Admin System (/adminchat)**
1. **Non-CRUD** → Enhanced AI responses with web knowledge
2. **CRUD Operations** → Requires `JAY_AI_MASTER_2024_SECURE` access key
3. **Session Management** → 1-hour timeout, auto-refresh on activity
4. **Web Research** → Automatically searches web to create comprehensive blogs

### **Search System (/search-blogs)**
1. **Embedding Search** → Uses ChromaDB semantic similarity
2. **Top 5 Results** → Ranked by similarity score
3. **Deduplication** → One result per unique blog
4. **Preview Text** → 200 characters preview

## 📊 System Architecture

```
┌─── FastAPI (5 Endpoints) ───┐
│  /chat - Jay Patel persona  │
│  /adminchat - Admin + CRUD   │
│  /search-blogs - Embedding   │
│  /blogs - List all          │
│  /blog/id - Get specific    │
└─────────────────────────────┘
            │
┌─── Data Sources ───┐    ┌─── ChromaDB Vector DB ───┐
│  personal_info.json │    │  • Blog Embeddings      │
│  • Jay's info      │    │  • Semantic Search      │
│  • Skills & Projects│    │  • all-MiniLM-L6-v2     │
│  • Contact details │    │  • Persistent Storage   │
└─────────────────────┘    └─────────────────────────┘
            │
┌─── Web Research ───┐    ┌─── SQLite Database ───┐
│  • Google Search   │    │  • Blog Metadata      │
│  • Content Extract │    │  • Full Text Storage  │
│  • Multi-source    │    │  • Backup System      │
└─────────────────────┘    └───────────────────────┘
```

## 🔒 Security Features

### **Authentication System**
- **Access Key**: `JAY_AI_MASTER_2024_SECURE`
- **Session Timeout**: 1 hour automatic expiry
- **CRUD Protection**: Authentication required for create/update/delete
- **Session Refresh**: Auto-refresh on valid activity

### **Authentication Flow**
1. **First CRUD Request**: Provide access key → Creates 1-hour session
2. **Subsequent Requests**: Session auto-validates and refreshes
3. **After 1 Hour**: Session expires → Must provide access key again
4. **Invalid Key**: Immediate rejection with clear error message

## 🎯 Usage Examples

### **Basic Chat**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi Jay, tell me about your experience with Python"}'
```

### **Admin Blog Creation**
```bash
curl -X POST "http://localhost:8000/adminchat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "create blog about React.js best practices",
    "access_key": "JAY_AI_MASTER_2024_SECURE"
  }'
```

### **Search Blogs**
```bash
curl -X POST "http://localhost:8000/search-blogs" \
  -H "Content-Type: application/json" \
  -d '{"query": "JavaScript frameworks"}'
```

### **List All Blogs**
```bash
curl "http://localhost:8000/blogs"
```

### **Get Specific Blog**
```bash
curl "http://localhost:8000/blog/1"
```

## 📁 File Structure

```
ai-chatbot/
├── main.py                    # FastAPI app (5 endpoints only)
├── tools.py                   # Blog management tools
├── database.py                # SQLite + ChromaDB integration
├── blog_service.py            # Core blog operations
├── personal_context.py        # Jay Patel's personal info manager
├── web_search_integration.py  # Web research capabilities
├── chromadb_integration.py    # Optimized ChromaDB manager
├── personal_info.json         # Jay Patel's personal information
├── requirements.txt           # Dependencies
└── README.md                  # This documentation
```

## ⚡ Performance

- **RAG Search**: Sub-second semantic search with ChromaDB
- **Embeddings**: all-MiniLM-L6-v2 (384 dimensions)
- **Database**: ChromaDB + SQLite hybrid storage
- **Chunking**: Smart sentence-boundary text splitting
- **Web Research**: Concurrent multi-source content extraction

## 🎭 Jay Patel Persona

The AI system represents **Jay Patel** and will:
- ✅ Always respond in first person as Jay Patel
- ✅ Use personal information from `personal_info.json`
- ✅ Reference "my blogs" and "my experience"
- ✅ Suggest creating blog posts for new topics
- ✅ Maintain professional but friendly tone
- ❌ Never claim to be a generic AI assistant

## 🔧 Configuration

### **Personal Info** (`personal_info.json`)
Update Jay Patel's information:
```json
{
  "personal_info": {
    "name": "Jay Patel",
    "role": "AI Developer & Tech Enthusiast",
    "expertise": ["Python", "AI/ML", "Web Development"],
    "bio": "Passionate developer working on AI-powered applications..."
  }
}
```

### **Environment Variables**
```bash
export MISTRAL_API_KEY="your_mistral_api_key_here"
```

## 🚨 Error Handling

### **Authentication Errors**
```json
{
  "response": "🔐 Authentication required for blog operations. Please provide your access key.",
  "action": "auth_required",
  "timestamp": "2024-12-29T10:30:00"
}
```

### **Session Expired**
```json
{
  "response": "❌ Invalid access key or session expired. Please provide a valid access key.",
  "action": "auth_failed",
  "timestamp": "2024-12-29T10:30:00"
}
```

### **Blog Not Found**
```json
{
  "response": "❌ Blog 999 not found.",
  "action": "blog_not_found",
  "timestamp": "2024-12-29T10:30:00"
}
```

---

## 🎉 Ready to Use!

Your AI blog system is production-ready with:
- ✅ 5 clean, focused endpoints
- ✅ Jay Patel persona with personal context
- ✅ Secure admin operations with session management
- ✅ Fast ChromaDB semantic search
- ✅ Web research capabilities
- ✅ Complete documentation

**Start the system:** `python main.py`  
**Test the API:** `http://localhost:8000/docs`

---

**Created by Jay Patel** • AI Developer & Tech Enthusiast  
*This system demonstrates clean architecture, RAG capabilities, and intelligent content management.*