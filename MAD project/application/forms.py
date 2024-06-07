from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])

    address = StringField('Address', validators=[DataRequired(), Length(min=6, max=100)])

    phone_num = StringField('Phone_num', validators=[DataRequired(), Length(min=2, max=20)])

    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    password = PasswordField('Password', validators=[DataRequired()])
    
    submit = SubmitField('Login')

class AdminForm(FlaskForm):
    admin_username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    admin_password = PasswordField('Password', validators=[DataRequired()])
    
    submit = SubmitField('Login')
