from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from EASIEST.database import Doctor
class RegistrationForm(FlaskForm):
    Name = StringField('Name',
                             validators=[DataRequired()])
    Surname = StringField('Surname',
                             validators=[DataRequired()])
    Username = StringField('Username',
                           validators=[DataRequired(),Length(min=2,max=20)])
    Email = StringField('Email',
                        validators=[DataRequired(),Email()])
    Tel = StringField('Tel')
    Address = StringField('Address',
                             validators=[DataRequired()])
    Hospital = StringField('Hospital',
                             validators=[DataRequired()])
    Password = PasswordField('Password',
                             validators=[DataRequired()])
    Confirm_password = PasswordField('Confirm Password',
                             validators=[DataRequired(),EqualTo('Password')])
    Submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Doctor.query.filter_by(Username=username.data).first()
        if user:
            raise ValidationError('That username is taken.')

    def validate_email(self, email):
        user = Doctor.query.filter_by(Email=email.data).first()
        if user:
            raise ValidationError('That email is taken.')


class LoginForm(FlaskForm):
    Email = StringField('Email',
                        validators=[DataRequired(),Email()])
    Password = PasswordField('Password',
                             validators=[DataRequired()])
    Remember = BooleanField('Remember me')
    Submit = SubmitField('Log In')


class PatientForm(FlaskForm):
    Name = StringField('Name',
                       validators=[DataRequired()])
    Surname = StringField('Surname',
                          validators=[DataRequired()])
    Tel = StringField('Tel')
    Submit = SubmitField('Create')
