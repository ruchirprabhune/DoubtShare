from datetime import date

from flask import Flask, render_template, request ,url_for, redirect, flash, send_from_directory
from flask_gravatar import Gravatar
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String , Text, ForeignKey
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
import forms
from forms import LoginForm
import os

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.utils import secure_filename





secret_key = ""
with open('secrets.txt',mode='r') as file :
    data = file.readline()
    secret_key= data

upload_folder = os.path.join('static','photos')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 4MB max-limit.



bootstrap = Bootstrap5(app)

# Flask-Login  login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATING DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ckeditor = CKEditor(app)


# Getting user uploaded photos


class User(db.Model,UserMixin):
    # Using multiple inheritance to include login attributes such as is_authenticated and is_logged_in
    __tablename__ = "users_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    doubts = relationship("Doubt", back_populates="author")  # establishing relation between posts and users posting them
    doubtcomments = relationship("DoubtComment", back_populates="comment_author")
    answercomments = relationship("AnswerComment", back_populates="comment_author")
    answers = relationship("Answer", back_populates="answer_author")
class Doubt(db.Model):
    __tablename__ = "doubts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    img_path: Mapped[str] = mapped_column(String(250),nullable=True)
    subject : Mapped[str] = mapped_column(String(250),nullable=False)

    author_id : Mapped[int] = mapped_column(Integer, db.ForeignKey("users_table.id"))
    author = relationship("User", back_populates="doubts")
    doubtcomments = relationship("DoubtComment", back_populates="parent_doubt")
    answers = relationship("Answer", back_populates="parent_doubt")

class Answer(Base):
    __tablename__ = "answers"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users_table.id"))
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    img_path: Mapped[str] = mapped_column(String(250),nullable=True)
    answer_author = relationship("User", back_populates="answers")
    doubt_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("doubts.id"))
    parent_doubt = relationship("Doubt", back_populates="answers")
    answercomments = relationship("AnswerComment",back_populates="parent_answer")

class DoubtComment(Base):
    __tablename__ = "doubtcomments"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users_table.id"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    comment_author = relationship("User", back_populates="doubtcomments")
    doubt_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("doubts.id"))
    parent_doubt = relationship("Doubt", back_populates="doubtcomments")

class AnswerComment(Base):
    __tablename__ = "answercomments"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users_table.id"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    comment_author = relationship("User", back_populates="answercomments")
    answer_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("answers.id"))
    parent_answer = relationship("Answer", back_populates="answercomments")


with app.app_context():
    #db.drop_all()
    db.create_all()


# User Avatar
gravatar = Gravatar(app,size=20,rating='g',default='retro',force_default=False,force_lower=False,use_ssl=False,base_url=None)


# home page route
@app.route('/')
def home():
    return render_template("index.html",logged_in=current_user.is_authenticated,current_user=current_user)

@app.route('/show-home-feed')
def show_feed():
    all_doubts = db.session.execute(db.select(Doubt).order_by(Doubt.id)).scalars()
    print(all_doubts)
    doubts_list = [doubt for doubt in all_doubts]
    print(doubts_list)
    return render_template('feed.html', all_doubts = doubts_list)
# registration route
@app.route('/register', methods=["GET", "POST"])
def register():
    registerform = forms.RegisterForm()

    if registerform.validate_on_submit():

        # hashing and salting the password
        hash_and_salted_password = generate_password_hash(
            registerform.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        # storing the hashed password in the database
        new_user = User(
            email= registerform.email.data,
            name=registerform.name.data,
            password=hash_and_salted_password
        )
        user = db.session.execute(db.select(User).where( User.email == new_user.email)).scalar()
        if user :  # if user has already signed up using the email , redirect to the login page
            flash("Email already registered with a different account , Log in instead ")
            return redirect(url_for('login'))
        else :   # add the user to the database
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return render_template("index.html",logged_in=current_user.is_authenticated,current_user=current_user)

    return render_template("register.html",form = registerform, logged_in=current_user.is_authenticated,current_user=current_user)


#login page route
@app.route('/login', methods=["POST","GET"])
def login():
    loginform = LoginForm()

    if request.method == "POST" and loginform.validate_on_submit():
        email = loginform.email.data
        password = loginform.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user :
            flash("That email is not associated with any account. Please try again")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else :
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form = loginform, logged_in=current_user.is_authenticated,current_user=current_user )


@app.route('/doubt/<int:doubt_id>',methods= ["GET","POST"])
def show_doubt(doubt_id):
    doubt_comment_form = forms.CommentForm()
    doubt = db.get_or_404(Doubt,doubt_id)
    if doubt_comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = DoubtComment(
            text=doubt_comment_form.comment_text.data,
            comment_author=current_user,
            parent_doubt=doubt
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_doubt', doubt_id = doubt_id))
    return render_template("doubt.html",doubt = doubt,dcform=doubt_comment_form)

@app.route("/new-doubt", methods=["GET", "POST"])
#@admin_only
def post_doubt():
    form = forms.DoubtForm()
    if form.validate_on_submit():
        image = form.image
        if image:
            print(image)
        new_doubt = Doubt(
            question=form.question.data,
            description=form.description.data,
            author=current_user,
            subject = form.subject.data,
            date=date.today().strftime("%B %d, %Y")
        )
        if form.image.data :
            photo = form.image.data.filename
            filename = secure_filename(photo)
            form.image.data.save('static/photos/' +filename)
            filepath = '../static/photos/' +filename
        else :
            filepath = ""
        new_doubt.img_path = filepath
        db.session.add(new_doubt)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("post-doubt.html", form=form, current_user=current_user)

@app.route("/post-answer/<int:doubt_id>", methods = ["GET","POST"])
def post_answer(doubt_id):
    form = forms.AnswerForm()
    if form.validate_on_submit():
        image = form.image
        if image:
            print(image)
        new_answer = Answer(
            text=form.description.data,
            answer_author=current_user,
            doubt_id = doubt_id ,
            date=date.today().strftime("%B %d, %Y")

        )
        if form.image.data :
            photo = form.image.data.filename
            filename = secure_filename(photo)
            form.image.data.save('static/photos/solutions/' +filename)
            filepath = '../static/photos/solutions/' +filename
        else :
             filepath = ""
        new_answer.img_path = filepath
        db.session.add(new_answer)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("post-answer.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))





if __name__ == "__main__":
    app.run(debug=True)
