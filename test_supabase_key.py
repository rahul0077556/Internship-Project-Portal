"""
Test script to diagnose Supabase API key issues.
This will help identify if the key format is the problem.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 Supabase API Key Diagnostic")
print("=" * 60)

supabase_url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
anon_key = os.getenv("SUPABASE_ANON_KEY")

print("\n📋 Environment Variables:")
print(f"   SUPABASE_URL: {supabase_url}")
print(f"\n   SUPABASE_SERVICE_ROLE_KEY:")
if service_key:
    print(f"      Length: {len(service_key)} characters")
    print(f"      Starts with: {service_key[:20]}...")
    print(f"      Format: {'✅ sb_secret_' if service_key.startswith('sb_secret_') else '❌ Not sb_secret_'}")
    print(f"      Full key: {service_key}")
else:
    print("      ❌ Not set")

print(f"\n   SUPABASE_ANON_KEY:")
if anon_key:
    print(f"      Length: {len(anon_key)} characters")
    print(f"      Starts with: {anon_key[:20]}...")
    print(f"      Format: {'✅ JWT (eyJ...)' if anon_key.startswith('eyJ') else '❌ Not JWT format'}")
else:
    print("      ❌ Not set")

print("\n🔧 Testing Supabase Client Initialization:")
print("-" * 60)

# Test with service role key
if service_key:
    print("\n1. Testing with SUPABASE_SERVICE_ROLE_KEY...")
    try:
        from supabase import create_client
        client = create_client(supabase_url, service_key)
        print("   ✅ Client created successfully!")
        
        # Try to access storage
        try:
            bucket = client.storage.from_("student-docs")
            print("   ✅ Storage access successful!")
        except Exception as e:
            print(f"   ⚠️  Storage access failed: {str(e)[:100]}")
    except Exception as e:
        print(f"   ❌ Client creation failed: {str(e)[:100]}")
        print(f"   Full error: {str(e)}")

# Test with anon key if available
if anon_key and not service_key:
    print("\n2. Testing with SUPABASE_ANON_KEY...")
    try:
        from supabase import create_client
        client = create_client(supabase_url, anon_key)
        print("   ✅ Client created successfully!")
    except Exception as e:
        print(f"   ❌ Client creation failed: {str(e)[:100]}")

print("\n" + "=" * 60)
print("💡 Recommendations:")
print("=" * 60)

if service_key and service_key.startswith('sb_secret_'):
    print("\n✅ You're using the new key format (sb_secret_)")
    print("   This format might not be supported by older Supabase Python clients.")
    print("\n   Try one of these solutions:")
    print("   1. Use the LEGACY JWT-based service_role key instead")
    print("      - Go to: Settings → API Keys → 'Legacy anon, service_role API keys' tab")
    print("      - Copy the 'service_role' key (starts with eyJ...)")
    print("      - Update .env: SUPABASE_SERVICE_ROLE_KEY=<legacy-jwt-key>")
    print("\n   2. Or upgrade to latest Supabase Python client:")
    print("      pip uninstall supabase -y")
    print("      pip install supabase --upgrade")
    
if service_key and len(service_key) < 50:
    print("\n⚠️  Your key seems short. Make sure you copied the FULL key!")
    print("   The key should be much longer. Check for truncation.")

print("\n" + "=" * 60)

