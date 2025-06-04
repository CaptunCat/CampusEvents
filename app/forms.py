from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=100)])
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')