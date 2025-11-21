# Google OAuth Setup Guide

## Overview
This guide will help you set up Google OAuth authentication for the MemoryGuard application.

## Prerequisites
- A Google account
- Access to Google Cloud Console

## Step-by-Step Instructions

### 1. Access Google Cloud Console
Go to [Google Cloud Console](https://console.cloud.google.com/)

### 2. Create or Select a Project
- Click on the project dropdown at the top of the page
- Either select an existing project or click "New Project"
- If creating new:
  - Enter project name: `MemoryGuard` (or your preferred name)
  - Click "Create"

### 3. Enable Google+ API (or Google Identity Services)
- In the left sidebar, go to "APIs & Services" > "Library"
- Search for "Google+ API" or "Google Identity Services"
- Click on it and press "Enable"

### 4. Create OAuth 2.0 Credentials
- Go to "APIs & Services" > "Credentials"
- Click "Create Credentials" > "OAuth client ID"
- If prompted, configure the OAuth consent screen first:
  - Choose "External" user type
  - Fill in required fields:
    - App name: `MemoryGuard`
    - User support email: Your email
    - Developer contact: Your email
  - Click "Save and Continue"
  - Skip scopes (click "Save and Continue")
  - Add test users if needed
  - Click "Save and Continue"

### 5. Configure OAuth Client ID
- Application type: Select "Web application"
- Name: `MemoryGuard Web Client`
- Authorized JavaScript origins:
  - Add: `http://localhost:5173` (for development)
  - Add: `http://localhost:3000` (alternative port)
  - Add your production URL when ready
- Authorized redirect URIs:
  - Add: `http://localhost:5173`
  - Add: `http://localhost:3000`
  - Add your production URL when ready
- Click "Create"

### 6. Copy Your Client ID
- After creation, a dialog will show your Client ID and Client Secret
- Copy the **Client ID** (it looks like: `xxxxx.apps.googleusercontent.com`)
- You don't need the Client Secret for frontend OAuth

### 7. Update Environment Variables
Open `frontend/.env` and replace the placeholder:

```env
VITE_GOOGLE_CLIENT_ID=your_actual_client_id_here.apps.googleusercontent.com
```

### 8. Restart Development Server
After updating the `.env` file, restart your Vite development server:

```bash
cd frontend
npm run dev
```

## Testing Google OAuth

1. Navigate to `http://localhost:5173`
2. Click on the "Continue with Google" button in the auth form
3. You should see the Google sign-in popup
4. Select your Google account
5. Grant permissions
6. You should be redirected to the dashboard

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Make sure `http://localhost:5173` is added to both:
  - Authorized JavaScript origins
  - Authorized redirect URIs

### Error: "Access blocked: This app's request is invalid"
- Check that you've configured the OAuth consent screen
- Make sure your email is added as a test user (for External apps in testing mode)

### Google Button Not Showing
- Verify `VITE_GOOGLE_CLIENT_ID` is set in `frontend/.env`
- Check browser console for errors
- Restart the development server after changing `.env`

## Production Deployment

When deploying to production:

1. Add your production domain to Authorized JavaScript origins:
   - Example: `https://memoryguard.com`

2. Add your production domain to Authorized redirect URIs:
   - Example: `https://memoryguard.com`

3. Update the OAuth consent screen:
   - Change from "Testing" to "In Production"
   - Complete the verification process if required

4. Set the environment variable in your production environment:
   ```
   VITE_GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   ```

## Security Notes

- Never commit your actual Client ID to public repositories (use environment variables)
- The `.env` file is already in `.gitignore`
- For production, use proper secrets management
- Regularly rotate credentials if compromised

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Sign-In for Websites](https://developers.google.com/identity/sign-in/web)
- [OAuth 2.0 Scopes](https://developers.google.com/identity/protocols/oauth2/scopes)
