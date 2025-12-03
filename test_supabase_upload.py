"""
Test script to verify Supabase Storage uploads and file checking functionality.

Usage:
    python test_supabase_upload.py

This script will:
1. Check if Supabase is configured
2. Test uploading a sample file
3. Verify the file exists
4. List files in the bucket
5. Check files for a specific student
"""

import os
import sys
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()

# Import after loading env
from supabase_storage import (
    is_supabase_configured,
    upload_file_to_supabase,
    check_file_exists,
    list_files_in_folder,
    get_file_info_from_url,
    get_all_student_files,
)

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_supabase_configuration():
    """Test 1: Check if Supabase is configured"""
    print_section("Test 1: Supabase Configuration Check")
    
    configured = is_supabase_configured()
    
    if configured:
        print("✅ Supabase is CONFIGURED and ready!")
        print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL', 'Not set')[:50]}...")
        print(f"   SUPABASE_BUCKET: {os.getenv('SUPABASE_BUCKET', 'student-docs')}")
    else:
        print("❌ Supabase is NOT configured or has errors")
        print("\n   Possible issues:")
        print("   1. Check your .env file has:")
        print("      - SUPABASE_URL")
        print("      - SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)")
        print("      - SUPABASE_BUCKET (optional, defaults to 'student-docs')")
        print("\n   2. If you see version compatibility errors, try:")
        print("      pip uninstall supabase httpx -y")
        print("      pip install supabase==2.3.0 httpx==0.25.0")
        print("\n   3. Or reinstall all dependencies:")
        print("      pip install -r requirements.txt --upgrade")
        return False
    
    return True

def test_file_upload():
    """Test 2: Upload a test file"""
    print_section("Test 2: File Upload Test")
    
    # Create a test file in memory
    test_content = b"This is a test file uploaded from test_supabase_upload.py"
    test_file = BytesIO(test_content)
    test_file.name = "test_file.txt"
    
    # Upload to test folder
    folder = "test"
    print(f"Uploading test file to folder: {folder}/")
    
    public_url = upload_file_to_supabase(test_file, "test_file.txt", folder)
    
    if public_url:
        print(f"✅ File uploaded successfully!")
        print(f"   Public URL: {public_url}")
        return public_url
    else:
        print("❌ File upload FAILED")
        print("   Check your Supabase credentials and bucket permissions")
        return None

def test_file_exists(url):
    """Test 3: Check if uploaded file exists"""
    print_section("Test 3: File Existence Check")
    
    if not url:
        print("⚠️  Skipping - no file URL from previous test")
        return
    
    # Extract storage path from URL
    file_info = get_file_info_from_url(url)
    
    if file_info:
        print(f"   Storage Path: {file_info['storage_path']}")
        print(f"   File Exists: {'✅ YES' if file_info['exists'] else '❌ NO'}")
        
        # Also check directly
        exists = check_file_exists(file_info['storage_path'])
        print(f"   Direct Check: {'✅ YES' if exists else '❌ NO'}")
    else:
        print("❌ Could not extract file info from URL")

def test_list_files():
    """Test 4: List files in bucket"""
    print_section("Test 4: List Files in Bucket")
    
    # List root files
    print("Listing files in root folder:")
    root_files = list_files_in_folder("", limit=10)
    
    if root_files:
        print(f"   Found {len(root_files)} item(s):")
        for item in root_files[:5]:  # Show first 5
            if isinstance(item, dict):
                name = item.get('name', 'Unknown')
                item_type = '📁 Folder' if item.get('metadata') is None else '📄 File'
                print(f"   {item_type}: {name}")
            else:
                print(f"   {item}")
    else:
        print("   No files found in root")
    
    # List test folder files
    print("\nListing files in 'test' folder:")
    test_files = list_files_in_folder("test", limit=10)
    
    if test_files:
        print(f"   Found {len(test_files)} file(s):")
        for item in test_files:
            if isinstance(item, dict):
                name = item.get('name', 'Unknown')
                size = item.get('metadata', {}).get('size', '?')
                print(f"   📄 {name} ({size} bytes)")
    else:
        print("   No files found in test folder")

def test_student_files():
    """Test 5: Check files for a specific student"""
    print_section("Test 5: Student Files Check")
    
    # You can change this to test with a real student ID
    test_student_id = 1
    print(f"Checking files for student ID: {test_student_id}")
    
    student_files = get_all_student_files(test_student_id)
    
    print(f"\n   Resumes: {len(student_files['resumes'])} file(s)")
    if student_files['resumes']:
        for item in student_files['resumes'][:3]:  # Show first 3
            if isinstance(item, dict):
                print(f"      - {item.get('name', 'Unknown')}")
    
    print(f"\n   Attachments: {len(student_files['attachments'])} file(s)")
    if student_files['attachments']:
        for item in student_files['attachments'][:3]:  # Show first 3
            if isinstance(item, dict):
                print(f"      - {item.get('name', 'Unknown')}")

def test_check_existing_files():
    """Test 6: Check existing files from database"""
    print_section("Test 6: Check Database File URLs")
    
    try:
        from models import db, StudentProfile, StudentAttachment
        from app import app
        
        with app.app_context():
            # Check student profiles with resume_path
            profiles_with_resume = StudentProfile.query.filter(
                StudentProfile.resume_path.isnot(None),
                StudentProfile.resume_path.like('http%')
            ).limit(5).all()
            
            print(f"Found {len(profiles_with_resume)} profile(s) with Supabase resume URLs:")
            for profile in profiles_with_resume:
                print(f"\n   Student ID {profile.id}:")
                print(f"      Resume URL: {profile.resume_path[:80]}...")
                
                file_info = get_file_info_from_url(profile.resume_path)
                if file_info:
                    status = "✅ EXISTS" if file_info['exists'] else "❌ NOT FOUND"
                    print(f"      Status: {status}")
            
            # Check attachments
            attachments_with_url = StudentAttachment.query.filter(
                StudentAttachment.file_path.like('http%')
            ).limit(5).all()
            
            print(f"\nFound {len(attachments_with_url)} attachment(s) with Supabase URLs:")
            for attachment in attachments_with_url:
                print(f"\n   Attachment ID {attachment.id}: {attachment.title}")
                print(f"      File URL: {attachment.file_path[:80]}...")
                
                file_info = get_file_info_from_url(attachment.file_path)
                if file_info:
                    status = "✅ EXISTS" if file_info['exists'] else "❌ NOT FOUND"
                    print(f"      Status: {status}")
                    
    except Exception as e:
        print(f"⚠️  Could not check database files: {e}")
        print("   Make sure your database is running and configured")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  SUPABASE STORAGE VERIFICATION TEST")
    print("="*60)
    
    # Test 1: Configuration
    if not test_supabase_configuration():
        print("\n❌ Supabase is not configured. Please set up your .env file first.")
        sys.exit(1)
    
    # Test 2: Upload
    uploaded_url = test_file_upload()
    
    # Test 3: Check existence
    test_file_exists(uploaded_url)
    
    # Test 4: List files
    test_list_files()
    
    # Test 5: Student files
    test_student_files()
    
    # Test 6: Check database files
    test_check_existing_files()
    
    print_section("Test Complete")
    print("✅ All tests completed!")
    print("\n💡 Tips:")
    print("   - Check Supabase Dashboard: Storage → student-docs bucket")
    print("   - URLs starting with 'http' are in Supabase")
    print("   - URLs starting with 'uploads/' are local files")

if __name__ == "__main__":
    main()

