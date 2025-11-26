from flask import Blueprint, redirect, url_for, flash, render_template, session
from app.models import Student, Attendance
from app.recognition import mark_attendance_loop # Import the core logic
from app import db
from sqlalchemy import func
from datetime import datetime
from functools import wraps # Ensure this is imported

# Assuming the blueprint and decorator are defined/imported
# from .decorators import role_required 

attendance_bp = Blueprint('attendance', __name__) 


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

# --- ABSENTEE MARKING HELPER (Called after session ends) ---
def mark_absentees_on_exit():
    """
    Marks all students who do not have a time_in record for today as Absent.
    """
    today = datetime.now().date()

    # Get IDs of all students who ARE marked (Present or Late/Time_in set) today
    present_or_late_ids = db.session.query(Attendance.student_id).filter(
        func.date(Attendance.time_in) == today
    ).distinct().subquery()

    # Get all students who are NOT in the 'present_or_late_ids' subquery
    absent_students = Student.query.filter(
        Student.id.notin_(present_or_late_ids)
    ).all()

    absent_count = 0
    
    for student in absent_students:
        # Create 'Absent' records
        new_entry = Attendance(
            student_id=student.id, 
            time_in=datetime.now(), # Set time_in for the record date reference
            status='Absent'
        )
        db.session.add(new_entry)
        absent_count += 1
        
    db.session.commit()
    return absent_count


@attendance_bp.route('/start_attendance_session')
@role_required('admin', 'teacher')
def start_attendance_session():
    """Initiates the synchronous camera feed and marks absentees upon termination."""
    from deepface import DeepFace 
    
    try:
        mark_attendance_loop(db, Attendance, Student, DeepFace)
        
        # 1. Finalize Absentees
        absent_count = mark_absentees_on_exit()
        flash(f"Attendance session ended. {absent_count} students marked as Absent.", 'info')
        
    except Exception as e:
        flash(f"Error starting attendance system: {e}", 'danger')
        
    return redirect(url_for('dashboard.manage_students')) 


@attendance_bp.route('/view_attendance_records')
@role_required('admin', 'teacher')
def view_attendance_records():
    """Fetches and displays all attendance records with status."""
    
    attendance_records = db.session.query(
        Attendance.time_in,
        Attendance.time_out,
        Student.name,
        Student.roll_no,
        Attendance.status 
    ).join(Student).order_by(Attendance.time_in.desc()).all()
    
    return render_template('attendance.html', records=attendance_records)

# --- ROUTE TO TRIGGER ABSENTEE MARKING MANUALLY ---
@attendance_bp.route('/mark_absentees', methods=['POST'])
@role_required('admin', 'teacher')
def mark_absentees():
    """Administrative trigger for absentee marking."""
    try:
        absent_count = mark_absentees_on_exit()
        flash(f"{absent_count} students were successfully marked as Absent.", 'warning')
    except Exception as e:
        flash("Failed to mark absentees. Ensure the attendance window is closed.", 'danger')
        
    return redirect(url_for('attendance.view_attendance_records'))