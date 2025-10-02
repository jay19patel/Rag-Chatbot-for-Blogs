from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.blog_service import create_blog_agent
from app.db_storage import search_blogs, list_all_stored_blogs, get_available_categories

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class CategoryInfo(BaseModel):
    name: str
    count: int

class BlogsResponse(BaseModel):
    blogs: List[Dict[str, Any]]
    total_count: int
    list_total: int
    limit: int
    query: Optional[str] = None
    category_filter: Optional[str] = None
    available_categories: List[CategoryInfo]

class BlogResponse(BaseModel):
    blog: Optional[Dict[str, Any]]
    message: str

class LikeResponse(BaseModel):
    success: bool
    message: str
    total_likes: Optional[int] = None

class CategoriesResponse(BaseModel):
    categories: List[str]
    total_count: int

# Initialize the agent
blog_agent = create_blog_agent()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for processing messages using the AI agent.
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Process the message using the agent with memory
        response = blog_agent.invoke(
            {"input": request.message},
            config={"configurable": {"session_id": request.session_id}}
        )

        return ChatResponse(
            response=response["output"],
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/blogs", response_model=BlogsResponse)
async def blogs_endpoint(
    search: Optional[str] = Query(None, description="Search query for blogs (optional)"),
    category: Optional[str] = Query(None, description="Filter blogs by category (optional)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of blogs to return")
):
    """
    List all blogs or search blogs based on query parameter, optionally filtered by category.
    Always includes available categories in the response.
    
    - If 'search' parameter is provided and not empty: performs vector similarity search
    - If 'search' parameter is empty/null/not provided: lists all blogs
    - If 'category' parameter is provided: filters blogs by category (case insensitive)
    - Always includes list of all available categories in response
    
    Args:
        search: Optional search query string
        category: Optional category filter (e.g., "tech", "business")
        limit: Maximum number of results (1-100)
        
    Returns:
        BlogsResponse with blogs, total count, available categories, and metadata
    """
    try:
        # Always get available categories with counts
        categories_data = get_available_categories()
        available_categories = [CategoryInfo(name=cat["name"], count=cat["count"]) for cat in categories_data]
        
        # Check if search parameter is provided and not empty
        if search and search.strip():
            # Perform vector search (category filtering not supported in vector search yet)
            result = search_blogs(search.strip(), limit)
            result["available_categories"] = available_categories
            return BlogsResponse(**result)
        else:
            # List all blogs with optional category filter
            result = list_all_stored_blogs(limit, category)
            result["available_categories"] = available_categories
            return BlogsResponse(**result)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blogs request: {str(e)}")

@router.get("/blogs/{slug}", response_model=BlogResponse)
async def get_blog_by_slug_endpoint(slug: str):
    """
    Get a blog by its slug and automatically increment view count.

    Args:
        slug: The blog slug to retrieve

    Returns:
        BlogResponse with full blog data or error message
    """
    try:
        from app.db_storage import get_blog_by_slug

        blog = get_blog_by_slug(slug)

        if blog:
            return BlogResponse(
                blog=blog,
                message="Blog retrieved successfully"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Blog with slug '{slug}' not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving blog: {str(e)}")

@router.post("/blogs/{slug}/like", response_model=LikeResponse)
async def like_blog_endpoint(slug: str):
    """
    Increment likes for a blog by its slug.

    Args:
        slug: The blog slug to like

    Returns:
        LikeResponse with success status and updated like count
    """
    try:
        from app.db_storage import increment_blog_likes, get_blog_by_slug_readonly

        # First check if blog exists (without incrementing views)
        blog = get_blog_by_slug_readonly(slug)
        if not blog:
            raise HTTPException(
                status_code=404,
                detail=f"Blog with slug '{slug}' not found"
            )

        # Increment likes and get updated blog
        updated_blog = increment_blog_likes(slug)

        if updated_blog:
            total_likes = updated_blog.get('likes', 0)

            return LikeResponse(
                success=True,
                message="Blog liked successfully! ❤️",
                total_likes=total_likes
            )
        else:
            return LikeResponse(
                success=False,
                message="Failed to like blog"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error liking blog: {str(e)}")

