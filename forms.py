from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    SelectField, DateField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class ApplicationForm(FlaskForm):
    company = StringField("Company", validators=[DataRequired(), Length(max=120)])
    role = StringField("Role", validators=[DataRequired(), Length(max=120)])
    status = SelectField(
        "Status",
        choices=[
            ("Applied", "Applied"),
            ("Interview", "Interview"),
            ("Offer", "Offer"),
            ("Rejected", "Rejected"),
        ],
    )
    job_type = SelectField(
        "Job type",
        choices=[
            ("Full-time", "Full-time"),
            ("Part-time", "Part-time"),
            ("Internship", "Internship"),
            ("Contract", "Contract"),
            ("Remote", "Remote"),
        ],
    )
    date_applied = DateField("Date applied", validators=[DataRequired()])
    submit = SubmitField("Save application")