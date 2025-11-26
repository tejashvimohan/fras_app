from flask import Blueprint, redirect, url_for, flash
from app.models import Student
from app.enroll_face import capture_embedding, check_face_duplicate
from app import db 

face_register_bp = Blueprint('face_register', __name__)

@face_register_bp.route('/register/face/<string:roll_no>', methods =["GET","POST"])
def register_face(roll_no):
    student = Student.query.filter_by(roll_no=roll_no).first()
    
    if not student:
        flash("Student Not Found. Please add student first.", "danger")
        return redirect(url_for("crud.add_student"))
    
   
    new_embedding_blob = capture_embedding()
    
    
    if new_embedding_blob is None:
        flash("Face capture failed. Try again!", "danger")
        return redirect(url_for("face_register.register_face"))
     
    duplicate_name= check_face_duplicate(new_embedding_blob, roll_no)
    
    if duplicate_name:
        flash(f"Face Registration Failed. This face is already registered as '{duplicate_name}'.", "error")
        return redirect(url_for("dashboard.manage_students"))
    
    student.face_embedding = new_embedding_blob
    db.session.commit()

    flash(f"Face registered successfully for {student.name}!", "success")
    return redirect(url_for("dashboard.manage_students"))
     
      
    
    
 
        