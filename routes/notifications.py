from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Notification, User
from datetime import datetime, timedelta
from routes.helpers import get_user_id

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_user_id()
        
        # Get query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        return jsonify([notif.to_dict() for notif in notifications]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notif_id):
    try:
        user_id = get_user_id()
        
        notification = Notification.query.get(notif_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        if notification.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        db.session.commit()
        
        # Emit update via socket (lazy import to avoid circular dependency)
        try:
            from app import get_socketio
            socketio = get_socketio()
            socketio.emit('notification_read', {'notification_id': notif_id, 'user_id': user_id})
        except Exception:
            pass  # SocketIO not available, continue without real-time update
        
        return jsonify({'message': 'Notification marked as read'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    try:
        user_id = get_user_id()
        
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        # Emit update via socket (lazy import to avoid circular dependency)
        try:
            from app import get_socketio
            socketio = get_socketio()
            socketio.emit('all_notifications_read', {'user_id': user_id})
        except Exception:
            pass  # SocketIO not available, continue without real-time update
        
        return jsonify({'message': 'All notifications marked as read'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    try:
        user_id = get_user_id()
        
        count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        return jsonify({'unread_count': count}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

