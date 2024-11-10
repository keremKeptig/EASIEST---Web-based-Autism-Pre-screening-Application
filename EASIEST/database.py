from EASIEST import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20),unique=False, nullable=False)
    email = db.Column(db.String(50),unique=True, nullable=False)
    phonenum = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(100), nullable=True)
    type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }

class Doctor(User):
    __tablename__='doctor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    #need to update to false everything that should not be unique
    adress = db.Column(db.String(100),unique=False, nullable=False)
    hospital_name = db.Column(db.String(50),unique=False, nullable=False)
    IsValidated = db.Column(db.Integer,nullable=False, default=0)
    patients = db.relationship('Patients', backref="supervise",lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
    }
    #how the object is printed on creation
    def __repr__(self):
        return f'Doctor {self.id} {self.name} {self.surname}'


class Admin(User):
    __tablename__='admin'
    id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    #need to update to false everything that should not be unique
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }
    #how the object is printed on creation
    def __repr__(self):
        return f'Admin {self.id} {self.name} {self.surname}'



class Patients(db.Model):
    __tablename__='patient'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    surname = db.Column(db.String(200),nullable=False)
    phonenum = db.Column(db.String(200),nullable=False)
    #test_id = db.Column(db.Integer,db.ForeignKey('TEST.id'),nullable=False)
    date = db.Column(db.DateTime,default = datetime.utcnow)
    #result = db.Column(db.Integer,default = -1)
    doctors_id = db.Column(db.Integer, db.ForeignKey('doctor.id'),nullable=False)
    tests = db.relationship('Test', backref="taker",lazy=True)

    def __repr__(self):
        return f'Patient {self.id} {self.name} {self.surname}'


class Test(db.Model):
    __tablename__='test'
    id = db.Column(db.Integer,primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    Accuracy = db.Column(db.Integer,nullable=False,default=0)
    result = db.Column(db.Integer, default=-1)
    Second_Accuracy = db.Column(db.Integer, nullable=False, default=0)
    Second_Result = db.Column(db.Integer, default=-1)
    date = db.Column(db.DateTime,default = datetime.utcnow)



    def __repr__(self):
        return f'Test {self.id} {self.result} {self.Accuracy}'