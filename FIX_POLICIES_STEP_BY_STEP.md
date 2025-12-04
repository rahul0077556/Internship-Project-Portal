# Fix Storage Policies - Step by Step

## Current Issue
- ✅ Supabase is connected
- ✅ Bucket is PUBLIC
- ✅ Policies exist
- ❌ But policies are missing `WITH CHECK` clause for INSERT operations

## Solution: Fix Policies in Supabase Dashboard

### Step 1: Go to SQL Editor
1. Open: https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/sql/new
2. Or: Dashboard → SQL Editor → New Query

### Step 2: Copy and Run This SQL

```sql
-- First, drop the existing policies
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_0" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_1" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_2" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_3" ON storage.objects;

-- Create ONE comprehensive policy for service_role (covers all operations)
CREATE POLICY "service_role_full_access_student_docs"
ON storage.objects
FOR ALL
TO service_role
USING (bucket_id = 'student-docs')
WITH CHECK (bucket_id = 'student-docs');

-- Allow public to read files (since bucket is public)
CREATE POLICY "public_read_access_student_docs"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'student-docs');
```

### Step 3: Click "Run" Button

### Step 4: Verify Policies
1. Go to: Storage → Files → Policies
2. You should see 2 policies (not 4):
   - `service_role_full_access_student_docs` (ALL operations)
   - `public_read_access_student_docs` (SELECT only)

### Step 5: Test Upload
```powershell
python test_supabase_upload.py
```

Should show: ✅ File uploaded successfully!

### Step 6: Migrate Existing Files
```powershell
python migrate_files_to_supabase.py
```

### Step 7: View Files in Dashboard
1. Go to: Storage → Files → Buckets
2. Click on "student-docs" bucket
3. You should see folders: `attachments/`, `resumes/`, `test/`

## Why This Works

The `WITH CHECK` clause is **required** for INSERT operations. It tells Supabase what conditions new rows must meet. Without it, INSERT operations fail with "new row violates row-level security policy".

The single policy with `FOR ALL` is cleaner than having 4 separate policies.

