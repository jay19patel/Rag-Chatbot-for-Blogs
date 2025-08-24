from simple_nodes import (
    general_chat_node, 
    create_blog_node, 
    save_blog_node, 
    authentication_node, 
    blog_query_node
)

class SimpleState(dict):
    pass

def smart_router(state):
    user_input = state.get("user_input", "").lower().strip()
    
    # Check for blog creation request
    create_keywords = ["create blog", "make blog", "write blog", "blog about", "need to create blog"]
    if any(keyword in user_input for keyword in create_keywords):
        # Extract topic
        topic = user_input.replace("create blog", "").replace("make blog", "").replace("write blog", "").replace("blog about", "").replace("need to create blog", "").strip()
        if "for this topic" in topic:
            topic = state.get("last_response_topic", "general topic")
        state["current_topic"] = topic if topic else "general topic"
        return create_blog_node(state)
    
    # Check for save request
    save_keywords = ["save this", "save blog", "save it"]
    if any(keyword in user_input for keyword in save_keywords):
        return save_blog_node(state)
    
    # Check for authentication
    if "123" in user_input or "access key" in user_input:
        return authentication_node(state)
    
    # Check for blog query
    blog_keywords = ["explain", "tell me about", "what is", "about"]
    if any(keyword in user_input for keyword in blog_keywords) and len(user_input.split()) > 2:
        # First try to find in blogs
        result = blog_query_node(state)
        if result.get("node_type") == "blog_found":
            return result
        # If not found in blogs, answer generally but offer to create blog
        general_result = general_chat_node(state)
        state["last_response_topic"] = user_input.replace("explain", "").replace("tell me about", "").replace("what is", "").replace("about", "").strip()
        general_result["response"] += "\n\n💡 Would you like me to create a blog about this topic?"
        return general_result
    
    # Default to general chat
    return general_chat_node(state)

def run_chat():
    print("🤖 Simple AI Chatbot with Blog System")
    print("="*40)
    print("💬 Just chat naturally!")
    print("✨ Ask me to explain topics, create blogs, or save them!")
    print("🔑 Access key: 123 (for saving blogs)")
    print("="*40)
    
    state = SimpleState()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            state["user_input"] = user_input
            result_state = smart_router(state)
            
            print(f"\n🤖 AI: {result_state['response']}")
            
            # Update state for next iteration
            state.update(result_state)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_chat()