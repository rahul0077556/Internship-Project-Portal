# How to Check if Files are Uploaded to Supabase

This guide explains multiple ways to verify that files are successfully uploaded to Supabase Storage.

## Method 1: Using the Test Script (Recommended)

Run the automated test script to check everything:

```bash
python test_supabase_upload.py
```

This script will:
- ✅ Check if Supabase is configured correctly
- ✅ Test uploading a sample file
- ✅ Verify the file exists in Supabase
- ✅ List files in your bucket
- ✅ Check files for specific students
- ✅ Verify existing database records

## Method 2: Check in Supabase Dashboard (Visual)

1. Go to [supabase.com](https://supabase.com) and log in
2. Select your project
3. Navigate to **Storage** → **Buckets**
4. Click on your bucket (default: `student-docs`)
5. Browse through folders:
   - `resumes/` - Contains student resumes
   - `attachments/` - Contains student attachments
   - Each student has their own subfolder by ID

**Visual verification:**
- You'll see file names, sizes, and upload dates
- Click on a file to see its public URL
- Files should appear immediately after upload

## Method 3: Check Database Records

Files stored in Supabase will have URLs starting with `https://` instead of local paths.

### Check Resumes:
```sql
-- In your PostgreSQL database (pgAdmin or psql)
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
- ✅ Supabase: `https://xxx.supabase.co/storage/v1/object/public/student-docs/...`
- ❌ Local: `uploads/resumes/123_20240101_resume.pdf`

## Method 4: Check Programmatically (Python)

### Check if a file exists:

```python
from supabase_storage import check_file_exists, get_file_info_from_url

# Method A: Check by storage path
storage_path = "resumes/123/abc123def456.pdf"
exists = check_file_exists(storage_path)
print(f"File exists: {exists}")

# Method B: Check by public URL
url = "https://xxx.supabase.co/storage/v1/object/public/student-docs/resumes/123/abc123def456.pdf"
file_info = get_file_info_from_url(url)
if file_info:
    print(f"Exists: {file_info['exists']}")
    print(f"Path: {file_info['storage_path']}")
```

### List all files for a student:

```python
from supabase_storage import get_all_student_files

student_id = 1
files = get_all_student_files(student_id)
print(f"Resumes: {len(files['resumes'])}")
print(f"Attachments: {len(files['attachments'])}")
```

### List files in a folder:

```python
from supabase_storage import list_files_in_folder

# List all resumes
resumes = list_files_in_folder("resumes", limit=50)

# List attachments for student ID 123
attachments = list_files_in_folder("attachments/123")
```

## Method 5: Check from API Response

When you upload a file via API, the response will contain the file path/URL:

### Upload Resume:
```bash
POST /api/student/resume/upload
Response: {
    "message": "Resume uploaded successfully",
    "resume_path": "https://xxx.supabase.co/storage/v1/object/public/student-docs/resumes/123/abc123.pdf"
}
```

### Upload Attachment:
```bash
POST /api/student/attachments
Response: {
    "message": "Attachment uploaded",
    "attachment": {
        "id": 1,
        "file_path": "https://xxx.supabase.co/storage/v1/object/public/student-docs/attachments/123/xyz789.pdf"
    }
}
```

**If URL starts with `http`, it's in Supabase!**

## Method 6: Test File Upload via API

Use curl or Postman to test:

```bash
# Upload a test resume (replace TOKEN with your JWT token)
curl -X POST http://localhost:5000/api/student/resume/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "resume=@/path/to/your/resume.pdf"

# Response will show the Supabase URL if configured
```

## Method 7: Check File Accessibility

Files in Supabase Storage are publicly accessible (if bucket is public). You can:

1. **Open URL in browser:**
   - Copy the `resume_path` or `file_path` from database
   - Paste in browser
   - If file opens → ✅ Successfully uploaded
   - If 404 error → ❌ File not found

2. **Use curl:**
```bash
curl -I "https://xxx.supabase.co/storage/v1/object/public/student-docs/resumes/123/file.pdf"
# If response is 200 OK → File exists
# If response is 404 → File not found
```

## Troubleshooting

### Files not uploading to Supabase?

1. **Check .env file:**
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-key-here
   SUPABASE_BUCKET=student-docs
   ```

2. **Verify bucket exists:**
   - Go to Supabase Dashboard → Storage → Buckets
   - Ensure bucket name matches `SUPABASE_BUCKET` in .env
   - Bucket should be **public** for easy access

3. **Check bucket permissions:**
   - Bucket should allow uploads
   - Public bucket allows direct URL access

4. **Run test script:**
   ```bash
   python test_supabase_upload.py
   ```
   This will show detailed error messages

### Files still saving locally?

- If Supabase is not configured, the system **automatically falls back** to local storage
- Check if `is_supabase_configured()` returns `True`
- Verify all environment variables are set correctly

### How to verify configuration:

```python
from supabase_storage import is_supabase_configured
print(f"Supabase configured: {is_supabase_configured()}")
```

## Quick Checklist

- [ ] `.env` file has `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_BUCKET`
- [ ] Bucket exists in Supabase Dashboard
- [ ] Bucket is set to **public**
- [ ] `pip install -r requirements.txt` (includes supabase package)
- [ ] Run `python test_supabase_upload.py` - all tests pass
- [ ] Upload a file via API - response contains `https://` URL
- [ ] Check database - `resume_path` or `file_path` starts with `http`
- [ ] Open URL in browser - file downloads/opens correctly

## Summary

**Easiest method:** Run `python test_supabase_upload.py` - it checks everything automatically!

**Quick check:** Look at database records - if `file_path` starts with `https://`, it's in Supabase!

**Visual check:** Supabase Dashboard → Storage → Buckets → `student-docs`

