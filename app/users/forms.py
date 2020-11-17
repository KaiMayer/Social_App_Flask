from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from app.users.models import User
from app.main.models import Role
from flask_login import current_user


class EditUserProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(0, 64)])
    description = TextAreaField('Description', validators=[Length(0, 256)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


class EditUserAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    name = StringField('Real name', validators=[Length(0, 64)])
    description = TextAreaField('Description', validators=[Length(0, 64)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Update')

    def __init__(self, user, *args, **kwargs):
        super(EditUserAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

