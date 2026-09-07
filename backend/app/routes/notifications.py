from flask import Blueprint, request, jsonify
from app import db
from app.models import Notification, User
from flask_jwt_extended import jwt_required, get_jwt_identity

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Obter notificações do usuário"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        notifications = Notification.query.filter_by(user_id=user_id).order_by(
            Notification.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page,
            'notifications': [notif.to_dict() for notif in notifications.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_notifications():
    """Obter contagem de notificações não lidas"""
    try:
        user_id = get_jwt_identity()
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return jsonify({'unread_count': unread_count}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    """Marcar notificação como lida"""
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({'error': 'Notificação não encontrada'}), 404
        
        if notification.user_id != user_id:
            return jsonify({'error': 'Você não tem permissão para marcar esta notificação como lida'}), 403
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Notificação marcada como lida',
            'notification': notification.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/mark-all-as-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """Marcar todas as notificações como lidas"""
    try:
        user_id = get_jwt_identity()
        
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        return jsonify({'message': 'Todas as notificações foram marcadas como lidas'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
