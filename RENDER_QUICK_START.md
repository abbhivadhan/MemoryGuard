# 🚀 Render Deployment - Quick Start

Deploy your MemoryGuard backend to Render in 15 minutes!

## 📋 What You Need

1. ✅ Render account (sign up at https://render.com)
2. ✅ GitHub repository with your code
3. ✅ Google OAuth credentials
4. ✅ Google Gemini API key
5. ✅ Vercel frontend URL

## 🎯 3-Step Deployment

### Step 1: Create Database (2 minutes)

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in:
   - Name: `memoryguard-db`
   - Database: `memoryguard`
   - Region: Choose closest to you
   - Plan: **Free** (or paid)
4. Click **"Create Database"**
5. 📋 **Copy the "Internal Database URL"** - you'll need this!

### Step 2: Create Redis (2 minutes)

1. Click **"New +"** → **"Redis"**
2. Fill in:
   - Name: `memoryguard-redis`
   - Region: Same as database
   - Plan: **Free** (or paid)
3. Click **"Create Redis"**
4. 📋 **Copy the "Internal Redis URL"** - you'll need this!

### Step 3: Deploy Backend (10 minutes)

1. Click **"New +"** → **"Web Service"**
2. Connect your **GitHub repository**
3. Configure:
   ```
   Name: memoryguard-backend
   Region: Same as database
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: chmod +x start.sh && ./start.sh
   Plan: Free (or paid)
   ```

4. Click **"Advanced"** → Add Environment Variables:

   **Quick Copy-Paste Template:**
   ```bash
   APP_NAME=MemoryGuard
   ENVIRONMENT=production
   DEBUG=false
   DATABASE_URL=<PASTE_YOUR_INTERNAL_DATABASE_URL>
   REDIS_URL=<PASTE_YOUR_INTERNAL_REDIS_URL>
   JWT_SECRET=<RUN: openssl rand -hex 32>
   GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
   GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
   GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
   CORS_ORIGINS=["https://your-app.vercel.app"]
   ```

   See `backend/.env.production.template` for complete list!

5. Click **"Create Web Service"**

6. ⏳ Wait 5-10 minutes for deployment

## ✅ Verify Deployment

Once deployed, test these URLs (replace with your Render URL):

1. **Root**: https://your-backend.onrender.com/
   - Should show: `{"message": "MemoryGuard API", "status": "running"}`

2. **API Docs**: https://your-backend.onrender.com/docs
   - Should show: Swagger UI

3. **Health Check**: https://your-backend.onrender.com/api/v1/health
   - Should show: `{"status": "healthy"}`

## 🔗 Connect Frontend

1. Go to **Vercel Dashboard**
2. Your Project → **Settings** → **Environment Variables**
3. Update or add:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```
4. **Redeploy** your frontend

## 🎉 Done!

Your backend is now live! Test by:
- Opening your Vercel frontend
- Logging in with Google
- Creating a health metric
- Checking the dashboard

## 🐛 Common Issues

### Build Fails
- Check logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure scripts are executable

### Database Connection Error
- Use **Internal** Database URL (not External)
- Check database is in same region
- Verify URL format is correct

### CORS Error
- Add your Vercel URL to `CORS_ORIGINS`
- Format: `["https://your-app.vercel.app"]`
- Redeploy after updating

### 502 Bad Gateway
- Check service logs for errors
- Verify migrations ran: `alembic upgrade head`
- Restart service in Render dashboard

## 📚 Need More Help?

- **Full Guide**: See `RENDER_DEPLOYMENT_GUIDE.md`
- **Checklist**: See `DEPLOYMENT_CHECKLIST.md`
- **Render Docs**: https://render.com/docs
- **Render Support**: https://community.render.com

## 💡 Pro Tips

1. **Free Tier**: Service sleeps after 15 min inactivity (first request will be slow)
2. **Paid Tier**: $7/month for always-on service
3. **Logs**: Real-time logs available in Render dashboard
4. **Auto-Deploy**: Push to GitHub → Render auto-deploys
5. **Custom Domain**: Add in Render settings (paid plans)

## 🔐 Security Checklist

- [ ] JWT_SECRET is unique (not default)
- [ ] DEBUG is set to false
- [ ] CORS_ORIGINS only includes your domains
- [ ] Google OAuth redirect URI is correct
- [ ] API keys are kept secret
- [ ] Database uses Internal URL
- [ ] HTTPS is enabled (automatic on Render)

## 📊 Monitoring

### View Logs
Render Dashboard → Your Service → **Logs** tab

### Check Metrics
Render Dashboard → Your Service → **Metrics** tab

### Database Stats
Render Dashboard → Your Database → **Info** tab

## 🔄 Updates & Maintenance

### Deploy Updates
1. Push to GitHub
2. Render auto-deploys
3. Check logs for success

### Manual Deploy
Render Dashboard → Your Service → **Manual Deploy**

### Run Migrations
Render Dashboard → Your Service → **Shell** → `alembic upgrade head`

### Restart Service
Render Dashboard → Your Service → **Manual Deploy** → **Deploy latest commit**

---

**Questions?** Check the full deployment guide or reach out to Render support!
