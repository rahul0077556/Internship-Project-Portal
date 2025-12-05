"""
Test script to demonstrate and test the Skills Matching System
Run this to see the output and verify everything works!
"""
import sys
from app import app, db
from models import (
    StudentProfile, Opportunity, Skill, StudentSkill, OpportunitySkill,
    ExternalJob, ExternalJobSkill, User, CompanyProfile
)
from skills_matching import SkillsMatchingService
from external_jobs_service import ExternalJobsService


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_database_setup():
    """Test 1: Check if tables exist and skills are seeded"""
    print_section("Test 1: Database Setup Check")
    
    try:
        # Check if skills table has data
        skills_count = Skill.query.count()
        print(f"✅ Skills table exists: {skills_count} skills found")
        
        if skills_count > 0:
            print("\n📋 Sample skills:")
            sample_skills = Skill.query.limit(10).all()
            for skill in sample_skills:
                print(f"   - {skill.name} ({skill.category})")
        else:
            print("⚠️  No skills found! Run: python create_skills_tables.py")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Run: python create_skills_tables.py first!")
        return False


def test_student_skills():
    """Test 2: Add skills to a student and verify"""
    print_section("Test 2: Student Skills Management")
    
    try:
        # Find or create a test student
        student = StudentProfile.query.first()
        
        if not student:
            print("⚠️  No students found in database")
            print("   Create a student account first through the API")
            return False
        
        print(f"📝 Testing with student: {student.first_name} {student.last_name} (ID: {student.id})")
        
        # Add skills
        test_skills = ["Python", "React", "JavaScript", "SQL", "Node.js"]
        print(f"\n➕ Adding skills: {', '.join(test_skills)}")
        
        SkillsMatchingService.update_student_skills(
            student.id,
            test_skills,
            {"Python": "advanced", "React": "intermediate"}
        )
        
        # Verify skills were added
        student_skills = StudentSkill.query.filter_by(student_id=student.id).all()
        print(f"\n✅ Student now has {len(student_skills)} skills:")
        for ss in student_skills:
            skill = Skill.query.get(ss.skill_id)
            print(f"   - {skill.name} ({ss.proficiency_level})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_opportunity_skills():
    """Test 3: Add skills to an opportunity"""
    print_section("Test 3: Opportunity Skills Management")
    
    try:
        # Find or create a test opportunity
        opportunity = Opportunity.query.first()
        
        if not opportunity:
            print("⚠️  No opportunities found in database")
            print("   Create an opportunity first through the API")
            return False
        
        print(f"📝 Testing with opportunity: {opportunity.title} (ID: {opportunity.id})")
        
        # Add skills
        required_skills = ["React", "JavaScript", "Node.js"]
        preferred_skills = ["MongoDB", "Express"]
        all_skills = required_skills + preferred_skills
        
        print(f"\n➕ Adding required skills: {', '.join(required_skills)}")
        print(f"➕ Adding preferred skills: {', '.join(preferred_skills)}")
        
        SkillsMatchingService.update_opportunity_skills(
            opportunity.id,
            all_skills,
            required_skills
        )
        
        # Verify skills were added
        opp_skills = OpportunitySkill.query.filter_by(opportunity_id=opportunity.id).all()
        print(f"\n✅ Opportunity now has {len(opp_skills)} skills:")
        
        required = [os for os in opp_skills if os.is_required]
        preferred = [os for os in opp_skills if not os.is_required]
        
        print(f"\n   Required ({len(required)}):")
        for os in required:
            skill = Skill.query.get(os.skill_id)
            print(f"      - {skill.name}")
        
        print(f"\n   Preferred ({len(preferred)}):")
        for os in preferred:
            skill = Skill.query.get(os.skill_id)
            print(f"      - {skill.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_matching():
    """Test 4: Test the matching algorithm"""
    print_section("Test 4: Skills Matching Algorithm")
    
    try:
        student = StudentProfile.query.first()
        opportunity = Opportunity.query.first()
        
        if not student or not opportunity:
            print("⚠️  Need both student and opportunity for matching test")
            return False
        
        print(f"🎯 Matching Student: {student.first_name} {student.last_name}")
        print(f"   Against Opportunity: {opportunity.title}\n")
        
        # Calculate match
        match_data = SkillsMatchingService.calculate_match_score(student.id, opportunity.id)
        
        print("📊 Match Results:")
        print(f"   Match Percentage: {match_data['match_percentage']}%")
        print(f"   Matched Skills: {match_data['matched_count']}/{match_data['total_required']}")
        
        if match_data['matched_skills']:
            print(f"\n   ✅ Matched Skills:")
            for skill in match_data['matched_skills']:
                print(f"      - {skill}")
        
        if match_data['missing_skills']:
            print(f"\n   ❌ Missing Skills:")
            for skill in match_data['missing_skills']:
                print(f"      - {skill}")
        
        if match_data['total_preferred'] > 0:
            print(f"\n   📌 Preferred Skills Matched: {match_data['preferred_skills_matched']}/{match_data['total_preferred']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_matched_opportunities():
    """Test 5: Get all matched opportunities for a student"""
    print_section("Test 5: Get Matched Opportunities")
    
    try:
        student = StudentProfile.query.first()
        
        if not student:
            print("⚠️  No students found")
            return False
        
        print(f"🔍 Finding matched opportunities for: {student.first_name} {student.last_name}\n")
        
        matched_opps = SkillsMatchingService.get_matched_opportunities(
            student.id,
            limit=10,
            min_match=0.0
        )
        
        print(f"📋 Found {len(matched_opps)} matched opportunities:\n")
        
        for i, opp in enumerate(matched_opps[:5], 1):  # Show top 5
            match_data = opp['match_data']
            print(f"{i}. {opp['title']}")
            print(f"   Company: {opp.get('company_name', 'N/A')}")
            print(f"   Match: {match_data['match_percentage']}%")
            print(f"   Matched: {', '.join(match_data['matched_skills'][:3])}")
            if match_data['missing_skills']:
                print(f"   Missing: {', '.join(match_data['missing_skills'][:3])}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_matching_students():
    """Test 6: Get matching students for an opportunity"""
    print_section("Test 6: Get Matching Students (Company View)")
    
    try:
        opportunity = Opportunity.query.first()
        
        if not opportunity:
            print("⚠️  No opportunities found")
            return False
        
        print(f"🔍 Finding matching students for: {opportunity.title}\n")
        
        matched_students = SkillsMatchingService.get_matching_students(
            opportunity.id,
            limit=10,
            min_match=0.0
        )
        
        print(f"📋 Found {len(matched_students)} matching students:\n")
        
        for i, student in enumerate(matched_students[:5], 1):  # Show top 5
            match_data = student['match_data']
            print(f"{i}. {student['name']}")
            print(f"   Email: {student.get('email', 'N/A')}")
            print(f"   Match: {match_data['match_percentage']}%")
            print(f"   Matched: {', '.join(match_data['matched_skills'][:3])}")
            if match_data['missing_skills']:
                print(f"   Missing: {', '.join(match_data['missing_skills'][:3])}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_external_jobs():
    """Test 7: Test external jobs (if API key is configured)"""
    print_section("Test 7: External Jobs (Optional)")
    
    try:
        # Check if any external jobs exist
        external_jobs_count = ExternalJob.query.count()
        
        if external_jobs_count > 0:
            print(f"✅ Found {external_jobs_count} external jobs in database")
            
            # Show sample
            sample_jobs = ExternalJob.query.filter_by(is_active=True).limit(3).all()
            print("\n📋 Sample external jobs:")
            for job in sample_jobs:
                print(f"\n   - {job.title}")
                print(f"     Company: {job.company_name}")
                print(f"     Source: {job.source}")
                print(f"     Location: {job.location}")
                
                # Get skills
                job_skills = ExternalJobSkill.query.filter_by(external_job_id=job.id).all()
                if job_skills:
                    skill_names = [Skill.query.get(js.skill_id).name for js in job_skills]
                    print(f"     Skills: {', '.join(skill_names[:5])}")
        else:
            print("ℹ️  No external jobs found")
            print("\n   To fetch external jobs:")
            print("   1. Add JSEARCH_API_KEY to .env file")
            print("   2. Run: python external_jobs_service.py")
            print("   3. Or use: ExternalJobsService.fetch_and_store_jobs()")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  SKILLS MATCHING SYSTEM - TEST SUITE")
    print("="*70)
    
    results = []
    
    with app.app_context():
        # Test 1: Database setup
        results.append(("Database Setup", test_database_setup()))
        
        if not results[0][1]:
            print("\n❌ Database not set up! Run: python create_skills_tables.py")
            return
        
        # Test 2: Student skills
        results.append(("Student Skills", test_student_skills()))
        
        # Test 3: Opportunity skills
        try:
            db.session.rollback()  # Rollback any previous errors
            results.append(("Opportunity Skills", test_opportunity_skills()))
        except Exception as e:
            print(f"Error in opportunity skills test: {e}")
            results.append(("Opportunity Skills", False))
        
        # Test 4: Matching algorithm
        results.append(("Matching Algorithm", test_matching()))
        
        # Test 5: Get matched opportunities
        results.append(("Get Matched Opportunities", test_get_matched_opportunities()))
        
        # Test 6: Get matching students
        results.append(("Get Matching Students", test_get_matching_students()))
        
        # Test 7: External jobs
        results.append(("External Jobs", test_external_jobs()))
    
    # Print summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Skills matching system is working!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()

