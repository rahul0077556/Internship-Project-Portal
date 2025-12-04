import os
import uuid
from typing import Optional

try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "student-docs")


_supabase_client: Optional["Client"] = None


def _get_client() -> Optional["Client"]:
    """
    Returns a cached Supabase client if configuration and dependency are present.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not create_client or not SUPABASE_URL or not SUPABASE_KEY:
        return None

    try:
        # Try creating client - if it fails due to version issues, return None
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase_client
    except TypeError as e:
        # Handle specific version compatibility errors
        if 'proxy' in str(e) or 'unexpected keyword' in str(e):
            import sys
            print(f"\n⚠️  Supabase Version Compatibility Issue Detected!", file=sys.stderr)
            print(f"   Error: {e}", file=sys.stderr)
            print(f"\n   💡 To fix this, run:", file=sys.stderr)
            print(f"      pip uninstall supabase httpx gotrue postgrest storage3 -y", file=sys.stderr)
            print(f"      pip install supabase==2.4.0 httpx==0.24.0", file=sys.stderr)
            print(f"   Or use local file storage (uploads/) instead.\n", file=sys.stderr)
        return None
    except Exception as e:
        # Handle other initialization errors
        import sys
        error_msg = str(e)
        if 'SUPABASE_URL' in error_msg or 'url' in error_msg.lower():
            # Missing configuration - this is fine, will fallback to local storage
            return None
        if 'Invalid API key' in error_msg or 'invalid' in error_msg.lower() and 'key' in error_msg.lower():
            print(f"\n❌ Invalid API Key Error!", file=sys.stderr)
            print(f"   Error: {error_msg}", file=sys.stderr)
            print(f"\n   💡 Common issues:", file=sys.stderr)
            print(f"      1. New key format (sb_secret_) may not be supported", file=sys.stderr)
            print(f"         → Try using LEGACY JWT-based service_role key instead", file=sys.stderr)
            print(f"         → Go to: Settings → API Keys → 'Legacy anon, service_role API keys' tab", file=sys.stderr)
            print(f"         → Copy the 'service_role' key (starts with eyJ...)", file=sys.stderr)
            print(f"", file=sys.stderr)
            print(f"      2. Key might be incomplete or truncated", file=sys.stderr)
            print(f"         → Make sure you copied the FULL key", file=sys.stderr)
            print(f"         → Run: python test_supabase_key.py to check", file=sys.stderr)
            print(f"", file=sys.stderr)
            print(f"      3. Using wrong key type", file=sys.stderr)
            print(f"         - Publishable key starts with: sb_publishable_", file=sys.stderr)
            print(f"         - Service role key starts with: sb_secret_ (new) or eyJ... (legacy)", file=sys.stderr)
            print(f"", file=sys.stderr)
        else:
            print(f"Warning: Could not initialize Supabase client: {error_msg[:100]}", file=sys.stderr)
        return None


def is_supabase_configured() -> bool:
    """
    Helper to check if Supabase Storage is available.
    """
    return bool(_get_client())


def upload_file_to_supabase(file_obj, original_filename: str, folder: str) -> Optional[str]:
    """
    Upload a file-like object to Supabase Storage and return a public URL.

    - file_obj: Werkzeug FileStorage or any file-like object supporting .read()
    - original_filename: used to preserve extension
    - folder: logical folder inside the bucket (e.g., "resumes/123")
    """
    client = _get_client()
    if not client:
        return None

    # Ensure folder prefix has no leading slash
    folder = folder.strip("/ ")

    _, ext = os.path.splitext(original_filename or "")
    unique_name = f"{uuid.uuid4().hex}{ext}"
    storage_path = f"{folder}/{unique_name}" if folder else unique_name

    # Ensure file pointer is at the start
    if hasattr(file_obj, 'seek'):
        file_obj.seek(0)
    
    # Read file content as bytes (new Supabase client requires bytes)
    try:
        if hasattr(file_obj, 'read'):
            file_content = file_obj.read()
        elif isinstance(file_obj, bytes):
            file_content = file_obj
        else:
            # Try to convert to bytes
            file_content = bytes(file_obj)
        
        # Reset pointer for potential fallback use
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
    except Exception as e:
        import sys
        print(f"Error reading file for upload: {str(e)}", file=sys.stderr)
        return None
    
    # Upload file content as bytes
    try:
        # New Supabase client (2.24+) requires bytes and content-type
        from mimetypes import guess_type
        content_type, _ = guess_type(original_filename or "")
        if not content_type:
            content_type = "application/octet-stream"
        
        # Upload with content type
        result = client.storage.from_(SUPABASE_BUCKET).upload(
            storage_path, 
            file_content,
            file_options={"content-type": content_type}
        )
        
        # Check if upload was successful
        if result:
            public_url = client.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
            return public_url
        else:
            return None
            
    except Exception as e:
        import sys
        error_msg = str(e)
        print(f"Error uploading to Supabase: {error_msg}", file=sys.stderr)
        return None

    public_url = client.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
    return public_url


def check_file_exists(storage_path: str) -> bool:
    """
    Check if a file exists in Supabase Storage.
    
    - storage_path: The path to the file in storage (e.g., "resumes/123/abc123.pdf")
    Returns True if file exists, False otherwise.
    """
    client = _get_client()
    if not client:
        return False
    
    try:
        files = client.storage.from_(SUPABASE_BUCKET).list(storage_path.rsplit('/', 1)[0] if '/' in storage_path else '')
        filename = storage_path.split('/')[-1]
        return any(f.get('name') == filename for f in files if isinstance(f, dict))
    except Exception:
        # Try alternative method - attempt to get file info
        try:
            client.storage.from_(SUPABASE_BUCKET).download(storage_path)
            return True
        except Exception:
            return False


def list_files_in_folder(folder: str = "", limit: int = 100) -> list:
    """
    List all files in a specific folder within the Supabase bucket.
    
    - folder: Folder path (e.g., "resumes/123" or "attachments/456")
    - limit: Maximum number of files to return
    
    Returns a list of file information dictionaries.
    """
    client = _get_client()
    if not client:
        return []
    
    folder = folder.strip("/ ") if folder else ""
    
    try:
        files = client.storage.from_(SUPABASE_BUCKET).list(folder, {"limit": limit})
        return files if isinstance(files, list) else []
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def get_file_info_from_url(public_url: str) -> Optional[dict]:
    """
    Extract storage path from a Supabase public URL and check if file exists.
    
    - public_url: The public URL of the file (e.g., "https://...supabase.co/storage/v1/object/public/student-docs/resumes/123/abc.pdf")
    Returns dict with 'exists': bool, 'storage_path': str, or None if URL is invalid
    """
    client = _get_client()
    if not client or not public_url:
        return None
    
    try:
        # Extract storage path from URL
        # URL format: https://xxx.supabase.co/storage/v1/object/public/BUCKET_NAME/path/to/file
        parts = public_url.split('/object/public/')
        if len(parts) < 2:
            return None
        
        full_path = parts[1]
        # Remove bucket name from path (it's in the URL before the actual path)
        bucket_prefix = f"{SUPABASE_BUCKET}/"
        if full_path.startswith(bucket_prefix):
            storage_path = full_path[len(bucket_prefix):]
        else:
            storage_path = full_path
        
        exists = check_file_exists(storage_path)
        
        return {
            'exists': exists,
            'storage_path': storage_path,
            'public_url': public_url
        }
    except Exception:
        return None


def get_all_student_files(student_id: int) -> dict:
    """
    Get all files uploaded by a specific student.
    
    - student_id: The student profile ID
    Returns a dict with 'resumes' and 'attachments' lists
    """
    client = _get_client()
    if not client:
        return {'resumes': [], 'attachments': []}
    
    result = {
        'resumes': [],
        'attachments': []
    }
    
    try:
        # List resumes
        resumes = list_files_in_folder(f"resumes/{student_id}")
        result['resumes'] = resumes
        
        # List attachments
        attachments = list_files_in_folder(f"attachments/{student_id}")
        result['attachments'] = attachments
    except Exception as e:
        print(f"Error getting student files: {e}")
    
    return result

