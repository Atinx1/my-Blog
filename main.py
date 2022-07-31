import os

import werkzeug
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, send_file
import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

from sqlalchemy import MetaData

#response = requests.get("https://api.npoint.io/37a9453ce49bb99c2e2f")
#result = response.json()
import datetime as dt

now=dt.datetime.now()
date=now.date()




app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///blog_content!.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# noinspection PyUnresolvedReferences
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=False, nullable=False)
    message = db.Column(db.String(3000), unique=True, nullable=False)

db.create_all()


# noinspection PyUnresolvedReferences
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), unique=False, nullable=False)
    subtitle = db.Column(db.String(3000), unique=False, nullable=False)
    author = db.Column(db.String(300), unique=True, nullable=False)
    blogcont = db.Column(db.String(3000), unique=True, nullable=False)
    date = db.Column(db.String(3000), unique=True, nullable=False)

# noinspection PyUnresolvedReferences
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    blog_genre = db.Column(db.String(250), nullable=False)
    ur_img = db.Column(db.String(250), nullable=False)
db.create_all()

# noinspection PyUnresolvedReferences
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB.
db.create_all()



class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    blog_genre = StringField("Blog Genre", validators=[DataRequired()])
    ur_img = StringField("Your Image URL", validators=[DataRequired(), URL()])
    date = StringField("Date", validators=[DataRequired()])

    # Notice body's StringField changed to CKEditorField
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class EditPostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    blog_genre = StringField("Blog Genre", validators=[DataRequired()])
    ur_img = StringField("Your Image URL", validators=[DataRequired(), URL()])
    date = StringField("Date", validators=[DataRequired()])

    # Notice body's StringField changed to CKEditorField
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        password1 = request.form["password"]
        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        new_register = User(
            name=request.form["name"],
            email=request.form["email"],
            password=werkzeug.security.generate_password_hash(password1, method='pbkdf2:sha256', salt_length=16)


        )
        db.session.add(new_register)
        db.session.commit()
        login_user(new_register)

        return redirect(url_for('homepage'))


    return render_template("signup.html", logged_in=current_user.is_authenticated)


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))

        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))

        else:
            login_user(user)
            return redirect(url_for('homepage'))

    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author=form.author.data,
            blog_genre=form.blog_genre.data,
            img_url=form.img_url.data,
            ur_img=form.ur_img.data,
            date=date.today().strftime("%B %d, %Y"),
            body=form.body.data,






        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("homepage"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated)

@app.route('/homepage')
@login_required
def homepage():
    all_blogs = db.session.query(Blog).all()
    all_posts = db.session.query(BlogPost).all()

    return render_template('index.html', Blog=all_blogs, NewPost=all_posts)



@app.route('/singlepost', methods=["GET", "POST"])
@login_required
def singleposts():
    all_blogs = db.session.query(Blog).all()
    now = dt.datetime.now()
    date = now.date()
    if request.method == "POST":
        new_book = Book(
            name=request.form["name"],
            email=request.form["email"],
            message=request.form["message"],


        )
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('singleposts'))
    all_books = db.session.query(Book).all()
    all_posts = db.session.query(BlogPost).all()
    return render_template('single-post.html', books=all_books, Blog=all_blogs, NewPost=all_posts, logged_in=current_user.is_authenticated)






@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
        blog_genre=post.blog_genre,
        ur_img=post.ur_img


    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        post.blog_genre = edit_form.blog_genre.data
        post.ur_img = edit_form.ur_img.data
        db.session.commit()
        return redirect(url_for("singleposts", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, logged_in=current_user.is_authenticated)






@app.route('/about')
@login_required
def aboutsection():
    return render_template('about.html', logged_in=current_user.is_authenticated)





@app.route('/contact')
@login_required
def contactpage():
    return render_template('contact.html', logged_in=current_user.is_authenticated)



@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):

    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)
