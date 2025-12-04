# Create Storage Policy for student-docs Bucket

## Quick Fix: Create Policy in Supabase Dashboard

1. **Go to the Policies page** (you're already there):
   - https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/storage/files/policies

2. **Click "New policy"** on the "STUDENT-DOCS" bucket card

3. **Create a policy for service_role:**

   **Policy Name:** `Allow service_role full access`
   
   **Allowed Operation:** `ALL` (or select INSERT, SELECT, UPDATE, DELETE)
   
   **Target Roles:** `service_role`
   
   **Policy Definition:**
   ```sql
   (bucket_id = 'student-docs')
   ```
   
   **Check Expression:** (same)
   ```sql
   (bucket_id = 'student-docs')
   ```

4. **Save the policy**

## Alternative: Use SQL Editor

1. Go to: SQL Editor in Supabase Dashboard
2. Run this SQL:

```sql
-- Allow service_role full access to student-docs bucket
CREATE POLICY "Allow service_role full access"
ON storage.objects
FOR ALL
TO service_role
USING (bucket_id = 'student-docs')
WITH CHECK (bucket_id = 'student-docs');
```

## After Creating Policy

1. **Test upload:**
   ```powershell
   python test_supabase_upload.py
   ```

2. **If successful, migrate files:**
   ```powershell
   python migrate_files_to_supabase.py
   ```

3. **View files in dashboard:**
   - Go to: Storage → Files → Buckets → student-docs
   - You should see your files in `attachments/` and `resumes/` folders

## Why This Is Needed

Even though the bucket is PUBLIC, Supabase's Row Level Security (RLS) requires explicit policies for:
- **service_role** to upload files (server-side)
- **public** to read files (client-side)

The "signature verification failed" error happens because there's no policy allowing service_role to upload.

