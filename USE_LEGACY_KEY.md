# Use Legacy JWT Key Instead

## The Problem

The new Supabase key format (`sb_secret_...`) may not be supported by the current Supabase Python client. You need to use the **legacy JWT-based service_role key** instead.

## Solution: Get Legacy Service Role Key

1. **Go to Supabase Dashboard:**
   - https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/settings/api-keys

2. **Click on the "Legacy anon, service_role API keys" tab** (next to "Publishable and secret API keys")

3. **Find the "service_role" key:**
   - It will be a long JWT token starting with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - This is different from the new `sb_secret_` format

4. **Copy the FULL service_role key** (it's very long, make sure you get it all)

5. **Update your `.env` file:**
   ```env
   SUPABASE_URL=https://ynaybgjcoeacgpbmcbvs.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluYXliZ2pjb2VhY2dwYm1jYnZzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzE2ODgwMCwiZXhwIjoyMDQ4NzQ0ODAwfQ.YOUR_FULL_KEY_HERE
   SUPABASE_BUCKET=student-docs
   ```

6. **Test it:**
   ```powershell
   python test_supabase_upload.py
   ```

## Quick Diagnostic

Run this to check your current key:
```powershell
python test_supabase_key.py
```

This will show:
- Key length
- Key format
- Whether it's complete

## Why This Happens

- Supabase introduced new key formats (`sb_secret_`, `sb_publishable_`)
- The Python client library may not support them yet
- Legacy JWT keys still work and are more compatible

## After Fixing

Once you update to the legacy key:
1. ✅ Test: `python test_supabase_upload.py`
2. ✅ Migrate files: `python migrate_files_to_supabase.py`
3. ✅ Check dashboard: Files should appear in Supabase Storage

