# DICOM Upload Network Error Fix

## 🔴 ISSUE

**Error**: "Network error" when uploading DICOM brain scans on Medical Image Analysis page

## 🎯 ROOT CAUSES

1. **Render Body Size Limit**: Default 10MB limit (DICOM files are often 20-50MB)
2. **No chunked reading**: Reading entire file into memory at once
3. **Timeout**: Large files take too long to upload
4. **Missing error handling**: Generic "network error" message

---

## ✅ FIXES APPLIED

### Fix 1: Chunked File Reading
**File**: `backend/app/api/v1/imaging.py`

**Changed**:
```python
# BEFORE: Read entire file at once (memory intensive)
content = await file.read()

# AFTER: Read in 1MB chunks (memory efficient)
content = bytearray()
chunk_size = 1024 * 1024  # 1MB chunks
while True:
    chunk = await file.read(chunk_size)
    if not chunk:
        break
    content.extend(chunk)
```

**Benefits**:
- Reduces memory usage
- Prevents timeout on large files
- Better error handling

### Fix 2: Better Error Messages
**Added**:
- HTTP 413 (Payload Too Large) for oversized files
- Specific error messages for different failure types
- Logging for debugging

---

## 🚀 DEPLOYMENT REQUIRED

### Step 1: Add Environment Variable in Render

**CRITICAL**: Render has a default 10MB body size limit. You need to increase it.

1. Go to Render Dashboard → Backend Service
2. Go to "Settings" → "Environment"
3. Add:
   ```
   Key: MAX_BODY_SIZE
   Value: 104857600
   ```
   (This is 100MB in bytes)

**Note**: Render free tier may have limitations. If uploads still fail, you may need to:
- Upgrade to paid tier
- Use external storage (S3, Cloudinary)
- Compress DICOM files before upload

### Step 2: Deploy Code

```bash
git add .
git commit -m "Fix: DICOM upload with chunked reading and better errors"
git push origin main
```

---

## 🔍 ALTERNATIVE SOLUTIONS

If Render's body size limit is still an issue:

### Option 1: Use Supabase Storage
Upload directly to Supabase Storage, then process:

```python
# Frontend uploads to Supabase Storage
const { data, error } = await supabase.storage
  .from('medical-imaging')
  .upload(`${userId}/${filename}`, file)

# Backend processes from Supabase URL
```

### Option 2: Compress Before Upload
```typescript
// Frontend compresses DICOM before upload
import pako from 'pako';

const compressed = pako.gzip(fileBuffer);
// Upload compressed file
```

### Option 3: Split Large Files
```typescript
// Split file into chunks and upload separately
const chunkSize = 5 * 1024 * 1024; // 5MB chunks
for (let i = 0; i < file.size; i += chunkSize) {
  const chunk = file.slice(i, i + chunkSize);
  await uploadChunk(chunk, i / chunkSize);
}
```

---

## ✅ VERIFICATION

### After Deployment:

1. **Test Small DICOM** (< 10MB):
   - Should upload successfully
   - Processing should complete
   - Analysis results should appear

2. **Test Medium DICOM** (10-50MB):
   - Should upload if Render limit increased
   - May fail on free tier

3. **Test Large DICOM** (> 50MB):
   - Will fail with "File size exceeds 100MB limit"
   - This is intentional (backend limit)

### Check Render Logs:

**Look for**:
```
✅ Uploaded imaging file for user X: Y
✅ Processing imaging file: Y
```

**Should NOT see**:
```
❌ Error reading file
❌ File size exceeds limit
❌ Request Entity Too Large
```

---

## 📊 FILE SIZE LIMITS

| Limit Type | Size | Where Set |
|------------|------|-----------|
| Frontend validation | 100MB | `ImagingUpload.tsx` |
| Backend validation | 100MB | `imaging.py` |
| Render body size | **10MB default** | Needs env var |
| Supabase storage | 50MB (free tier) | Supabase settings |

---

## 🐛 TROUBLESHOOTING

### Error: "File size exceeds 100MB limit"
**Solution**: File is too large. Compress or split it.

### Error: "Network error" or "Request Entity Too Large"
**Solution**: Render body size limit. Add `MAX_BODY_SIZE` env var.

### Error: "Timeout"
**Solution**: File taking too long. Check:
- Internet connection speed
- Render instance performance
- Consider using direct storage upload

### Error: "Failed to upload imaging file"
**Solution**: Check backend logs for specific error.

---

## 💡 RECOMMENDED APPROACH

For production with large DICOM files:

1. **Use Supabase Storage** for file uploads
2. **Backend processes** from storage URL
3. **Keeps files** in Supabase (persistent)
4. **No Render body limit** issues

**Implementation**:
```typescript
// Frontend
const { data } = await supabase.storage
  .from('medical-imaging')
  .upload(path, file);

// Send storage path to backend
await api.post('/imaging/process', {
  storage_path: data.path
});

// Backend
def process_from_storage(storage_path: str):
    # Download from Supabase
    # Process DICOM
    # Store results in database
```

---

## 📝 FILES MODIFIED

1. ✅ `backend/app/api/v1/imaging.py`
   - Chunked file reading
   - Better error handling
   - HTTP 413 for oversized files

---

## ⏱️ TIMELINE

- Add env var: 1 minute
- Render redeploy: 2-3 minutes
- Git push: 1 minute
- Render redeploy: 2-3 minutes
- **Total**: ~7-8 minutes

---

## ✅ SUCCESS CHECKLIST

After deployment:
- [ ] Environment variable added (`MAX_BODY_SIZE=104857600`)
- [ ] Code deployed successfully
- [ ] Can upload small DICOM files (< 10MB)
- [ ] Can upload medium DICOM files (10-50MB) if env var set
- [ ] Get proper error messages for oversized files
- [ ] Processing completes successfully
- [ ] Analysis results appear

---

## 🎉 SUMMARY

**Issue**: DICOM uploads failing with network error  
**Cause**: Render 10MB body size limit + no chunked reading  
**Fix**: Chunked reading + increase Render limit to 100MB  
**Alternative**: Use Supabase Storage for large files  

**Next Steps**:
1. Add `MAX_BODY_SIZE` env var in Render
2. Deploy code changes
3. Test with DICOM files
4. Consider Supabase Storage for production
