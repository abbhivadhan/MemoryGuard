import api from './api';

export interface CommunityPost {
  id: string;
  user: {
    id: string;
    name: string;
    is_anonymous: boolean;
  };
  title: string;
  content: string;
  category: 'general' | 'support' | 'tips' | 'questions' | 'resources';
  visibility: 'public' | 'members_only' | 'matched_users';
  is_flagged: boolean;
  view_count: number;
  reply_count: number;
  created_at: string;
  updated_at: string;
}

export interface CommunityReply {
  id: string;
  post_id: string;
  user: {
    id: string;
    name: string;
    is_anonymous: boolean;
  };
  content: string;
  is_flagged: boolean;
  created_at: string;
  updated_at: string;
}

export interface CommunityPostDetail extends CommunityPost {
  replies: CommunityReply[];
}

export interface CreatePostData {
  title: string;
  content: string;
  category: 'general' | 'support' | 'tips' | 'questions' | 'resources';
  visibility: 'public' | 'members_only' | 'matched_users';
  is_anonymous: boolean;
}

export interface CreateReplyData {
  content: string;
  is_anonymous: boolean;
}

export interface FlagContentData {
  reason: string;
  description?: string;
}

export interface EducationalResource {
  id: string;
  title: string;
  description?: string;
  content: string;
  resource_type: string;
  author?: string;
  source_url?: string;
  tags?: string;
  view_count: number;
  is_featured: boolean;
  created_at: string;
}

export interface UserMatch {
  user_id: string;
  match_score: number;
  match_reasons: string[];
  risk_profile_similarity?: number;
  disease_stage_match?: boolean;
}

const communityService = {
  // Get posts
  async getPosts(category?: string, skip = 0, limit = 20): Promise<CommunityPost[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    const response = await api.get(`/community/posts?${params.toString()}`);
    return response.data;
  },

  // Get single post with replies
  async getPost(postId: string): Promise<CommunityPostDetail> {
    const response = await api.get(`/community/posts/${postId}`);
    return response.data;
  },

  // Create post
  async createPost(data: CreatePostData): Promise<CommunityPost> {
    const response = await api.post('/community/posts', data);
    return response.data;
  },

  // Create reply
  async createReply(postId: string, data: CreateReplyData): Promise<CommunityReply> {
    const response = await api.post(`/community/posts/${postId}/reply`, data);
    return response.data;
  },

  // Flag post
  async flagPost(postId: string, data: FlagContentData): Promise<void> {
    await api.post(`/community/posts/${postId}/flag`, data);
  },

  // Flag reply
  async flagReply(replyId: string, data: FlagContentData): Promise<void> {
    await api.post(`/community/replies/${replyId}/flag`, data);
  },

  // Get educational resources
  async getResources(
    resourceType?: string,
    featuredOnly = false,
    skip = 0,
    limit = 20
  ): Promise<EducationalResource[]> {
    const params = new URLSearchParams();
    if (resourceType) params.append('resource_type', resourceType);
    if (featuredOnly) params.append('featured_only', 'true');
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    const response = await api.get(`/community/resources?${params.toString()}`);
    return response.data;
  },

  // Get single resource
  async getResource(resourceId: string): Promise<EducationalResource> {
    const response = await api.get(`/community/resources/${resourceId}`);
    return response.data;
  },

  // Get matched users
  async getMatchedUsers(): Promise<UserMatch[]> {
    const response = await api.get('/community/match-users');
    return response.data;
  },
};

export default communityService;
