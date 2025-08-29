from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os
from contextlib import asynccontextmanager

from tools import BlogTools, create_tools_instance
from langchain_mistralai.chat_models import ChatMistralAI

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

async def get_blog_tools() -> BlogTools:
    if blog_tools is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    return blog_tools

@app.post("/chat")
async def chat(request: ChatRequest, tools: BlogTools = Depends(get_blog_tools)):
    try:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)