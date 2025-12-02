from flask import Blueprint, request, jsonify, Response
import csv
import io
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from datetime import datetime

from models import (
    db,
    User,
    StudentProfile,
    StudentInternship,
    StudentOffer,
    CompanyProfile,
)
from routes.helpers import get_user_id


faculty_bp = Blueprint("faculty", __name__)


def _ensure_faculty():
    """Ensure the current user is a faculty (or admin) user."""
    user_id = get_user_id()
    user = User.query.get(user_id)
    if not user or user.role not in ["faculty", "admin"]:
        return None, jsonify({"error": "Unauthorized"}), 403
    return user, None, None


def _parse_ctc_to_lpa(ctc_value: str):
    """
    Best-effort parsing of CTC strings to numeric LPA for analytics.
    Accepts formats like '6', '6 LPA', '6.5 LPA', '600000', etc.
    Returns a float in LPA or None if parsing fails.
    """
    if not ctc_value:
        return None

    try:
        text = str(ctc_value).lower().replace("lpa", "").strip()
        # If looks like a big number (e.g. 600000), convert to LPA assuming per annum INR
        if text.isdigit() and len(text) >= 6:
            value = float(text) / 100000.0
        else:
            # Extract first float-like segment
            import re

            match = re.search(r"\\d+(?:\\.\\d+)?", text)
            if not match:
                return None
            value = float(match.group(0))
        return value
    except Exception:
        return None


def _fetch_placements(filters=None):
    """Reusable placement query returning structured rows."""
    filters = filters or {}
    branch = filters.get("branch")
    company = filters.get("company")
    min_ctc = filters.get("min_ctc")
    max_ctc = filters.get("max_ctc")

    query = (
        db.session.query(StudentOffer, StudentProfile)
        .join(StudentProfile, StudentProfile.id == StudentOffer.student_id)
        .filter(StudentOffer.status == "accepted")
    )

    if branch:
        query = query.filter(
            (func.lower(StudentProfile.course) == branch.lower())
            | (func.lower(StudentProfile.specialization) == branch.lower())
        )
    if company:
        query = query.filter(func.lower(StudentOffer.company_name) == company.lower())

    rows = []
    for offer, profile in query.all():
        ctc_lpa = _parse_ctc_to_lpa(offer.ctc)
        if min_ctc is not None and (ctc_lpa is None or ctc_lpa < min_ctc):
            continue
        if max_ctc is not None and (ctc_lpa is None or ctc_lpa > max_ctc):
            continue

        rows.append(
            {
                "student_name": f"{profile.first_name} {profile.last_name}".strip(),
                "prn": getattr(profile, "prn_number", None),
                "branch": profile.course or profile.specialization,
                "company": offer.company_name,
                "ctc": offer.ctc,
                "ctc_lpa": ctc_lpa,
                "role": offer.role,
                "location": offer.location,
                "joining_date": offer.joining_date.isoformat()
                if offer.joining_date
                else None,
                "offer_date": offer.offer_date.isoformat() if offer.offer_date else None,
                "ppo": False,
            }
        )
    return rows


def _collect_internship_rows():
    """Return all internships with student context."""
    query = (
        db.session.query(StudentInternship, StudentProfile)
        .join(StudentProfile, StudentProfile.id == StudentInternship.student_id)
    )

    rows = []
    for internship, profile in query.all():
        rows.append(
            {
                "student_name": f"{profile.first_name} {profile.last_name}".strip(),
                "branch": profile.course or profile.specialization,
                "organization": internship.organization,
                "designation": internship.designation,
                "domain": internship.industry_sector,
                "stipend": internship.stipend,
                "internship_type": internship.internship_type,
                "start_date": internship.start_date.isoformat()
                if internship.start_date
                else None,
                "end_date": internship.end_date.isoformat() if internship.end_date else None,
                "is_paid": bool(internship.stipend and internship.stipend.strip()),
            }
        )
    return rows


