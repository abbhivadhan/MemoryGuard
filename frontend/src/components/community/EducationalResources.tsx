import { useState, useEffect } from 'react';
import communityService, { EducationalResource } from '../../services/communityService';

export default function EducationalResources() {
  const [resources, setResources] = useState<EducationalResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string | undefined>(undefined);
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
  const [selectedResource, setSelectedResource] = useState<EducationalResource | null>(null);

  useEffect(() => {
    loadResources();
  }, [selectedType, showFeaturedOnly]);

  const loadResources = async () => {
    try {
      setLoading(true);
      const data = await communityService.getResources(selectedType, showFeaturedOnly);
      setResources(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const handleResourceClick = async (resource: EducationalResource) => {
    setSelectedResource(resource);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'article':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'video':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        );
      case 'qa':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'guide':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      article: 'bg-blue-100 text-blue-800',
      video: 'bg-purple-100 text-purple-800',
      qa: 'bg-green-100 text-green-800',
      guide: 'bg-orange-100 text-orange-800',
    };
    return colors[type] || 'bg-white/10 text-blue-50';
  };

  if (selectedResource) {
    return (
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6">
        <button
          onClick={() => setSelectedResource(null)}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Resources
        </button>

        <div className="flex items-center gap-2 mb-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 ${getTypeColor(selectedResource.resource_type)}`}>
            {getTypeIcon(selectedResource.resource_type)}
            {selectedResource.resource_type}
          </span>
          {selectedResource.is_featured && (
            <span className="px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
              ⭐ Featured
            </span>
          )}
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-4">{selectedResource.title}</h1>

        {selectedResource.author && (
          <p className="text-gray-400 mb-2">By {selectedResource.author}</p>
        )}

        {selectedResource.description && (
          <p className="text-lg text-gray-300 mb-6">{selectedResource.description}</p>
        )}

        <div className="prose max-w-none mb-6">
          <div className="text-gray-300 whitespace-pre-wrap">{selectedResource.content}</div>
        </div>

        {selectedResource.source_url && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm font-medium text-gray-900 mb-2">Source</p>
            <a
              href={selectedResource.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 text-sm break-all"
            >
              {selectedResource.source_url}
            </a>
          </div>
        )}

        <div className="mt-4 text-sm text-gray-500">
          {selectedResource.view_count} views
        </div>
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <h2 className="text-2xl font-bold text-gray-900">Educational Resources</h2>
      </div>

      <p className="text-gray-400 mb-6">
        Learn about Alzheimer's disease, prevention strategies, and expert advice.
      </p>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4 items-center">
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedType(undefined)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedType === undefined
                ? 'bg-blue-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-gray-200'
            }`}
          >
            All Types
          </button>
          <button
            onClick={() => setSelectedType('article')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedType === 'article'
                ? 'bg-blue-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-gray-200'
            }`}
          >
            Articles
          </button>
          <button
            onClick={() => setSelectedType('video')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedType === 'video'
                ? 'bg-blue-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-gray-200'
            }`}
          >
            Videos
          </button>
          <button
            onClick={() => setSelectedType('qa')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedType === 'qa'
                ? 'bg-blue-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-gray-200'
            }`}
          >
            Q&A
          </button>
          <button
            onClick={() => setSelectedType('guide')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedType === 'guide'
                ? 'bg-blue-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-gray-200'
            }`}
          >
            Guides
          </button>
        </div>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showFeaturedOnly}
            onChange={(e) => setShowFeaturedOnly(e.target.checked)}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-300">Featured only</span>
        </label>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          {error}
        </div>
      ) : resources.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No resources found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {resources.map((resource) => (
            <div
              key={resource.id}
              onClick={() => handleResourceClick(resource)}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getTypeColor(resource.resource_type)}`}>
                  {getTypeIcon(resource.resource_type)}
                  {resource.resource_type}
                </span>
                {resource.is_featured && (
                  <span className="text-yellow-500">⭐</span>
                )}
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {resource.title}
              </h3>

              {resource.description && (
                <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                  {resource.description}
                </p>
              )}

              {resource.author && (
                <p className="text-xs text-gray-500 mb-2">By {resource.author}</p>
              )}

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{resource.view_count} views</span>
                <span className="text-blue-600 hover:text-blue-700">Read more →</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
