from flask import Blueprint,request, render_template, session, redirect, url_for, flash
from app.models import  Teacher, Student, Attendance
from app import db

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')

# simple login_required decorator (role optional)
def login_required(*roles):
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

@dashboard_bp.route('/dashboard/admin')
@login_required('admin')
def admin_dashboard():
    all_students = Student.query.all()
    return render_template('admin_dashboard.html',  students=all_students)

@dashboard_bp.route('/dashboard/teachers')
@login_required('admin')
def manage_teacher():
    all_teacher = Teacher.query.all()
    return render_template('manage_teacher.html', teachers=all_teacher)

@dashboard_bp.route('/dashboard/students')
@login_required('admin', 'teacher')
def manage_students():
    all_students = Student.query.all()
    return render_template('manage_students.html',  students=all_students)

@dashboard_bp.route('/dashboard/attendance')
@login_required("admin", "teacher")
def attendance():
        
    return render_template('attendance.html', )

@dashboard_bp.route('/dashboard/report')
@login_required("admin", "teacher")
def report():
    all_teacher = Teacher.query.all()
    all_students = Student.query.all()
    attend = Attendance.query.all()
    return render_template('report.html',  teachers=all_teacher, students=all_students, attendances=attend)


@dashboard_bp.route('/admin/requests', methods=['GET', 'POST'])
@login_required('admin')
def pending_requests():
    # Fetch all pending users (Students and Teachers)
    pending_students = Student.query.filter_by(is_approved=False).all()
    pending_teachers = Teacher.query.filter_by(is_approved=False).all()
    
    if request.method == 'POST':
        action = request.form.get('action') # 'approve' or 'reject'
        user_type = request.form.get('user_type')
        user_id = request.form.get('user_id')
        
        # Determine the correct model and user
        Model = Student if user_type == 'student' else Teacher
        user = Model.query.get(user_id)
        
        if user:
            if action == 'approve':
                user.is_approved = True
                db.session.commit()
                flash(f"{user.name} approved.", 'success')
            elif action == 'reject':
                db.session.delete(user) # Optionally delete the user
                db.session.commit()
                flash(f"{user.name} rejected and removed.", 'info')

        return redirect(url_for('dashboard.pending_requests'))
        
    return render_template('approval_queue.html', students=pending_students, teachers=pending_teachers)

@dashboard_bp.route('/dashboard/teacher')
@login_required('teacher')
def teacher_dashboard():
    return render_template("teacher_dashboard.html")

@dashboard_bp.route('/dashboard/student')
@login_required('student')
def student_dashboard():
    return render_template("student_dashboard.html")
