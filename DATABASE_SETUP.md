# PostgreSQL Database Setup Guide

## Step 1: Verify Your PostgreSQL Credentials

From your pgAdmin screenshot, I can see:
- **Server**: RNSSS (PostgreSQL 17)
- **Database**: MyPortalDb
- **Username**: postgres

To find your password:
1. Open pgAdmin 4
2. Right-click on the "RNSSS" server
3. Select "Properties"
4. Go to the "Connection" tab
5. Check the password (it might be masked)

## Step 2: Create .env File

Create a `.env` file in the project root with your credentials:

```env
DATABASE_USER=postgres
DATABASE_PASSWORD=YOUR_ACTUAL_PASSWORD_HERE
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=MyPortalDb
```

**Note**: If your PostgreSQL server is on a different host (not localhost), update `DATABASE_HOST` accordingly.

## Step 3: Test Database Connection

Run the connection test script:

```bash
python test_db_connection.py --password YOUR_ACTUAL_PASSWORD
```

Or if you've created the `.env` file:

```bash
python test_db_connection.py
```

## Step 4: Ensure Database Exists

Make sure the database `MyPortalDb` exists in PostgreSQL:
1. Open pgAdmin 4
2. Connect to your RNSSS server
3. Right-click on "Databases"
4. Select "Create" → "Database"
5. Name it `MyPortalDb` (if it doesn't exist)

## Step 5: Initialize Database Tables

Once the connection test passes, run:

```bash
python init_postgres_db.py
```

This will create all necessary tables for:
- Users and authentication
- Student profiles and all related data
- Company profiles
- Opportunities/Internships
- Applications
- Messages and notifications

## Step 6: Verify Tables Created

After initialization, you can verify in pgAdmin:
1. Expand `MyPortalDb` → `Schemas` → `public` → `Tables`
2. You should see tables like:
   - `users`
   - `student_profiles`
   - `student_education`
   - `student_internships`
   - `student_projects`
   - `company_profiles`
   - `opportunities`
   - `applications`
   - And many more...

## Troubleshooting

### Password Authentication Failed
- Double-check your password in pgAdmin
- Make sure you're using the correct username
- Verify the server is running

### Database Does Not Exist
- Create the database `MyPortalDb` in pgAdmin first
- Or use an existing database name and update `.env`

### Connection Refused
- Ensure PostgreSQL server is running
- Check if the port (default 5432) is correct
- Verify firewall settings if connecting remotely

## Student Profile Data Mapping

All student data will be saved in these tables:

### Main Profile (`student_profiles`)
- Basic info: first_name, last_name, middle_name, phone, email (from users table)
- Academic: prn_number, course, specialization, gender
- Personal: date_of_birth, address, bio
- Links: linkedin_url, github_url, portfolio_url
- Files: resume_path, profile_picture
- JSON fields: education, skills, interests

### Related Tables
- `student_education` - Education history
- `student_experiences` - Work experience
- `student_internships` - Internship history
- `student_projects` - Projects
- `student_trainings` - Training programs
- `student_certifications` - Certifications
- `student_publications` - Publications
- `student_positions` - Positions held
- `student_attachments` - Resume, certificates, documents
- `student_offers` - Job offers received

All data is properly mapped and will be saved when students create/update their profiles!

