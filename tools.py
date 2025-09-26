from langchain.tools import tool

@tool
def list_blogs() -> str:
    """List all stored blogs with their IDs, versions, and titles."""
    from ai_service import list_all_blogs

    blogs = list_all_blogs()
    if blogs:
        result = "📚 Stored Blogs:\n"
        for blog_id, info in blogs.items():
            result += f"  🆔 {blog_id[:8]}... | v{info['version']} | {info['title']}\n"
        return result
    else:
        return "📭 No blogs stored yet."

@tool
def create_new_blog(topic: str) -> str:
    """Generate and store a new blog based on the given topic."""
    from ai_service import generate_blog, store_blog

    if not topic.strip():
        return "❌ Please provide a topic for the blog"

    try:
        print(f"🔄 Generating blog for: {topic}")
        blog = generate_blog(topic)
        blog_id = store_blog(blog)
        return f"✅ Blog generated and stored!\n🆔 Blog ID: {blog_id}\n📝 Title: {blog.title}\n🔢 Version: {blog.blog_version}"
    except Exception as e:
        return f"❌ Error generating blog: {str(e)}"

@tool
def update_existing_blog(blog_id: str, new_topic: str) -> str:
    """Update an existing blog with a new topic."""
    from ai_service import get_blog, generate_blog, update_blog

    if not blog_id.strip() or not new_topic.strip():
        return "❌ Please provide both blog_id and new_topic"

    existing_blog = get_blog(blog_id)
    if not existing_blog:
        return f"❌ Blog with ID {blog_id} not found"

    try:
        print(f"🔄 Updating blog: {existing_blog.title}")
        new_blog = generate_blog(new_topic)
        updated_blog = update_blog(blog_id, new_blog)
        if updated_blog:
            return f"✅ Blog updated!\n📝 New Title: {updated_blog.title}\n🔢 New Version: {updated_blog.blog_version}"
        else:
            return "❌ Failed to update blog"
    except Exception as e:
        return f"❌ Error updating blog: {str(e)}"

@tool
def show_blog_details(blog_id: str) -> str:
    """Show detailed information about a specific blog."""
    from ai_service import get_blog

    if not blog_id.strip():
        return "❌ Please provide a blog_id"

    blog = get_blog(blog_id)
    if blog:
        details = f"""📖 Blog Details:
🆔 ID: {blog.blog_id}
📝 Title: {blog.title}
🔢 Version: {blog.blog_version}
🏷️ Slug: {blog.slug}
📅 Published: {blog.publishedDate}
⏱️ Read Time: {blog.readTime}
🏷️ Tags: {', '.join(blog.tags)}
📁 Category: {blog.category}
👀 Views: {blog.views}
❤️ Likes: {blog.likes}
📄 Excerpt: {blog.excerpt}"""
        return details
    else:
        return f"❌ Blog with ID {blog_id} not found"

@tool
def save_blog_to_file(blog_id: str) -> str:
    """Save a blog to a JSON file."""
    from ai_service import get_blog, save_blog_to_json

    if not blog_id.strip():
        return "❌ Please provide a blog_id"

    blog = get_blog(blog_id)
    if blog:
        try:
            filename = save_blog_to_json(blog)
            return f"💾 Blog saved to: {filename}"
        except Exception as e:
            return f"❌ Error saving blog: {str(e)}"
    else:
        return f"❌ Blog with ID {blog_id} not found"

# List of all available tools
available_tools = [
    list_blogs,
    create_new_blog,
    update_existing_blog,
    show_blog_details,
    save_blog_to_file
]