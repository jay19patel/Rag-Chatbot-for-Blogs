from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from contextlib import asynccontextmanager
import asyncio

from tools import BlogTools, create_tools_instance
from langchain_mistralai.chat_models import ChatMistralAI
from auth_system import auth_system
from personal_context import personal_context
from web_search_integration import web_search_creator

API_KEY = os.getenv("MISTRAL_API_KEY", "yCVIzpE6wyS0uE6Y48ZFgErfPuv0rDfJ")

blog_tools: Optional[BlogTools] = None
llm: Optional[ChatMistralAI] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global blog_tools, llm
    blog_tools = create_tools_instance(API_KEY)
    llm = ChatMistralAI(model="mistral-small", api_key=API_KEY)
    print("🚀 RAG Blog System started!")
    yield

app = FastAPI(title="RAG Blog System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

class BlogSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)

class WebBlogRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    access_key: str = Field(..., min_length=1)
    max_sources: int = Field(default=4, ge=1, le=8)

class UpdateBlogRequest(BaseModel):
    blog_id: int
    access_key: str
    title: Optional[str] = None
    content: Optional[str] = None
    topic: Optional[str] = None

class DeleteBlogRequest(BaseModel):
    blog_id: int
    access_key: str

async def get_blog_tools() -> BlogTools:
    if blog_tools is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    return blog_tools

@app.post("/chat")
async def chat(request: ChatRequest, tools: BlogTools = Depends(get_blog_tools)):
    try:
        # Check for personal information queries first
        if personal_context.is_personal_query(request.message):
            personal_info = personal_context.get_personal_context(request.message)
            if personal_info:
                return {
                    "response": f"👤 **Personal Information:**\n\n{personal_info}",
                    "source": "personal_context",
                    "action": "personal_info_provided"
                }
        
        message = request.message.lower().strip()
        
        # Check if user wants to create a blog
        create_keywords = ["create blog", "make blog", "write blog", "blog about", "generate blog"]
        if any(keyword in message for keyword in create_keywords):
            # Extract topic
            topic = message
            for keyword in create_keywords:
                topic = topic.replace(keyword, "").strip()
            
            if not topic:
                return {"response": "❌ Please specify a topic. Example: 'create blog about Python programming'"}
            
            # Generate blog
            title_response = llm.invoke(f"Generate a catchy blog title about: {topic}")
            content_response = llm.invoke(f"Write a detailed blog post about: {topic}")
            
            # Create blog
            result = tools.create_blog_tool(
                title=title_response.content.strip(),
                content=content_response.content.strip(),
                topic=topic
            )
            
            if result["status"] == "success":
                return {
                    "response": f"📝 **Blog Created Successfully!**\n\n**Title:** {title_response.content.strip()}\n\n**Blog ID:** {result['blog_id']}\n\n✅ Blog indexed with {result['chunks_created']} searchable chunks",
                    "blog_id": result['blog_id'],
                    "action": "blog_created"
                }
            else:
                return {"response": f"❌ Failed to create blog: {result['message']}"}
        
        # Check if user wants to list blogs
        list_keywords = ["list blogs", "show blogs", "my blogs", "all blogs"]
        if any(keyword in message for keyword in list_keywords):
            result = tools.list_blogs_tool()
            
            if result["status"] == "success":
                blogs = result["blogs"]
                blog_list = "\n\n".join([
                    f"📄 **{blog['title']}** (ID: {blog['id']})\n📅 {blog['created_at']}\n📝 {blog['preview']}"
                    for blog in blogs
                ])
                return {
                    "response": f"📚 **Your Blogs** ({len(blogs)} total):\n\n{blog_list}",
                    "blogs": blogs,
                    "action": "blogs_listed"
                }
            else:
                return {"response": "📭 No blogs found. Create your first blog by saying 'create blog about [topic]'"}
        
        # Regular chat with RAG search
        search_result = tools.hybrid_search_tool(request.message)
        
        if search_result["primary_source"] == "blog_database":
            # Found in blogs
            chunks = search_result["blog_results"][:2]
            context = "\n\n".join([f"From '{chunk['blog_title']}':\n{chunk['text']}" for chunk in chunks])
            
            prompt = f"""Answer based on this blog content: "{request.message}"

Blog Content:
{context}

Provide helpful answer from this information."""

            response = llm.invoke(prompt)
            
            return {
                "response": f"📚 **From your blogs:**\n\n{response.content}\n\n---\n📖 Source: {', '.join([chunk['blog_title'] for chunk in chunks])}",
                "source": "blog_rag",
                "blog_sources": [chunk['blog_title'] for chunk in chunks]
            }
        else:
            # Not found in blogs, use Google search
            prompt = f"""Answer the user's question: "{request.message}"

Provide helpful, informative response about this topic."""

            response = llm.invoke(prompt)
            
            return {
                "response": f"🌐 **General Response:**\n\n{response.content}\n\n---\n💡 This topic wasn't found in your blogs. Want me to create a blog about it?",
                "source": "general",
                "suggestion": f"create blog about {request.message}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/blogs")
