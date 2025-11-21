import { useState } from 'react';

interface FlaggedContent {
  id: string;
  type: 'post' | 'reply';
  content_id: string;
  title?: string;
  content: string;
  author: string;
  reporter: string;
  reason: string;
  description?: string;
  created_at: string;
  status: 'pending' | 'reviewed' | 'resolved';
}

export default function ModerationDashboard() {
  const [flaggedContent] = useState<FlaggedContent[]>([
    // Mock data - in production this would come from an API
  ]);
  const [filter, setFilter] = useState<'all' | 'pending' | 'reviewed' | 'resolved'>('pending');

  const handleReview = (contentId: string, action: 'approve' | 'remove') => {
    // In production, this would call an API endpoint
    console.log(`${action} content ${contentId}`);
    alert(`Content ${action === 'approve' ? 'approved' : 'removed'}`);
  };

  const filteredContent = flaggedContent.filter(
    item => filter === 'all' || item.status === filter
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-6">
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
        </svg>
        <h2 className="text-2xl font-bold text-gray-900">Content Moderation</h2>
      </div>

      <p className="text-gray-600 mb-6">
        Review and moderate flagged content to maintain community standards.
      </p>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 font-medium transition-colors ${
            filter === 'all'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('pending')}
          className={`px-4 py-2 font-medium transition-colors ${
            filter === 'pending'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Pending
        </button>
        <button
          onClick={() => setFilter('reviewed')}
          className={`px-4 py-2 font-medium transition-colors ${
            filter === 'reviewed'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Reviewed
        </button>
        <button
          onClick={() => setFilter('resolved')}
          className={`px-4 py-2 font-medium transition-colors ${
            filter === 'resolved'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Resolved
        </button>
      </div>

      {/* Moderation guidelines */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-2">Moderation Guidelines</h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• Remove content that contains personal attacks or harassment</li>
          <li>• Remove content with personal identifiable information (PII)</li>
          <li>• Remove spam, advertising, or promotional content</li>
          <li>• Remove medical advice that could be harmful</li>
          <li>• Approve content that is flagged incorrectly</li>
        </ul>
      </div>

      {/* Flagged content list */}
      {filteredContent.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-lg">No flagged content to review</p>
          <p className="text-sm mt-2">All content has been moderated</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredContent.map((item) => (
            <div
              key={item.id}
              className="border border-red-200 rounded-lg p-4 bg-red-50"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-1 bg-red-200 text-red-800 text-xs font-medium rounded">
                      {item.type}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      item.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : item.status === 'reviewed'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                  {item.title && (
                    <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                  )}
                  <p className="text-sm text-gray-600">By {item.author}</p>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>

              <div className="mb-3 p-3 bg-white rounded border border-gray-200">
                <p className="text-sm text-gray-700">{item.content}</p>
              </div>

              <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm font-medium text-gray-900 mb-1">
                  Flagged by: {item.reporter}
                </p>
                <p className="text-sm text-gray-700">
                  <strong>Reason:</strong> {item.reason}
                </p>
                {item.description && (
                  <p className="text-sm text-gray-700 mt-1">
                    <strong>Details:</strong> {item.description}
                  </p>
                )}
              </div>

              {item.status === 'pending' && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleReview(item.content_id, 'approve')}
                    className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Approve Content
                  </button>
                  <button
                    onClick={() => handleReview(item.content_id, 'remove')}
                    className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Remove Content
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Statistics */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Pending Review</p>
          <p className="text-2xl font-bold text-yellow-800">
            {flaggedContent.filter(i => i.status === 'pending').length}
          </p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Reviewed</p>
          <p className="text-2xl font-bold text-blue-800">
            {flaggedContent.filter(i => i.status === 'reviewed').length}
          </p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Resolved</p>
          <p className="text-2xl font-bold text-green-800">
            {flaggedContent.filter(i => i.status === 'resolved').length}
          </p>
        </div>
      </div>
    </div>
  );
}
