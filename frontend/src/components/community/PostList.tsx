import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { User, MessageCircle, Eye, Clock, Trash2 } from 'lucide-react';
import communityService, { CommunityPost } from '../../services/communityService';
import EmptyState, { EmptyStateIcons } from '../ui/EmptyState';
import { useAuthStore } from '../../store/authStore';

interface PostListProps {
  category?: string;
}

export default function PostList({ category }: PostListProps) {
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingPostId, setDeletingPostId] = useState<string | null>(null);
  const navigate = useNavigate();
  const { user } = useAuthStore();

  useEffect(() => {
    loadPosts();
  }, [category]);

  const loadPosts = async () => {
    try {
      setLoading(true);
      console.log('[PostList] Fetching posts with category:', category);
      console.log('[PostList] User:', user);
      console.log('[PostList] Token exists:', !!localStorage.getItem('access_token'));
      
      const data = await communityService.getPosts(category);
      console.log('[PostList] Posts received:', data);
      console.log('[PostList] Number of posts:', data?.length);
      
      setPosts(data);
    } catch (err: any) {
      console.error('[PostList] Error loading posts:', err);
      console.error('[PostList] Error response:', err.response);
      console.error('[PostList] Error status:', err.response?.status);
      console.error('[PostList] Error data:', err.response?.data);
      setError(err.response?.data?.detail || 'Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (cat: string) => {
    const colors: Record<string, string> = {
      general: 'from-blue-500/20 to-blue-600/20 border-blue-500/30 text-blue-300',
      support: 'from-green-500/20 to-green-600/20 border-green-500/30 text-green-300',
      tips: 'from-purple-500/20 to-purple-600/20 border-purple-500/30 text-purple-300',
      questions: 'from-yellow-500/20 to-yellow-600/20 border-yellow-500/30 text-yellow-300',
      resources: 'from-pink-500/20 to-pink-600/20 border-pink-500/30 text-pink-300',
    };
    return colors[cat] || 'from-gray-500/20 to-gray-600/20 border-gray-500/30 text-gray-300';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const handleDeletePost = async (postId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent navigation to post detail
    
    if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingPostId(postId);
      await communityService.deletePost(postId);
      // Remove post from list
      setPosts(posts.filter(p => p.id !== postId));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete post');
    } finally {
      setDeletingPostId(null);
    }
  };

  const isOwnPost = (post: CommunityPost) => {
    return user && post.user.id === user.id && !post.user.is_anonymous;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full"
        />
      </div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-r from-red-500/10 to-pink-500/10 border border-red-500/20 rounded-xl p-6 text-red-300"
      >
        {error}
      </motion.div>
    );
  }

  if (posts.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10"
      >
        <EmptyState
          icon={EmptyStateIcons.NoPosts}
          title="No Posts Yet"
          description="Be the first to start a discussion in this category. Share your experiences, ask questions, or offer support to others in the community."
          action={{
            label: 'Create Post',
            onClick: () => navigate('/community?tab=create'),
          }}
        />
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      <AnimatePresence>
        {posts.map((post, index) => (
          <motion.div
            key={post.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ scale: 1.01, y: -2 }}
            onClick={() => navigate(`/community/posts/${post.id}`)}
            className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10 transition-all cursor-pointer group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-3 flex-wrap">
                  <span className={`px-3 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r ${getCategoryColor(post.category)} border backdrop-blur-sm`}>
                    {post.category.toUpperCase()}
                  </span>
                  {post.is_flagged && (
                    <span className="px-3 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 text-red-300">
                      ⚠️ Flagged
                    </span>
                  )}
                </div>
                
                <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-blue-300 transition-colors">
                  {post.title}
                </h3>
                
                <p className="text-gray-400 line-clamp-2 mb-4 leading-relaxed">
                  {post.content}
                </p>
                
                <div className="flex items-center gap-6 text-sm text-gray-400 flex-wrap">
                  <span className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    <span className="text-blue-300">{post.user.name}</span>
                  </span>
                  
                  <span className="flex items-center gap-2">
                    <MessageCircle className="w-4 h-4" />
                    {post.reply_count} {post.reply_count === 1 ? 'reply' : 'replies'}
                  </span>
                  
                  <span className="flex items-center gap-2">
                    <Eye className="w-4 h-4" />
                    {post.view_count} views
                  </span>
                  
                  <span className="flex items-center gap-2 ml-auto">
                    <Clock className="w-4 h-4" />
                    {formatDate(post.created_at)}
                  </span>
                </div>
              </div>

              {/* Delete button for own posts */}
              {isOwnPost(post) && (
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={(e) => handleDeletePost(post.id, e)}
                  disabled={deletingPostId === post.id}
                  className="p-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 hover:border-red-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Delete post"
                >
                  {deletingPostId === post.id ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      className="w-5 h-5 border-2 border-red-400/30 border-t-red-400 rounded-full"
                    />
                  ) : (
                    <Trash2 className="w-5 h-5" />
                  )}
                </motion.button>
              )}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </motion.div>
  );
}
