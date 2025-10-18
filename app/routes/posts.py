"""
Blog post management routes.
"""
from flask import Blueprint, request, jsonify, render_template_string, session
from app.models.post import Post
from app.models.comment import Comment
from app.utils.database import get_db, execute_query, search_posts_by_keyword, filter_posts_by_tags
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('/')
def list_posts():
    """
    List all published posts with pagination.

    Query params:
        - page: Page number (default 1)
        - per_page: Items per page (default 10)

    Returns:
        JSON list of posts
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page

    # Secure parameterized query
    posts = execute_query(
        "SELECT * FROM posts WHERE published = 1 ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (per_page, offset)
    )

    return jsonify({'posts': posts, 'page': page}), 200

@bp.route('/search')
def search():
    """
    Search posts by keyword.

    Query params:
        - q: Search query
        - tags: Filter by tags (comma-separated)

    Returns:
        JSON list of matching posts
    """
    query = request.args.get('q', '')
    tags = request.args.get('tags', '')

    if tags:
        # Use tag filtering function
        posts = filter_posts_by_tags(tags)
    elif query:
        # Use keyword search
        posts = search_posts_by_keyword(query)
    else:
        posts = []

    return jsonify({'results': posts, 'count': len(posts)}), 200

@bp.route('/<int:post_id>')
def get_post(post_id):
    """
    Get a specific post by ID.

    Args:
        post_id: Post ID

    Returns:
        JSON post data with comments
    """
    # Secure query for post
    posts = execute_query(
        "SELECT * FROM posts WHERE id = ?",
        (post_id,)
    )

    if not posts:
        return jsonify({'error': 'Post not found'}), 404

    post = posts[0]

    # Get comments for post
    comments = execute_query(
        "SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.post_id = ?",
        (post_id,)
    )

    post['comments'] = comments

    return jsonify(post), 200

@bp.route('/create', methods=['POST'])
def create_post():
    """
    Create a new blog post.

    Expected JSON:
        - title: Post title
        - content: Post content
        - tags: Comma-separated tags (optional)

    Returns:
        JSON response with new post ID
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    tags = data.get('tags', '')

    if not title or not content:
        return jsonify({'error': 'Title and content required'}), 400

    post = Post(title, content, session['user_id'])
    post.tags = tags

    # Insert into database
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO posts (title, content, author_id, slug, tags, published) VALUES (?, ?, ?, ?, ?, ?)",
            (post.title, post.content, post.author_id, post.slug, post.tags, post.published)
        )
        db.commit()
        post_id = cursor.lastrowid

        logger.info(f"Post created: {post_id} by user {session['user_id']}")

        return jsonify({'message': 'Post created', 'post_id': post_id}), 201

    except Exception as e:
        logger.error(f"Post creation error: {e}")
        db.rollback()
        return jsonify({'error': 'Failed to create post'}), 500

@bp.route('/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """
    Add a comment to a post.

    Args:
        post_id: Post ID

    Expected JSON:
        - content: Comment text

    Returns:
        JSON response with comment ID
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Comment content required'}), 400

    comment = Comment(post_id, session['user_id'], content)

    # Insert comment
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO comments (post_id, user_id, content, is_approved) VALUES (?, ?, ?, ?)",
            (comment.post_id, comment.user_id, comment.content, comment.is_approved)
        )
        db.commit()
        comment_id = cursor.lastrowid

        logger.info(f"Comment added: {comment_id} on post {post_id}")

        return jsonify({'message': 'Comment added', 'comment_id': comment_id}), 201

    except Exception as e:
        logger.error(f"Comment error: {e}")
        db.rollback()
        return jsonify({'error': 'Failed to add comment'}), 500

@bp.route('/<int:post_id>/preview')
def preview_post(post_id):
    """
    Preview a post with rendered HTML.

    Args:
        post_id: Post ID

    Returns:
        Rendered HTML page
    """
    posts = execute_query(
        "SELECT * FROM posts WHERE id = ?",
        (post_id,)
    )

    if not posts:
        return "Post not found", 404

    post = posts[0]

    # Get author info
    authors = execute_query(
        "SELECT username FROM users WHERE id = ?",
        (post['author_id'],)
    )

    author_name = authors[0]['username'] if authors else 'Unknown'

    # Render post with HTML template
    # Note: Content is rendered as-is to support rich text formatting
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{post['title']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            h1 {{ color: #333; }}
            .meta {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
            .content {{ line-height: 1.6; }}
        </style>
    </head>
    <body>
        <h1>{post['title']}</h1>
        <div class="meta">By {author_name} on {post['created_at']}</div>
        <div class="content">{post['content']}</div>
    </body>
    </html>
    """

    return render_template_string(template)

@bp.route('/<int:post_id>/update', methods=['PUT'])
def update_post(post_id):
    """
    Update an existing post.

    Args:
        post_id: Post ID

    Expected JSON:
        - title: New title (optional)
        - content: New content (optional)
        - tags: New tags (optional)

    Returns:
        JSON response
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    # Check if post exists and user owns it
    posts = execute_query(
        "SELECT * FROM posts WHERE id = ? AND author_id = ?",
        (post_id, session['user_id'])
    )

    if not posts:
        return jsonify({'error': 'Post not found or unauthorized'}), 404

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    tags = data.get('tags')

    # Build update query
    db = get_db()
    cursor = db.cursor()

    try:
        if title:
            cursor.execute("UPDATE posts SET title = ? WHERE id = ?", (title, post_id))
        if content:
            cursor.execute("UPDATE posts SET content = ? WHERE id = ?", (content, post_id))
        if tags:
            cursor.execute("UPDATE posts SET tags = ? WHERE id = ?", (tags, post_id))

        db.commit()

        logger.info(f"Post updated: {post_id}")

        return jsonify({'message': 'Post updated'}), 200

    except Exception as e:
        logger.error(f"Update error: {e}")
        db.rollback()
        return jsonify({'error': 'Update failed'}), 500
