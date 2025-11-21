# Dev Login Setup Complete! 🎉

## Services Running

✅ **Backend API**: http://localhost:8000
✅ **Frontend**: http://localhost:3001

## Dev Login Credentials

```
Email: abbhivadhan279@gmail.com
Password: 123456
```

## How to Login

1. Open your browser and go to: **http://localhost:3001**

2. On the login page, enter:
   - Email: `abbhivadhan279@gmail.com`
   - Password: `123456`

3. Click "Sign In" or "Login"

4. You should be redirected to the dashboard!

## What Was Fixed

1. ✅ Added `/auth/dev-login` endpoint that bypasses database
2. ✅ Fixed missing dependencies (psycopg2, email-validator, libomp)
3. ✅ Fixed model errors (relationship column conflict, missing imports)
4. ✅ Made database connection optional in dev mode
5. ✅ Disabled XGBoost ML models temporarily (they need PostgreSQL data)
6. ✅ Started both backend and frontend servers

## API Endpoints Available

- `POST /api/v1/auth/dev-login` - Dev login (no database needed)
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/health` - Health check
- `GET /docs` - Swagger API documentation

## Testing the API

```bash
# Test dev login
curl -X POST http://localhost:8000/api/v1/auth/dev-login \
  -H "Content-Type: application/json" \
  -d '{"email":"abbhivadhan279@gmail.com","password":"123456"}'

# Test health endpoint
curl http://localhost:8000/api/v1/health

# View API docs
open http://localhost:8000/docs
```

## Notes

- This is a **development-only** setup
- The ML features (risk assessment) won't work without a database
- To enable full features, you'll need to set up PostgreSQL
- The dev user ID is `dev-user-123`

## Stopping Services

```bash
# Stop backend
lsof -ti:8000 | xargs kill

# Stop frontend  
lsof -ti:3001 | xargs kill
```

## Next Steps

To enable full functionality:
1. Set up PostgreSQL database
2. Run database migrations
3. Re-enable ML model imports
4. Add real user data

Enjoy testing! 🚀
