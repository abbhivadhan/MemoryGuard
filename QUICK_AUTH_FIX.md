# Quick Auth Fix for Medication Testing

## Problem
Getting 401 Unauthorized when trying to access `/api/v1/medications`

## Solution

### Option 1: Login via UI (Recommended)
1. Go to the home page: `http://localhost:5173/`
2. Click "Sign in with Google" or use email/password
3. Once logged in, go to Memory Assistant page
4. Try accessing medications again

### Option 2: Check if Token Exists
Open browser console and run:
```javascript
localStorage.getItem('access_token')
```

If it returns `null`, you're not logged in.

### Option 3: Manual Login via Console
If you have a test account, you can login via console:

```javascript
// Login with email/password
fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'your-password'
  })
})
.then(r => r.json())
.then(data => {
  localStorage.setItem('access_token', data.access_token);
  console.log('Logged in!', data.user);
  location.reload();
});
```

### Option 4: Use Dev Login (If Available)
Check if there's a dev login endpoint in the backend:

```javascript
// Dev login (if enabled)
fetch('http://localhost:8000/api/v1/auth/dev-login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'dev@example.com'
  })
})
.then(r => r.json())
.then(data => {
  localStorage.setItem('access_token', data.access_token);
  console.log('Logged in!', data.user);
  location.reload();
});
```

## After Login

Once you're logged in, check the medications endpoint:

```javascript
// Check if medications load
fetch('http://localhost:8000/api/v1/medications/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(data => console.log('Medications:', data));
```

## Debug Adherence Calculation

Once medications load, check the adherence data:

```javascript
// Get medications and check adherence log
fetch('http://localhost:8000/api/v1/medications/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(medications => {
  medications.forEach(med => {
    console.log('Medication:', med.name);
    console.log('Schedule:', med.schedule);
    console.log('Adherence Log:', med.adherence_log);
    console.log('---');
  });
});
```

## Next Steps

1. Login first
2. Then we can debug the adherence calculation
3. The adherence showing 0% is a separate issue from the 401 error
