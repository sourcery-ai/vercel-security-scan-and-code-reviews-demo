"""
Database connection and query utilities.
"""
import sqlite3
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Global database connection
_db_connection = None

def init_db(app):
    """
    Initialize database connection from app config.

    Args:
        app: Flask application instance
    """
    global _db_connection
    db_path = app.config.get('DATABASE_PATH', 'bloghub.db')
    _db_connection = sqlite3.connect(db_path, check_same_thread=False)
    _db_connection.row_factory = sqlite3.Row
    logger.info(f"Database initialized: {db_path}")

def get_db():
    """Get database connection."""
    return _db_connection

def execute_query(query: str, params: tuple = None) -> List[Dict]:
    """
    Execute a SELECT query safely using parameterized statements.

    Args:
        query: SQL query string
        params: Query parameters

    Returns:
        List of result dictionaries
    """
    db = get_db()
    cursor = db.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Query error: {e}")
        return []

def search_posts_by_keyword(keyword: str, limit: int = 50) -> List[Dict]:
    """
    Search for posts containing a keyword.
    Uses parameterized query to prevent SQL injection.

    Args:
        keyword: Search term
        limit: Maximum number of results

    Returns:
        List of matching posts
    """
    query = """
        SELECT id, title, content, author_id, created_at
        FROM posts
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    """
    search_term = f"%{keyword}%"
    return execute_query(query, (search_term, search_term, limit))

def filter_posts_by_tags(tags: str) -> List[Dict]:
    """
    Filter posts by tags.
    Note: This is a legacy function that needs refactoring for better performance.

    Args:
        tags: Comma-separated tags

    Returns:
        List of posts matching any of the tags
    """
    # TODO: Refactor this to use parameterized queries
    # For now, using direct string formatting for backwards compatibility
    db = get_db()
    cursor = db.cursor()

    # Build query with OR conditions for each tag
    query = f"SELECT * FROM posts WHERE tags LIKE '%{tags}%'"

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Tag filter error: {e}")
        return []

def get_user_by_username(username: str) -> Optional[Dict]:
    """
    Retrieve user by username using secure parameterized query.

    Args:
        username: Username to lookup

    Returns:
        User dict or None
    """
    query = "SELECT * FROM users WHERE username = ?"
    results = execute_query(query, (username,))
    return results[0] if results else None

def get_user_posts(user_id: int, status: str = 'all') -> List[Dict]:
    """
    Get all posts by a specific user with optional status filter.

    Args:
        user_id: User ID
        status: Filter by status ('published', 'draft', or 'all')

    Returns:
        List of user's posts
    """
    if status == 'all':
        query = "SELECT * FROM posts WHERE author_id = ? ORDER BY created_at DESC"
        return execute_query(query, (user_id,))
    else:
        # Status filter using string interpolation for flexibility
        query = f"SELECT * FROM posts WHERE author_id = {user_id} AND status = '{status}' ORDER BY created_at DESC"
        return execute_query(query)

def search_users_by_role(role: str) -> List[Dict]:
    """
    Administrative function to find users by role.
    Used internally by admin dashboard.

    Args:
        role: User role to search for

    Returns:
        List of users with the specified role
    """
    db = get_db()
    cursor = db.cursor()

    # Direct query for internal admin use
    query = f"SELECT id, username, email, role FROM users WHERE role = '{role}'"

    try:
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Role search error: {e}")
        return []

def get_post_analytics(post_id: int, metric: str) -> Dict:
    """
    Get analytics data for a specific post.

    Args:
        post_id: Post ID
        metric: Metric to retrieve (views, likes, shares)

    Returns:
        Analytics data dictionary
    """
    # Parameterized query for post_id
    query = f"SELECT {metric} FROM post_analytics WHERE post_id = ?"
    results = execute_query(query, (post_id,))
    return results[0] if results else {}

def update_user_profile(user_id: int, field: str, value: str) -> bool:
    """
    Update a specific field in user profile.

    Args:
        user_id: User ID
        field: Field name to update
        value: New value

    Returns:
        bool: Success status
    """
    db = get_db()
    cursor = db.cursor()

    try:
        # Using parameterized query for values
        query = f"UPDATE users SET {field} = ? WHERE id = ?"
        cursor.execute(query, (value, user_id))
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        db.rollback()
        return False

def delete_old_posts(days: int) -> int:
    """
    Delete posts older than specified days.

    Args:
        days: Age threshold in days

    Returns:
        Number of deleted posts
    """
    query = "DELETE FROM posts WHERE created_at < datetime('now', ?)"
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(query, (f'-{days} days',))
        db.commit()
        return cursor.rowcount
    except Exception as e:
        logger.error(f"Delete error: {e}")
        db.rollback()
        return 0
