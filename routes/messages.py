from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from models import db, Message, User, Application
from datetime import datetime
from routes.helpers import get_user_id

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('', methods=['GET'])
@jwt_required()
def get_messages():
    try:
        user_id = get_user_id()
        
        # Get query parameters
        conversation_with = request.args.get('conversation_with', None)
        message_type = request.args.get('type', None)
        
        if conversation_with:
            # Get conversation between two users
            messages = Message.query.filter(
                ((Message.sender_id == user_id) & (Message.receiver_id == conversation_with)) |
                ((Message.sender_id == conversation_with) & (Message.receiver_id == user_id))
            )
            if message_type:
                messages = messages.filter_by(message_type=message_type)
            messages = messages.order_by(Message.created_at.asc()).all()
        else:
            # Get all messages for user
            messages = Message.query.filter(
                (Message.sender_id == user_id) | (Message.receiver_id == user_id)
            )
            if message_type:
                messages = messages.filter_by(message_type=message_type)
            messages = messages.order_by(Message.created_at.desc()).all()
        
        return jsonify([msg.to_dict() for msg in messages]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        subject = data.get('subject', '')
        message_type = data.get('message_type', 'message')
        related_application_id = data.get('related_application_id', None)
        
        if not receiver_id:
            return jsonify({'error': 'receiver_id is required'}), 400
        
        if not content:
            return jsonify({'error': 'Message content is required'}), 400
        
        # Verify receiver exists
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        # Verify application if provided
        if related_application_id:
            application = Application.query.get(related_application_id)
            if not application:
                return jsonify({'error': 'Application not found'}), 404
        
        message = Message(
            sender_id=user_id,
            receiver_id=receiver_id,
            subject=subject,
            content=content,
            message_type=message_type,
            related_application_id=related_application_id
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Emit real-time notification (lazy import to avoid circular dependency)
        try:
            from app import get_socketio
            socketio = get_socketio()
            socketio.emit('new_message', {
                'message': message.to_dict(),
                'receiver_id': receiver_id
            })
        except Exception:
            pass  # SocketIO not available, continue without real-time update
        
        return jsonify({
            'message': 'Message sent successfully',
            'data': message.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/<int:msg_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(msg_id):
    try:
        user_id = get_user_id()
        
        message = Message.query.get(msg_id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        if message.receiver_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        message.is_read = True
        db.session.commit()
        
        return jsonify({'message': 'Message marked as read'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    try:
        user_id = get_user_id()
        
        # Get unique conversations
        sent_messages = db.session.query(Message.receiver_id).filter_by(sender_id=user_id).distinct().all()
        received_messages = db.session.query(Message.sender_id).filter_by(receiver_id=user_id).distinct().all()
        
        user_ids = set()
        for msg in sent_messages:
            user_ids.add(msg[0])
        for msg in received_messages:
            user_ids.add(msg[0])
        
        conversations = []
        for other_user_id in user_ids:
            other_user = User.query.get(other_user_id)
            if other_user:
                last_message = Message.query.filter(
                    ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
                    ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
                ).order_by(Message.created_at.desc()).first()
                
                unread_count = Message.query.filter_by(
                    sender_id=other_user_id,
                    receiver_id=user_id,
                    is_read=False
                ).count()
                
                conversations.append({
                    'user': other_user.to_dict(),
                    'last_message': last_message.to_dict() if last_message else None,
                    'unread_count': unread_count
                })
        
        # Sort by last message time
        conversations.sort(key=lambda x: x['last_message']['created_at'] if x['last_message'] else '', reverse=True)
        
        return jsonify(conversations), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

