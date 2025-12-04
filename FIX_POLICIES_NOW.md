# Fix: "new row violates row-level security policy"

## The Problem

Your policies exist but they're missing the proper `USING` and `WITH CHECK` clauses. The policies need to specify `bucket_id = 'student-docs'` in both clauses.

## Quick Fix: Update Policies in SQL Editor

1. **Go to SQL Editor** in Supabase Dashboard:
   - https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/sql/new

2. **Run this SQL** (it will replace your existing policies):

```sql
-- Drop existing policies
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_0" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_1" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_2" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_3" ON storage.objects;

-- Create a single comprehensive policy for service_role
CREATE POLICY "Allow service_role full access to student-docs"
ON storage.objects
FOR ALL
TO service_role
USING (bucket_id = 'student-docs')
WITH CHECK (bucket_id = 'student-docs');

-- Also allow public read access
CREATE POLICY "Allow public read access to student-docs"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'student-docs');
```

3. **Click "Run"** to execute

## Alternative: Fix via Dashboard

1. Go to: Storage → Files → Policies
2. Click the **three dots** (⋮) on each existing policy
3. Click **Edit**
4. Make sure both **USING** and **WITH CHECK** have:
   ```sql
   (bucket_id = 'student-docs')
   ```
5. Save each policy

## After Fixing

1. **Test upload:**
   ```powershell
   python test_supabase_upload.py
   ```
   Should show: ✅ File uploaded successfully!

2. **Migrate existing files:**
   ```powershell
   python migrate_files_to_supabase.py
   ```

3. **View files:**
   - Go to: Storage → Files → Buckets → student-docs
   - Click on the bucket (not Policies tab)
   - You should see folders: `attachments/`, `resumes/`, etc.

## Why This Happens

The policies were created but without the proper `WITH CHECK` clause, which is required for INSERT operations. The `WITH CHECK` clause tells Supabase what conditions new rows must meet.

