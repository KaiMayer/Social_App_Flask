from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_login import current_user


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    content = TextAreaField("Tell us something", validators=[DataRequired()])
    picture = FileField('Add post picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')
