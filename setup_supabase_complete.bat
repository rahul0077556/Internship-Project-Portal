@echo off
echo ========================================
echo   Complete Supabase Setup Fix
echo ========================================
echo.

echo Step 1: Fixing Supabase versions...
pip uninstall supabase httpx gotrue postgrest storage3 -y
pip install supabase==2.4.0 httpx==0.24.0
echo.

echo Step 2: Checking .env file...
if exist .env (
    echo .env file found
    findstr /C:"SUPABASE_SERVICE_ROLE_KEY" .env >nul
    if errorlevel 1 (
        echo.
        echo ⚠️  WARNING: SUPABASE_SERVICE_ROLE_KEY not found in .env
        echo.
        echo Please update your .env file with:
        echo   SUPABASE_SERVICE_ROLE_KEY=your-secret-key-here
        echo.
        echo Get your secret key from:
        echo   https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/settings/api-keys
        echo.
        echo The key should start with sb_secret_ (NOT sb_publishable_)
        echo.
        pause
    ) else (
        echo SUPABASE_SERVICE_ROLE_KEY found in .env
    )
) else (
    echo ❌ .env file not found!
    echo Please create a .env file with your Supabase credentials
    pause
    exit /b 1
)

echo.
echo Step 3: Testing Supabase configuration...
python test_supabase_upload.py

echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo.
echo 1. If test passed, migrate existing files:
echo    python migrate_files_to_supabase.py
echo.
echo 2. Check Supabase Dashboard:
echo    https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/storage/buckets/student-docs
echo.
pause

