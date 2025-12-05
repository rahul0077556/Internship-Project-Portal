"""
Test script to demonstrate API endpoints with sample requests
Shows how to use the skills matching endpoints via HTTP requests
"""
import json

def print_api_examples():
    """Print examples of API endpoint usage"""
    
    print("\n" + "="*70)
    print("  SKILLS MATCHING API - ENDPOINT EXAMPLES")
    print("="*70)
    
    print("\n📚 All endpoints require JWT authentication")
    print("   Get token by logging in: POST /api/auth/login")
    
    # Student endpoints
    print("\n" + "="*70)
    print("  STUDENT ENDPOINTS")
    print("="*70)
    
    print("\n1️⃣  GET /api/student/skills")
    print("   Get all available skills and student's current skills")
    print("   Response:")
    print(json.dumps({
        "all_skills": [
            {"id": 1, "name": "Python", "category": "programming", "has_skill": True},
            {"id": 2, "name": "React", "category": "framework", "has_skill": False}
        ],
        "current_skills": [
            {"skill_name": "Python", "proficiency_level": "advanced"}
        ]
    }, indent=2))
    
    print("\n2️⃣  POST /api/student/skills")
    print("   Add/update student skills")
    print("   Request Body:")
    print(json.dumps({
        "skills": ["Python", "React", "JavaScript", "SQL"],
        "proficiency_levels": {
            "Python": "advanced",
            "React": "intermediate"
        }
    }, indent=2))
    
    print("\n3️⃣  GET /api/student/matched-opportunities?min_match=50&limit=20")
    print("   Get opportunities matched with student's skills")
    print("   Response:")
    print(json.dumps({
        "matched_opportunities": [
            {
                "id": 1,
                "title": "React Developer Internship",
                "company_name": "Tech Corp",
                "match_data": {
                    "match_percentage": 75.5,
                    "matched_skills": ["React", "JavaScript", "HTML"],
                    "missing_skills": ["Node.js", "Express"],
                    "total_required": 5,
                    "matched_count": 3
                }
            }
        ],
        "total": 15
    }, indent=2))
    
    print("\n4️⃣  GET /api/student/matched-external-jobs?min_match=60&limit=20")
    print("   Get external jobs matched with student's skills")
    
    print("\n5️⃣  GET /api/student/opportunities/{id}/match")
    print("   Get detailed match information for a specific opportunity")
    
    # Company endpoints
    print("\n" + "="*70)
    print("  COMPANY ENDPOINTS")
    print("="*70)
    
    print("\n1️⃣  GET /api/company/opportunities/{id}/skills")
    print("   Get all skills and opportunity's current skills")
    
    print("\n2️⃣  PUT /api/company/opportunities/{id}/skills")
    print("   Update required skills for an opportunity")
    print("   Request Body:")
    print(json.dumps({
        "skills": ["React", "Node.js", "MongoDB", "Express"],
        "required_skills": ["React", "Node.js"]  # These are required, others preferred
    }, indent=2))
    
    print("\n3️⃣  GET /api/company/opportunities/{id}/matching-students?min_match=70&limit=50")
    print("   Get students matched with an opportunity")
    print("   Response:")
    print(json.dumps({
        "opportunity": {"id": 1, "title": "React Developer Internship"},
        "matched_students": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "match_data": {
                    "match_percentage": 85.0,
                    "matched_skills": ["React", "JavaScript", "Node.js"],
                    "missing_skills": ["MongoDB"],
                    "total_required": 4,
                    "matched_count": 3
                }
            }
        ],
        "total": 12
    }, indent=2))
    
    print("\n4️⃣  GET /api/company/skills")
    print("   Get all available skills")
    
    # Testing with curl
    print("\n" + "="*70)
    print("  TESTING WITH CURL")
    print("="*70)
    
    print("\n📝 Example: Get matched opportunities")
    print("""
# 1. Login to get token
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "student@example.com", "password": "password"}'

# 2. Use token to get matched opportunities
curl -X GET "http://localhost:5000/api/student/matched-opportunities?min_match=50" \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
""")
    
    print("\n📝 Example: Add student skills")
    print("""
curl -X POST http://localhost:5000/api/student/skills \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "skills": ["Python", "React", "JavaScript"],
    "proficiency_levels": {"Python": "advanced"}
  }'
""")
    
    print("\n📝 Example: Update opportunity skills (Company)")
    print("""
curl -X PUT http://localhost:5000/api/company/opportunities/1/skills \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "skills": ["React", "Node.js", "MongoDB"],
    "required_skills": ["React", "Node.js"]
  }'
""")


if __name__ == "__main__":
    print_api_examples()
    
    print("\n" + "="*70)
    print("  QUICK TEST COMMANDS")
    print("="*70)
    print("""
1. Run database migration:
   python create_skills_tables.py

2. Test the matching system:
   python test_skills_matching.py

3. Start your Flask server:
   python app.py

4. Test API endpoints (in another terminal):
   # See examples above or use Postman/Thunder Client
""")

