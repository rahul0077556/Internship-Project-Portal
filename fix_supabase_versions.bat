@echo off
echo Fixing Supabase version compatibility...
echo.

echo Step 1: Uninstalling old versions...
pip uninstall supabase httpx gotrue postgrest storage3 -y

echo.
echo Step 2: Installing compatible versions...
pip install supabase==2.4.0 httpx==0.24.0

echo.
echo Step 3: Verifying installation...
python -c "from supabase import create_client; print('✅ Supabase installed successfully!')"

echo.
echo Done! Now run: python test_supabase_upload.py
pause

