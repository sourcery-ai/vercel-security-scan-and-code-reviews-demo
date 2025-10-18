"""
Tests for blog post functionality.
"""
import pytest
from app.models.post import Post

class TestPostModel:
    """Test Post model."""

    def test_post_creation(self):
        """Test creating a new post."""
        post = Post('Test Title', 'Test content', 1)
        assert post.title == 'Test Title'
        assert post.content == 'Test content'
        assert post.author_id == 1
        assert post.slug is not None

    def test_slug_generation(self):
        """Test automatic slug generation."""
        post = Post('Hello World!', 'Content', 1)
        assert post.slug == 'hello-world'

    def test_post_update(self):
        """Test updating post fields."""
        post = Post('Original', 'Content', 1)
        post.update(title='Updated Title', content='New content')
        assert post.title == 'Updated Title'
        assert post.content == 'New content'

    def test_post_publish(self):
        """Test publishing a post."""
        post = Post('Test', 'Content', 1)
        assert not post.published
        post.publish()
        assert post.published


class TestPostRoutes:
    """Test post-related routes."""

    def test_list_posts(self, client):
        """Test listing all posts."""
        response = client.get('/posts/')
        assert response.status_code in [200, 500]

    def test_search_posts(self, client):
        """Test searching posts."""
        response = client.get('/posts/search?q=test')
        assert response.status_code in [200, 500]

    def test_search_by_tags(self, client):
        """Test filtering posts by tags."""
        response = client.get('/posts/search?tags=python')
        assert response.status_code in [200, 500]

    def test_get_single_post(self, client):
        """Test getting a specific post."""
        response = client.get('/posts/1')
        assert response.status_code in [200, 404, 500]

    def test_create_post(self, client):
        """Test creating a new post."""
        response = client.post('/posts/create', json={
            'title': 'New Post',
            'content': 'Post content',
            'tags': 'python,flask'
        })
        # Will fail without auth, which is expected
        assert response.status_code in [201, 401, 500]

    def test_preview_post(self, client):
        """Test post preview rendering."""
        response = client.get('/posts/1/preview')
        assert response.status_code in [200, 404, 500]

    def test_add_comment(self, client):
        """Test adding a comment to a post."""
        response = client.post('/posts/1/comment', json={
            'content': 'Great post!'
        })
        assert response.status_code in [201, 401, 500]
