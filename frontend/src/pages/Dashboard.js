import React, { useState, useEffect, useContext } from 'react';
import { usersAPI, postsAPI } from '../services/api';
import { AuthContext } from '../context/AuthContext';
import PostCard from '../components/PostCard';

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const [posts, setPosts] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('feed');

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'feed') {
        const response = await postsAPI.listPosts();
        setPosts(response.data.posts);
      } else if (activeTab === 'agentes') {
        const response = await usersAPI.listAgentes();
        setUsers(response.data.agentes);
      } else if (activeTab === 'clientes') {
        const response = await usersAPI.listClientes();
        setUsers(response.data.clientes);
      }
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-800">Bem-vindo, {user?.full_name}!</h1>
          <p className="text-gray-600">Tipo de usuário: <span className="font-bold capitalize">{user?.user_type}</span></p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 flex gap-4">
          <button
            onClick={() => setActiveTab('feed')}
            className={`py-4 px-4 font-bold ${activeTab === 'feed' ? 'border-b-4 border-blue-500 text-blue-500' : 'text-gray-600'}`}
          >
            Feed
          </button>
          <button
            onClick={() => setActiveTab('agentes')}
            className={`py-4 px-4 font-bold ${activeTab === 'agentes' ? 'border-b-4 border-blue-500 text-blue-500' : 'text-gray-600'}`}
          >
            Agentes
          </button>
          <button
            onClick={() => setActiveTab('clientes')}
            className={`py-4 px-4 font-bold ${activeTab === 'clientes' ? 'border-b-4 border-blue-500 text-blue-500' : 'text-gray-600'}`}
          >
            Clientes
          </button>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center text-gray-600">Carregando...</div>
        ) : (
          <>
            {activeTab === 'feed' && (
              <div className="space-y-4">
                {posts.length > 0 ? (
                  posts.map(post => (
                    <PostCard key={post.id} post={post} />
                  ))
                ) : (
                  <p className="text-center text-gray-600">Nenhum post encontrado</p>
                )}
              </div>
            )}

            {(activeTab === 'agentes' || activeTab === 'clientes') && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {users.length > 0 ? (
                  users.map(u => (
                    <div key={u.id} className="bg-white p-4 rounded-lg shadow">
                      <h3 className="font-bold text-lg mb-2">{u.full_name}</h3>
                      <p className="text-gray-600 mb-2">{u.bio || 'Sem bio'}</p>
                      {u.user_type === 'agente' && (
                        <>
                          <p className="text-sm text-gray-500">Profissão: {u.profissao}</p>
                          <p className="text-sm text-gray-500">Rating: ⭐ {u.rating}</p>
                        </>
                      )}
                      <button className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded">
                        Seguir
                      </button>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-gray-600">Nenhum usuário encontrado</p>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
