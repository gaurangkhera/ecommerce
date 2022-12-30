from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, IntegerField, EmailField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Log in")

class RegForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired()])
    image = FileField('Upload a profile picture', validators=[FileAllowed('png', 'jpg')])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Register")

class EditUserForm(FlaskForm):
    username = StringField('Updated text', validators=[DataRequired()])
    email = EmailField('Updated text2', validators=[DataRequired()])
    points = IntegerField('Points')
    submit = SubmitField('Submit')

class CreditForm(FlaskForm):
    credits = IntegerField('credits', validators=[DataRequired()])
    submit = SubmitField('Get')

class ProfileForm(FlaskForm):
    image = FileField('upload image')
    username = StringField('username')
    email = EmailField('email')
    password = PasswordField('password')
    submit = SubmitField('Save changes')

class ReviewForm(FlaskForm):
    review = StringField('review', validators=[DataRequired()])
    submit = SubmitField('submit')

