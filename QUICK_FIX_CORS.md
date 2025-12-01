# 🚨 Quick Fix: CORS_ORIGINS Error on Render

## The Error
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
pydantic_settings.exceptions.SettingsError: error parsing value for field "CORS_ORIGINS"
```

## The Fix (30 seconds)

### In Render Dashboard:

1. Go to your service → **Environment** tab
2. Find `CORS_ORIGINS`
3. Change from:
   ```
   ["https://your-app.vercel.app"]
   ```
   To:
   ```
   https://your-app.vercel.app,http://localhost:3000
   ```
4. Click **Save Changes**
5. Wait for auto-redeploy

### That's it! ✅

## Why?
Render treats environment variables as plain strings. The code now accepts comma-separated values instead of JSON arrays.

## Multiple Origins?
```
https://app1.com,https://app2.com,https://app3.com
```

## Single Origin?
```
https://your-app.vercel.app
```

## Empty/Default?
Leave it empty or delete it - defaults to `http://localhost:3000`

---

**Still having issues?** See `RENDER_DEPLOYMENT_FIX.md` for detailed troubleshooting.
