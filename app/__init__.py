from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Global database object
db = SQLAlchemy()

#app factory for flask app
def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config['SECRET_KEY'] = 'superkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    #initialzing database  
    db.init_app(app)
    
    #import models
    from app import models
    with app.app_context():
        db.create_all()
        print("✅ Database created successfully (attendance.db)")
        
    #import blueprint 
    from app.routes.auth import auth_bp
    from app.routes.register import register_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.home import home_bp
    from app.routes.face_register import face_register_bp
    from app.routes.crud import crud_bp
    from app.routes.attendance import attendance_bp
    from app.routes.report import report_bp
    
    #register blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(dashboard_bp)  
    app.register_blueprint(home_bp)  
    app.register_blueprint(face_register_bp)
    app.register_blueprint(crud_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(report_bp)
    
    return app
     