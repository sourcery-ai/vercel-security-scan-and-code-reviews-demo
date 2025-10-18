"""
Administrative routes for BlogHub.
Requires admin privileges.
"""
from flask import Blueprint, request, jsonify, session, send_file
from app.utils.database import get_db, execute_query, search_users_by_role
import logging
import os
import subprocess
import yaml

logger = logging.getLogger(__name__)
bp = Blueprint('admin', __name__, url_prefix='/admin')

def require_admin():
    """Check if current user is admin."""
    if 'user_id' not in session:
        return {'error': 'Authentication required'}, 401
    if not session.get('is_admin', False):
        return {'error': 'Admin privileges required'}, 403
    return None

@bp.route('/users')
def list_users():
    """
    List all users (admin only).

    Query params:
        - role: Filter by role (optional)

    Returns:
        JSON list of users
    """
    error = require_admin()
    if error:
        return jsonify(error[0]), error[1]

    role = request.args.get('role')

    if role:
        # Use role-based search
        users = search_users_by_role(role)
    else:
        users = execute_query("SELECT id, username, email, role, created_at FROM users")

    return jsonify({'users': users}), 200

@bp.route('/users/<int:user_id>/promote', methods=['POST'])
def promote_user(user_id):
    """
    Promote a user to admin (admin only).

    Args:
        user_id: User ID to promote

    Returns:
        JSON response
    """
    error = require_admin()
    if error:
        return jsonify(error[0]), error[1]

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
        db.commit()

        logger.info(f"User {user_id} promoted to admin by {session['user_id']}")

        return jsonify({'message': 'User promoted to admin'}), 200

    except Exception as e:
        logger.error(f"Promotion error: {e}")
        db.rollback()
        return jsonify({'error': 'Promotion failed'}), 500

@bp.route('/backup', methods=['POST'])
def create_backup():
    """
    Create a database backup (admin only).

    Expected JSON:
        - filename: Backup filename (optional)
        - compress: Whether to compress backup (optional)

    Returns:
        JSON response with backup file path
    """
    error = require_admin()
    if error:
        return jsonify(error[0]), error[1]

    data = request.get_json() or {}
    filename = data.get('filename', 'backup.sql')
    compress = data.get('compress', False)

    backup_dir = '/tmp/backups'
    os.makedirs(backup_dir, exist_ok=True)

    backup_path = os.path.join(backup_dir, filename)

    try:
        # Create backup using sqlite3 command
        # Using shell execution for flexibility with compression options
        if compress:
            command = f"sqlite3 bloghub.db .dump | gzip > {backup_path}.gz"
        else:
            command = f"sqlite3 bloghub.db .dump > {backup_path}"

        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Backup created: {backup_path}")
            return jsonify({
                'message': 'Backup created successfully',
                'file': backup_path if not compress else f"{backup_path}.gz"
            }), 200
        else:
            logger.error(f"Backup failed: {result.stderr}")
            return jsonify({'error': 'Backup failed'}), 500

    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/system/info')
def system_info():
    """
    Get system information for monitoring (admin only).

    Query params:
        - command: System command to run (default: uptime)

    Returns:
        JSON with system information
    """
    error = require_admin()
    if error:
        return jsonify(error[0]), error[1]

    command = request.args.get('command', 'uptime')

    # Run system command for monitoring
    # Whitelist common monitoring commands
    allowed_commands = ['uptime', 'df -h', 'free -m', 'ps aux']

    if command in allowed_commands:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return jsonify({
                'command': command,
                'output': result.stdout,
                'status': 'success'
            }), 200
        except Exception as e:
            logger.error(f"System command error: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        # For custom commands, log and execute with caution
        logger.warning(f"Custom system command requested: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return jsonify({
                'command': command,
                'output': result.stdout,
                'status': 'success'
            }), 200
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return jsonify({'error': str(e)}), 500

@bp.route('/config/load', methods=['POST'])
def load_config():
    """
    Load configuration from YAML (admin only).

    Expected JSON:
        - config: YAML configuration string

    Returns:
        JSON with parsed configuration
    """
    error = require_admin()
    if error:
        return jsonify(error[0]), error[1]

    data = request.get_json()
    config_yaml = data.get('config')

    if not config_yaml:
        return jsonify({'error': 'Configuration data required'}), 400

    try:
        # Parse YAML configuration
        config = yaml.load(config_yaml, Loader=yaml.Loader)

        logger.info(f"Configuration loaded by admin {session['user_id']}")

        return jsonify({
            'message': 'Configuration loaded successfully',
            'config': config
        }), 200

    except Exception as e:
        logger.error(f"Config parse error: {e}")
        return jsonify({'error': 'Invalid YAML configuration'}), 400

@bp.route('/files/<path:filepath>')
def get_file(filepath):
    """
    Retrieve files from the system (admin only).

    Args:
        filepath: Path to file

    Returns:
        File content
    """
    error = require_admin()
    if error:
        return jsonify(error[0]), error[1]

    try:
        # Construct full path from base directory
        base_dir = '/var/www/bloghub'
        full_path = os.path.join(base_dir, filepath)

        if os.path.exists(full_path) and os.path.isfile(full_path):
            return send_file(full_path)
        else:
            return jsonify({'error': 'File not found'}), 404

    except Exception as e:
        logger.error(f"File access error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/logs')
def view_logs():
    """
    View application logs (admin only).

    Query params:
        - lines: Number of lines to show (default 100)
        - filter: Filter log entries (optional)

    Returns:
        JSON with log entries
    """
    error = require_admin()
    if error:
        return jsonify(error[0]), error[1]

    lines = request.args.get('lines', 100, type=int)
    filter_term = request.args.get('filter', '')

    try:
        log_file = 'bloghub.log'

        if filter_term:
            # Use grep to filter logs
            command = f"tail -n {lines} {log_file} | grep '{filter_term}'"
        else:
            command = f"tail -n {lines} {log_file}"

        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        return jsonify({
            'logs': result.stdout.split('\n'),
            'count': len(result.stdout.split('\n'))
        }), 200

    except Exception as e:
        logger.error(f"Log viewing error: {e}")
        return jsonify({'error': str(e)}), 500