@faculty_bp.route("/login", methods=["POST"])
def faculty_login():
    """Faculty/admin specific login endpoint."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if (
        not user
        or user.role not in ["faculty", "admin"]
        or not user.check_password(password)
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    if not user.is_approved:
        return jsonify({"error": "Account pending approval"}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = user.generate_token()
    profile = user.company_profile

    return (
        jsonify(
            {
                "message": "Login successful",
                "token": token,
                "user": user.to_dict(),
                "profile": profile.to_dict() if profile else None,
            }
        ),
        200,
    )


def _build_dashboard_payload():
    """Utility that aggregates dashboard statistics + chart data."""
    # Total students
    total_students = StudentProfile.query.count()

    # Placements based on accepted offers
    accepted_offers = StudentOffer.query.filter_by(status="accepted").all()
    placed_student_ids = {offer.student_id for offer in accepted_offers}
    total_placed = len(placed_student_ids)
    total_unplaced = max(total_students - total_placed, 0)

    # Internships
    total_internships = StudentInternship.query.count()

    # Package analytics
    ctc_values = []
    for offer in accepted_offers:
        value = _parse_ctc_to_lpa(offer.ctc)
        if value is not None:
            ctc_values.append(value)

    highest_package = max(ctc_values) if ctc_values else 0
    average_package = (sum(ctc_values) / len(ctc_values)) if ctc_values else 0

    # Companies visited (from offers)
    total_companies = (
        db.session.query(func.count(func.distinct(StudentOffer.company_name)))
        .filter(StudentOffer.status == "accepted")
        .scalar()
        or 0
    )

    # Company-wise placements (bar chart)
    company_data = (
        db.session.query(StudentOffer.company_name, func.count(StudentOffer.id))
        .filter(StudentOffer.status == "accepted")
        .group_by(StudentOffer.company_name)
        .order_by(func.count(StudentOffer.id).desc())
        .limit(15)
        .all()
    )
    company_wise = [
        {"company": name, "placed": count} for name, count in company_data if name
    ]

    # Branch-wise placement percentage (donut)
    branch_totals = (
        db.session.query(StudentProfile.course, func.count(StudentProfile.id))
        .group_by(StudentProfile.course)
        .all()
    )
    branch_placed = (
        db.session.query(StudentProfile.course, func.count(func.distinct(StudentOffer.student_id)))
        .join(StudentOffer, StudentOffer.student_id == StudentProfile.id)
        .filter(StudentOffer.status == "accepted")
        .group_by(StudentProfile.course)
        .all()
    )
    branch_totals_dict = {branch or "Unknown": total for branch, total in branch_totals}
    branch_placed_dict = {branch or "Unknown": placed for branch, placed in branch_placed}

    branch_wise = []
    for branch, total in branch_totals_dict.items():
        placed = branch_placed_dict.get(branch, 0)
        percentage = (placed / total * 100) if total else 0
        branch_wise.append(
            {"branch": branch or "Unknown", "placed": placed, "total": total, "percentage": round(percentage, 1)}
        )

    # Package distribution buckets
    buckets = {
        "0-3": 0,
        "3-5": 0,
        "5-7": 0,
        "7-10": 0,
        "10+": 0,
    }
    for value in ctc_values:
        if value < 3:
            buckets["0-3"] += 1
        elif value < 5:
            buckets["3-5"] += 1
        elif value < 7:
            buckets["5-7"] += 1
        elif value < 10:
            buckets["7-10"] += 1
        else:
            buckets["10+"] += 1
    package_distribution = [
        {"range": key, "count": count} for key, count in buckets.items()
    ]

    # Simple year-wise (batch) trends based on joining_date year
    year_counts = {}
    for offer in accepted_offers:
        if offer.joining_date:
            year = offer.joining_date.year
        elif offer.offer_date:
            year = offer.offer_date.year
        else:
            continue
        year_counts[year] = year_counts.get(year, 0) + 1

    batch_trends = [
        {"year": str(year), "placed": count}
        for year, count in sorted(year_counts.items())
    ]

    return {
        "stats": {
            "total_students": total_students,
            "placed_students": total_placed,
            "unplaced_students": total_unplaced,
            "total_internships": total_internships,
            "highest_package_lpa": round(highest_package, 2),
            "average_package_lpa": round(average_package, 2),
            "total_companies": total_companies,
        },
        "charts": {
            "company_wise": company_wise,
            "branch_wise": branch_wise,
            "package_distribution": package_distribution,
            "batch_trends": batch_trends,
        },
    }


@faculty_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_faculty_stats():
    """
    High-level placement + internship statistics for faculty dashboard.
    """
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    return jsonify(_build_dashboard_payload()), 200


@faculty_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_faculty_profile():
    """Return faculty profile + user meta."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    profile = user.company_profile
    if not profile:
        profile = CompanyProfile(user_id=user.id, name=user.email.split("@")[0], is_faculty=True)
        db.session.add(profile)
        db.session.commit()

    return (
        jsonify(
            {
                "user": user.to_dict(),
                "profile": profile.to_dict(),
            }
        ),
        200,
    )


