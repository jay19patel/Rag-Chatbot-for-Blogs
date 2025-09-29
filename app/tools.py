from langchain.tools import tool

@tool
def list_blogs() -> str:
    """List all stored blogs with their IDs, versions, and titles."""
    from app.blog_service import list_memory_blogs

    blogs = list_memory_blogs()
    if blogs:
        result = "📚 Stored Blogs:\n"
        for blog_id, info in blogs.items():
            result += f"  🆔 {blog_id[:8]}... | v{info['version']} | {info['title']}\n"
        return result
    else:
        return "📭 No blogs stored yet."

@tool
def create_new_blog(topic: str) -> str:
    """Generate a new blog based on the given topic (stores in memory only)."""
    from app.blog_service import generate_blog, store_blog_in_memory

    if not topic.strip():
        return "❌ Please provide a topic for the blog"

    try:
        blog = generate_blog(topic)
        blog_id = store_blog_in_memory(blog)
        return f"✅ Blog generated successfully!\n🆔 Blog ID: {blog_id}\n📝 Title: {blog.title}\n🔢 Version: {blog.blog_version}\n\n⚠️ Blog is created but not yet saved to database. Use save_blog_to_database tool to save it permanently."
    except Exception as e:
        return f"❌ Error generating blog: {str(e)}"

@tool
def update_existing_blog(blog_id: str, new_topic: str) -> str:
    """Update an existing blog with a new topic."""
    from app.blog_service import get_blog_from_memory, generate_blog, update_blog_content

    if not blog_id.strip() or not new_topic.strip():
        return "❌ Please provide both blog_id and new_topic"

    existing_blog = get_blog_from_memory(blog_id)
    if not existing_blog:
        return f"❌ Blog with ID {blog_id} not found"

    try:
        new_blog = generate_blog(new_topic)
        updated_blog = update_blog_content(blog_id, new_blog)
        if updated_blog:
            return f"✅ Blog updated!\n📝 New Title: {updated_blog.title}\n🔢 New Version: {updated_blog.blog_version}"
        else:
            return "❌ Failed to update blog"
    except Exception as e:
        return f"❌ Error updating blog: {str(e)}"

@tool
def show_blog_details(blog_id: str) -> str:
    """Show detailed information about a specific blog."""
    from app.blog_service import get_blog_from_memory

    if not blog_id.strip():
        return "❌ Please provide a blog_id"

    blog = get_blog_from_memory(blog_id)
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
def save_blog_to_database(blog_id: str) -> str:
    """Save a blog to MongoDB database with embeddings."""
    from app.blog_service import get_blog_from_memory, save_blog_to_database

    # Validate blog_id
    if blog_id is None:
        return "❌ Please provide a blog_id. No blog_id was provided."

    if not isinstance(blog_id, str):
        return f"❌ Invalid blog_id format. Expected string, got {type(blog_id).__name__}"

    if not blog_id.strip():
        return "❌ Please provide a valid blog_id. Empty string provided."

    blog = get_blog_from_memory(blog_id.strip())
    if blog:
        try:
            save_blog_to_database(blog)
            return f"💾 Blog saved to database successfully!\n🆔 Blog ID: {blog_id.strip()}\n📝 Title: {blog.title}\n🔍 Embeddings created for search functionality"
        except Exception as e:
            return f"❌ Error saving blog to database: {str(e)}"
    else:
        return f"❌ Blog with ID '{blog_id.strip()}' not found in memory. Make sure to create the blog first using create_new_blog tool."

@tool
def save_latest_blog_to_database() -> str:
    """Save the most recently created blog to MongoDB database with embeddings."""
    from app.blog_service import blog_storage, save_blog_to_database

    if not blog_storage:
        return "❌ No blogs found in memory. Please create a blog first using create_new_blog tool."

    # Get the most recent blog (last added to storage)
    latest_blog_id = list(blog_storage.keys())[-1]
    latest_blog = blog_storage[latest_blog_id]

    try:
        save_blog_to_database(latest_blog)
        return f"💾 Latest blog saved to database successfully!\n🆔 Blog ID: {latest_blog_id}\n📝 Title: {latest_blog.title}\n🔍 Embeddings created for search functionality"
    except Exception as e:
        return f"❌ Error saving latest blog to database: {str(e)}"

# Available tools for the blog agent
available_tools = [
    list_blogs,
    create_new_blog,
    update_existing_blog,
    show_blog_details,
    save_blog_to_database,
    save_latest_blog_to_database
]