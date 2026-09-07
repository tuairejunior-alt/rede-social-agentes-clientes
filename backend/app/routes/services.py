from flask import Blueprint, request, jsonify
from app import db
from app.models import Service, ServiceBooking, User, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

services_bp = Blueprint('services', __name__)

@services_bp.route('', methods=['POST'])
@jwt_required()
def create_service():
    """Criar novo serviço (apenas agentes)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.user_type != 'agente':
            return jsonify({'error': 'Apenas agentes podem criar serviços'}), 403
        
        data = request.get_json()
        
        if not data.get('title') or not data.get('description') or not data.get('price'):
            return jsonify({'error': 'Título, descrição e preço são obrigatórios'}), 400
        
        service = Service(
            provider_id=user_id,
            title=data['title'],
            description=data['description'],
            price=data['price'],
            duration=data.get('duration'),
            image=data.get('image')
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço criado com sucesso',
            'service': service.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@services_bp.route('', methods=['GET'])
def list_services():
    """Listar serviços"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        provider_id = request.args.get('provider_id', type=int)
        
        query = Service.query.filter_by(is_available=True)
        
        if provider_id:
            query = query.filter_by(provider_id=provider_id)
        
        services = query.order_by(Service.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': services.total,
            'pages': services.pages,
            'current_page': page,
            'services': [service.to_dict() for service in services.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """Obter detalhes de um serviço"""
    try:
        service = Service.query.get(service_id)
        
        if not service:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        return jsonify(service.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    """Atualizar serviço (apenas o provider)"""
    try:
        user_id = get_jwt_identity()
        service = Service.query.get(service_id)
        
        if not service:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        if service.provider_id != user_id:
            return jsonify({'error': 'Você não tem permissão para editar este serviço'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            service.title = data['title']
        if 'description' in data:
            service.description = data['description']
        if 'price' in data:
            service.price = data['price']
        if 'duration' in data:
            service.duration = data['duration']
        if 'image' in data:
            service.image = data['image']
        if 'is_available' in data:
            service.is_available = data['is_available']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço atualizado com sucesso',
            'service': service.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@services_bp.route('/booking', methods=['POST'])
@jwt_required()
def create_booking():
    """Agendar um serviço"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('service_id') or not data.get('scheduled_date'):
            return jsonify({'error': 'Service ID e data são obrigatórios'}), 400
        
        service = Service.query.get(data['service_id'])
        if not service:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        if user_id == service.provider_id:
            return jsonify({'error': 'Você não pode agendar seu próprio serviço'}), 400
        
        # Parse da data
        try:
            scheduled_date = datetime.fromisoformat(data['scheduled_date'])
        except:
            return jsonify({'error': 'Formato de data inválido'}), 400
        
        booking = ServiceBooking(
            service_id=data['service_id'],
            client_id=user_id,
            scheduled_date=scheduled_date,
            notes=data.get('notes')
        )
        
        # Criar notificação para o provider
        client = User.query.get(user_id)
        notification = Notification(
            user_id=service.provider_id,
            title='Novo agendamento',
            message=f"{client.full_name} agendou seu serviço '{service.title}' para {scheduled_date.strftime('%d/%m/%Y às %H:%M')}",
            type='booking',
            related_id=user_id
        )
        
        db.session.add(booking)
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento criado com sucesso',
            'booking': booking.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@services_bp.route('/booking/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """Atualizar status do agendamento"""
    try:
        user_id = get_jwt_identity()
        booking = ServiceBooking.query.get(booking_id)
        
        if not booking:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Apenas o provider pode atualizar o status
        if booking.service.provider_id != user_id:
            return jsonify({'error': 'Você não tem permissão para atualizar este agendamento'}), 403
        
        data = request.get_json()
        
        if 'status' in data:
            if data['status'] not in ['pending', 'confirmed', 'completed', 'cancelled']:
                return jsonify({'error': 'Status inválido'}), 400
            
            booking.status = data['status']
            
            # Criar notificação para o cliente
            provider = User.query.get(user_id)
            status_messages = {
                'confirmed': f"Seu agendamento foi confirmado",
                'completed': f"Seu agendamento foi completado",
                'cancelled': f"Seu agendamento foi cancelado"
            }
            
            if data['status'] in status_messages:
                notification = Notification(
                    user_id=booking.client_id,
                    title='Atualização de agendamento',
                    message=status_messages[data['status']],
                    type='booking',
                    related_id=user_id
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento atualizado com sucesso',
            'booking': booking.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@services_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """Obter agendamentos do usuário (como cliente)"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        bookings = ServiceBooking.query.filter_by(client_id=user_id).order_by(
            ServiceBooking.scheduled_date.desc()
        ).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page,
            'bookings': [booking.to_dict() for booking in bookings.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
