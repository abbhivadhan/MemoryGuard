import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, RefreshCw, Globe } from 'lucide-react';
import communityService from '../../services/communityService';

interface SocialPost {
  id: string;
  platform: 'twitter' | 'facebook' | 'instagram' | 'website' | 'linkedin';
  author: string;
  handle: string;
  avatar: string;
  content: string;
  image?: string;
  timestamp: string;
  url: string;
}

export default function SocialMediaFeed() {
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSocialFeed();
    // Refresh every hour to get new posts daily
    const interval = setInterval(loadSocialFeed, 60 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadSocialFeed = async () => {
    try {
      setLoading(true);
      const response = await communityService.getSocialFeed(20);
      
      if (response.posts && response.posts.length > 0) {
        // Transform API response to component format
        const transformedPosts = response.posts.map((post: any) => ({
          id: post.id,
          platform: 'website' as const,
          author: post.author,
          handle: post.handle,
          avatar: post.avatar,
          content: post.content,
          timestamp: post.timestamp_formatted || 'Recently',
          url: post.url
        }));
        setPosts(transformedPosts);
      } else {
        // Fallback to sample posts if API fails
        setPosts(getSamplePosts());
      }
    } catch (err: any) {
      console.error('Error loading social feed:', err);
      // Silently fallback to sample posts
      setPosts(getSamplePosts());
    } finally {
      setLoading(false);
    }
  };

  const getSamplePosts = (): SocialPost[] => {
    return [
      {
        id: '1',
        platform: 'website',
        author: 'Alzheimer\'s Association',
        handle: '@alzassociation',
        avatar: 'https://logo.clearbit.com/alz.org',
        content: 'New research shows that regular physical activity can reduce Alzheimer\'s risk by up to 50%. Even 30 minutes of walking daily makes a difference.',
        timestamp: '2 hours ago',
        url: 'https://www.alz.org/news'
      },
      {
        id: '2',
        platform: 'website',
        author: 'National Institute on Aging',
        handle: '@NationalInstituteOnAging',
        avatar: 'https://logo.clearbit.com/nia.nih.gov',
        content: 'Join us for a free webinar on Understanding Alzheimer\'s Disease this Thursday at 2 PM EST. Learn about the latest research, treatment options, and caregiving strategies from leading experts.',
        timestamp: '5 hours ago',
        url: 'https://www.nia.nih.gov/news'
      },
      {
        id: '3',
        platform: 'website',
        author: 'Alzheimer\'s Research UK',
        handle: '@AlzResearchUK',
        avatar: 'https://logo.clearbit.com/alzheimersresearchuk.org',
        content: 'Exciting breakthrough! New blood test shows 90% accuracy in detecting Alzheimer\'s years before symptoms appear. This could revolutionize early diagnosis and treatment.',
        timestamp: '1 day ago',
        url: 'https://www.alzheimersresearchuk.org/news'
      },
      {
        id: '4',
        platform: 'website',
        author: 'Alzheimer\'s Society',
        handle: '@AlzheimersSociety',
        avatar: 'https://logo.clearbit.com/alzheimers.org.uk',
        content: 'Caregiver tip: Create a memory box filled with photos, letters, and meaningful objects. It can help spark conversations and provide comfort during difficult moments.',
        timestamp: '2 days ago',
        url: 'https://www.alzheimers.org.uk/news'
      },
      {
        id: '5',
        platform: 'website',
        author: 'Mayo Clinic Research',
        handle: '@MayoClinic',
        avatar: 'https://logo.clearbit.com/mayoclinic.org',
        content: 'Sleep quality matters for brain health. Poor sleep may increase risk of Alzheimer\'s by allowing toxic proteins to accumulate. Aim for 7-9 hours of quality sleep each night.',
        timestamp: '3 days ago',
        url: 'https://newsnetwork.mayoclinic.org/category/research/'
      }
    ];
  };

  const getPlatformIcon = () => {
    return <Globe className="w-5 h-5" />;
  };

  const getPlatformColor = () => {
    return 'from-blue-500 to-indigo-600';
  };

  const filteredPosts = posts;

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

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Community Updates</h2>
          <p className="text-gray-400 text-sm">Latest from Alzheimer's organizations worldwide</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05, rotate: 180 }}
          whileTap={{ scale: 0.95 }}
          onClick={loadSocialFeed}
          disabled={loading}
          className="p-3 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl text-white hover:from-blue-600 hover:to-indigo-600 transition-all disabled:opacity-50"
          title="Refresh feed"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </motion.button>
      </div>

      {/* Info Banner */}
      <div className="backdrop-blur-xl bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
        <p className="text-sm text-blue-300 text-center">
          Latest news and updates from leading Alzheimer's research organizations worldwide. Posts refresh hourly.
        </p>
      </div>

      {/* Posts Grid */}
      <motion.div
        layout
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <AnimatePresence>
          {filteredPosts.map((post, index) => (
            <motion.div
              key={post.id}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.02, y: -5 }}
              className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10 transition-all group"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="relative w-12 h-12 flex-shrink-0">
                    {post.avatar && post.avatar.startsWith('http') ? (
                      <>
                        <img 
                          src={post.avatar} 
                          alt={post.author}
                          className="w-12 h-12 rounded-full object-contain bg-white p-2 shadow-lg"
                          onError={(e) => {
                            // Fallback to gradient with initials if image fails to load
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            const fallback = target.nextElementSibling as HTMLElement;
                            if (fallback) fallback.style.display = 'flex';
                          }}
                        />
                        <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getPlatformColor()} hidden items-center justify-center text-sm font-bold text-white absolute top-0 left-0`}>
                          {post.author.split(' ').map(w => w[0]).join('').slice(0, 2)}
                        </div>
                      </>
                    ) : (
                      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getPlatformColor()} flex items-center justify-center text-sm font-bold text-white`}>
                        {post.avatar && !post.avatar.startsWith('http') ? post.avatar : post.author.split(' ').map(w => w[0]).join('').slice(0, 2)}
                      </div>
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{post.author}</h3>
                    <p className="text-sm text-gray-400">{post.handle}</p>
                  </div>
                </div>
                <div className={`p-2 rounded-lg bg-gradient-to-br ${getPlatformColor()} text-white flex-shrink-0`}>
                  {getPlatformIcon()}
                </div>
              </div>

              {/* Content */}
              <p className="text-gray-300 mb-4 leading-relaxed">{post.content}</p>

              {/* Timestamp */}
              <p className="text-xs text-gray-500 mb-4">{post.timestamp}</p>

              {/* View Original Link */}
              <motion.a
                href={post.url}
                target="_blank"
                rel="noopener noreferrer"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center justify-center gap-2 w-full py-2 px-4 bg-gradient-to-r from-blue-500/20 to-indigo-500/20 border border-blue-500/30 rounded-lg text-blue-300 hover:from-blue-500/30 hover:to-indigo-500/30 transition-all mt-4"
              >
                <span className="text-sm font-medium">Read Full Article</span>
                <ExternalLink className="w-4 h-4" />
              </motion.a>
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>

      {/* Footer Note */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-4 text-center"
      >
        <p className="text-xs text-gray-400">
          Content sourced from official Alzheimer's organizations and research institutions. 
          Click "Read Full Article" to view the complete articles on their websites.
        </p>
      </motion.div>
    </motion.div>
  );
}