async def list_blogs(tools: BlogTools = Depends(get_blog_tools)):
    try:
        result = tools.list_blogs_tool()
        
        if result["status"] in ["success", "empty"]:
            return {
                "success": True,
                "blogs": result["blogs"],
                "total_count": result["total_count"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/blogs/{blog_id}")
async def get_blog(blog_id: int, tools: BlogTools = Depends(get_blog_tools)):
    try:
        result = tools.get_blog_by_id_tool(blog_id)
        
        if result["status"] == "success":
            return {"success": True, "blog": result["blog"]}
        else:
            raise HTTPException(status_code=404, detail="Blog not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/blog-search")
async def search_blogs(request: BlogSearchRequest, tools: BlogTools = Depends(get_blog_tools)):
    try:
        result = tools.search_blogs_tool(request.query, "rag")
        
        if result["status"] == "success":
            # Return blog IDs and relevance scores
            blog_matches = []
            for chunk in result["results"]:
                blog_matches.append({
                    "blog_id": chunk['blog_id'],
                    "blog_title": chunk['blog_title'],
                    "similarity": chunk['similarity'],
                    "text_snippet": chunk['text'][:200] + "..."
                })
            
            return {
                "success": True,
                "query": request.query,
                "matches": blog_matches,
                "total_found": len(blog_matches)
            }
        else:
            return {
                "success": True,
                "query": request.query,
                "matches": [],
                "total_found": 0,
                "message": "No matching blogs found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/create-web-blog")
async def create_web_blog(request: WebBlogRequest, tools: BlogTools = Depends(get_blog_tools)):
    """Create a blog using web search and research"""
    try:
        # Authenticate access key
        auth_result = auth_system.validate_access_key(request.access_key, "create_blog")
        if not auth_result["valid"]:
            raise HTTPException(status_code=401, detail=auth_result["message"])
        
        print(f"🔍 Creating web-researched blog for topic: {request.topic}")
        
        # Use web search to create blog content
        blog_result = await web_search_creator.create_blog_from_web_research(
            topic=request.topic,
            max_sources=request.max_sources
        )
        
        if not blog_result.get("success"):
            return {
                "success": False,
                "error": blog_result.get("error", "Web research failed"),
                "topic": request.topic
            }
        
        # Create blog in database
        create_result = tools.create_blog_tool(
            title=blog_result["title"],
            content=blog_result["content"],
            topic=request.topic
        )
        
        if create_result["status"] == "success":
            return {
                "success": True,
                "message": f"🌐 **Web-Researched Blog Created!**\n\n**Title:** {blog_result['title']}\n\n**Sources:** {blog_result['total_sources']} web sources\n**Quality:** {blog_result['research_quality']}\n**Blog ID:** {create_result['blog_id']}",
                "blog_id": create_result["blog_id"],
                "title": blog_result["title"],
                "topic": request.topic,
                "sources_used": blog_result["total_sources"],
                "research_quality": blog_result["research_quality"],
                "word_count": blog_result["estimated_word_count"],
                "action": "web_blog_created"
            }
        else:
            return {
                "success": False,
                "error": create_result["message"],
                "blog_data": blog_result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating web blog: {str(e)}")

@app.put("/update-blog")
async def update_blog(request: UpdateBlogRequest, tools: BlogTools = Depends(get_blog_tools)):
    """Update an existing blog with authentication"""
    try:
        # Authenticate access key
        auth_result = auth_system.validate_access_key(request.access_key, "update_blog")
        if not auth_result["valid"]:
            raise HTTPException(status_code=401, detail=auth_result["message"])
        
        # Update blog
        update_data = {}
        if request.title:
            update_data["title"] = request.title
        if request.content:
            update_data["content"] = request.content
        if request.topic:
            update_data["topic"] = request.topic
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        # Use blog service to update
        result = tools.blog_service.update_blog(request.blog_id, **update_data)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ Blog {request.blog_id} updated successfully",
                "blog_id": request.blog_id,
                "updated_fields": list(update_data.keys()),
                "action": "blog_updated"
            }
        else:
            raise HTTPException(status_code=404, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating blog: {str(e)}")

@app.delete("/delete-blog")
async def delete_blog(request: DeleteBlogRequest, tools: BlogTools = Depends(get_blog_tools)):
    """Delete a blog with authentication"""
    try:
        # Authenticate access key
        auth_result = auth_system.validate_access_key(request.access_key, "delete_blog")
        if not auth_result["valid"]:
            raise HTTPException(status_code=401, detail=auth_result["message"])
        
        # Delete blog
        result = tools.blog_service.delete_blog(request.blog_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"🗑️ Blog {request.blog_id} deleted successfully",
                "blog_id": request.blog_id,
                "action": "blog_deleted"
            }
        else:
            raise HTTPException(status_code=404, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting blog: {str(e)}")

@app.get("/auth-info/{access_key}")
async def get_auth_info(access_key: str):
    """Get information about access key permissions"""
    try:
        info = auth_system.get_access_key_info(access_key)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/system-stats")
async def get_system_stats(access_key: str = Header(None), tools: BlogTools = Depends(get_blog_tools)):
    """Get comprehensive system statistics"""
    try:
        # Optional authentication for detailed stats
        detailed_access = False
        if access_key:
            auth_result = auth_system.validate_access_key(access_key, "admin_access")
            detailed_access = auth_result.get("valid", False)
        
        # Get blog stats
        blog_stats = tools.get_search_stats_tool()
        
        # Get auth stats if authorized
        auth_stats = {}
        if detailed_access:
            auth_stats = auth_system.get_security_stats()
        
        return {
            "success": True,
            "blog_statistics": blog_stats,
            "authentication_stats": auth_stats if detailed_access else {"message": "Provide access key for detailed auth stats"},
            "system_info": {
                "storage": "ChromaDB + SQLite",
                "embedding_model": "all-MiniLM-L6-v2",
                "features": ["RAG Search", "Web Research", "Personal Context", "Authentication"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)