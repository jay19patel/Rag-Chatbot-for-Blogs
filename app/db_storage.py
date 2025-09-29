from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.db import vector_store, collection
from app.blog_schema import Blog
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_embedding_text(blog: Blog) -> str:
    """
    Create a comprehensive text representation of the blog for embedding.
    This combines title, subtitle, excerpt, content, and tags for better search.
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
    """
    Store a blog in MongoDB with proper embedding for vector search.

    Args:
        blog: Blog object to store

    Returns:
        str: The blog_id of the stored blog
    """
    try:
        # Create embedding text
        embedding_text = create_embedding_text(blog)

        # Convert blog to dict for storage
        blog_dict = blog.model_dump(mode='json')

        # Add metadata for better organization
        blog_dict.update({
            'embedding_text': embedding_text,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
            'document_type': 'blog'
        })

        # Store in vector store (this will automatically create embeddings)
        vector_store.add_texts(
            texts=[embedding_text],
            metadatas=[blog_dict],
            ids=[blog.blog_id]
        )

        logger.info(f"Successfully stored blog {blog.blog_id} with embeddings")
        return blog.blog_id

    except Exception as e:
        logger.error(f"Error storing blog {blog.blog_id}: {str(e)}")
        raise

def update_blog_with_embedding(blog: Blog) -> str:
    """
    Update an existing blog in MongoDB with new embeddings.

    Args:
        blog: Updated Blog object

    Returns:
        str: The blog_id of the updated blog
    """
    try:
        # First, delete the existing document
        collection.delete_one({"blog_id": blog.blog_id})

        # Then store the updated version
        return store_blog_with_embedding(blog)

    except Exception as e:
        logger.error(f"Error updating blog {blog.blog_id}: {str(e)}")
        raise

def search_blogs(query: str, limit: int = 5) -> List[Dict]:
    """
    Search blogs using vector similarity search.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        List[Dict]: List of matching blog documents with similarity scores
    """
    try:
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
                'blog_id': blog_data.get('blog_id'),
                'title': blog_data.get('title'),
                'excerpt': blog_data.get('excerpt'),
                'category': blog_data.get('category'),
                'tags': blog_data.get('tags'),
                'relevance_score': score,
                'full_data': blog_data
            })

        return formatted_results

    except Exception as e:
        logger.error(f"Error searching blogs: {str(e)}")
        raise

def get_blog_by_id(blog_id: str) -> Optional[Dict]:
    """
    Retrieve a specific blog by its ID.

    Args:
        blog_id: The blog ID to search for

    Returns:
        Optional[Dict]: Blog data if found, None otherwise
    """
    try:
        result = collection.find_one({"blog_id": blog_id})
        if result:
            # Remove MongoDB's _id field for cleaner response
            result.pop('_id', None)
        return result

    except Exception as e:
        logger.error(f"Error retrieving blog {blog_id}: {str(e)}")
        raise

def list_all_stored_blogs(limit: int = 50) -> List[Dict]:
    """
    List all blogs stored in MongoDB.

    Args:
        limit: Maximum number of blogs to return

    Returns:
        List[Dict]: List of blog summaries
    """
    try:
        cursor = collection.find(
            {"document_type": "blog"},
            {
                "blog_id": 1,
                "title": 1,
                "excerpt": 1,
                "category": 1,
                "tags": 1,
                "blog_version": 1,
                "created_at": 1,
                "_id": 0
            }
        ).limit(limit).sort("created_at", -1)

        return list(cursor)

    except Exception as e:
        logger.error(f"Error listing blogs: {str(e)}")
        raise

def get_blog_by_slug(slug: str) -> Optional[Dict]:
    """
    Retrieve a blog by its slug and increment view count.

    Args:
        slug: The blog slug to search for

    Returns:
        Optional[Dict]: Blog data if found, None otherwise
    """
    try:
        # Find and increment views in one operation
        result = collection.find_one_and_update(
            {"slug": slug, "document_type": "blog"},
            {"$inc": {"views": 1}},
            return_document=True
        )

        if result:
            # Remove MongoDB's _id field for cleaner response
            result.pop('_id', None)

        return result

    except Exception as e:
        logger.error(f"Error retrieving blog by slug {slug}: {str(e)}")
        raise

def increment_blog_likes(slug: str) -> Optional[Dict]:
    """
    Increment the likes count for a blog by slug and return updated blog.

    Args:
        slug: The blog slug

    Returns:
        Optional[Dict]: Updated blog data if successful, None if blog not found
    """
    try:
        result = collection.find_one_and_update(
            {"slug": slug, "document_type": "blog"},
            {"$inc": {"likes": 1}},
            return_document=True
        )

        if result:
            # Remove MongoDB's _id field for cleaner response
            result.pop('_id', None)

        return result

    except Exception as e:
        logger.error(f"Error incrementing likes for blog {slug}: {str(e)}")
        raise

def get_blog_by_slug_without_view_increment(slug: str) -> Optional[Dict]:
    """
    Retrieve a blog by its slug WITHOUT incrementing view count.

    Args:
        slug: The blog slug to search for

    Returns:
        Optional[Dict]: Blog data if found, None otherwise
    """
    try:
        result = collection.find_one(
            {"slug": slug, "document_type": "blog"}
        )

        if result:
            # Remove MongoDB's _id field for cleaner response
            result.pop('_id', None)

        return result

    except Exception as e:
        logger.error(f"Error retrieving blog by slug {slug}: {str(e)}")
        raise

def delete_blog(blog_id: str) -> bool:
    """
    Delete a blog from MongoDB.

    Args:
        blog_id: The blog ID to delete

    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        result = collection.delete_one({"blog_id": blog_id})
        return result.deleted_count > 0

    except Exception as e:
        logger.error(f"Error deleting blog {blog_id}: {str(e)}")
        raise

# Migration function to move existing in-memory blogs to MongoDB
def migrate_memory_to_mongodb(blog_storage: Dict[str, Blog]) -> int:
    """
    Migrate existing in-memory blog storage to MongoDB with embeddings.

    Args:
        blog_storage: Dictionary of blog_id -> Blog objects

    Returns:
        int: Number of blogs successfully migrated
    """
    migrated_count = 0

    for blog_id, blog in blog_storage.items():
        try:
            store_blog_with_embedding(blog)
            migrated_count += 1
            logger.info(f"Migrated blog: {blog.title}")
        except Exception as e:
            logger.error(f"Failed to migrate blog {blog_id}: {str(e)}")

    logger.info(f"Migration complete. Migrated {migrated_count} out of {len(blog_storage)} blogs.")
    return migrated_count