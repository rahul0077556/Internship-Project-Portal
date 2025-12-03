# Fix Supabase Setup - Complete Guide

## Issue: "Invalid API key" Error

Your `.env` file is using the **PUBLISHABLE** key instead of the **SERVICE_ROLE** key.

## Step 1: Get Your Service Role Key

1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/settings/api-keys
2. In the "Secret keys" section, find the key named "default"
3. Click the **eye icon** 👁️ to reveal the full key
4. Click the **copy icon** 📋 to copy it
5. The key should start with `sb_secret_` (not `sb_publishable_`)

## Step 2: Update Your .env File

Replace your current `.env` file with:

```env
DATABASE_USER=postgres
DATABASE_PASSWORD=rahul
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=MyPortalDb

# Supabase settings
SUPABASE_URL=https://ynaybgjcoeacgpbmcbvs.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SECRET_KEY_HERE
SUPABASE_BUCKET=student-docs
```

**Important:** 
- Replace `YOUR_SECRET_KEY_HERE` with the secret key you copied (starts with `sb_secret_`)
- Do NOT use the publishable key (`sb_publishable_...`)
- Do NOT use the anon public key (JWT token starting with `eyJ...`)

## Step 3: Fix Supabase Versions

Run these commands:

```powershell
pip uninstall supabase httpx gotrue postgrest storage3 -y
pip install supabase==2.4.0 httpx==0.24.0
```

Or use the helper script:
```powershell
.\fix_supabase_versions.bat
```

## Step 4: Test Configuration

```powershell
python test_supabase_upload.py
```

You should see:
- ✅ Supabase is CONFIGURED and ready!
- ✅ File uploaded successfully!

## Step 5: Migrate Existing Files

After fixing the configuration, migrate your existing local files to Supabase:

```powershell
python migrate_files_to_supabase.py
```

This will:
- Upload all files from `uploads/` to Supabase Storage
- Update database records with Supabase URLs
- Delete local files after successful upload

## Step 6: Verify in Supabase Dashboard

1. Go to: https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/storage/buckets/student-docs
2. You should see folders like:
   - `attachments/1/` - Contains student attachments
   - `resumes/1/` - Contains student resumes

## Troubleshooting

### Still getting "Invalid API key"?
- Make sure you copied the **SECRET** key, not the publishable key
- The secret key should start with `sb_secret_`
- Restart your Flask server after updating `.env`

### Files still not showing in dashboard?
- Make sure the bucket name is exactly `student-docs`
- Check bucket is set to **public** in Supabase Dashboard
- Run the migration script to upload existing files

### Version errors?
- Make sure you uninstalled all old versions first
- Use the exact versions: `supabase==2.4.0` and `httpx==0.24.0`

