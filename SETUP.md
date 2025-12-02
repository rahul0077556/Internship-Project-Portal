# Complete Setup Guide

## Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask server:**
   ```bash
   python app.py
   ```
   Server runs on http://localhost:5000

3. **Seed dummy data:**
   ```bash
   python seed_data.py
   ```

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```
   Frontend runs on http://localhost:3000

## Test Accounts (after seeding)

- **Admin:** admin@pict.edu / admin123
- **Faculty:** faculty@pict.edu / faculty123
- **Company:** techcorp@example.com / company123
- **Student:** john@student.pict.edu / student123

## Features Implemented

### For Students
✅ Sign up / Login / Profile creation
✅ Resume upload
✅ Dashboard with recommendations
✅ Search & filter opportunities
✅ Apply to opportunities
✅ Notifications
✅ AI-powered recommendations
✅ Resume scoring

### For Companies/Faculty
✅ Sign up / Login / Profile
✅ Post opportunities
✅ Dashboard
✅ View applicants
✅ AI-powered screening
✅ Update application status
✅ Messaging

### Common Features
✅ Real-time notifications
✅ Messaging system
✅ Responsive UI

