from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Register")

class IdeaForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10)])
    tags = StringField("Tags (comma separated)", validators=[DataRequired()])
    category = SelectField("Category", choices=[
        ('Software', 'Software'),
        ('Hardware', 'Hardware'),
        ('Food', 'Food'),
        ('Nonprofit', 'Nonprofit'),
        ('Other', 'Other')
    ])
    submit = SubmitField("Submit Idea")