@faculty_bp.route("/profile/update", methods=["PATCH"])
@jwt_required()
def update_faculty_profile():
    """Allow faculty to update profile/settings."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    data = request.get_json() or {}
    profile = user.company_profile

    if not profile:
        profile = CompanyProfile(user_id=user.id, is_faculty=True, name=data.get("name") or user.email.split("@")[0])
        db.session.add(profile)

    for field in [
        "name",
        "description",
        "website",
        "phone",
        "address",
        "faculty_department",
        "company_size",
    ]:
        if field in data:
            setattr(profile, field, data[field])

    db.session.commit()

    return jsonify({"message": "Profile updated", "profile": profile.to_dict()}), 200


@faculty_bp.route("/placements/stats", methods=["GET"])
@jwt_required()
def get_placement_stats():
    """Alias endpoint required by API spec."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    return jsonify(_build_dashboard_payload()), 200


@faculty_bp.route("/placements/company/<company_name>", methods=["GET"])
@jwt_required()
def get_company_breakdown(company_name):
    """Detailed analytics for a specific company."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    normalized = (company_name or "").strip().lower()
    if not normalized:
        return jsonify({"error": "Company name is required"}), 400

    rows = (
        db.session.query(StudentOffer, StudentProfile)
        .join(StudentProfile, StudentProfile.id == StudentOffer.student_id)
        .filter(StudentOffer.status == "accepted")
        .filter(func.lower(StudentOffer.company_name) == normalized)
        .all()
    )

    if not rows:
        return jsonify({"error": "No placements found for this company"}), 404

    packages = []
    roles = set()
    branch_breakdown = {}
    students = []

    for offer, profile in rows:
        ctc_value = _parse_ctc_to_lpa(offer.ctc)
        if ctc_value is not None:
            packages.append(ctc_value)
        if offer.role:
            roles.add(offer.role)
        branch = profile.course or profile.specialization or "Unknown"
        branch_breakdown[branch] = branch_breakdown.get(branch, 0) + 1

        students.append(
            {
                "student_name": f"{profile.first_name} {profile.last_name}".strip(),
                "prn": getattr(profile, "prn_number", None),
                "branch": branch,
                "package_lpa": ctc_value,
                "role": offer.role,
                "location": offer.location,
                "joining_date": offer.joining_date.isoformat()
                if offer.joining_date
                else None,
            }
        )

    summary = {
        "company": company_name,
        "total_students": len(rows),
        "min_package_lpa": min(packages) if packages else None,
        "max_package_lpa": max(packages) if packages else None,
        "avg_package_lpa": round(sum(packages) / len(packages), 2) if packages else None,
        "roles": sorted(list(roles)),
        "branch_breakdown": [{"branch": k, "count": v} for k, v in branch_breakdown.items()],
    }

    return jsonify({"summary": summary, "students": students}), 200


@faculty_bp.route("/placements/all", methods=["GET"])
@jwt_required()
def get_all_placements():
    """
    Full table of placed students (based on offers).
    Supports basic filters via query params.
    """
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    rows = _fetch_placements(
        {
            "branch": request.args.get("branch"),
            "company": request.args.get("company"),
            "min_ctc": request.args.get("min_ctc", type=float),
            "max_ctc": request.args.get("max_ctc", type=float),
        }
    )

    return jsonify(rows), 200


@faculty_bp.route("/placements/branch/<branch_name>", methods=["GET"])
@jwt_required()
def get_branch_breakdown(branch_name):
    """Analytics for all placements in a branch."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    normalized = (branch_name or "").strip().lower()
    if not normalized:
        return jsonify({"error": "Branch name is required"}), 400

    rows = (
        db.session.query(StudentOffer, StudentProfile)
        .join(StudentProfile, StudentProfile.id == StudentOffer.student_id)
        .filter(StudentOffer.status == "accepted")
        .filter(
            (func.lower(StudentProfile.course) == normalized)
            | (func.lower(StudentProfile.specialization) == normalized)
        )
        .all()
    )

    if not rows:
        return jsonify({"error": "No placements found for this branch"}), 404

    packages = []
    companies = {}
    students = []

    for offer, profile in rows:
        ctc_value = _parse_ctc_to_lpa(offer.ctc)
        if ctc_value is not None:
            packages.append(ctc_value)
        comp_key = offer.company_name or "Unknown"
        companies[comp_key] = companies.get(comp_key, 0) + 1

        students.append(
            {
                "student_name": f"{profile.first_name} {profile.last_name}".strip(),
                "company": offer.company_name,
                "role": offer.role,
                "package_lpa": ctc_value,
                "location": offer.location,
                "joining_date": offer.joining_date.isoformat()
                if offer.joining_date
                else None,
            }
        )

    summary = {
        "branch": branch_name,
        "total_students": len(rows),
        "companies": [{"company": k, "count": v} for k, v in companies.items()],
        "avg_package_lpa": round(sum(packages) / len(packages), 2) if packages else None,
        "max_package_lpa": max(packages) if packages else None,
    }

    return jsonify({"summary": summary, "students": students}), 200


