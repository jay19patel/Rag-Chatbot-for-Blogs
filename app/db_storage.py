from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

from app.db import vector_store, collection
from app.blog_schema import Blog

logger = logging.getLogger(__name__)

def create_embedding_text(blog: Blog) -> str:
    """Create comprehensive text representation for embedding.

    Combines all blog content into a single text for vector search.

    Args:
        blog: Blog object to create embedding text for

    Returns:
        Combined text string for embedding
    """
    embedding_parts = []

    # Add title and subtitle
    embedding_parts.append(f"Title: {blog.title}")
    if blog.subtitle:
        embedding_parts.append(f"Subtitle: {blog.subtitle}")

    # Add excerpt
    embedding_parts.append(f"Excerpt: {blog.excerpt}")

    # Add introduction
    embedding_parts.append(f"Introduction: {blog.content.introduction}")

    # Add all section content
    for section in blog.content.sections:
        if section.type == "text":
            embedding_parts.append(f"Section - {section.title}: {section.content}")
        elif section.type == "bullets":
            bullets_text = " ".join(section.items)
            embedding_parts.append(f"Section - {section.title}: {bullets_text}")
        elif section.type == "code":
            embedding_parts.append(f"Code Section - {section.title}: {section.content}")
        elif section.type == "note":
            embedding_parts.append(f"Note - {section.title}: {section.content}")
        elif section.type == "table":
            table_text = " ".join([" ".join(row) for row in section.rows])
            embedding_parts.append(f"Table - {section.title}: {table_text}")
        elif section.type == "links":
            links_text = " ".join([f"{link.text}: {link.description or ''}" for link in section.links])
            embedding_parts.append(f"Links - {section.title}: {links_text}")

    # Add conclusion
    embedding_parts.append(f"Conclusion: {blog.content.conclusion}")

    # Add tags
    if blog.tags:
        embedding_parts.append(f"Tags: {', '.join(blog.tags)}")

    # Add category
    embedding_parts.append(f"Category: {blog.category}")

    return " | ".join(embedding_parts)

def store_blog_with_embedding(blog: Blog) -> str:
    """Store blog in MongoDB with vector embeddings.

    Args:
        blog: Blog object to store

    Returns:
        MongoDB _id of stored blog

    Raises:
        Exception: If storage fails
    """
    try:
        # Create embedding text
        embedding_text = create_embedding_text(blog)

        # Convert blog to dict for storage
        blog_dict = blog.model_dump(mode='json')

        # Add metadata for better organization
        blog_dict.update({
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
            'document_type': 'blog'
        })

        # Insert into MongoDB first to get _id
        result = collection.insert_one(blog_dict)
        blog_id = str(result.inserted_id)

        # Store in vector store with MongoDB _id
        vector_store.add_texts(
            texts=[embedding_text],
            metadatas=[blog_dict],
            ids=[blog_id]
        )

        logger.info(f"Successfully stored blog {blog_id} with embeddings")
        return blog_id

    except Exception as e:
        logger.error(f"Error storing blog: {str(e)}")
        raise

def update_blog_with_embedding(blog_id: str, blog: Blog) -> str:
    """Update existing blog with new embeddings.

    Args:
        blog_id: MongoDB _id of the blog to update
        blog: Updated Blog object

    Returns:
        MongoDB _id of updated blog

    Raises:
        Exception: If update fails
    """
    try:
        from bson.objectid import ObjectId

        # First, delete the existing document
        collection.delete_one({"_id": ObjectId(blog_id)})

        # Then store the updated version
        return store_blog_with_embedding(blog)

    except Exception as e:
        logger.error(f"Error updating blog {blog_id}: {str(e)}")
        raise

def search_blogs(query: str, limit: int = 5) -> Dict:
    """Search blogs using vector similarity.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        Dictionary with search results and metadata

    Raises:
        Exception: If search fails
    """
    try:
        # Get total count of all blogs
        total_count = get_total_blogs_count()
        
        # Perform similarity search
        results = vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=limit
        )

        # Format results
        formatted_results = []
        for doc, score in results:
            blog_data = doc.metadata
            formatted_results.append({
                '_id': blog_data.get('_id'),
                'title': blog_data.get('title'),
                'excerpt': blog_data.get('excerpt'),
                'category': blog_data.get('category'),
                'tags': blog_data.get('tags'),
                'relevance_score': score,
                'image': blog_data.get('image'),
                "slug": blog_data.get('slug'),
                'date': blog_data.get('publishedDate'),
                'views': blog_data.get('views'),
                'likes': blog_data.get('likes'),
            })

        return {
            "blogs": formatted_results,
            "total_count": total_count,
            "list_total": len(formatted_results),
            "limit": limit,
            "query": query
        }

    except Exception as e:
        logger.error(f"Error searching blogs: {str(e)}")
        raise

def get_blog_by_id(blog_id: str) -> Optional[Dict]:
    """Retrieve blog by MongoDB _id.

    Args:
        blog_id: MongoDB _id to search for

    Returns:
        Blog data if found, None otherwise

    Raises:
        Exception: If retrieval fails
    """
    try:
        from bson.objectid import ObjectId

        result = collection.find_one({"_id": ObjectId(blog_id)})
        if result:
            # Convert ObjectId to string
            result['_id'] = str(result['_id'])
        return result

    except Exception as e:
        logger.error(f"Error retrieving blog {blog_id}: {str(e)}")
        raise

