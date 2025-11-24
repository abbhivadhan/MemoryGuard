import { useState } from 'react';
import communityService, { CreatePostData } from '../../services/communityService';
import PrivacySettings from './PrivacySettings';

interface CreatePostFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function CreatePostForm({ onSuccess, onCancel }: CreatePostFormProps) {
  const [formData, setFormData] = useState<CreatePostData>({
    title: '',
    content: '',
    category: 'general',
    visibility: 'public',
    is_anonymous: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.content.trim()) {
      setError('Title and content are required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await communityService.createPost(formData);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Create New Post</h2>

      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-300">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            placeholder="Enter post title..."
            maxLength={255}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Category
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value as any })}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
          >
            <option value="general" className="bg-gray-900">General Discussion</option>
            <option value="support" className="bg-gray-900">Support & Encouragement</option>
            <option value="tips" className="bg-gray-900">Tips & Advice</option>
            <option value="questions" className="bg-gray-900">Questions</option>
            <option value="resources" className="bg-gray-900">Resources</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Content
          </label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-none"
            rows={8}
            placeholder="Share your thoughts..."
          />
        </div>

        <PrivacySettings
          isAnonymous={formData.is_anonymous}
          visibility={formData.visibility}
          onAnonymousChange={(value) => setFormData({ ...formData, is_anonymous: value })}
          onVisibilityChange={(value) => setFormData({ ...formData, visibility: value })}
        />
      </div>

      <div className="flex gap-4 mt-6">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg shadow-blue-500/20"
        >
          {loading ? 'Creating...' : 'Create Post'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="px-6 py-3 border border-white/20 text-gray-300 rounded-lg hover:bg-white/5 hover:border-white/30 transition-all disabled:opacity-50 font-medium"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