@faculty_bp.route("/placements/student/<prn>", methods=["GET"])
@jwt_required()
def get_student_placement(prn):
    """Detailed placement record for a specific student PRN."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    normalized = (prn or "").strip()
    if not normalized:
        return jsonify({"error": "PRN is required"}), 400

    profile = StudentProfile.query.filter_by(prn_number=normalized).first()
    if not profile:
        return jsonify({"error": "Student not found"}), 404

    offers = [offer.to_dict() for offer in profile.offers]
    internships = [internship.to_dict() for internship in profile.internships]

    return (
        jsonify(
            {
                "student": profile.to_dict(),
                "offers": offers,
                "internships": internships,
            }
        ),
        200,
    )


def _build_internship_stats_payload():
    """Shared internship stats builder."""
    total_internships = StudentInternship.query.count()

    domain_counts = (
        db.session.query(StudentInternship.industry_sector, func.count(StudentInternship.id))
        .group_by(StudentInternship.industry_sector)
        .all()
    )
    domain_wise = [
        {"domain": domain or "Unknown", "count": count}
        for domain, count in domain_counts
    ]

    paid_count = (
        StudentInternship.query.filter(
            StudentInternship.stipend.isnot(None),
            StudentInternship.stipend != "",
        ).count()
    )
    unpaid_count = total_internships - paid_count

    return {
        "total_internships": total_internships,
        "domain_wise": domain_wise,
        "paid": paid_count,
        "unpaid": unpaid_count,
    }


@faculty_bp.route("/internships/stats", methods=["GET"])
@jwt_required()
def get_internship_stats():
    """
    Aggregated internship statistics for faculty.
    """
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    return jsonify(_build_internship_stats_payload()), 200


@faculty_bp.route("/internships/all", methods=["GET"])
@jwt_required()
def get_all_internships():
    """Detailed internship table with filters."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    branch = (request.args.get("branch") or "").strip().lower()
    domain = (request.args.get("domain") or "").strip().lower()
    company = (request.args.get("company") or "").strip().lower()
    internship_type = (request.args.get("type") or "").strip().lower()
    paid_filter = request.args.get("paid")

    query = (
        db.session.query(StudentInternship, StudentProfile)
        .join(StudentProfile, StudentProfile.id == StudentInternship.student_id)
    )

    rows = []
    for internship, profile in query.all():
        branch_value = (profile.course or profile.specialization or "").lower()
        domain_value = (internship.industry_sector or "").lower()
        company_value = (internship.organization or "").lower()
        type_value = (internship.internship_type or "").lower()
        is_paid = bool(internship.stipend and internship.stipend.strip())

        if branch and branch_value != branch:
            continue
        if domain and domain_value != domain:
            continue
        if company and company_value != company:
            continue
        if internship_type and type_value != internship_type:
            continue
        if paid_filter == "paid" and not is_paid:
            continue
        if paid_filter == "unpaid" and is_paid:
            continue

        rows.append(
            {
                "student_name": f"{profile.first_name} {profile.last_name}".strip(),
                "branch": profile.course or profile.specialization,
                "organization": internship.organization,
                "designation": internship.designation,
                "domain": internship.industry_sector,
                "stipend": internship.stipend,
                "internship_type": internship.internship_type,
                "start_date": internship.start_date.isoformat()
                if internship.start_date
                else None,
                "end_date": internship.end_date.isoformat() if internship.end_date else None,
                "is_paid": is_paid,
                "technologies": internship.technologies.split(",")
                if internship.technologies
                else [],
            }
        )

    return jsonify(rows), 200


@faculty_bp.route("/filters/branches", methods=["GET"])
@jwt_required()
def get_filter_branches():
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    branches = (
        db.session.query(StudentProfile.course)
        .filter(StudentProfile.course.isnot(None))
        .distinct()
        .all()
    )
    return jsonify(sorted([b[0] for b in branches if b[0]])), 200


