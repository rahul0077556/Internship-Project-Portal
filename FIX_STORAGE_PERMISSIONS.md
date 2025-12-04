# Fix: "signature verification failed" Error

## Current Status
- ✅ Supabase client is connected
- ✅ Bucket is PUBLIC
- ❌ Getting "signature verification failed" when uploading

## The Problem

The service_role key might be:
1. **Expired or invalid** - JWT tokens can expire
2. **Wrong format** - New Supabase might need different key format
3. **Missing permissions** - Storage policies might be blocking

## Solutions

### Option 1: Regenerate Service Role Key (Recommended)

1. Go to: https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/settings/api-keys
2. Click "Legacy anon, service_role API keys" tab
3. Find the "service_role" key
4. Click the **refresh/regenerate icon** (if available) or copy a fresh key
5. Update your `.env` file with the new key
6. Restart your Flask server

### Option 2: Check Storage Policies

1. Go to: https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/storage/policies
2. Find policies for `student-docs` bucket
3. Make sure there's a policy that allows:
   - **INSERT** for service_role
   - **SELECT** for service_role
   - **UPDATE** for service_role
   - **DELETE** for service_role

Or create a policy:
```sql
-- Allow service_role full access
CREATE POLICY "Service role full access"
ON storage.objects
FOR ALL
TO service_role
USING (bucket_id = 'student-docs')
WITH CHECK (bucket_id = 'student-docs');
```

### Option 3: Use New API Key Format

Try using the new `sb_secret_` key format instead:
1. Go to: Settings → API Keys
2. Copy the "Secret key" (starts with `sb_secret_`)
3. Update `.env`: `SUPABASE_SERVICE_ROLE_KEY=sb_secret_...`
4. Test again

### Option 4: Temporary Workaround - Use Anon Key for Public Bucket

If bucket is truly public, you can try using the anon key:
1. Get anon key from: Settings → API Keys → Legacy keys
2. Update `.env`: `SUPABASE_ANON_KEY=eyJ...` (remove SERVICE_ROLE_KEY)
3. Test upload

**Note:** This only works if bucket is public and has proper policies.

## Test After Fixing

```powershell
python test_supabase_upload.py
```

You should see:
- ✅ File uploaded successfully!

## Why Files Aren't Showing

Your files are currently:
- ✅ Saved in PostgreSQL database
- ✅ Stored locally in `uploads/` folder
- ❌ NOT in Supabase Storage (due to upload failures)

Once uploads work, run:
```powershell
python migrate_files_to_supabase.py
```

This will upload all existing files to Supabase Storage.

