from flask import Blueprint, request, jsonify
from app import db
from app.models import Post, Comment, User
from flask_jwt_extended import jwt_required, get_jwt_identity

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/post/<int:post_id>', methods=['GET'])
def get_post_comments(post_id):
    """Obter comentários de um post"""
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post não encontrado'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        comments = Comment.query.filter_by(post_id=post_id).order_by(
            Comment.created_at.desc()
        ).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'total': comments.total,
            'pages': comments.pages,
            'current_page': page,
            'comments': [comment.to_dict() for comment in comments.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@comments_bp.route('', methods=['POST'])
@jwt_required()
def create_comment():
    """Criar novo comentário"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('post_id') or not data.get('content'):
            return jsonify({'error': 'Post ID e conteúdo são obrigatórios'}), 400
        
        post = Post.query.get(data['post_id'])
        if not post:
            return jsonify({'error': 'Post não encontrado'}), 404
        
        comment = Comment(
            post_id=data['post_id'],
            user_id=user_id,
            content=data['content']
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comentário criado com sucesso',
            'comment': comment.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Atualizar comentário (apenas o autor)"""
    try:
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'error': 'Comentário não encontrado'}), 404
        
        if comment.user_id != user_id:
            return jsonify({'error': 'Você não tem permissão para editar este comentário'}), 403
        
        data = request.get_json()
        if 'content' in data:
            comment.content = data['content']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comentário atualizado com sucesso',
            'comment': comment.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Deletar comentário (apenas o autor ou dono do post)"""
    try:
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'error': 'Comentário não encontrado'}), 404
        
        if comment.user_id != user_id and comment.post.user_id != user_id:
            return jsonify({'error': 'Você não tem permissão para deletar este comentário'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comentário deletado com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
