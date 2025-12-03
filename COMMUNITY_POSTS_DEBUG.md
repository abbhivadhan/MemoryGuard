# Community Posts Not Showing - Debug Guide

## Status
- ✅ Database has 11 posts (verified by running seed script)
- ✅ Backend API endpoint exists at `/api/v1/community/posts`
- ✅ Frontend service is correctly configured
- ❓ Posts not displaying in the UI

## Possible Issues

### 1. Authentication Problem
The API requires authentication. If the user is not properly logged in, the API will return 401.

**Check:**
- Open browser DevTools → Network tab
- Navigate to Community page
- Look for the `/api/v1/community/posts` request
- Check if it returns 401 Unauthorized or 403 Forbidden

**Fix if needed:**
- Ensure user is logged in
- Check if access_token is in localStorage
- Verify token is being sent in Authorization header

### 2. CORS Issue
If the frontend is on a different domain than the backend, CORS might be blocking the request.

**Check:**
- Look for CORS errors in browser console
- Check if OPTIONS preflight request succeeds

### 3. API Response Format Mismatch
The backend might be returning data in a different format than expected.

**Check:**
- Look at the actual API response in Network tab
- Compare with the TypeScript interface in `communityService.ts`

### 4. Frontend Error Handling
The error might be silently caught and not displayed.

**Debug Steps:**

1. **Add console logging to PostList component:**
```typescript
const loadPosts = async () => {
  try {
    setLoading(true);
    console.log('Fetching posts with category:', category);
    const data = await communityService.getPosts(category);
    console.log('Posts received:', data);
    setPosts(data);
  } catch (err: any) {
    console.error('Error loading posts:', err);
    console.error('Error response:', err.response);
    setError(err.response?.data?.detail || 'Failed to load posts');
  } finally {
    setLoading(false);
  }
};
```

2. **Check browser console for:**
   - Any error messages
   - The actual API response
   - Network request details

3. **Test API directly:**
```bash
# Get a valid token first by logging in
# Then test the API:
curl -X GET "https://memoryguard-backend.onrender.com/api/v1/community/posts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Quick Fix to Test

Add this temporary debug component to see what's happening:

```typescript
// Add to PostList.tsx after the loadPosts function
useEffect(() => {
  console.log('PostList mounted');
  console.log('Category:', category);
  console.log('User:', user);
  console.log('Auth token:', localStorage.getItem('access_token'));
}, []);
```

## Most Likely Issue

Based on the logs showing "JWT decode error: Not enough segments", the issue is likely:

**The user is not properly authenticated or the token is invalid/missing.**

### Solution:
1. Log out and log back in
2. Check if the token is being stored correctly after login
3. Verify the token is being sent with API requests

## Backend Verification

Run this to check if posts exist and are accessible:

```bash
cd backend
python3 -c "
from app.core.database import SessionLocal
from app.models.community_post import CommunityPost

db = SessionLocal()
posts = db.query(CommunityPost).all()
print(f'Total posts: {len(posts)}')
for post in posts[:3]:
    print(f'- {post.title} (category: {post.category}, visibility: {post.visibility})')
db.close()
"
```

## Next Steps

1. Check browser console for errors
2. Check Network tab for API request/response
3. Verify user is logged in with valid token
4. If still not working, add console.log statements to debug
