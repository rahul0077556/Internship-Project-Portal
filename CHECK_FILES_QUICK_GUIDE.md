# Quick Guide: How to Check if Files are Uploaded to Supabase

Since you already have the Supabase Dashboard open, here's the **easiest way** to check:

## ✅ Method 1: Check in Supabase Dashboard (Easiest!)

You're already in the right place! In your Supabase Dashboard:

1. **Storage** → **Buckets** → **student-docs**
2. After a student uploads a file, you'll see:
   - **Folders**: `resumes/`, `attachments/`
   - Inside each folder, subfolders by student ID (e.g., `resumes/123/`)
   - **Files** will appear with their names

**What you'll see:**
- ✅ File appears = Successfully uploaded!
- ❌ Empty folder = No uploads yet

## 🔍 Method 2: Check Database Records

In your PostgreSQL database, check if URLs start with `https://`:

### Check Resumes:
```sql
SELECT id, user_id, resume_path 
FROM student_profiles 
WHERE resume_path LIKE 'http%';
```

### Check Attachments:
```sql
SELECT id, student_id, title, file_path 
FROM student_attachments 
WHERE file_path LIKE 'http%';
```

**URL Format:**
- ✅ Supabase URL: `https://xxx.supabase.co/storage/v1/object/public/student-docs/...`
- ❌ Local file: `uploads/resumes/123_resume.pdf`

## 🌐 Method 3: Test File URL Directly

1. Get the URL from your database
2. Copy and paste it in your browser
3. If the file downloads/opens → ✅ File exists!
4. If you get 404 → ❌ File not found

## 🔧 Method 4: Use API Endpoint

I created a new API endpoint for you. Once your Flask app is running:

```bash
GET /api/student/files/check
Authorization: Bearer YOUR_JWT_TOKEN
```

This returns:
- Which files are in Supabase vs local storage
- If files exist
- File counts

## 📊 Current Status

Looking at your Supabase Dashboard screenshot:
- ✅ Your bucket `student-docs` exists
- ✅ It's set to **PUBLIC** (good!)
- ⚠️  Currently empty (no files uploaded yet)

## 🚀 After Student Uploads

Once a student uploads via your app:

1. **Check Dashboard**: Go to `student-docs` bucket → You'll see folders appear
2. **Check Database**: Run SQL query → See URLs starting with `https://`
3. **Test URL**: Copy URL from DB → Paste in browser → File should download

## 💡 Quick Test

To test if uploads are working:

1. **Upload a file** through your app (as a student)
2. **Check Supabase Dashboard** → Files should appear in `resumes/` or `attachments/` folder
3. **Check Database** → `resume_path` or `file_path` should be a URL starting with `https://`

## 🔴 If Files Still Go to Local Storage

If files are still saving in `uploads/` folder instead of Supabase:

1. Check `.env` file has:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-key-here
   SUPABASE_BUCKET=student-docs
   ```

2. The system will **automatically fallback** to local storage if Supabase isn't configured
   - This is fine for development!
   - Files in `uploads/` = Working, just stored locally
   - Files with `https://` URLs = Stored in Supabase

## 📝 Summary

**Easiest way to check:**
1. Open Supabase Dashboard
2. Go to Storage → Buckets → student-docs  
3. Look for files in `resumes/` and `attachments/` folders

**That's it!** No need to run test scripts. Just check the dashboard after uploads! 🎉

