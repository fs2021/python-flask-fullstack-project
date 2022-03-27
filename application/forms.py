from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import PasswordInput

from application.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired(), Length(min=6, max=15)],
        widget=PasswordInput(hide_value=False)) 
        ##hide_value: either to clear field during each refresh 
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired(), Length(min=6, max=15)],
        widget=PasswordInput(hide_value=False))

##another way to make password field   
    password_confirm = PasswordField('Repeat password', 
        validators=[DataRequired(), Length(min=6, max=15), EqualTo('password')])

    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=55)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(min=2, max=55)])

    submit = SubmitField('Register')

    def validate_email(self, email):
        ## find 1st occurence of entered email in db:
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use')

