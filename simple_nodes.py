from langchain_mistralai.chat_models import ChatMistralAI
import json
import os

LLM_API_KEY = "yCVIzpE6wyS0uE6Y48ZFgErfPuv0rDfJ"
llm = ChatMistralAI(model="mistral-small", api_key=LLM_API_KEY)

def load_blogs():
    if os.path.exists("blogs.json"):
        with open("blogs.json", "r") as f:
            return json.load(f)
    return []

def save_blogs(blogs):
    with open("blogs.json", "w") as f:
        json.dump(blogs, f, indent=2)

def general_chat_node(state):
    user_input = state.get("user_input", "")
    
    response = llm.invoke(user_input)
    
    state["response"] = response.content
    state["node_type"] = "general_chat"
    return state

def create_blog_node(state):
    topic = state.get("current_topic", "")
    
    if not topic:
        state["response"] = "❌ No topic found to create blog"
        return state
    
    title_prompt = f"Generate a catchy blog title about: {topic}"
    content_prompt = f"Write a detailed blog post about: {topic}. Make it informative and engaging."
    
    title_response = llm.invoke(title_prompt)
    content_response = llm.invoke(content_prompt)
    
    blog_data = {
        "title": title_response.content,
        "content": content_response.content,
        "topic": topic,
        "created_at": "now"
    }
    
    state["current_blog"] = blog_data
    state["response"] = f"📝 Blog Created!\n\nTitle: {blog_data['title']}\n\nContent: {blog_data['content']}\n\nSay 'save this' to save the blog!"
    state["node_type"] = "blog_created"
    return state

def save_blog_node(state):
    if not state.get("is_authenticated", False):
        state["response"] = "🔒 Permission denied! You need authentication to save blogs. Share your access key."
        state["node_type"] = "auth_required"
        return state
    
    blog_data = state.get("current_blog", {})
    if not blog_data:
        state["response"] = "❌ No blog to save. Create a blog first!"
        return state
    
    blogs = load_blogs()
    blogs.append(blog_data)
    save_blogs(blogs)
    
    state["response"] = "✅ Blog saved successfully!"
    state["current_blog"] = None
    state["node_type"] = "blog_saved"
    return state

def authentication_node(state):
    user_input = state.get("user_input", "").lower()
    access_key = "123"
    
    if access_key in user_input:
        state["is_authenticated"] = True
        state["response"] = "✅ Authentication successful! You can now save blogs."
        state["node_type"] = "authenticated"
        
        if state.get("current_blog"):
            return save_blog_node(state)
    else:
        state["is_authenticated"] = False
        state["response"] = "❌ Invalid access key! Please provide the correct key."
        state["node_type"] = "auth_failed"
    
    return state

def blog_query_node(state):
    query = state.get("user_input", "")
    blogs = load_blogs()
    
    if not blogs:
        state["response"] = "📭 No blogs found. Create some blogs first!"
        state["node_type"] = "no_blogs"
        return state
    
    for blog in blogs:
        if query.lower() in blog.get("title", "").lower() or query.lower() in blog.get("content", "").lower():
            state["response"] = f"📖 Found Blog:\n\nTitle: {blog['title']}\n\nContent: {blog['content']}"
            state["node_type"] = "blog_found"
            return state
    
    state["response"] = f"🔍 No blog found about '{query}'. Would you like me to create one?"
    state["node_type"] = "blog_not_found"
    return state