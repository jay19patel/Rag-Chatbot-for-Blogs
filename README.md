# Simple AI Chatbot with Node-Based Blog System

A clean, minimalistic chatbot that automatically handles conversations, blog creation, and authentication using a smart node-based architecture.

## 🚀 Quick Start

```bash
pip install langchain-mistralai
python app.py
```

## 💬 How It Works

Just chat naturally! The system intelligently routes to the right nodes:

### Example Conversations:

**General Chat:**
```
You: Hey, how are you?
AI: Hello! I'm doing great, thanks for asking! How can I help you today?
```

**Explain + Auto Blog Offer:**
```
You: explain python and what is its use
AI: Python is a versatile programming language...

💡 Would you like me to create a blog about this topic?
```

**Create Blog:**
```
You: now i need to create blog for this topic
AI: 📝 Blog Created!

Title: "Python Programming: A Complete Guide"
Content: [Full blog content...]

Say 'save this' to save the blog!
```

**Save Blog (Authentication Required):**
```
You: now save this  
AI: 🔒 Permission denied! You need authentication to save blogs. Share your access key.

You: my access key is 123
AI: ✅ Authentication successful! Blog saved successfully!
```

## 🏗️ Architecture

### Files:
- **`app.py`** - Main orchestrator with smart routing
- **`simple_nodes.py`** - Individual node functions
- **`schema.py`** - Data structures  
- **`blogs.json`** - Auto-created blog storage

### Nodes:
- **`general_chat_node`** - AI conversation
- **`create_blog_node`** - Auto blog generation
- **`save_blog_node`** - Blog persistence  
- **`authentication_node`** - Access control
- **`blog_query_node`** - Search existing blogs

### Smart Router:
- No if/else chains - pure node-based routing
- Contextual keyword detection
- State management across nodes
- Automatic topic extraction

## 🔧 Customization

### Add New Node:
1. Create function in `simple_nodes.py`
2. Add routing logic in `smart_router()`
3. Done! No complex configuration needed.

### Modify Authentication:
Change access key in `authentication_node()` function.

### Extend Functionality:
Each node is independent - modify or add features without affecting others.

## 🎯 Features

- **Natural Conversations** - No commands, just chat
- **Auto Blog Creation** - Intelligent topic extraction  
- **Smart Authentication** - Seamless access control
- **Persistent Storage** - JSON-based blog database
- **Modular Design** - Easy to extend and customize
- **No Dependencies** - Minimal requirements

The system automatically detects intent and routes to appropriate nodes without any complex configuration!