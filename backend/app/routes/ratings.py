from flask import Blueprint, request, jsonify
from app import db
from app.models import Rating, User, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity

ratings_bp = Blueprint('ratings', __name__)

@ratings_bp.route('', methods=['POST'])
@jwt_required()
def create_rating():
    """Criar avaliação para um usuário"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('rated_user_id') or not data.get('score'):
            return jsonify({'error': 'Usuário a avaliar e score são obrigatórios'}), 400
        
        if user_id == data['rated_user_id']:
            return jsonify({'error': 'Você não pode avaliar a si mesmo'}), 400
        
        if not (1 <= data['score'] <= 5):
            return jsonify({'error': 'Score deve estar entre 1 e 5'}), 400
        
        rated_user = User.query.get(data['rated_user_id'])
        if not rated_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se já existe avaliação
        existing_rating = Rating.query.filter_by(
            rater_id=user_id,
            rated_user_id=data['rated_user_id']
        ).first()
        
        if existing_rating:
            return jsonify({'error': 'Você já avaliou este usuário'}), 400
        
        rating = Rating(
            rater_id=user_id,
            rated_user_id=data['rated_user_id'],
            score=data['score'],
            comment=data.get('comment')
        )
        
        # Atualizar rating do usuário avaliado
        all_ratings = Rating.query.filter_by(rated_user_id=data['rated_user_id']).all()
        total_score = sum([r.score for r in all_ratings]) + data['score']
        average_rating = total_score / (len(all_ratings) + 1)
        
        rated_user.rating = round(average_rating, 2)
        
        # Criar notificação
        notification = Notification(
            user_id=data['rated_user_id'],
            title='Nova avaliação',
            message=f"Você recebeu uma avaliação de {User.query.get(user_id).full_name}: {data['score']} ⭐",
            type='rating',
            related_id=user_id
        )
        
        db.session.add(rating)
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Avaliação criada com sucesso',
            'rating': rating.to_dict(),
            'new_average_rating': rated_user.rating
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ratings_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_ratings(user_id):
    """Obter avaliações de um usuário"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        ratings = Rating.query.filter_by(rated_user_id=user_id).order_by(
            Rating.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': ratings.total,
            'pages': ratings.pages,
            'current_page': page,
            'average_rating': user.rating,
            'ratings': [rating.to_dict() for rating in ratings.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
