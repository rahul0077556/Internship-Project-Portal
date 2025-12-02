# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run the Application

### Windows:
```bash
python app.py
```
Or double-click `run.bat`

### Linux/Mac:
```bash
python app.py
```
Or run `bash run.sh`

## Step 3: Access the Application

Open your browser and go to: **http://localhost:5000**

## Step 4: Create an Admin Account (Optional)

To create an admin account for managing the portal:

```bash
python setup_admin.py
```

Follow the prompts to create an admin user.

## Step 5: Start Using the Portal

1. **As a Student:**
   - Click "Sign Up" and select "Student"
   - Fill in your details and create an account
   - Complete your profile with skills and interests
   - Upload your resume
   - Browse opportunities and apply!

2. **As a Company:**
   - Click "Sign Up" and select "Company"
   - Fill in company details
   - Wait for admin approval (or auto-approve if configured)
   - Post internship/project opportunities
   - Review and manage applications

3. **As Faculty:**
   - Click "Sign Up" and select "Faculty"
   - Fill in faculty details
   - Post academic projects
   - Manage student applications

4. **As Admin:**
   - Use the admin account created in Step 4
   - Approve/reject user registrations
   - Approve/reject opportunities
   - View analytics and manage the system

## Features to Try

### For Students:
- ✅ Complete your profile with skills
- ✅ Upload a resume (PDF/DOCX)
- ✅ Browse opportunities with filters
- ✅ Get AI-powered recommendations
- ✅ Apply to opportunities
- ✅ Track application status
- ✅ Receive notifications

### For Companies/Faculty:
- ✅ Post opportunities with detailed requirements
- ✅ View and filter applicants
- ✅ Use AI screening to rank candidates
- ✅ Update application status
- ✅ Send messages to candidates
- ✅ View analytics

### For Admins:
- ✅ Manage all users
- ✅ Approve/reject opportunities
- ✅ View comprehensive analytics
- ✅ Manage blacklist
- ✅ Monitor system activity

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `app.py` line 73:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Database Issues
If you encounter database errors, delete `internship_portal.db` and restart the application. The database will be recreated automatically.

### Missing Dependencies
Make sure all packages are installed:
```bash
pip install -r requirements.txt
```

## Real-time Features

The application uses Socket.IO for real-time updates. Make sure you have a stable internet connection for:
- Real-time notifications
- Live message updates
- Application status changes

## Need Help?

Refer to the main `README.md` for detailed documentation and API endpoints.

