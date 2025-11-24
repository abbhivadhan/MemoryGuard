import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, Video, HelpCircle, FileText, Star, Eye, ExternalLink, ArrowLeft } from 'lucide-react';
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
        return <FileText className="w-4 h-4" />;
      case 'video':
        return <Video className="w-4 h-4" />;
      case 'qa':
        return <HelpCircle className="w-4 h-4" />;
      case 'guide':
        return <BookOpen className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      article: 'from-blue-500/20 to-blue-600/20 border-blue-500/30 text-blue-300',
      video: 'from-purple-500/20 to-purple-600/20 border-purple-500/30 text-purple-300',
      qa: 'from-green-500/20 to-green-600/20 border-green-500/30 text-green-300',
      guide: 'from-orange-500/20 to-orange-600/20 border-orange-500/30 text-orange-300',
    };
    return colors[type] || 'from-gray-500/20 to-gray-600/20 border-gray-500/30 text-gray-300';
  };

  if (selectedResource) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-6"
      >
        <motion.button
          whileHover={{ scale: 1.02, x: -5 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setSelectedResource(null)}
          className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Resources
        </motion.button>

        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6 flex-wrap">
            <span className={`px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2 bg-gradient-to-r ${getTypeColor(selectedResource.resource_type)} border backdrop-blur-sm`}>
              {getTypeIcon(selectedResource.resource_type)}
              {selectedResource.resource_type.toUpperCase()}
            </span>
            {selectedResource.is_featured && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="px-4 py-2 rounded-xl text-sm font-medium bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border border-yellow-500/30 text-yellow-300 flex items-center gap-2"
              >
                <Star className="w-4 h-4 fill-current" />
                Featured
              </motion.span>
            )}
          </div>

          <h1 className="text-4xl font-bold text-white mb-4">{selectedResource.title}</h1>

          {selectedResource.author && (
            <p className="text-gray-400 mb-2 flex items-center gap-2">
              <span className="text-blue-400">By</span> {selectedResource.author}
            </p>
          )}

          {selectedResource.description && (
            <p className="text-lg text-gray-300 mb-8 leading-relaxed">{selectedResource.description}</p>
          )}

          <div className="prose prose-invert max-w-none mb-8">
            <div className="text-gray-300 whitespace-pre-wrap leading-relaxed">{selectedResource.content}</div>
          </div>

          {selectedResource.source_url && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-6 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border border-blue-500/20 rounded-xl"
            >
              <p className="text-sm font-medium text-blue-300 mb-3 flex items-center gap-2">
                <ExternalLink className="w-4 h-4" />
                Source
              </p>
              <a
                href={selectedResource.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 text-sm break-all transition-colors underline"
              >
                {selectedResource.source_url}
              </a>
            </motion.div>
          )}

          <div className="mt-6 flex items-center gap-2 text-sm text-gray-400">
            <Eye className="w-4 h-4" />
            <span>{selectedResource.view_count} views</span>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <motion.div
          whileHover={{ rotate: 10 }}
          className="p-3 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl"
        >
          <BookOpen className="w-6 h-6 text-white" />
        </motion.div>
        <div>
          <h2 className="text-2xl font-bold text-white">Educational Resources</h2>
          <p className="text-gray-400 text-sm">
            Learn about Alzheimer's disease, prevention strategies, and expert advice
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="backdrop-blur-xl bg-white/5 rounded-xl border border-white/10 p-4">
        <div className="flex flex-wrap gap-3 items-center">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedType(undefined)}
            className={`px-4 py-2 rounded-lg transition-all font-medium ${
              selectedType === undefined
                ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            All Types
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedType('article')}
            className={`px-4 py-2 rounded-lg transition-all font-medium flex items-center gap-2 ${
              selectedType === 'article'
                ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <FileText className="w-4 h-4" />
            Articles
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedType('video')}
            className={`px-4 py-2 rounded-lg transition-all font-medium flex items-center gap-2 ${
              selectedType === 'video'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <Video className="w-4 h-4" />
            Videos
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedType('qa')}
            className={`px-4 py-2 rounded-lg transition-all font-medium flex items-center gap-2 ${
              selectedType === 'qa'
                ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            Q&A
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedType('guide')}
            className={`px-4 py-2 rounded-lg transition-all font-medium flex items-center gap-2 ${
              selectedType === 'guide'
                ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            Guides
          </motion.button>

          <div className="ml-auto">
            <label className="flex items-center gap-2 cursor-pointer backdrop-blur-sm bg-white/5 px-4 py-2 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
              <input
                type="checkbox"
                checked={showFeaturedOnly}
                onChange={(e) => setShowFeaturedOnly(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-gray-300 font-medium">Featured only</span>
            </label>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full"
          />
        </div>
      ) : error ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-r from-red-500/10 to-pink-500/10 border border-red-500/20 rounded-xl p-6 text-red-300"
        >
          {error}
        </motion.div>
      ) : resources.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-20 backdrop-blur-xl bg-white/5 rounded-xl border border-white/10"
        >
          <BookOpen className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <p className="text-lg text-gray-400">No resources found.</p>
          <p className="text-sm text-gray-500 mt-2">Try adjusting your filters</p>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <AnimatePresence>
            {resources.map((resource, index) => (
              <motion.div
                key={resource.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.02, y: -5 }}
                onClick={() => handleResourceClick(resource)}
                className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10 transition-all cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-4">
                  <span className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 bg-gradient-to-r ${getTypeColor(resource.resource_type)} border backdrop-blur-sm`}>
                    {getTypeIcon(resource.resource_type)}
                    {resource.resource_type.toUpperCase()}
                  </span>
                  {resource.is_featured && (
                    <motion.div
                      animate={{ rotate: [0, 10, -10, 0] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <Star className="w-5 h-5 text-yellow-400 fill-current" />
                    </motion.div>
                  )}
                </div>

                <h3 className="text-lg font-semibold text-white mb-3 group-hover:text-blue-300 transition-colors line-clamp-2">
                  {resource.title}
                </h3>

                {resource.description && (
                  <p className="text-sm text-gray-400 mb-4 line-clamp-3">
                    {resource.description}
                  </p>
                )}

                {resource.author && (
                  <p className="text-xs text-gray-500 mb-4 flex items-center gap-1">
                    <span className="text-blue-400">By</span> {resource.author}
                  </p>
                )}

                <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-white/10">
                  <span className="flex items-center gap-1">
                    <Eye className="w-3 h-3" />
                    {resource.view_count} views
                  </span>
                  <span className="text-blue-400 group-hover:text-blue-300 flex items-center gap-1 transition-colors">
                    Read more
                    <ExternalLink className="w-3 h-3" />
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}
    </motion.div>
  );
}
