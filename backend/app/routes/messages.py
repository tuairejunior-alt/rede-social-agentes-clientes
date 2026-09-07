from flask import Blueprint, request, jsonify
from app import db
from app.models import Message, User, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    """Enviar mensagem direta"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('receiver_id') or not data.get('content'):
            return jsonify({'error': 'Receptor e conteúdo são obrigatórios'}), 400
        
        if user_id == data['receiver_id']:
            return jsonify({'error': 'Você não pode enviar mensagem para si mesmo'}), 400
        
        receiver = User.query.get(data['receiver_id'])
        if not receiver:
            return jsonify({'error': 'Receptor não encontrado'}), 404
        
        message = Message(
            sender_id=user_id,
            receiver_id=data['receiver_id'],
            content=data['content']
        )
        
        # Criar notificação
        notification = Notification(
            user_id=data['receiver_id'],
            title='Nova mensagem',
            message=f"Você recebeu uma nova mensagem de {User.query.get(user_id).full_name}",
            type='message',
            related_id=user_id
        )
        
        db.session.add(message)
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Mensagem enviada com sucesso',
            'data': message.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/conversation/<int:user_id>', methods=['GET'])
@jwt_required()
def get_conversation(user_id):
    """Obter conversa entre dois usuários"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Buscar mensagens entre os dois usuários
        messages = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user_id, Message.receiver_id == user_id),
                db.and_(Message.sender_id == user_id, Message.receiver_id == current_user_id)
            )
        ).order_by(Message.created_at.desc()).paginate(page=page, per_page=per_page)
        
        # Marcar como lido
        Message.query.filter(
            Message.receiver_id == current_user_id,
            Message.sender_id == user_id,
            Message.is_read == False
        ).update({'is_read': True})
        db.session.commit()
        
        return jsonify({
            'total': messages.total,
            'pages': messages.pages,
            'current_page': page,
            'messages': [msg.to_dict() for msg in reversed(messages.items)]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/inbox', methods=['GET'])
@jwt_required()
def get_inbox():
    """Obter inbox (últimas mensagens de cada conversa)"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Subquery para obter a última mensagem de cada conversa
        from sqlalchemy import func
        last_messages = db.session.query(
            func.max(Message.id).label('id')
        ).filter(
            db.or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).group_by(
            db.case(
                (Message.sender_id == user_id, Message.receiver_id),
                else_=Message.sender_id
            )
        ).subquery()
        
        messages = Message.query.filter(
            Message.id.in_(db.session.query(last_messages.c.id))
        ).order_by(Message.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': messages.total,
            'pages': messages.pages,
            'current_page': page,
            'conversations': [msg.to_dict() for msg in messages.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Obter contagem de mensagens não lidas"""
    try:
        user_id = get_jwt_identity()
        unread_count = Message.query.filter_by(
            receiver_id=user_id,
            is_read=False
        ).count()
        
        return jsonify({'unread_count': unread_count}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
