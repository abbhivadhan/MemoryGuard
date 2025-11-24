import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import communityService, { CommunityPostDetail, CreateReplyData } from '../../services/communityService';
import { useAuthStore } from '../../store/authStore';

export default function PostDetail() {
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [post, setPost] = useState<CommunityPostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (postId) {
      loadPost();
    }
  }, [postId]);

  const loadPost = async () => {
    try {
      setLoading(true);
      const data = await communityService.getPost(postId!);
      setPost(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load post');
    } finally {
      setLoading(false);
    }
  };

  const handleReplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!replyContent.trim()) return;

    try {
      setSubmitting(true);
      const replyData: CreateReplyData = {
        content: replyContent,
        is_anonymous: isAnonymous,
      };
      await communityService.createReply(postId!, replyData);
      setReplyContent('');
      setIsAnonymous(false);
      await loadPost(); // Reload to show new reply
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to post reply');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) return;

    try {
      await communityService.deletePost(postId!);
      alert('Post deleted successfully');
      navigate('/community');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete post');
    }
  };

  const handleFlag = async () => {
    if (!confirm('Are you sure you want to flag this post for moderation?')) return;
    
    const reason = prompt('Please provide a reason for flagging:');
    if (!reason) return;

    try {
      await communityService.flagPost(postId!, { reason });
      alert('Post has been flagged for review');
      await loadPost();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to flag post');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getCategoryColor = (cat: string) => {
    const colors: Record<string, string> = {
      general: 'bg-gradient-to-r from-blue-500/20 to-blue-600/20 border border-blue-500/30 text-blue-300',
      support: 'bg-gradient-to-r from-green-500/20 to-green-600/20 border border-green-500/30 text-green-300',
      tips: 'bg-gradient-to-r from-purple-500/20 to-purple-600/20 border border-purple-500/30 text-purple-300',
      questions: 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border border-yellow-500/30 text-yellow-300',
      resources: 'bg-gradient-to-r from-pink-500/20 to-pink-600/20 border border-pink-500/30 text-pink-300',
    };
    return colors[cat] || 'bg-gradient-to-r from-gray-500/20 to-gray-600/20 border border-gray-500/30 text-gray-300';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="backdrop-blur-xl bg-gradient-to-r from-red-500/10 to-pink-500/10 border border-red-500/20 rounded-xl p-6 text-red-300">
        {error || 'Post not found'}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate('/community')}
        className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Community
      </button>

      {/* Post */}
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <span className={`px-4 py-2 rounded-xl text-sm font-medium ${getCategoryColor(post.category)}`}>
            {post.category.toUpperCase()}
          </span>
          {post.is_flagged && (
            <span className="px-4 py-2 rounded-xl text-sm font-medium bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 text-red-300">
              ⚠️ Flagged
            </span>
          )}
        </div>

        <h1 className="text-4xl font-bold text-white mb-6">{post.title}</h1>

        <div className="flex items-center gap-6 text-sm text-gray-400 mb-8 pb-6 border-b border-white/10">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="text-blue-300">{post.user.name}</span>
          </span>
          <span>{formatDate(post.created_at)}</span>
          <span>{post.view_count} views</span>
        </div>

        <div className="prose prose-invert max-w-none mb-8">
          <p className="text-gray-300 text-lg leading-relaxed whitespace-pre-wrap">{post.content}</p>
        </div>

        <div className="flex gap-3">
          {user && post.user.id === user.id && !post.user.is_anonymous && (
            <button
              onClick={handleDelete}
              className="text-sm text-red-400 hover:text-red-300 flex items-center gap-2 transition-colors backdrop-blur-sm bg-red-500/10 px-4 py-2 rounded-lg border border-red-500/30 hover:bg-red-500/20"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete Post
            </button>
          )}
          <button
            onClick={handleFlag}
            className="text-sm text-gray-400 hover:text-red-400 flex items-center gap-2 transition-colors backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
            </svg>
            Report
          </button>
        </div>
      </div>

      {/* Replies */}
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-8 shadow-xl">
        <h2 className="text-2xl font-bold text-white mb-6">
          Replies ({post.replies.length})
        </h2>

        <div className="space-y-4 mb-8">
          {post.replies.map((reply) => (
            <div key={reply.id} className="border-l-4 border-blue-500/50 pl-6 py-4 backdrop-blur-sm bg-white/5 rounded-r-xl">
              <div className="flex items-center gap-3 mb-3">
                <span className="font-semibold text-blue-300">{reply.user.name}</span>
                <span className="text-sm text-gray-400">{formatDate(reply.created_at)}</span>
                {reply.is_flagged && (
                  <span className="px-3 py-1 rounded-lg text-xs font-medium bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 text-red-300">
                    ⚠️ Flagged
                  </span>
                )}
              </div>
              <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{reply.content}</p>
            </div>
          ))}

          {post.replies.length === 0 && (
            <p className="text-gray-400 text-center py-8 backdrop-blur-sm bg-white/5 rounded-xl border border-white/10">
              No replies yet. Be the first to reply!
            </p>
          )}
        </div>

        {/* Reply form */}
        <form onSubmit={handleReplySubmit} className="border-t border-white/10 pt-8">
          <h3 className="text-xl font-semibold text-white mb-4">Add a Reply</h3>
          
          <textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            className="w-full px-4 py-3 backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-4 text-white placeholder-gray-400 transition-all"
            rows={4}
            placeholder="Share your thoughts..."
            required
          />

          <div className="flex items-center justify-between">
            <div className="flex items-center backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10">
              <input
                type="checkbox"
                id="reply-anonymous"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="reply-anonymous" className="ml-2 text-sm text-gray-300">
                Reply anonymously
              </label>
            </div>

            <button
              type="submit"
              disabled={submitting || !replyContent.trim()}
              className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-8 py-3 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {submitting ? 'Posting...' : 'Post Reply'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
