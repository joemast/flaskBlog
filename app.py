from flask import (Flask, g, session, redirect, url_for, render_template,
                    request, flash)

from flask_login import (LoginManager, login_required, logout_user,
                            current_user, login_user)

from models import db, Login, Post

from datetime import datetime

from werkzeug.security import check_password_hash as chpass


app = Flask(__name__)
app.config.from_pyfile("config.py")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    return Login.query.get(int(user_id))


@app.before_request
def before_request():
    db.create_all()


@app.errorhandler(404)
def errorhandler(e):
    return redirect(url_for("login"))


@app.route("/sign", methods=["GET", "POST"])
def sign():
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
            user = Login(request.form["username"],
                request.form["email"],
                request.form["name"],
                request.form["password"])
            db.session.add(user)
            db.session.commit()
            flash("User Sign")
            return redirect(url_for("login"))

    return render_template("sign.html")


@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    if request.method == "POST":
        fname = request.form["name"]
        fcontent = request.form["content"]

        post = Post(title=fname, content=fcontent, login_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("result"))

    return render_template("index.html")


@app.route("/result", methods=["POST", "GET"])
@login_required
def result():
    post = Post.query.filter_by(login_id=current_user.id)
    return render_template("result.html", result=post, user=current_user.username)


@app.route("/public", methods=["POST", "GET"])
def public():
    post = Post.query.all()
    return render_template("public.html", result=post)


@app.route("/update/<int:uid>", methods=["POST", "GET"])
@login_required
def update(uid):
    post = Post.query.filter_by(id=uid).first()
    # user_id = User.query.filter_by(id=uid).first()
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.pub_date = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("result"))

    return render_template("update.html", post=post)


@app.route("/delete/<int:uid>")
@login_required
def delete(uid):
    db.session.query(Post).filter_by(id=uid).delete()
    db.session.commit()
    return redirect(url_for("result"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now Logged Out !")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        log_user = Login.query.filter_by(username=request.form["username"]).first()
        if log_user:
            if log_user.username == request.form["username"] and (
            chpass(log_user.password, request.form["password"]) == True):
                login_user(log_user)
                flash("You are Logged")
                return redirect(url_for("index"))

        return redirect(url_for("login"))

    flash("Something Goes Wrong!")
    return render_template("login.html")


if __name__ == '__main__':
    app.run()
