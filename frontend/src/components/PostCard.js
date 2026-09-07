import React from 'react';
import { FiHeart, FiMessageCircle } from 'react-icons/fi';
import { AiOutlineLike } from 'react-icons/ai';

const PostCard = ({ post }) => {
  const handleLike = async () => {
    // TODO: Implementar like
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-4">
      {/* Header */}
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full mr-4"></div>
        <div>
          <h3 className="font-bold text-lg">{post.author?.full_name}</h3>
          <p className="text-gray-500 text-sm">{new Date(post.created_at).toLocaleDateString('pt-BR')}</p>
        </div>
      </div>

      {/* Content */}
      <h2 className="text-xl font-bold mb-2">{post.title}</h2>
      <p className="text-gray-700 mb-4">{post.description}</p>

      {post.image && (
        <img 
          src={post.image} 
          alt={post.title} 
          className="w-full h-64 object-cover rounded mb-4"
        />
      )}

      {post.category && (
        <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm mb-4">
          {post.category}
        </span>
      )}

      {/* Actions */}
      <div className="flex gap-4 pt-4 border-t">
        <button 
          onClick={handleLike}
          className="flex items-center gap-2 text-gray-600 hover:text-red-500 transition"
        >
          <AiOutlineLike size={20} />
          <span>{post.likes_count}</span>
        </button>
        <button className="flex items-center gap-2 text-gray-600 hover:text-blue-500 transition">
          <FiMessageCircle size={20} />
          <span>Comentar</span>
        </button>
      </div>
    </div>
  );
};

export default PostCard;
