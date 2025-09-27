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
import json
from typing import Dict

# In-memory blog storage
blog_storage: Dict[str, Blog] = {}

# LangChain memory for conversation history
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output"
)

# Session store for message history
session_store = {}

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

# Function to get session history
def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

# Agent prompt template with memory
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant that manages blog operations and remembers our conversation history.

    You have access to the following blog management tools:
    - list_blogs: List all stored blogs
    - create_new_blog: Generate and store a new blog based on a topic
    - update_existing_blog: Update an existing blog with new content
    - show_blog_details: Show detailed information about a specific blog
    - save_blog_to_file: Save a blog to a JSON file

    You remember our previous conversations and can reference:
    - Previously created blogs and their IDs
    - User preferences and topics discussed
    - Previous requests and their outcomes

    When users ask you to perform blog operations, use the appropriate tools.

    Examples:
    - "list all blogs" → use list_blogs tool
    - "create a blog about AI" → use create_new_blog tool with topic "AI"
    - "update blog abc123 with topic machine learning" → use update_existing_blog tool
    - "show details of blog xyz789" → use show_blog_details tool
    - "save blog def456 to file" → use save_blog_to_file tool
    - "update my last blog" → reference previous conversation to get blog ID

    Always be helpful and provide clear feedback to the user. Use the conversation history to provide context-aware responses."""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

def generate_blog(user_prompt):
    chain = prompt | llm | parser
    result = chain.invoke({"text": user_prompt})
    return result

def store_blog(blog_data):
    """Store blog in memory and return the blog_id"""
    blog_storage[blog_data.blog_id] = blog_data
    return blog_data.blog_id

def get_blog(blog_id):
    """Retrieve blog from memory by blog_id"""
    return blog_storage.get(blog_id)

def update_blog(blog_id, updated_data):
    """Update existing blog and increment version"""
    if blog_id in blog_storage:
        existing_blog = blog_storage[blog_id]
        existing_blog.blog_version += 1

        # Update the blog with new data while keeping the same blog_id and incrementing version
        updated_blog_dict = updated_data.model_dump()
        updated_blog_dict['blog_id'] = blog_id
        updated_blog_dict['blog_version'] = existing_blog.blog_version

        updated_blog = Blog(**updated_blog_dict)
        blog_storage[blog_id] = updated_blog
        return updated_blog
    return None

def list_all_blogs():
    """List all stored blogs with their IDs and versions"""
    return {blog_id: {"title": blog.title, "version": blog.blog_version, "slug": blog.slug}
            for blog_id, blog in blog_storage.items()}

def save_blog_to_json(blog_data, filename=None):
    if filename is None:
        filename = f"blog_{blog_data.slug}_v{blog_data.blog_version}.json"

    # Use mode='json' to serialize HttpUrl and other custom types properly
    blog_dict = blog_data.model_dump(mode='json')

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(blog_dict, f, indent=2, ensure_ascii=False)

    return filename

# Create agent with memory
def create_blog_agent():
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