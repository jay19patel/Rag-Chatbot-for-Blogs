from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
from contextlib import asynccontextmanager
import time
from datetime import datetime, timedelta

from tools import BlogTools, create_tools_instance
from langchain_mistralai.chat_models import ChatMistralAI
from personal_context import personal_context

API_KEY = os.getenv("MISTRAL_API_KEY", "yCVIzpE6wyS0uE6Y48ZFgErfPuv0rDfJ")

# Global variables
blog_tools: Optional[BlogTools] = None
llm: Optional[ChatMistralAI] = None

# Simple session management
admin_sessions = {}
MASTER_KEY = "JAY_AI_MASTER_2024_SECURE"
SESSION_TIMEOUT = 3600  # 1 hour

@asynccontextmanager
async def lifespan(app: FastAPI):
    global blog_tools, llm
    blog_tools = create_tools_instance(API_KEY)
    llm = ChatMistralAI(model="mistral-small", api_key=API_KEY)
    print("🚀 Jay Patel's AI Blog System started!")
    yield

app = FastAPI(
    title="Jay Patel's AI Blog System", 
    description="Personal AI blog system with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

class AdminChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    access_key: Optional[str] = None

class SearchBlogsRequest(BaseModel):
    query: str = Field(..., min_length=1)

# Helper functions
async def get_blog_tools() -> BlogTools:
    if blog_tools is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    return blog_tools

def validate_session(access_key: str) -> bool:
    """Validate access key and session"""
    if access_key != MASTER_KEY:
        return False
    
    current_time = time.time()
    
    # Check if session exists and is valid
    if access_key in admin_sessions:
        if current_time - admin_sessions[access_key] < SESSION_TIMEOUT:
            admin_sessions[access_key] = current_time  # Refresh session
            return True
        else:
            # Session expired
            del admin_sessions[access_key]
            return False
    
    # Create new session
    admin_sessions[access_key] = current_time
    return True

def create_session(access_key: str):
    """Create new session"""
    admin_sessions[access_key] = time.time()

# API Endpoints

@app.post("/chat")
async def chat(request: ChatRequest, tools: BlogTools = Depends(get_blog_tools)):
    """
    Main chat endpoint - responds as Jay Patel using personal context and blog database
    """
    try:
        message = request.message.strip()
        
        # Check for personal information queries first
        if personal_context.is_personal_query(message):
            personal_info = personal_context.get_personal_context(message)
            if personal_info:
                return {
                    "response": f"Hi! I'm Jay Patel. {personal_info}",
                    "source": "personal_context",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Check for greetings and basic interactions
        message_lower = message.lower()
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "namaste"]):
            return {
                "response": "Hello! I'm Jay Patel, an AI developer. How can I help you today? You can ask me about my projects, skills, or anything from my blog database.",
                "source": "greeting",
                "timestamp": datetime.now().isoformat()
            }
        
        # Search in blog database using RAG
        search_result = tools.hybrid_search_tool(message)
        
        if search_result["primary_source"] == "blog_database":
            # Found in blogs - respond as Jay
            chunks = search_result["blog_results"][:2]
            context = "\n\n".join([f"From my blog '{chunk['blog_title']}':\n{chunk['text']}" for chunk in chunks])
            
            prompt = f"""You are Jay Patel responding to: "{message}"

Based on my blog content:
{context}

Respond as Jay Patel in first person, providing helpful information from my blogs."""

            response = llm.invoke(prompt)
            
            return {
                "response": response.content,
                "source": "blog_database",
                "blog_sources": [chunk['blog_title'] for chunk in chunks],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Not found in blogs - general knowledge response as Jay
            prompt = f"""You are Jay Patel, an AI developer. Someone asked: "{message}"

Respond helpfully in first person as Jay Patel. If this topic could make a good blog post, mention that you could write about it."""

            response = llm.invoke(prompt)
            
            return {
                "response": response.content + "\n\n💡 This would make a great blog topic! If you want me to write about this, use /adminchat with the access key.",
                "source": "general_knowledge",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/adminchat")
async def admin_chat(request: AdminChatRequest, tools: BlogTools = Depends(get_blog_tools)):
    """
    Admin chat with authentication for blog CRUD operations and web research
    """
    try:
        message = request.message.strip().lower()
        
        # Check if this is a CRUD operation
        crud_keywords = ["create blog", "update blog", "delete blog", "edit blog"]
        is_crud_operation = any(keyword in message for keyword in crud_keywords)
        
        if is_crud_operation:
            # Require authentication for CRUD operations
            if not request.access_key:
                return {
                    "response": "🔐 Authentication required for blog operations. Please provide your access key.",
                    "action": "auth_required",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate session
            if not validate_session(request.access_key):
                return {
                    "response": "❌ Invalid access key or session expired. Please provide a valid access key.",
                    "action": "auth_failed",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Handle CRUD operations
            if "create blog" in message:
                return await handle_create_blog(request.message, tools)
            elif "update blog" in message or "edit blog" in message:
                return await handle_update_blog(request.message, tools)
            elif "delete blog" in message:
                return await handle_delete_blog(request.message, tools)
        
        # Non-CRUD operations - use web search and general knowledge
        return await handle_general_admin_query(request.message, tools)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def handle_create_blog(message: str, tools: BlogTools) -> Dict[str, Any]:
    """Handle blog creation from admin chat"""
    # Extract topic from message
    topic = message.lower().replace("create blog about", "").replace("create blog", "").strip()
    
    if not topic:
        return {
            "response": "Please specify a topic. Example: 'create blog about Python programming'",
            "action": "topic_required",
            "timestamp": datetime.now().isoformat()
        }
    
    # Use web search to create comprehensive blog
    try:
        from web_search_integration import web_search_creator
        blog_result = await web_search_creator.create_blog_from_web_research(topic, max_sources=3)
        
        if blog_result.get("success"):
            # Save to database
            create_result = tools.create_blog_tool(
                title=blog_result["title"],
                content=blog_result["content"],
                topic=topic
            )
            
            if create_result["status"] == "success":
                return {
                    "response": f"✅ Blog created successfully!\n\n**Title:** {blog_result['title']}\n**Blog ID:** {create_result['blog_id']}\n**Sources:** {blog_result.get('total_sources', 0)} web sources\n\nYou can continue editing with: 'update blog {create_result['blog_id']}'",
                    "blog_id": create_result['blog_id'],
                    "action": "blog_created",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "response": f"❌ Failed to save blog: {create_result['message']}",
                    "action": "create_failed",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            # Fallback to AI generation
            prompt = f"Write a comprehensive blog post about: {topic}"
            ai_response = llm.invoke(prompt)
            
            create_result = tools.create_blog_tool(
                title=f"Guide to {topic.title()}",
                content=ai_response.content,
                topic=topic
            )
            
            return {
                "response": f"✅ Blog created with AI content!\n**Blog ID:** {create_result['blog_id']}\n\nYou can continue editing with: 'update blog {create_result['blog_id']}'",
                "blog_id": create_result['blog_id'],
                "action": "blog_created_ai",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "response": f"❌ Error creating blog: {str(e)}",
            "action": "create_error",
            "timestamp": datetime.now().isoformat()
        }

async def handle_update_blog(message: str, tools: BlogTools) -> Dict[str, Any]:
    """Handle blog updates from admin chat"""
    # Extract blog ID from message
    words = message.split()
    blog_id = None
    
    for i, word in enumerate(words):
        if word.isdigit():
            blog_id = int(word)
            break
    
    if not blog_id:
        return {
            "response": "Please specify blog ID. Example: 'update blog 1 add section about machine learning'",
            "action": "blog_id_required",
            "timestamp": datetime.now().isoformat()
        }
    
    # Get current blog
    current_blog = tools.get_blog_by_id_tool(blog_id)
    if current_blog["status"] != "success":
        return {
            "response": f"❌ Blog {blog_id} not found.",
            "action": "blog_not_found",
            "timestamp": datetime.now().isoformat()
        }
    
    # Get update instructions
    update_instruction = message.lower()
    current_content = current_blog["blog"]["content"]
    
    # Use AI to generate updated content
    prompt = f"""Current blog content:
{current_content}

User wants to: {update_instruction}

Please provide the updated blog content based on the user's request."""

    ai_response = llm.invoke(prompt)
    
    # Update the blog
    result = tools.blog_service.update_blog(
        blog_id=blog_id,
        content=ai_response.content
    )
    
    if result["success"]:
        return {
            "response": f"✅ Blog {blog_id} updated successfully!\n\nYou can continue editing with more updates.",
            "blog_id": blog_id,
            "action": "blog_updated",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "response": f"❌ Failed to update blog: {result['message']}",
            "action": "update_failed",
            "timestamp": datetime.now().isoformat()
        }

async def handle_delete_blog(message: str, tools: BlogTools) -> Dict[str, Any]:
    """Handle blog deletion from admin chat"""
    words = message.split()
    blog_id = None
    
    for word in words:
        if word.isdigit():
            blog_id = int(word)
            break
    
    if not blog_id:
        return {
            "response": "Please specify blog ID. Example: 'delete blog 1'",
            "action": "blog_id_required",
            "timestamp": datetime.now().isoformat()
        }
    
    result = tools.blog_service.delete_blog(blog_id)
    
    if result["success"]:
        return {
            "response": f"🗑️ Blog {blog_id} deleted successfully!",
            "blog_id": blog_id,
            "action": "blog_deleted",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "response": f"❌ Failed to delete blog: {result['message']}",
            "action": "delete_failed",
            "timestamp": datetime.now().isoformat()
        }

async def handle_general_admin_query(message: str, tools: BlogTools) -> Dict[str, Any]:
    """Handle general queries with web search and advanced knowledge"""
    # Use AI with enhanced capabilities for admin queries
    prompt = f"""You are Jay Patel's AI assistant with access to web knowledge. 
    
User query: {message}

Provide a comprehensive, informative response using your knowledge. Be helpful and detailed."""

    response = llm.invoke(prompt)
    
    return {
        "response": response.content,
        "source": "enhanced_ai",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/search-blogs")
async def search_blogs(request: SearchBlogsRequest, tools: BlogTools = Depends(get_blog_tools)):
    """
    Search blogs using embedding-based similarity search
    """
    try:
        result = tools.search_blogs_tool(request.query, "rag")
        
        if result["status"] == "success":
            # Format top 5 results
            top_blogs = []
            seen_blog_ids = set()
            
            for chunk in result["results"]:
                blog_id = chunk['blog_id']
                if blog_id not in seen_blog_ids and len(top_blogs) < 5:
                    top_blogs.append({
                        "blog_id": blog_id,
                        "title": chunk['blog_title'],
                        "similarity_score": round(chunk['similarity'], 3),
                        "preview": chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                    })
                    seen_blog_ids.add(blog_id)
            
            return {
                "success": True,
                "query": request.query,
                "results": top_blogs,
                "total_found": len(top_blogs),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "query": request.query,
                "results": [],
                "total_found": 0,
                "message": "No matching blogs found",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/blogs")
async def list_blogs(tools: BlogTools = Depends(get_blog_tools)):
    """
    List all blogs with title and basic info
    """
    try:
        result = tools.list_blogs_tool()
        
        if result["status"] in ["success", "empty"]:
            blogs_list = []
            for blog in result["blogs"]:
                blogs_list.append({
                    "id": blog["id"],
                    "title": blog["title"],
                    "topic": blog.get("topic", "General"),
                    "created_at": blog["created_at"],
                    "preview": blog["preview"]
                })
            
            return {
                "success": True,
                "blogs": blogs_list,
                "total_count": len(blogs_list),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "blogs": [],
                "total_count": 0,
                "message": "No blogs found",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/blog/{blog_id}")
async def get_blog(blog_id: int, tools: BlogTools = Depends(get_blog_tools)):
    """
    Get complete blog data by ID
    """
    try:
        result = tools.get_blog_by_id_tool(blog_id)
        
        if result["status"] == "success":
            blog_data = result["blog"]
            return {
                "success": True,
                "blog": {
                    "id": blog_data["id"],
                    "title": blog_data["title"],
                    "content": blog_data["content"],
                    "topic": blog_data.get("topic", "General"),
                    "tags": blog_data.get("tags", []),
                    "created_at": blog_data["created_at"],
                    "word_count": len(blog_data["content"].split()),
                    "author": "Jay Patel"
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Blog not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)