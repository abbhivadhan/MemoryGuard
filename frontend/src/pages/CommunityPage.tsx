import { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MessageCircle, BookOpen, Users } from 'lucide-react';
import PostList from '../components/community/PostList';
import CreatePostForm from '../components/community/CreatePostForm';
import UserMatching from '../components/community/UserMatching';
import EducationalResources from '../components/community/EducationalResources';
import Scene from '../components/3d/Scene';
import Starfield from '../components/3d/Starfield';

type TabType = 'forum' | 'resources' | 'matches';

export default function CommunityPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('forum');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);
  const [refreshKey, setRefreshKey] = useState(0);

  const categories = [
    { value: undefined, label: 'All Topics' },
    { value: 'general', label: 'General Discussion' },
    { value: 'support', label: 'Support & Encouragement' },
    { value: 'tips', label: 'Tips & Advice' },
    { value: 'questions', label: 'Questions' },
    { value: 'resources', label: 'Resources' },
  ];

  const handlePostCreated = () => {
    setShowCreateForm(false);
    setRefreshKey(prev => prev + 1);
  };

  const tabs = [
    { id: 'forum' as TabType, label: 'Forum', icon: <MessageCircle className="w-5 h-5" /> },
    { id: 'resources' as TabType, label: 'Resources', icon: <BookOpen className="w-5 h-5" /> },
    { id: 'matches' as TabType, label: 'Connect', icon: <Users className="w-5 h-5" /> },
  ];

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* 3D Background Scene */}
      <div className="fixed inset-0 z-0">
        <Scene camera={{ position: [0, 0, 8], fov: 75 }} enablePhysics={false}>
          <Suspense fallback={null}>
            <Starfield count={200} />
          </Suspense>
        </Scene>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Back Button */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => navigate('/dashboard')}
          className="mb-6 flex items-center gap-2 text-gray-300 hover:text-white transition-colors backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </motion.button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <motion.div 
              className="p-3 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400 }}
            >
              <Users className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold text-blue-50">
              Community Forum
            </h1>
          </div>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Connect with others, share experiences, and find support
          </p>
        </motion.div>

        {/* Navigation tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center mb-8"
        >
          <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-2 inline-flex gap-2">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-6 py-3 rounded-xl transition-all text-sm font-medium flex items-center gap-2 relative overflow-hidden ${
                  activeTab === tab.id ? 'text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeCommunityTab"
                    className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl"
                    transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <span className="relative z-10">{tab.icon}</span>
                <span className="relative z-10">{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Category Filter for Forum */}
        {activeTab === 'forum' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-center mb-6"
          >
            <div className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-2 inline-flex gap-2 flex-wrap">
              {categories.map((cat) => (
                <motion.button
                  key={cat.value || 'all'}
                  onClick={() => setSelectedCategory(cat.value)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-4 py-2 rounded-lg transition-all text-sm font-medium ${
                    selectedCategory === cat.value
                      ? 'bg-white/10 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {cat.label}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6"
        >
          {/* Tab content */}
          {activeTab === 'forum' && (
            <>
              {/* Create post button */}
              {!showCreateForm && (
                <div className="flex justify-end mb-4">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowCreateForm(true)}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-6 py-2 rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all shadow-lg flex items-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Post
                  </motion.button>
                </div>
              )}

              {/* Create post form */}
              {showCreateForm && (
                <div className="mb-6">
                  <CreatePostForm
                    onSuccess={handlePostCreated}
                    onCancel={() => setShowCreateForm(false)}
                  />
                </div>
              )}

              {/* Post list */}
              <PostList key={refreshKey} category={selectedCategory} />
            </>
          )}

          {activeTab === 'resources' && <EducationalResources />}
          
          {activeTab === 'matches' && <UserMatching />}
        </motion.div>
      </div>
    </div>
  );
}
