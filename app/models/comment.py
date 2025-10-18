"""
Comment model for blog posts.
"""
from datetime import datetime

class Comment:
    """
    Comment model for user comments on blog posts.

    Attributes:
        id: Unique comment identifier
        post_id: ID of the post this comment belongs to
        user_id: ID of the user who created the comment
        content: Comment text
        created_at: Comment creation timestamp
        is_approved: Moderation status
    """

    def __init__(self, post_id, user_id, content):
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.created_at = datetime.utcnow()
        self.is_approved = True  # Auto-approve for now

    def approve(self):
        """Approve the comment for display."""
        self.is_approved = True

    def to_dict(self):
        """
        Convert comment to dictionary.

        Returns:
            dict: Comment data
        """
        return {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'is_approved': self.is_approved
        }

    def __repr__(self):
        return f'<Comment on post {self.post_id}>'
