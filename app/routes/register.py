from flask import  Blueprint, request, render_template, flash, redirect, url_for
from app import db
from app.models import Admin, Teacher, Student


# creating blueprint 
register_bp = Blueprint('register', __name__)

#route for registering user
@register_bp.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        user_type = request.form.get('user_type')
        name = request.form.get('name')
        email = request.form.get('email')
        roll_no = request.form.get('roll_no')
        contact = request.form.get('contact')
        password = request.form.get('password')
        
        
        #For registering admin
        if user_type == "admin":
            
            if Admin.query.first():
                # If an admin already exists, deny public creation
                flash('Admin accounts must be created internally.', 'danger')
                return redirect(url_for('register.register'))
             
            if  Admin.query.filter_by(email=email).first():
                flash('Email already registerd.', 'error')
                return redirect(url_for('register.register'))
        
            new_user = Admin(username=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Admin Registered Successfully.', 'success')
        
        #for registering teacher   
        elif user_type == "teacher":
            
            if Teacher.query.filter_by(email=email).first():
                flash('Email already registerd. Please try with different email.', 'error')
                return redirect(url_for('register.register'))
                
            new_user = Teacher(
                name=name, 
                email=email, 
                contact=contact,
                password=password,
                is_approved=False
            )
            
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Awaiting Admin approval before login.', 'info')
        
        #for registering student    
        elif user_type == "student":
            
            if Student.query.filter_by(email=email).first():
                flash('Email already registerd. Please try with different email.', 'error')
                return redirect(url_for('register.register'))
            
            new_user = Student(
                name=name, 
                email=email, 
                roll_no=roll_no,                
                contact=contact,
                password=password, 
                is_approved=False
            )
            
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Awaiting Admin approval before login.', 'info')
            
        else:
            flash('Invalid User Type. Please enter valid type.', 'error')

        return redirect(url_for("auth.login"))
        
    return render_template("registration.html")
            
        