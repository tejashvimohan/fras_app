from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import Admin, Teacher, Student, Attendance # Import all models
from app import db # Database instance
from datetime import datetime
from sqlalchemy import func # For database functions like counting and dates

report_bp = Blueprint('report', __name__)

def role_required(*roles):
    def decorator(f):
        def wrapped(*args, **kwargs):
            if 'user_type' not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))
            if session['user_type'] not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

@report_bp.route('/reports')
@role_required('admin') # Only Admin should see this comprehensive report
def view_reports():
    
    # Pre-calculate the date outside the query context
    today_date_str = datetime.now().strftime('%Y-%m-%d')
    today_db = datetime.now().date()
    
    try:
        # 1. Fetch Summary Counts 
        total_teachers = db.session.query(Teacher).count()
        total_students = db.session.query(Student).count()
        total_attendance_entries = db.session.query(Attendance).count()
        
        # 2. Fetch Attendance Metrics 
        present_today = db.session.query(Attendance).filter(
            func.date(Attendance.timestamp) == today_db,
            Attendance.status.in_(['Present', 'Late'])
        ).count()

        late_today = db.session.query(Attendance).filter(
            func.date(Attendance.timestamp) == today_db,
            Attendance.status == 'Late'
        ).count()

        # 3. Compile Data Dictionary
        report_data = {
            'total_teachers': total_teachers,
            'total_students': total_students,
            'total_entries': total_attendance_entries,
            'present_today': present_today,
            'late_today': late_today,
            'recently_added_students': Student.query.order_by(Student.id.desc()).limit(5).all(),
            'all_unapproved_teachers': Teacher.query.filter_by(is_approved=False).all()
        }

    except Exception as e:
        print(f"REPORT GENERATION ERROR: {e}")
        flash("Could not load full report data due to a database error.", 'danger')
        
        # Return default data structure on failure
        report_data = {
            'total_teachers': 0, 'total_students': 0, 'total_entries': 0,
            'present_today': 0, 'late_today': 0,
            'recently_added_students': [], 'all_unapproved_teachers': []
        }

    # 4. CRITICAL FIX: Ensure template name matches the file, and pass the date
    return render_template('report.html', data=report_data, today_date=today_date_str)