def get_total_blogs_count() -> int:
    """Get total count of all blogs in database.

    Returns:
        Total number of blogs

    Raises:
        Exception: If count fails
    """
    try:
        return collection.count_documents({"document_type": "blog"})
    except Exception as e:
        logger.error(f"Error counting blogs: {str(e)}")
        raise

def list_all_stored_blogs(limit: int = 50, category: Optional[str] = None) -> Dict:
    """List all stored blogs with total count, optionally filtered by category.

    Args:
        limit: Maximum number of blogs to return
        category: Optional category filter

    Returns:
        Dictionary with blogs list and total count

    Raises:
        Exception: If listing fails
    """
    try:
        # Build query filter
        query_filter = {"document_type": "blog"}
        if category:
            query_filter["category"] = {"$regex": f"^{category}$", "$options": "i"}  # Case insensitive match
        
        # Get total count with filter
        total_count = collection.count_documents(query_filter)
        
        cursor = collection.find(
            query_filter,
            {
                "_id": 1,
                "slug": 1,
                "publishedDate": 1,
                "views": 1,
                "likes": 1,
                "title": 1,
                "excerpt": 1,
                "image": 1,
                "category": 1,
                "tags": 1,
                "blog_version": 1,
                "publishedDate": 1
            }
        ).limit(limit).sort("created_at", -1)

        blogs = []
        for blog in cursor:
            blog['_id'] = str(blog['_id'])
            blogs.append(blog)

        return {
            "blogs": blogs,
            "total_count": total_count,
            "list_total": len(blogs),
            "limit": limit,
            "category_filter": category
        }

    except Exception as e:
        logger.error(f"Error listing blogs: {str(e)}")
        raise

def get_blog_by_slug(slug: str) -> Optional[Dict]:
    """Retrieve blog by slug and increment views.

    Args:
        slug: Blog slug to search for

    Returns:
        Blog data if found, None otherwise

    Raises:
        Exception: If retrieval fails
    """
    try:
        # Find and increment views in one operation
        result = collection.find_one_and_update(
            {"slug": slug, "document_type": "blog"},
            {"$inc": {"views": 1}},
            return_document=True
        )

        if result:
            # Convert ObjectId to string
            result['_id'] = str(result['_id'])

        return result

    except Exception as e:
        logger.error(f"Error retrieving blog by slug {slug}: {str(e)}")
        raise

def increment_blog_likes(slug: str) -> Optional[Dict]:
    """Increment likes count for blog.

    Args:
        slug: Blog slug

    Returns:
        Updated blog data if successful, None if not found

    Raises:
        Exception: If update fails
    """
    try:
        result = collection.find_one_and_update(
            {"slug": slug, "document_type": "blog"},
            {"$inc": {"likes": 1}},
            return_document=True
        )

        if result:
            # Convert ObjectId to string
            result['_id'] = str(result['_id'])

        return result

    except Exception as e:
        logger.error(f"Error incrementing likes for blog {slug}: {str(e)}")
        raise

def get_blog_by_slug_readonly(slug: str) -> Optional[Dict]:
    """Retrieve blog by slug without incrementing views.

    Args:
        slug: Blog slug to search for

    Returns:
        Blog data if found, None otherwise

    Raises:
        Exception: If retrieval fails
    """
    try:
        result = collection.find_one(
            {"slug": slug, "document_type": "blog"}
        )

        if result:
            # Convert ObjectId to string
            result['_id'] = str(result['_id'])

        return result

    except Exception as e:
        logger.error(f"Error retrieving blog by slug {slug}: {str(e)}")
        raise

def delete_blog(blog_id: str) -> bool:
    """Delete blog from MongoDB.

    Args:
        blog_id: MongoDB _id to delete

    Returns:
        True if deleted successfully, False otherwise

    Raises:
        Exception: If deletion fails
    """
    try:
        from bson.objectid import ObjectId

        result = collection.delete_one({"_id": ObjectId(blog_id)})
        return result.deleted_count > 0

    except Exception as e:
        logger.error(f"Error deleting blog {blog_id}: {str(e)}")
        raise

def get_available_categories() -> List[Dict[str, Any]]:
    """Get all available categories from stored blogs with blog counts.

    Returns:
        List of dictionaries with category name and count

    Raises:
        Exception: If retrieval fails
    """
    try:
        pipeline = [
            {"$match": {"document_type": "blog"}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        result = collection.aggregate(pipeline)
        categories = []
        for doc in result:
            if doc["_id"]:  # Skip null/empty categories
                categories.append({
                    "name": doc["_id"],
                    "count": doc["count"]
                })
        
        return categories

    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise

def get_available_categories_simple() -> List[str]:
    """Get all available categories from stored blogs (simple list).

    Returns:
        List of unique category names

    Raises:
        Exception: If retrieval fails
    """
    try:
        categories_with_count = get_available_categories()
        return [cat["name"] for cat in categories_with_count]

    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise

def bulk_store_blogs(blogs: List[Blog]) -> int:
    """Store multiple blogs in MongoDB with embeddings.

    Args:
        blogs: List of Blog objects to store

    Returns:
        Number of blogs successfully stored
    """
    stored_count = 0

    for blog in blogs:
        try:
            store_blog_with_embedding(blog)
            stored_count += 1
            logger.info(f"Stored blog: {blog.title}")
        except Exception as e:
            logger.error(f"Failed to store blog {blog.blog_id}: {str(e)}")

    logger.info(f"Bulk storage complete. Stored {stored_count} out of {len(blogs)} blogs.")
    return stored_count