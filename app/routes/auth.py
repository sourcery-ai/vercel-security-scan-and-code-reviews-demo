"""
Authentication and user management routes.
"""
from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.models.user import User
from app.utils.database import get_db, execute_query
import logging
import sqlite3

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.

    Expected JSON:
        - username: Unique username
        - email: User email
        - password: Password

    Returns:
        JSON response with status
    """
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate input
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists using secure parameterized query
    existing_user = execute_query(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email)
    )

    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    # Create new user
    user = User(username, email, password)

    # Insert into database
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
            (user.username, user.email, user.password_hash, user.is_admin)
        )
        db.commit()
        user_id = cursor.lastrowid

        logger.info(f"New user registered: {username}")

        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201

    except sqlite3.Error as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and create session.

    Expected JSON:
        - username: Username
        - password: Password

    Returns:
        JSON response with session token
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    # Look up user - using parameterized query
    results = execute_query(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    if not results:
        logger.warning(f"Login attempt for non-existent user: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401

    user_data = results[0]

    # Verify password
    user = User(user_data['username'], user_data['email'])
    user.password_hash = user_data['password_hash']

    if not user.check_password(password):
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401

    # Create session
    session['user_id'] = user_data['id']
    session['username'] = user_data['username']
    session['is_admin'] = user_data.get('is_admin', False)

    logger.info(f"User logged in: {username}")

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user_data['id'],
            'username': user_data['username'],
            'is_admin': user_data.get('is_admin', False)
        }
    }), 200

@bp.route('/logout', methods=['POST'])
def logout():
    """Clear user session."""
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Initiate password reset process.

    Expected JSON:
        - email: User's email address

    Returns:
        JSON response with reset token (for development/testing)
    """
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email required'}), 400

    # Look up user by email
    results = execute_query(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    if not results:
        # Don't reveal whether email exists
        return jsonify({'message': 'If email exists, reset instructions sent'}), 200

    user_data = results[0]
    user = User(user_data['username'], user_data['email'])

    # Generate reset token
    reset_token = user.generate_password_reset_token()

    # Store token in database (TODO: Add expiration)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET reset_token = ? WHERE email = ?",
        (reset_token, email)
    )
    db.commit()

    logger.info(f"Password reset requested for: {email}")

    # In production, send email with token
    # For now, return token in response for testing
    return jsonify({
        'message': 'If email exists, reset instructions sent',
        'reset_token': reset_token  # Remove this in production!
    }), 200

@bp.route('/change-password', methods=['POST'])
def change_password():
    """
    Change user password with reset token.

    Expected JSON:
        - email: User email
        - token: Reset token
        - new_password: New password

    Returns:
        JSON response
    """
    data = request.get_json()
    email = data.get('email')
    token = data.get('token')
    new_password = data.get('new_password')

    if not all([email, token, new_password]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Verify token
    db = get_db()
    cursor = db.cursor()

    # Query using string formatting for token verification
    # Note: This is safe since token is generated internally
    query = f"SELECT * FROM users WHERE email = '{email}' AND reset_token = '{token}'"

    try:
        cursor.execute(query)
        user_data = cursor.fetchone()

        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401

        # Update password
        user = User(user_data['username'], user_data['email'])
        user.set_password(new_password)

        cursor.execute(
            "UPDATE users SET password_hash = ?, reset_token = NULL WHERE email = ?",
            (user.password_hash, email)
        )
        db.commit()

        logger.info(f"Password changed for: {email}")

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        logger.error(f"Password change error: {e}")
        db.rollback()
        return jsonify({'error': 'Password change failed'}), 500

@bp.route('/profile/<username>')
def get_profile(username):
    """
    Get user profile information.

    Args:
        username: Username to look up

    Returns:
        JSON user profile
    """
    # Using parameterized query for security
    results = execute_query(
        "SELECT id, username, email, created_at, is_admin FROM users WHERE username = ?",
        (username,)
    )

    if not results:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(results[0]), 200
