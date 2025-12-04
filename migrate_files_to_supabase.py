"""
Migration Script: Upload Local Files to Supabase Storage

This script migrates existing local files (stored in uploads/) to Supabase Storage
and updates the database records with the new Supabase URLs.

Usage:
    python migrate_files_to_supabase.py

Make sure your .env file has:
    - SUPABASE_URL
    - SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)
    - SUPABASE_BUCKET (optional, defaults to 'student-docs')
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Import Flask app and models
from app import app, db
from models import StudentAttachment, StudentProfile
from supabase_storage import is_supabase_configured, upload_file_to_supabase

def migrate_attachments():
    """Migrate StudentAttachment files from local storage to Supabase."""
    if not is_supabase_configured():
        print("❌ Supabase is not configured!")
        print("   Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file")
        return False
    
    print("✅ Supabase is configured")
    print("\n📦 Migrating Student Attachments...")
    
    # Find all attachments with local file paths (not starting with http)
    attachments = StudentAttachment.query.filter(
        ~StudentAttachment.file_path.like('http%')
    ).all()
    
    if not attachments:
        print("   No local attachments found to migrate.")
        return True
    
    print(f"   Found {len(attachments)} attachment(s) to migrate")
    
    migrated = 0
    failed = 0
    skipped = 0
    
    for attachment in attachments:
        file_path = attachment.file_path
        
        # Normalize Windows paths - convert backslashes to forward slashes for display
        normalized_path = file_path.replace("\\", "/") if file_path else ""
        
        # Check if file exists (use original path for OS check)
        if not os.path.exists(file_path):
            print(f"   ⚠️  Skipping attachment ID {attachment.id}: File not found: {normalized_path}")
            skipped += 1
            continue
        
        try:
            # Get absolute path to handle relative paths correctly
            abs_file_path = os.path.abspath(file_path)
            
            # Extract original filename from path or use title
            original_filename = os.path.basename(abs_file_path)
            
            # Remove the timestamp prefix if present (format: student_id_timestamp_filename)
            if '_' in original_filename:
                parts = original_filename.split('_', 2)
                if len(parts) >= 3 and parts[0].isdigit():
                    original_filename = parts[2]  # Get the actual filename
            
            # Use title if filename extraction failed or is empty
            if not original_filename or original_filename == "":
                original_filename = attachment.title or "document"
            
            # Ensure filename has extension
            if not os.path.splitext(original_filename)[1]:
                # Try to get extension from original path
                _, ext = os.path.splitext(abs_file_path)
                if ext:
                    original_filename = original_filename + ext
            
            # Check file size
            file_size = os.path.getsize(abs_file_path)
            if file_size == 0:
                print(f"   ⚠️  Skipping attachment ID {attachment.id}: File is empty: {normalized_path}")
                skipped += 1
                continue
            
            # Read the file
            with open(abs_file_path, 'rb') as f:
                file_content = f.read()
                
                # Verify file was read correctly
                if not file_content or len(file_content) == 0:
                    print(f"   ⚠️  Skipping attachment ID {attachment.id}: Could not read file content: {normalized_path}")
                    skipped += 1
                    continue
                
                # Create a BytesIO object for upload
                from io import BytesIO
                file_data = BytesIO(file_content)
                file_data.name = original_filename
                
                # Upload to Supabase - folder path will be normalized in upload function
                folder = f"attachments/{attachment.student_id}"
                supabase_url = upload_file_to_supabase(
                    file_data,
                    original_filename,
                    folder
                )
                
                if supabase_url:
                    # Update database record
                    old_path = attachment.file_path
                    attachment.file_path = supabase_url
                    db.session.commit()
                    
                    print(f"   ✅ Migrated attachment ID {attachment.id}: {original_filename}")
                    print(f"      Old: {normalized_path}")
                    print(f"      New: {supabase_url}")
                    
                    # Optionally delete local file after successful migration
                    try:
                        os.remove(abs_file_path)
                        print(f"      🗑️  Deleted local file")
                    except OSError as e:
                        print(f"      ⚠️  Could not delete local file: {e}")
                    
                    migrated += 1
                    # Add small delay between successful uploads to avoid connection issues
                    time.sleep(0.5)
                else:
                    print(f"   ❌ Failed to upload attachment ID {attachment.id}: Upload returned None")
                    print(f"      File path: {normalized_path}")
                    print(f"      Filename: {original_filename}")
                    failed += 1
                    # Add delay after failures too to allow connection to reset
                    time.sleep(1.0)
                
        except Exception as e:
            import traceback
            print(f"   ❌ Error migrating attachment ID {attachment.id}: {str(e)}")
            print(f"      File path: {normalized_path}")
            print(f"      Traceback: {traceback.format_exc()}")
            failed += 1
            db.session.rollback()
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Migrated: {migrated}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⚠️  Skipped: {skipped}")
    
    return failed == 0


def migrate_resumes():
    """Migrate StudentProfile resume files from local storage to Supabase."""
    if not is_supabase_configured():
        return False
    
    print("\n📄 Migrating Student Resumes...")
    
    # Find all profiles with local resume paths (not starting with http)
    profiles = StudentProfile.query.filter(
        StudentProfile.resume_path.isnot(None),
        ~StudentProfile.resume_path.like('http%')
    ).all()
    
    if not profiles:
        print("   No local resumes found to migrate.")
        return True
    
    print(f"   Found {len(profiles)} resume(s) to migrate")
    
    migrated = 0
    failed = 0
    skipped = 0
    
    for profile in profiles:
        file_path = profile.resume_path
        
        # Normalize Windows paths - convert backslashes to forward slashes for display
        normalized_path = file_path.replace("\\", "/") if file_path else ""
        
        # Check if file exists (use original path for OS check)
        if not os.path.exists(file_path):
            print(f"   ⚠️  Skipping profile ID {profile.id}: Resume file not found: {normalized_path}")
            skipped += 1
            continue
        
        try:
            # Get absolute path to handle relative paths correctly
            abs_file_path = os.path.abspath(file_path)
            
            # Extract original filename from path
            original_filename = os.path.basename(abs_file_path)
            
            # Remove the timestamp prefix if present
            if '_' in original_filename:
                parts = original_filename.split('_', 2)
                if len(parts) >= 3:
                    original_filename = parts[2]
            
            # Ensure filename has extension
            if not os.path.splitext(original_filename)[1]:
                # Try to get extension from original path
                _, ext = os.path.splitext(abs_file_path)
                if ext:
                    original_filename = original_filename + ext
            
            # Check file size
            file_size = os.path.getsize(abs_file_path)
            if file_size == 0:
                print(f"   ⚠️  Skipping profile ID {profile.id}: Resume file is empty: {normalized_path}")
                skipped += 1
                continue
            
            # Read the file
            with open(abs_file_path, 'rb') as f:
                file_content = f.read()
                
                # Verify file was read correctly
                if not file_content or len(file_content) == 0:
                    print(f"   ⚠️  Skipping profile ID {profile.id}: Could not read resume file content: {normalized_path}")
                    skipped += 1
                    continue
                
                # Create a BytesIO object for upload
                from io import BytesIO
                file_data = BytesIO(file_content)
                file_data.name = original_filename
                
                # Upload to Supabase - folder path will be normalized in upload function
                folder = f"resumes/{profile.id}"
                supabase_url = upload_file_to_supabase(
                    file_data,
                    original_filename,
                    folder
                )
                
                if supabase_url:
                    # Update database record
                    old_path = profile.resume_path
                    profile.resume_path = supabase_url
                    db.session.commit()
                    
                    print(f"   ✅ Migrated resume for profile ID {profile.id}: {original_filename}")
                    print(f"      Old: {normalized_path}")
                    print(f"      New: {supabase_url}")
                    
                    # Optionally delete local file after successful migration
                    try:
                        os.remove(abs_file_path)
                        print(f"      🗑️  Deleted local file")
                    except OSError as e:
                        print(f"      ⚠️  Could not delete local file: {e}")
                    
                    migrated += 1
                    # Add small delay between successful uploads
                    time.sleep(0.5)
                else:
                    print(f"   ❌ Failed to upload resume for profile ID {profile.id}: Upload returned None")
                    print(f"      File path: {normalized_path}")
                    print(f"      Filename: {original_filename}")
                    failed += 1
                    # Add delay after failures to allow connection to reset
                    time.sleep(1.0)
                
        except Exception as e:
            import traceback
            print(f"   ❌ Error migrating resume for profile ID {profile.id}: {str(e)}")
            print(f"      File path: {normalized_path}")
            print(f"      Traceback: {traceback.format_exc()}")
            failed += 1
            db.session.rollback()
    
    print(f"\n📊 Resume Migration Summary:")
    print(f"   ✅ Migrated: {migrated}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⚠️  Skipped: {skipped}")
    
    return failed == 0


def main():
    """Main migration function."""
    import sys
    import io
    # Fix encoding for Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("Migrating Local Files to Supabase Storage")
    print("=" * 60)
    
    # Check Supabase configuration
    if not is_supabase_configured():
        print("\n❌ Supabase is not configured!")
        print("\nPlease set the following in your .env file:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)")
        print("   - SUPABASE_BUCKET (optional, defaults to 'student-docs')")
        sys.exit(1)
    
    with app.app_context():
        # Migrate attachments
        attachments_success = migrate_attachments()
        
        # Migrate resumes
        resumes_success = migrate_resumes()
        
        if attachments_success and resumes_success:
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print("\n💡 Check your Supabase Dashboard:")
            print("   https://supabase.com/dashboard/project/ynaybgjcoeacgpbmcbvs/storage/buckets/student-docs")
        else:
            print("\n" + "=" * 60)
            print("⚠️  Migration completed with some errors. Please review the output above.")
            print("=" * 60)


if __name__ == '__main__':
    main()

