# 🎯 Skills Matching System - Complete Guide

## Overview

This system provides **real-time, accurate skills matching** between:
1. **Students ↔ Company Job Posts** (Internal matching)
2. **Students ↔ External Online Jobs** (Web-based matching)

All matching is calculated **dynamically** - no static percentages!

---

## 🗄️ Database Structure

### Tables Created:

1. **`skills`** - Master list of all skills
   - `id`, `name`, `category`, `normalized_name`, `aliases`

2. **`student_skills`** - Student skill mappings
   - `student_id`, `skill_id`, `proficiency_level`, `years_of_experience`

3. **`opportunity_skills`** - Job requirement mappings
   - `opportunity_id`, `skill_id`, `is_required`, `priority`

4. **`external_jobs`** - External jobs from web APIs
   - `title`, `company_name`, `description`, `location`, `source`, etc.

5. **`external_job_skills`** - Skills extracted from external jobs
   - `external_job_id`, `skill_id`, `confidence`

---

## 🚀 Setup

### Step 1: Create Database Tables

```bash
python create_skills_tables.py
```

This will:
- Create all skills tables
- Seed common skills (Python, React, JavaScript, etc.)

### Step 2: Configure External Job APIs (Optional)

Add to your `.env` file:

```env
# For fetching external jobs (optional)
JSEARCH_API_KEY=your_rapidapi_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
```

Get API key from: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

---

## 📚 API Endpoints

### For Students

#### 1. Get/Update Skills
```http
GET /api/student/skills
POST /api/student/skills
PUT /api/student/skills
```

**Request Body (POST/PUT):**
```json
{
  "skills": ["Python", "React", "JavaScript", "SQL"],
  "proficiency_levels": {
    "Python": "advanced",
    "React": "intermediate"
  }
}
```

**Response:**
```json
{
  "message": "Skills updated successfully",
  "skills": [
    {
      "id": 1,
      "skill_id": 5,
      "skill_name": "Python",
      "proficiency_level": "advanced"
    }
  ]
}
```

#### 2. Get Matched Opportunities
```http
GET /api/student/matched-opportunities?min_match=50&limit=20
```

**Response:**
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

#### 3. Get Matched External Jobs
```http
GET /api/student/matched-external-jobs?min_match=60&limit=20
```

#### 4. Get Match Details for Specific Opportunity
```http
GET /api/student/opportunities/{opportunity_id}/match
```

---

### For Companies

#### 1. Update Opportunity Skills
```http
PUT /api/company/opportunities/{opp_id}/skills
```

**Request Body:**
```json
{
  "skills": ["React", "Node.js", "MongoDB", "Express"],
  "required_skills": ["React", "Node.js"]  // Optional: mark which are required
}
```

#### 2. Get Matching Students for Opportunity
```http
GET /api/company/opportunities/{opp_id}/matching-students?min_match=70&limit=50
```

**Response:**
```json
{
  "opportunity": {...},
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

#### 3. Get All Available Skills
```http
GET /api/company/skills
```

---

## 🧮 Matching Algorithm

### How It Works:

1. **Normalization**: All skill names are normalized (lowercase, handle variations)
   - "React" = "react"
   - "JavaScript" = "javascript" = "js"
   - "Node.js" = "nodejs" = "node.js"

2. **Real-time Calculation**:
   ```python
   match_percentage = (matched_required_skills / total_required_skills) * 80% 
                    + (matched_preferred_skills / total_preferred_skills) * 20%
   ```

3. **Weighted Scoring**:
   - Required skills: 80% weight
   - Preferred skills: 20% weight

4. **Returns**:
   - Match percentage (0-100)
   - List of matched skills
   - List of missing skills
   - Total required vs matched count

---

## 🌐 External Jobs Integration

### Fetch External Jobs

```bash
python external_jobs_service.py
```

Or programmatically:

```python
from external_jobs_service import ExternalJobsService
from app import app

with app.app_context():
    result = ExternalJobsService.fetch_and_store_jobs(
        query="internship python react",
        location="",
        num_pages=2,
        source="jsearch"
    )
    print(result)
```

### Supported Sources:

1. **JSearch API** (via RapidAPI)
   - Supports: LinkedIn, Indeed, Glassdoor, etc.
   - Requires: RapidAPI key

2. **Custom Scrapers** (can be added)
   - Internshala
   - Naukri
   - Custom job boards

### Skill Extraction:

External jobs automatically extract skills from job descriptions using keyword matching. Skills are stored with confidence scores.

---

## 💡 Usage Examples

### Example 1: Student Adds Skills

```python
# Student profile update
POST /api/student/skills
{
  "skills": ["Python", "Django", "PostgreSQL", "React", "JavaScript"]
}
```

### Example 2: Company Posts Job with Skills

```python
# Create opportunity
POST /api/company/opportunities
{
  "title": "Full Stack Developer Intern",
  "description": "...",
  "required_skills": ["Python", "React", "PostgreSQL"]
}

# Or update skills separately
PUT /api/company/opportunities/1/skills
{
  "skills": ["Python", "React", "PostgreSQL", "Docker"],
  "required_skills": ["Python", "React"]
}
```

### Example 3: Student Views Matched Jobs

```python
# Get all opportunities matching student's skills
GET /api/student/matched-opportunities?min_match=50

# Response shows jobs sorted by match percentage
```

### Example 4: Company Finds Matching Students

```python
# Get students matching an opportunity
GET /api/company/opportunities/1/matching-students?min_match=70

# Response shows students sorted by match percentage
```

---

## 🔧 Advanced Features

### Skill Normalization

The system handles skill name variations automatically:
- "React" = "react" = "ReactJS" = "react.js"
- "JavaScript" = "javascript" = "JS" = "js"
- "Node.js" = "nodejs" = "NodeJS"

### Proficiency Levels

Students can set proficiency levels:
- `beginner`
- `intermediate`
- `advanced`
- `expert`

(Currently used for display, can be enhanced for weighted matching)

### Skill Categories

Skills are categorized:
- `programming` - Languages
- `framework` - Frameworks
- `database` - Databases
- `cloud` - Cloud platforms
- `devops` - DevOps tools
- `mobile` - Mobile development
- `data-science` - Data science
- `design` - Design tools

---

## 📊 Performance

- **Real-time matching**: Calculated on-demand, no caching needed
- **Efficient queries**: Uses indexed foreign keys
- **Scalable**: Handles thousands of students and jobs

---

## 🐛 Troubleshooting

### Skills not matching?

1. Check skill names are normalized correctly
2. Verify skills exist in `skills` table
3. Check student has skills assigned
4. Check opportunity has skills assigned

### External jobs not fetching?

1. Verify API keys in `.env`
2. Check API rate limits
3. Verify network connectivity

### Match percentage seems wrong?

1. Check if skills are marked as "required" vs "preferred"
2. Verify skill names match exactly (case-insensitive)
3. Check for duplicate skills

---

## 🎯 Next Steps

1. **Run migration**: `python create_skills_tables.py`
2. **Add student skills**: Use POST `/api/student/skills`
3. **Add job skills**: Use PUT `/api/company/opportunities/{id}/skills`
4. **Fetch external jobs**: `python external_jobs_service.py`
5. **View matches**: Use GET endpoints for students/companies

---

## 📝 Notes

- All matching is **real-time** - no static percentages
- Skills are **normalized** automatically
- External jobs **auto-extract** skills from descriptions
- System handles **skill variations** (React = ReactJS = react.js)

---

**Happy Matching! 🚀**

