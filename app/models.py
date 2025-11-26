from app import db
from datetime import datetime, date, time

    
    
# -------------------- ADMIN MODEL --------------------
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship with teachers
    teachers = db.relationship('Teacher', backref='admin', lazy=True)

    def __repr__(self):
        return f"<Admin {self.username}>"

# -------------------- TEACHER MODEL --------------------
class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False) 
    course = db.Column(db.String(100))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship with subjects
    subjects = db.relationship('Subject', backref='teacher', lazy=True)

    def __repr__(self):
        return f"<Teacher {self.name}>"

# -------------------- STUDENT MODEL --------------------
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    contact = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False) 
    face_embedding = db.Column(db.LargeBinary)   # stored face vector
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship with attendance
    attendances = db.relationship('Attendance', backref='student', cascade="all, delete")
     # Relationship with report
    report = db.relationship('Report', backref='student', uselist=False)
    
    
   
    def __repr__(self):
        return f"<Student {self.name}>"

# -------------------- SUBJECT MODEL --------------------
class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    students = db.relationship('Student', backref='subject', lazy=True)
    attendances = db.relationship('Attendance', backref='subject', lazy=True)

    def __repr__(self):
        return f"<Course {self.name}>"

# -------------------- ATTENDANCE MODEL --------------------
class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    date = db.Column(db.Date, default=date.today)
    time_in = db.Column(db.DateTime, default=datetime.now) # Must be DateTime
    time_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(10), default='Absent')  # Present/Absent/Late
    emotion_score = db.Column(db.Float, nullable=True)
    liveness_score = db.Column(db.Float, nullable=True)
    mode = db.Column(db.String(20), default='Face')  # Face/Voice/Both
    @staticmethod
    def get_late_policy_time():
        return 9, 0, 0

    def __repr__(self):
        return f"<Attendance {self.student_id} - {self.status}>"

# -------------------- REPORT MODEL --------------------
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    total_classes = db.Column(db.Integer, default=0)
    attended_classes = db.Column(db.Integer, default=0)
    attendance_percentage = db.Column(db.Float, default=0.0)
    avg_emotion_score = db.Column(db.Float, default=0.0)
    avg_liveness_score = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Report {self.student_id} - {self.attendance_percentage}%>"
