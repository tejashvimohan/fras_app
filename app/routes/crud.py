from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from app.models import Student, Teacher
from app import db

crud_bp = Blueprint('crud', __name__)

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

#route for adding new teacher via admin
@crud_bp.route('/dashboard/teacher/add', methods = ["GET","POST"])
@role_required("admin")
def add_teacher():
    if request.method == "POST":
       
        name = request.form.get('name')
        email = request.form.get('email')
        contact= request.form.get('contact')
        password = request.form.get('password')
        
        if Teacher.query.filter_by(email=email).first():
                flash('Email already registerd. Please try with different email.', 'error')
                return redirect(url_for('crud.add_teacher'))
            
        new_user = Teacher(name=name, email=email, contact=contact, password=password)   
        db.session.add(new_user)
        db.session.commit()
        flash('Teacher Added Successfully.', 'success')
        return redirect(url_for('dashboard.manage_teacher'))
    
    return render_template("add_teacher_form.html")

#route for updating existing teacher data via admin
@crud_bp.route('/dashboard/teacher/update/<int:teacher_id>', methods = ["GET","POST"])
@role_required("admin")
def update_teacher(teacher_id):
    updated_teacher = Teacher.query.get_or_404(teacher_id)

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        email_check = Teacher.query.filter(
            Teacher.email == email, 
            Teacher.id != teacher_id
        ).first()
        
        if email_check:
            flash(f"Error: The email '{email}' is already registered to another teacher.", 'danger')
            return redirect(url_for("crud.update_teacher", teacher_id=teacher_id))
        
        updated_teacher.name = name
        updated_teacher.email = email
        updated_teacher.password = password
    
        db.session.commit()
    
        flash(f"Teacher data for {name} updated successfully.", "success")
        return redirect(url_for("dashboard.manage_teacher"))
    
    return render_template("update_teacher_form.html", teacher=updated_teacher)

#route for deleting teacher data via admin
@crud_bp.route('/dashboard/teacher/delete/<int:teacher_id>', methods=["POST"])
@role_required("admin")
def delete_teacher(teacher_id):
    deleted_teacher = Teacher.query.get_or_404(teacher_id)

     
    teacher = deleted_teacher.name
    
    try:
        db.session.delete(deleted_teacher)
        db.session.commit()
        flash(f"Teacher '{teacher}' successfully deleted.", 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Database Error during deletion: {e}")
        flash("An error occurred during deletion.", 'danger')
    
    return redirect(url_for("dashboard.manage_teacher"))
        
#route for adding new student via admin or teacher
@crud_bp.route('/dashboard/students/add', methods = ["GET","POST"])
@role_required("admin", "teacher")
def add_student():
    if request.method == "POST":
       
        name = request.form.get('name')
        email = request.form.get('email')
        roll_no = request.form.get('roll_no')
        contact= request.form.get('contact')
        password = request.form.get('password')
        
        if Student.query.filter_by(email=email).first():
                flash('Email already registerd. Please try with different email.', 'error')
                return redirect(url_for('crud.add_student'))
            
        new_user = Student(name=name, email=email, roll_no=roll_no, contact=contact, password=password)   
        db.session.add(new_user)
        db.session.commit()
        flash('Student Added Successfully.', 'success')
        return redirect(url_for('dashboard.manage_students'))
    
    return render_template("add_student_form.html")
   
#route for updating existing student data via admin or teacher
@crud_bp.route('/dashboard/students/update/<int:student_id>', methods = ["GET","POST"])
@role_required("admin", "teacher")
def update_student(student_id):
    updated_student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        roll_no = request.form.get('roll_no')
        contact = request.form.get('contact')
        password = request.form.get('password')
        
        email_check = Student.query.filter(
            Student.email == email, 
            Student.id != student_id
        ).first()
        
        if email_check:
            flash(f"Error: The email '{email}' is already registered to another student.", 'danger')
            return redirect(url_for("crud.update_student", student_id=student_id))
        
        updated_student.name = name
        updated_student.email = email
        updated_student.roll_no = roll_no
        updated_student.contact = contact
        updated_student.password = password
    
        db.session.commit()
    
        flash(f"Student data for {name} updated successfully.", "success")
        return redirect(url_for("dashboard.manage_students"))
    
    return render_template("update_student_form.html", student=updated_student)
            
#route for deleting student data via admin or teacher
@crud_bp.route('/dashboard/students/delete/<int:student_id>', methods=["POST"])
@role_required("admin", "teacher")
def delete_student(student_id):
    deleted_student = Student.query.get_or_404(student_id)

     
    student = deleted_student.name
    
    try:
        db.session.delete(deleted_student)
        db.session.commit()
        flash(f"Student '{student}' successfully deleted.", 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Database Error during deletion: {e}")
        flash("An error occurred during deletion.", 'danger')
    
    return redirect(url_for("dashboard.manage_students"))
        

        
        