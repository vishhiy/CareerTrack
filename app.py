import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from models import db, bcrypt, User, Application
from forms import LoginForm, RegisterForm, ApplicationForm

app = Flask(__name__)

# ---------- Config ----------
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///careertrack.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------- Auth Routes ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("That email is already registered.", "danger")
            return redirect(url_for("login"))

        user = User(name=form.name.data.strip(), email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created — you can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------- Dashboard ----------
@app.route("/")
@login_required
def dashboard():
    apps = Application.query.filter_by(user_id=current_user.id).all()

    stats = {
        "totalApplications": len(apps),
        "totalInterviews": sum(1 for a in apps if a.status == "Interview"),
        "totalOffers": sum(1 for a in apps if a.status == "Offer"),
        "totalRejected": sum(1 for a in apps if a.status == "Rejected"),
    }

    recent = sorted(apps, key=lambda a: a.date_applied, reverse=True)[:5]

    return render_template(
        "index.html", user=current_user, stats=stats, recent=recent
    )


# ---------- Applications ----------
@login_required
@app.route("/applications")
@login_required
def applications():
    apps = Application.query.filter_by(user_id=current_user.id)\
        .order_by(Application.date_applied.desc()).all()
    return render_template("applications.html", applications=apps)


@app.route("/applications/add", methods=["GET", "POST"])
@login_required
def add_application():
    form = ApplicationForm()
    if form.validate_on_submit():
        entry = Application(
            user_id=current_user.id,
            company=form.company.data.strip(),
            role=form.role.data.strip(),
            status=form.status.data,
            job_type=form.job_type.data,
            date_applied=form.date_applied.data,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Application added.", "success")
        return redirect(url_for("applications"))

    return render_template("add_application.html", form=form)

@app.route("/applications/<int:app_id>/edit", methods=["GET", "POST"])
@login_required
def edit_application(app_id):
    entry = Application.query.filter_by(
        id=app_id, user_id=current_user.id
    ).first_or_404()

    form = ApplicationForm(obj=entry)
    if form.validate_on_submit():
        entry.company = form.company.data.strip()
        entry.role = form.role.data.strip()
        entry.status = form.status.data
        entry.job_type = form.job_type.data
        entry.date_applied = form.date_applied.data
        db.session.commit()
        flash("Application updated.", "success")
        return redirect(url_for("applications"))

    return render_template("edit_application.html", form=form, entry=entry)


@app.route("/applications/<int:app_id>/delete", methods=["POST"])
@login_required
def delete_application(app_id):
    entry = Application.query.filter_by(
        id=app_id, user_id=current_user.id
    ).first_or_404()

    db.session.delete(entry)
    db.session.commit()
    flash("Application deleted.", "info")
    return redirect(url_for("applications"))
# ---------- Init DB ----------
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)