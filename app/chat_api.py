from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.blog_service import create_blog_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

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



