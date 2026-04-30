# AI-Powered Internship Management Portal

A full-stack web application that connects students, companies, and faculty through an intelligent internship lifecycle platform — with AI-driven features for matching, resume parsing, and opportunity recommendations.

---
<img width="1600" height="1000" alt="IMG-20251202-WA0021" src="https://github.com/user-attachments/assets/249e21ee-fd82-4425-a017-655573ec674c" />
<img width="1600" height="1000" alt="IMG-20251202-WA0022" src="https://github.com/user-attachments/assets/524c446b-c951-4e06-b764-e027332d9fb6" />
<img width="1600" height="1000" alt="IMG-20251205-WA0028" src="https://github.com/user-attachments/assets/29f1589c-f577-4e95-8529-d26cf6c63354" />
<img width="1600" height="1000" alt="IMG-20251205-WA0027" src="https://github.com/user-attachments/assets/cf96311b-1947-4d5e-b7c1-81d2ffb14e22" />
<img width="1600" height="1000" alt="IMG-20251202-WA0023" src="https://github.com/user-attachments/assets/b9987bfe-823c-4542-9c84-add64a8554e7" />



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

