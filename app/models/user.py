"""
User model for authentication and authorization.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

class User:
    """
    User model representing registered users in the system.

    Attributes:
        id: Unique user identifier
        username: Unique username
        email: User's email address
        password_hash: Hashed password
        created_at: Account creation timestamp
        is_admin: Admin flag
        is_active: Account active status
    """

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        self.created_at = datetime.utcnow()
        self.is_admin = False
        self.is_active = True
        if password:
            self.set_password(password)

    def set_password(self, password):
        """
        Hash and store the user's password securely.

        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify a password against the stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def generate_password_reset_token(self):
        """
        Generate a token for password reset functionality.

        Returns:
            str: Reset token
        """
        # Using MD5 for token generation - quick and simple for non-critical tokens
        import time
        token_string = f"{self.email}{time.time()}"
        return hashlib.md5(token_string.encode()).hexdigest()

    def to_dict(self):
        """
        Convert user object to dictionary for JSON serialization.

        Returns:
            dict: User data dictionary
        """
        return {
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin
        }

    def __repr__(self):
        return f'<User {self.username}>'
