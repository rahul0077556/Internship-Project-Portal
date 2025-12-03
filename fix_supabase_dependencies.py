"""
Quick script to fix Supabase dependency compatibility issues.

Run this script to reinstall Supabase with compatible versions.
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and show output"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def main():
    print("\n" + "="*60)
    print("  SUPABASE DEPENDENCY FIX SCRIPT")
    print("="*60)
    print("\nThis script will:")
    print("1. Uninstall conflicting Supabase packages")
    print("2. Reinstall with compatible versions")
    print("3. Verify installation")
    print("\n" + "="*60)
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    # Step 1: Uninstall
    print("\n[Step 1/3] Uninstalling conflicting packages...")
    run_command("pip uninstall supabase httpx postgrest gotrue -y")
    
    # Step 2: Install compatible versions
    print("\n[Step 2/3] Installing compatible versions...")
    success = run_command("pip install supabase==2.3.0 httpx==0.25.0")
    
    if not success:
        print("\n⚠️  Installation had issues. Trying alternative...")
        run_command("pip install supabase httpx --upgrade")
    
    # Step 3: Verify
    print("\n[Step 3/3] Verifying installation...")
    try:
        from supabase import create_client
        print("✅ Supabase package imported successfully!")
        
        import httpx
        print(f"✅ httpx version: {httpx.__version__}")
        
        print("\n" + "="*60)
        print("✅ DEPENDENCY FIX COMPLETE!")
        print("="*60)
        print("\nNow try running the test again:")
        print("  python test_supabase_upload.py")
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        print("\nManual fix instructions:")
        print("1. pip uninstall supabase httpx postgrest gotrue -y")
        print("2. pip install supabase==2.3.0 httpx==0.25.0")
        print("3. Or: pip install -r requirements.txt")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

