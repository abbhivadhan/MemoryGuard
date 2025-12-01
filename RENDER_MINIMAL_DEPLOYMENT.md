# Render Minimal Deployment Guide

## 🎯 Deploy in 5 Minutes with Minimal Config

This guide shows you how to deploy with the absolute minimum required configuration.

## ✅ Required Environment Variables (Only 6!)

In Render Dashboard → Your Service → Environment, add:

```bash
# 1. Environment
ENVIRONMENT=production

# 2. Debug mode
DEBUG=false

# 3. Database (from Render PostgreSQL)
DATABASE_URL=<PASTE_INTERNAL_DATABASE_URL>

# 4. Redis (from Render Redis)
REDIS_URL=<PASTE_INTERNAL_REDIS_URL>

# 5. Security (generate new secret)
JWT_SECRET=<RUN: openssl rand -hex 32>

# 6. CORS (your frontend URL)
CORS_ORIGINS=https://your-frontend.vercel.app
```

**That's it!** These 6 variables are all you need to deploy.

## 🔧 Generate JWT Secret

On your local machine, run:
```bash
openssl rand -hex 32
```

Copy the output and use it as your `JWT_SECRET`.

## 📝 Get Database and Redis URLs

### Database URL
1. Render Dashboard → Your PostgreSQL Database
2. Copy the **"Internal Database URL"** (not External!)
3. Should look like: `postgresql://user:pass@hostname.internal:5432/database`

### Redis URL
1. Render Dashboard → Your Redis Instance
2. Copy the **"Internal Redis URL"** (not External!)
3. Should look like: `redis://hostname.internal:6379`

## 🚀 Deploy

1. Add the 6 environment variables above
2. Click **"Save Changes"**
3. Render will auto-deploy
4. Wait 5-10 minutes
5. Check logs for: `Application startup complete`

## ✅ Verify Deployment

Test these URLs (replace with your Render URL):

```bash
# Health check
curl https://your-backend.onrender.com/api/v1/health

# Should return: {"status":"healthy"}
```

## 🎨 Optional Features (Add Later)

### Google OAuth (for Google Sign-In)
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/api/v1/auth/google/callback
```

### Gemini AI (for AI features)
```bash
GEMINI_API_KEY=your-gemini-api-key
```

### Sentry (for error tracking)
```bash
SENTRY_DSN=your-sentry-dsn
SENTRY_ENABLED=true
```

## 🐛 Troubleshooting

### Error: "DATABASE_URL must be configured"
- Make sure you're using the **Internal** URL (not External)
- Check it starts with `postgresql://`

### Error: "CORS_ORIGINS" parsing error
- Use comma-separated format: `https://app1.com,https://app2.com`
- Don't use brackets: ~~`["https://app1.com"]`~~

### Error: "JWT_SECRET must be changed"
- Generate a new secret with `openssl rand -hex 32`
- Don't use the default value

### Service won't start
- Check logs in Render Dashboard
- Verify all 6 required variables are set
- Make sure `DEBUG=false` (not `true`)

## 📊 What Gets Deployed

With minimal config, you get:
- ✅ REST API endpoints
- ✅ Database connectivity
- ✅ Redis caching
- ✅ Health monitoring
- ✅ CORS protection
- ✅ JWT authentication
- ✅ Rate limiting

Without optional config, these features are disabled:
- ❌ Google OAuth (users can still register with email)
- ❌ AI features (Gemini)
- ❌ Error tracking (Sentry)

You can add these features later by adding the environment variables and redeploying.

## 🔐 Security Notes

- ✅ Always use **Internal** URLs for database and Redis
- ✅ Generate a unique `JWT_SECRET` (never use default)
- ✅ Set `DEBUG=false` in production
- ✅ Only add your actual frontend URL to `CORS_ORIGINS`
- ✅ Keep your environment variables secret

## 📚 Next Steps

1. ✅ Deploy with minimal config (this guide)
2. ✅ Test basic functionality
3. ✅ Add optional features as needed
4. ✅ Set up monitoring (Sentry)
5. ✅ Configure custom domain (optional)

## 💡 Pro Tips

- **Free Tier**: Service sleeps after 15 min inactivity
- **Paid Tier**: $7/month for always-on service
- **Auto-Deploy**: Push to GitHub → Render auto-deploys
- **Logs**: Real-time logs in Render Dashboard
- **Rollback**: Easy rollback to previous deploys

---

**Questions?** See `RENDER_QUICK_START.md` for detailed guide or `PRODUCTION_VALIDATION_FIX.md` for technical details.
