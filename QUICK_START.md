# MemoryGuard - Quick Start Guide

## 🚀 Getting Started

### Current Status
✅ 3D Homepage with stunning animations  
✅ Email/Password authentication  
⚠️ Google OAuth (requires configuration)  
✅ Modern UI with glassmorphism effects  

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL
- Redis

## 🔧 Setup Instructions

### 1. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env` file (already created):
```env
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_API_URL=http://localhost:8000/api/v1
```

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/memoryguard
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your_google_client_id_here
```

Run database migrations:
```bash
alembic upgrade head
```

Start the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 🔐 Google OAuth Setup (Optional)

Google OAuth is optional - users can sign up with email/password. To enable Google OAuth:

1. Follow the detailed guide in `GOOGLE_OAUTH_SETUP.md`
2. Get your Google Client ID from Google Cloud Console
3. Update `VITE_GOOGLE_CLIENT_ID` in `frontend/.env`
4. Restart the frontend dev server

**Without Google OAuth configured:**
- The "Continue with Google" button will show a configuration message
- Users can still register and login with email/password
- All other features work normally

## 🎨 Features Implemented

### Homepage
- **3D Animations**: Dynamic scenes that change on scroll
  - Brain model with neural connections
  - DNA helix visualization
  - Neural network with pulsing nodes
  - Floating orbs with physics
- **Scroll Sections**: 4 informative sections with smooth transitions
- **Modern UI**: Glassmorphism, gradients, and smooth animations

### Authentication
- **Email/Password**: Full registration and login system
- **Google OAuth**: Optional social login
- **Session Management**: JWT tokens with refresh
- **Protected Routes**: Dashboard access control

### 3D Components
- `BrainModel`: Animated brain with deterioration effects
- `DNAHelix`: Rotating DNA double helix
- `NeuralNetwork`: Connected nodes with pulsing animations
- `FloatingOrbs`: Physics-based glowing spheres
- `PhysicsButton`: Interactive 3D buttons (currently not visible in 2D layout)

## 🧪 Testing the App

### Without Google OAuth
1. Navigate to `http://localhost:5173`
2. Use the email/password form to register
3. Login with your credentials
4. Access the dashboard

### With Google OAuth
1. Configure Google Client ID (see `GOOGLE_OAUTH_SETUP.md`)
2. Click "Continue with Google"
3. Sign in with your Google account
4. Access the dashboard

## 📁 Project Structure

```
memoryguard/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── 3d/          # 3D components
│   │   │   └── auth/        # Authentication components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── store/           # State management
│   └── .env                 # Environment variables
├── backend/
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   └── .env                # Environment variables
└── .kiro/specs/            # Feature specifications
```

## 🐛 Troubleshooting

### "Google Client ID not configured" message
- This is expected if you haven't set up Google OAuth yet
- Users can still use email/password authentication
- See `GOOGLE_OAUTH_SETUP.md` to enable Google OAuth

### 3D animations not showing
- Check browser console for WebGL errors
- Ensure your browser supports WebGL 2.0
- Try a different browser (Chrome/Firefox recommended)

### Backend connection errors
- Verify backend is running on `http://localhost:8000`
- Check `VITE_API_URL` in `frontend/.env`
- Ensure PostgreSQL and Redis are running

## 📚 Additional Documentation

- `GOOGLE_OAUTH_SETUP.md` - Detailed Google OAuth setup guide
- `SETUP.md` - Full project setup instructions
- `STRUCTURE.md` - Project architecture overview
- `.kiro/specs/alzheimers-web-app/` - Feature specifications

## 🎯 Next Steps

1. **Configure Google OAuth** (optional) - Follow `GOOGLE_OAUTH_SETUP.md`
2. **Set up database** - Create PostgreSQL database and run migrations
3. **Test authentication** - Try both email/password and Google login
4. **Explore 3D animations** - Scroll through the homepage
5. **Access dashboard** - Login and explore the dashboard features

## 💡 Tips

- The homepage 3D animations are GPU-intensive - performance may vary
- Use Chrome or Firefox for best 3D rendering performance
- The app works perfectly without Google OAuth configured
- All environment variables are in `.env` files (not committed to git)

## 🆘 Need Help?

- Check the browser console for errors
- Review the documentation files
- Ensure all services (PostgreSQL, Redis, Backend) are running
- Verify environment variables are set correctly
