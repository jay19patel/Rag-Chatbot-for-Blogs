from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.blog_service import create_blog_agent
from app.db_storage import search_blogs, list_all_stored_blogs

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class SearchBlogsResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int

class ListBlogsResponse(BaseModel):
    blogs: List[Dict[str, Any]]
    total_count: int
    limit: int

class BlogResponse(BaseModel):
    blog: Optional[Dict[str, Any]]
    message: str

class LikeResponse(BaseModel):
    success: bool
    message: str
    total_likes: Optional[int] = None

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

@router.get("/blogs/search", response_model=SearchBlogsResponse)
async def search_blogs_endpoint(
    q: str = Query(..., description="Search query for blogs"),
    limit: int = Query(5, ge=1, le=50, description="Maximum number of results to return")
):
    """
    Search blogs using vector similarity search.

    Args:
        q: Search query string
        limit: Maximum number of results (1-50)

    Returns:
        SearchBlogsResponse with matching blogs and relevance scores
    """
    try:
        if not q.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")

        # Perform vector search
        results = search_blogs(q, limit)

        return SearchBlogsResponse(
            results=results,
            query=q,
            total_results=len(results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching blogs: {str(e)}")

@router.get("/blogs", response_model=ListBlogsResponse)
async def list_blogs_endpoint(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of blogs to return")
):
    """
    List all stored blogs from MongoDB.

    Args:
        limit: Maximum number of blogs to return (1-100)

    Returns:
        ListBlogsResponse with blog summaries
    """
    try:
        # Get all blogs from MongoDB
        blogs = list_all_stored_blogs(limit)

        return ListBlogsResponse(
            blogs=blogs,
            total_count=len(blogs),
            limit=limit
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing blogs: {str(e)}")

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
        from app.db_storage import increment_blog_likes, get_blog_by_slug_without_view_increment

        # First check if blog exists (without incrementing views)
        blog = get_blog_by_slug_without_view_increment(slug)
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

