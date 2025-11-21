import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import communityService, { CommunityPostDetail, CreateReplyData } from '../../services/communityService';

export default function PostDetail() {
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();
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
      general: 'bg-blue-100 text-blue-800',
      support: 'bg-green-100 text-green-800',
      tips: 'bg-purple-100 text-purple-800',
      questions: 'bg-yellow-100 text-yellow-800',
      resources: 'bg-pink-100 text-pink-800',
    };
    return colors[cat] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        {error || 'Post not found'}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate('/community')}
        className="flex items-center gap-2 text-blue-600 hover:text-blue-700"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Community
      </button>

      {/* Post */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(post.category)}`}>
            {post.category}
          </span>
          {post.is_flagged && (
            <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
              Flagged
            </span>
          )}
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-4">{post.title}</h1>

        <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            {post.user.name}
          </span>
          <span>{formatDate(post.created_at)}</span>
          <span>{post.view_count} views</span>
        </div>

        <div className="prose max-w-none mb-6">
          <p className="text-gray-700 whitespace-pre-wrap">{post.content}</p>
        </div>

        <button
          onClick={handleFlag}
          className="text-sm text-gray-500 hover:text-red-600 flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
          </svg>
          Report
        </button>
      </div>

      {/* Replies */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Replies ({post.replies.length})
        </h2>

        <div className="space-y-4 mb-6">
          {post.replies.map((reply) => (
            <div key={reply.id} className="border-l-4 border-blue-200 pl-4 py-2">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-medium text-gray-900">{reply.user.name}</span>
                <span className="text-sm text-gray-500">{formatDate(reply.created_at)}</span>
                {reply.is_flagged && (
                  <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Flagged
                  </span>
                )}
              </div>
              <p className="text-gray-700 whitespace-pre-wrap">{reply.content}</p>
            </div>
          ))}

          {post.replies.length === 0 && (
            <p className="text-gray-500 text-center py-4">No replies yet. Be the first to reply!</p>
          )}
        </div>

        {/* Reply form */}
        <form onSubmit={handleReplySubmit} className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add a Reply</h3>
          
          <textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
            rows={4}
            placeholder="Share your thoughts..."
            required
          />

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="reply-anonymous"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="reply-anonymous" className="ml-2 text-sm text-gray-700">
                Reply anonymously
              </label>
            </div>

            <button
              type="submit"
              disabled={submitting || !replyContent.trim()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Posting...' : 'Post Reply'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
