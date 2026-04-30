# AI-Powered Internship Management Portal

A full-stack web application that connects students, companies, and faculty through an intelligent internship lifecycle platform — with AI-driven features for matching, resume parsing, and opportunity recommendations.

---

## Features

### Student
- Profile creation with resume & certificate uploads
- AI-powered internship recommendations based on skills
- Browse and apply to internship opportunities
- Real-time application status tracking
- In-app messaging with companies

### Company
- Post and manage internship listings
- AI-assisted candidate shortlisting with fit scores
- Document verification and status management
- Communicate with applicants via messaging

### Faculty
- Monitor student internship progress
- Review and verify student documents
- Track placement statistics

### Admin
- Full platform oversight and user management
- Analytics dashboard
- Notification and policy management

---

## AI Features
- **Resume Parser** — Extracts skills, education, and experience using NLP/NER
- **Job-Candidate Matching** — Ranks applicants by resume-JD similarity
- **Smart Recommendations** — Suggests relevant internships based on student profile
- **Anomaly Detection** — Flags duplicate or suspicious applications

---

## 🗂️ Project Structure
├── frontend/
├── routes/
│   ├── ai_features.py
│   ├── applications.py
│   ├── auth.py
│   ├── company.py
│   ├── student.py
│   ├── faculty.py
│   ├── admin.py
│   ├── opportunities.py
│   ├── messages.py
│   ├── notifications.py
│   └── helpers.py
├── static/
├── templates/
└── README.md

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | Supabase (PostgreSQL) |
| AI/ML | NLP, NER, Transformer Embeddings |
| Auth | Role-based (Student / Company / Faculty / Admin) |
| Storage | Supabase Storage |

---

## ⚙️ Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/internship-portal.git
cd internship-portal

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add environment variables
cp .env.example .env

# 5. Run the application
python app.py


## Built as part of an academic internship project.
Feel free to raise issues or contribute via pull requests.

