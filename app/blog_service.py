from typing import Dict, Optional
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.blog_schema import Blog
from app.config import settings
from app.db_storage import (
    store_blog_with_embedding,
    update_blog_with_embedding
)

# Temporary in-memory blog storage for session management
blog_storage: Dict[str, Blog] = {}

# Session management
session_store = {}
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output"
)

parser = PydanticOutputParser(pydantic_object=Blog)

PROMPT = """
You are an expert content writer who creates simple, easy-to-understand blog posts.
Create a comprehensive yet accessible blog post based on the following topic/prompt.

Generate content that follows this exact JSON structure:
{schema}

Writing Style Requirements:
- Use SIMPLE language that anyone can understand
- Write in a conversational, friendly tone
- Explain technical concepts in plain English
- Use short sentences and paragraphs for better readability
- Include practical examples and real-world applications
- Make content engaging and relatable

Content Structure Requirements:
- Generate a SEO-friendly slug from the title (lowercase, hyphens instead of spaces)
- Write a compelling but simple title and subtitle
- Create an engaging excerpt (2-3 sentences that clearly explain what the reader will learn)
- Find and include a relevant image URL from Unsplash that relates to the topic
- The content field MUST include:
  * introduction: Write a simple, welcoming introduction (2-3 paragraphs) that explains what the topic is about and why it matters
  * sections: Include multiple easy-to-understand sections with varied types:
    - Use "text" sections for explanations with simple examples
    - Use "bullets" sections for easy-to-scan lists of key points
    - Use "code" sections only when absolutely necessary, with clear explanations
    - Each section should have a clear, descriptive title
  * conclusion: Write a practical conclusion (2-3 paragraphs) that summarizes key takeaways and gives actionable next steps
- Add relevant, popular tags that people would search for
- Set appropriate category
- Calculate realistic read time based on content length (typically 200 words per minute)
- Set views=0, likes=0

Image Guidelines:
- Use Unsplash URLs in format: https://images.unsplash.com/photo-[photo-id]?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80
- Choose images that directly relate to the topic
- Prefer images that are visually appealing and professional

CRITICAL:
1. The content field must have ALL THREE required fields: introduction, sections, AND conclusion
2. Keep language simple and avoid jargon
3. Include a relevant Unsplash image
4. Make content practical and actionable

Topic/Prompt: {text}

Return only the JSON response that matches the schema above.
"""

prompt = PromptTemplate(
    template=PROMPT,
    input_variables=["text"],
    partial_variables={"schema": parser.get_format_instructions()}
)

llm = ChatMistralAI(
    model=settings.DEFAULT_MODEL,
    api_key=settings.MISTRAL_API_KEY,
    temperature=settings.TEMPERATURE,
    max_retries=2
)

def get_session_history(session_id: str) -> ChatMessageHistory:
    """Get or create chat message history for a session.

    Args:
        session_id: Unique session identifier

    Returns:
        ChatMessageHistory for the session
    """
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

# Agent prompt template with memory
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant that manages blog operations and remembers our conversation history.

    You have access to the following blog management tools:
    - list_blogs: List all stored blogs
    - create_new_blog: Generate a new blog based on a topic (creates in memory only)
    - update_existing_blog: Update an existing blog with new content
    - show_blog_details: Show detailed information about a specific blog
    - save_blog_to_database: Save a specific blog to MongoDB database with embeddings (requires blog_id)
    - save_latest_blog_to_database: Save the most recently created blog to MongoDB database with embeddings (no blog_id needed)

    IMPORTANT WORKFLOW:
    1. When creating a blog: Use create_new_blog tool (this only creates the blog in memory)
    2. When user wants to save:
       - Use save_blog_to_database tool if you know the specific blog_id
       - Use save_latest_blog_to_database tool to save the most recently created blog
    3. The user has full control over when blogs are saved to the database

    You remember our previous conversations and can reference:
    - Previously created blogs and their IDs
    - User preferences and topics discussed
    - Previous requests and their outcomes

    When users ask you to perform blog operations, use the appropriate tools.

    Examples:
    - "list all blogs" → use list_blogs tool
    - "create a blog about AI" → use create_new_blog tool with topic "AI" (blog will be created but not saved to database)
    - "save my blog" or "save latest blog" → use save_latest_blog_to_database tool
    - "save blog abc123" → use save_blog_to_database tool with specific blog_id
    - "update blog abc123 with topic machine learning" → use update_existing_blog tool
    - "show details of blog xyz789" → use show_blog_details tool
    - "update my last blog" → reference previous conversation to get blog ID

    Always be helpful and provide clear feedback to the user. Use the conversation history to provide context-aware responses."""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

def generate_blog(user_prompt: str) -> Blog:
    """Generate a blog post from a user prompt.

    Args:
        user_prompt: The topic or prompt for blog generation

    Returns:
        Blog: Generated blog object
    """
    chain = prompt | llm | parser
    result = chain.invoke({"text": user_prompt})
    return result

def store_blog_in_memory(blog_data: Blog) -> str:
    """Store blog temporarily in memory for session management.

    Args:
        blog_data: Blog object to store

    Returns:
        str: Blog ID
    """
    blog_storage[blog_data.blog_id] = blog_data
    return blog_data.blog_id

def save_blog_to_database(blog_data: Blog) -> str:
    """Save blog permanently to MongoDB with embeddings.

    Args:
        blog_data: Blog object to save

    Returns:
        str: Blog ID

    Raises:
        Exception: If saving to database fails
    """
    try:
        store_blog_with_embedding(blog_data)
        return blog_data.blog_id
    except Exception as e:
        raise Exception(f"Failed to save blog to database: {str(e)}")

def get_blog_from_memory(blog_id: str) -> Optional[Blog]:
    """Retrieve blog from memory by blog_id.

    Args:
        blog_id: ID of the blog to retrieve

    Returns:
        Blog object if found, None otherwise
    """
    return blog_storage.get(blog_id)

def update_blog_content(blog_id: str, updated_data: Blog) -> Optional[Blog]:
    """Update existing blog in memory and MongoDB.

    Args:
        blog_id: ID of the blog to update
        updated_data: New blog data

    Returns:
        Updated Blog object if successful, None if blog not found

    Raises:
        Exception: If updating in database fails
    """
    if blog_id not in blog_storage:
        return None

    existing_blog = blog_storage[blog_id]
    existing_blog.blog_version += 1

    # Update the blog with new data while preserving ID and incrementing version
    updated_blog_dict = updated_data.model_dump()
    updated_blog_dict['blog_id'] = blog_id
    updated_blog_dict['blog_version'] = existing_blog.blog_version

    updated_blog = Blog(**updated_blog_dict)
    blog_storage[blog_id] = updated_blog

    # Update in MongoDB with new embeddings
    try:
        update_blog_with_embedding(updated_blog)
        return updated_blog
    except Exception as e:
        raise Exception(f"Failed to update blog in database: {str(e)}")

def list_memory_blogs() -> Dict[str, Dict[str, any]]:
    """List all blogs currently in memory.

    Returns:
        Dictionary mapping blog IDs to blog info
    """
    return {
        blog_id: {
            "title": blog.title,
            "version": blog.blog_version,
            "slug": blog.slug
        }
        for blog_id, blog in blog_storage.items()
    }



def create_blog_agent():
    """Create blog management agent with conversation history.

    Returns:
        Agent executor with chat history support
    """
    from app.tools import available_tools

    agent = create_tool_calling_agent(llm, available_tools, agent_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=available_tools,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True
    )

    # Wrap with message history
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return agent_with_chat_history