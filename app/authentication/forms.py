from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from wtforms import ValidationError
from app.users.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64), ])
    password = PasswordField('Password', validators=[DataRequired()])
    stay_logged_in = BooleanField('Stay logged in?')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                          'Use only letters, numbers, dots, underscores')])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         EqualTo('password2', message='passwords must be the same')])
    password2 = PasswordField('Password confirmation', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
