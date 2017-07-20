from datetime import datetime
from os import path

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for, Blueprint)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flaskext.markdown import Markdown
from models import Login, Post, db
from sqlalchemy import exc
from werkzeug.security import check_password_hash as chpass

app = Flask(__name__)
app.config.from_pyfile("config.py")
login_manager = LoginManager()
login_manager.init_app(app)
Markdown(app)
login_manager.login_view = "login"
db.init_app(app)
Markdown(app)


# Filters
@app.template_filter('truncate_chars')
def truncate_chars(s):
    return s[:500]


@app.template_filter('format_date')
def format_date(date, fmt=None):
    if fmt:
        return date.strftime(fmt)
    else:
        return date.strftime("%a, %d %b %Y")


# Context Managers
@login_manager.user_loader
def user_loader(user_id):
    return Login.query.get(int(user_id))


@app.before_request
def before_request():
    db.create_all()


# Error Handlers
@app.errorhandler(404)
def errorhandler(e):
    return redirect(url_for("auth.login"))


# Blueprints
blog = Blueprint('blog', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')


# Routes
@blog.route("/new_post", methods=["POST", "GET"])
@login_required
def new_post():
    if request.method == "POST":
        fname = request.form["name"]
        fcontent = request.form["content"]
        post = Post(title=fname, content=fcontent, login_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("blog.my_posts"))
    return render_template("blog/new_post.html")


@blog.route("/my_posts", methods=["POST", "GET"])
@login_required
def my_posts():
    posts = Post.query.filter_by(login_id=current_user.id)
    return render_template("blog/my_posts.html", posts=posts)


@blog.route("/")
def index():
    posts = Post.query.all()
    return render_template("blog/index.html", posts=posts)


@blog.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get(post_id)
    return render_template("blog/post.html", post=post)


@blog.route("/edit_post/<int:post_id>", methods=["POST", "GET"])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if request.method == "POST" and post.login_id == current_user.id:
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.pub_date = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("blog.my_posts"))
    return render_template("blog/edit_post.html", post=post)


@blog.route("/delete_post/<int:post_id>")
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post.login_id != current_user.id:
        flash("voce não tem permissão para excluir este post.")
        return redirect(url_for('blog.index'))
    db.session.query(Post).filter_by(id=post_id).delete()
    db.session.commit()
    return redirect(url_for("blog.my_posts"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now Logged Out !")
    return redirect(url_for("blog.index"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        log_user = Login.query.filter_by(username=request.form["username"]).first()
        if log_user and chpass(log_user.password, request.form["password"]):
            login_user(log_user)
            flash("You are Logged")
            return redirect(url_for("blog.index"))
        else:
            flash("Username or password are wrong.")
    return render_template("auth/login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form["username"]:
            flash("Enter with a Username")
        elif not request.form["email"]:
            flash("Enter with a Email")
        elif not request.form["name"]:
            flash("Enter with a Name")
        elif not request.form["password"]:
            flash("Enter with a Password")
        else:
            try:
                user = Login(request.form["username"], request.form["email"],
                             request.form["name"], request.form["password"])
                db.session.add(user)
                db.session.commit()
                flash("User Sign")
                return redirect(url_for("auth.login"))
            except exc.IntegrityError:
                flash("This Username Or Email Alredy Exists")
                return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


app.register_blueprint(blog)
app.register_blueprint(auth)

if __name__ == '__main__':
    app.run()
