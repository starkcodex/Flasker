from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, FileField


class SearchForm(FlaskForm):
    searched = StringField('Search:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    # content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    # author = StringField('Author')
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    favourite_color = StringField('Favourite Color')
    about_author = TextAreaField('About Author')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField('Profile Pic')
    submit = SubmitField("Submit")
    
    
# create a form for input 
class PasswordForm(FlaskForm):
    email = StringField('Your Email:', validators=[DataRequired()])
    password_hash = PasswordField('Your Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")


# create a form for input 
class NamerForm(FlaskForm):
    name = StringField('Please Enter Your Name:', validators=[DataRequired()])
    submit = SubmitField("Submit")
    