@faculty_bp.route("/filters/companies", methods=["GET"])
@jwt_required()
def get_filter_companies():
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    companies = (
        db.session.query(StudentOffer.company_name)
        .filter(StudentOffer.company_name.isnot(None))
        .distinct()
        .all()
    )
    return jsonify(sorted([c[0] for c in companies if c[0]])), 200


@faculty_bp.route("/filters/packages", methods=["GET"])
@jwt_required()
def get_filter_packages():
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    ctc_values = []
    for (ctc,) in db.session.query(StudentOffer.ctc).distinct().all():
        value = _parse_ctc_to_lpa(ctc)
        if value is not None:
            ctc_values.append(value)
    # Return sorted unique band edges
    return jsonify(sorted(list(set(round(v, 1) for v in ctc_values)))), 200


@faculty_bp.route("/filters/skills", methods=["GET"])
@jwt_required()
def get_filter_skills():
    """
    Placeholder endpoint - skills would typically come from a normalized skills table.
    For now, return an empty list to keep the API contract.
    """
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    return jsonify([]), 200


@faculty_bp.route("/filters/batches", methods=["GET"])
@jwt_required()
def get_filter_batches():
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    years = set()
    for offer in StudentOffer.query.filter(StudentOffer.status == "accepted").all():
        year = None
        if offer.joining_date:
            year = offer.joining_date.year
        elif offer.offer_date:
            year = offer.offer_date.year
        if year:
            years.add(str(year))

    return jsonify(sorted(list(years))), 200


@faculty_bp.route("/filters/genders", methods=["GET"])
@jwt_required()
def get_filter_genders():
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    genders = (
        db.session.query(StudentProfile.gender)
        .filter(StudentProfile.gender.isnot(None))
        .distinct()
        .all()
    )
    return jsonify(sorted([g[0] for g in genders if g[0]])), 200


@faculty_bp.route("/filters/domains", methods=["GET"])
@jwt_required()
def get_filter_domains():
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    domains = (
        db.session.query(StudentInternship.industry_sector)
        .filter(StudentInternship.industry_sector.isnot(None))
        .distinct()
        .all()
    )
    return jsonify(sorted([d[0] for d in domains if d[0]])), 200


def _build_report_payload(report_type: str):
    """Compose structured report data for different report types."""
    dashboard = _build_dashboard_payload()
    placements = _fetch_placements()
    internships = _collect_internship_rows()

    base = {
        "generated_at": datetime.utcnow().isoformat(),
        "report_type": report_type,
    }

    if report_type == "placement":
        base["summary"] = dashboard["stats"]
        base["charts"] = dashboard["charts"]
        base["table"] = placements
    elif report_type == "internship":
        internship_stats = _build_internship_stats_payload()
        base["summary"] = internship_stats
        base["table"] = internships
    elif report_type == "branch":
        base["summary"] = {
            "branch_wise": dashboard["charts"]["branch_wise"],
            "total_students": dashboard["stats"]["total_students"],
        }
        base["table"] = placements
    elif report_type == "company":
        base["summary"] = {
            "company_wise": dashboard["charts"]["company_wise"],
            "total_companies": dashboard["stats"]["total_companies"],
        }
        base["table"] = placements
    elif report_type == "yearly":
        base["summary"] = {
            "batch_trends": dashboard["charts"]["batch_trends"],
            "placed_students": dashboard["stats"]["placed_students"],
        }
        base["table"] = placements
    else:
        base["summary"] = dashboard["stats"]
        base["table"] = placements

    return base


def _table_to_csv(rows, headers):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in headers})
    return output.getvalue()


@faculty_bp.route("/reports/<report_type>", methods=["GET"])
@jwt_required()
def generate_report(report_type):
    """Return structured report data or downloadable CSV for the requested type."""
    user, error_response, status = _ensure_faculty()
    if error_response:
        return error_response, status

    report_type = (report_type or "").lower()
    if report_type not in {"placement", "internship", "branch", "company", "yearly"}:
        return jsonify({"error": "Unsupported report type"}), 400

    payload = _build_report_payload(report_type)
    export_format = (request.args.get("format") or "json").lower()

    if export_format == "csv":
        table = payload.get("table", [])
        if not table:
            return jsonify({"error": "No table data available for CSV export"}), 400
        headers = list(table[0].keys())
        csv_data = _table_to_csv(table, headers)
        filename = f"{report_type}_report.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    return jsonify(payload), 200


