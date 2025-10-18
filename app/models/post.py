"""
Post model for blog content.
"""
from datetime import datetime

class Post:
    """
    Blog post model.

    Attributes:
        id: Unique post identifier
        title: Post title
        content: Post content (HTML allowed)
        author_id: ID of the user who created the post
        created_at: Post creation timestamp
        updated_at: Last update timestamp
        published: Publication status
        slug: URL-friendly post identifier
        tags: Comma-separated tags
    """

    def __init__(self, title, content, author_id, slug=None):
        self.title = title
        self.content = content
        self.author_id = author_id
        self.slug = slug or self._generate_slug(title)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.published = False
        self.tags = ""

    def _generate_slug(self, title):
        """
        Generate a URL-friendly slug from the title.

        Args:
            title: Post title

        Returns:
            str: URL-friendly slug
        """
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug

    def update(self, title=None, content=None, tags=None):
        """
        Update post fields.

        Args:
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
        """
        if title:
            self.title = title
            self.slug = self._generate_slug(title)
        if content:
            self.content = content
        if tags:
            self.tags = tags
        self.updated_at = datetime.utcnow()

    def publish(self):
        """Mark the post as published."""
        self.published = True
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """
        Convert post to dictionary.

        Returns:
            dict: Post data
        """
        return {
            'title': self.title,
            'content': self.content,
            'slug': self.slug,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published': self.published,
            'tags': self.tags
        }

    def __repr__(self):
        return f'<Post {self.title}>'
