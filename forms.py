from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,URLField, SelectField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed


subjects_list = [ "DSA", "MPT","DC","VCPD","SA","TOC"]

class LoginForm(FlaskForm):
    email = EmailField("Email",validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    login = SubmitField("login")




class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class CommentForm(FlaskForm):
    comment_text = StringField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

class DoubtForm(FlaskForm):
    question = StringField("question", validators=[DataRequired()])
    image = FileField( validators = [FileAllowed(['jpg', 'png'], 'Images only!')])
    description = CKEditorField("description", validators=[DataRequired()])
    subject = SelectField(choices=subjects_list, validators=[DataRequired()])
    submit = SubmitField("post doubt")

class AnswerForm(FlaskForm):
    image = FileField( validators = [FileAllowed(['jpg', 'png'], 'Images only!')])
    description = CKEditorField("description", validators=[DataRequired()])
    submit = SubmitField("post answer")
