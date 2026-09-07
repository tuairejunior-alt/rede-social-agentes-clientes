from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Post
from sqlalchemy import or_

search_bp = Blueprint('search', __name__)

@search_bp.route('/users', methods=['GET'])
def search_users():
    """Buscar usuários por nome ou email"""
    try:
        query = request.args.get('q', '')
        user_type = request.args.get('user_type')  # 'agente' ou 'cliente'
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Query deve ter no mínimo 2 caracteres'}), 400
        
        search_query = User.query.filter(
            or_(
                User.full_name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        )
        
        if user_type:
            search_query = search_query.filter_by(user_type=user_type)
        
        results = search_query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': results.total,
            'pages': results.pages,
            'current_page': page,
            'results': [user.to_dict() for user in results.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@search_bp.route('/posts', methods=['GET'])
def search_posts():
    """Buscar posts por título ou descrição"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Query deve ter no mínimo 2 caracteres'}), 400
        
        search_query = Post.query.filter(
            Post.is_published == True,
            or_(
                Post.title.ilike(f'%{query}%'),
                Post.description.ilike(f'%{query}%')
            )
        )
        
        if category:
            search_query = search_query.filter_by(category=category)
        
        results = search_query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': results.total,
            'pages': results.pages,
            'current_page': page,
            'results': [post.to_dict() for post in results.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@search_bp.route('/agentes', methods=['GET'])
def search_agentes():
    """Buscar agentes por profissão ou rating"""
    try:
        profissao = request.args.get('profissao')
        min_rating = request.args.get('min_rating', 0, type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = User.query.filter_by(user_type='agente')
        
        if profissao:
            query = query.filter(User.agente.profissao.ilike(f'%{profissao}%'))
        
        if min_rating:
            query = query.filter(User.agente.rating >= min_rating)
        
        results = query.order_by(User.agente.rating.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': results.total,
            'pages': results.pages,
            'current_page': page,
            'results': [user.to_dict() for user in results.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
