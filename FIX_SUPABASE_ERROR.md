# Fix: TypeError with Supabase Client

You're encountering a dependency compatibility error with the Supabase Python client. Here's how to fix it:

## Quick Fix (Recommended)

Run these commands in your terminal:

```bash
# Step 1: Uninstall conflicting packages
pip uninstall supabase httpx postgrest gotrue storage3 -y

# Step 2: Reinstall with compatible versions
pip install supabase==2.3.0 httpx==0.24.1

# Step 3: Test the fix
python test_supabase_upload.py
```

## Alternative: Use the Fix Script

I've created an automated fix script for you:

```bash
python fix_supabase_dependencies.py
```

This script will:
- Automatically uninstall conflicting packages
- Reinstall compatible versions
- Verify the installation

## Manual Fix Steps

If the quick fix doesn't work, try this:

### Step 1: Clean uninstall
```bash
pip uninstall supabase httpx postgrest gotrue storage3 -y
```

### Step 2: Install compatible versions
```bash
pip install supabase==2.3.0
pip install httpx==0.24.1
```

### Step 3: Verify installation
```python
python -c "from supabase import create_client; print('✅ Success!')"
```

### Step 4: Test again
```bash
python test_supabase_upload.py
```

## If Still Not Working

### Option 1: Update to latest versions
```bash
pip uninstall supabase httpx -y
pip install supabase httpx --upgrade
```

### Option 2: Use specific working versions
```bash
pip install supabase==2.4.0 httpx==0.25.0
```

### Option 3: Install from requirements.txt
```bash
pip install -r requirements.txt --upgrade --force-reinstall
```

## What's Happening?

The error `TypeError: Client.__init__() got an unexpected keyword argument 'proxy'` occurs because:

1. **Version mismatch**: The `supabase` library expects a specific version of `httpx`
2. **API changes**: Newer versions of `httpx` changed their API, breaking compatibility
3. **Dependency conflict**: Multiple packages are trying to use different versions

## Verify Your Setup

After fixing, check your environment variables in `.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=student-docs
```

## Test Connection

Run the test script again:

```bash
python test_supabase_upload.py
```

You should see:
```
✅ Supabase is CONFIGURED and ready!
```

## Still Having Issues?

1. **Check Python version**: Supabase works best with Python 3.8+
   ```bash
   python --version
   ```

2. **Use virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

3. **Check for multiple Python installations**:
   ```bash
   where python  # On Windows
   which python  # On Linux/Mac
   ```

## Summary

The simplest fix is:
```bash
pip uninstall supabase httpx -y
pip install supabase==2.3.0 httpx==0.24.1
python test_supabase_upload.py
```

This should resolve the compatibility issue! 🚀

