# 📺 How to See Output While Running

## 🎯 Quick Ways to See Results

### 1. **Run the Test Script** (Easiest!)

```bash
python test_skills_matching.py
```

**This shows:**
- ✅ Database setup status
- ✅ Student skills being added
- ✅ Opportunity skills being added  
- ✅ **Real-time match calculations**
- ✅ **Matched opportunities with percentages**
- ✅ **Matching students for companies**

**Example Output:**
```
📊 Match Results:
   Match Percentage: 80.0%
   Matched Skills: 3/3
   ✅ Matched Skills: React, JavaScript, Node.js
   ❌ Missing Skills: MongoDB, Express
```

---

### 2. **View API Endpoint Examples**

```bash
python test_api_endpoints.py
```

Shows you:
- All available endpoints
- Request/response examples
- curl command examples

---

### 3. **Test via API (Using Flask Server)**

#### Step 1: Start your Flask server
```bash
python app.py
```

#### Step 2: Test endpoints (in another terminal or browser)

**Using curl:**
```bash
# Get matched opportunities
curl -X GET "http://localhost:5000/api/student/matched-opportunities?min_match=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Using Python requests:**
```python
import requests

# Login first
response = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'student@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Get matched opportunities
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:5000/api/student/matched-opportunities?min_match=50',
    headers=headers
)
print(response.json())
```

**Using Postman/Thunder Client:**
1. Import the endpoints
2. Set Authorization header with JWT token
3. Send requests and see JSON responses

---

### 4. **Interactive Python Console**

```python
from app import app, db
from models import StudentProfile, Opportunity
from skills_matching import SkillsMatchingService

with app.app_context():
    # Get a student
    student = StudentProfile.query.first()
    
    # Calculate match for an opportunity
    opportunity = Opportunity.query.first()
    
    match_data = SkillsMatchingService.calculate_match_score(
        student.id, 
        opportunity.id
    )
    
    print(f"Match: {match_data['match_percentage']}%")
    print(f"Matched: {match_data['matched_skills']}")
    print(f"Missing: {match_data['missing_skills']}")
```

---

## 📊 What You'll See

### Student View - Matched Opportunities:
```json
{
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
}
```

### Company View - Matching Students:
```json
{
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
}
```

---

## 🎬 Step-by-Step Demo

### 1. Setup (One-time)
```bash
python create_skills_tables.py
```

### 2. Add Student Skills
```bash
# Via API or test script
python test_skills_matching.py  # Adds skills automatically
```

### 3. Add Job Skills
```bash
# Via API or test script
python test_skills_matching.py  # Adds skills automatically
```

### 4. See Matches
```bash
python test_skills_matching.py
```

**Output shows:**
- ✅ Skills added successfully
- ✅ Match percentage calculated
- ✅ Matched skills listed
- ✅ Missing skills listed
- ✅ All matched opportunities sorted by match %

---

## 🔍 Real-Time Testing

### Option 1: Test Script (Recommended)
```bash
python test_skills_matching.py
```
**Shows everything in one go!**

### Option 2: Flask Server + API Calls
```bash
# Terminal 1: Start server
python app.py

# Terminal 2: Make API calls
curl http://localhost:5000/api/student/matched-opportunities
```

### Option 3: Python Interactive
```python
python
>>> from app import app
>>> from skills_matching import SkillsMatchingService
>>> with app.app_context():
...     matches = SkillsMatchingService.get_matched_opportunities(1)
...     for m in matches[:3]:
...         print(f"{m['title']}: {m['match_data']['match_percentage']}%")
```

---

## 💡 Pro Tips

1. **Use the test script first** - It shows everything working
2. **Check the console output** - All calculations are printed
3. **Use Postman/Thunder Client** - Visual API testing
4. **Check database directly** - See raw data in PostgreSQL

---

## 🎯 Quick Test Commands

```bash
# 1. Test everything
python test_skills_matching.py

# 2. See API examples
python test_api_endpoints.py

# 3. Start server and test endpoints
python app.py
# Then use Postman/curl to test endpoints
```

---

**The test script (`test_skills_matching.py`) is your best friend!** 
It shows all the output you need to see the matching system in action! 🚀

