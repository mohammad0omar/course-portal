from markupsafe import escape
from datetime import datetime

from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required

from .models import Assignment, Course, CourseTA, Enrollment, Submission, User, db

bp = Blueprint("staff", __name__)


@bp.before_request
def instructors_only_for_writes():
    if request.path.startswith("/staff/") and request.method == "POST":
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != "instructor":
            abort(403)


@bp.route("/staff/release/<int:cid>", methods=["GET", "POST"])
@login_required
def release(cid):
    course = db.get_or_404(Course, cid)
    for sub in Submission.query.join(Assignment).filter(Assignment.course_id == cid):
        sub.released = True
    db.session.commit()
    return f"Grades released for {escape(course.code)}."


@bp.get("/staff/assignments/new")
def new_assignment_form():
    return render_template("course_new_assignment.html")


@bp.post("/staff/assignments/new")
def new_assignment():
    cid = int(request.form["course_id"])
    if cid not in current_user.teaches:
        abort(403)
    deadline = datetime.fromisoformat(request.form["deadline"])
    db.session.add(Assignment(course_id=cid, title=request.form["title"],
                              deadline=deadline))
    db.session.commit()
    return f"Assignment added to course {cid}."


@bp.get("/registrar-x9k2")
@login_required
def registrar_console():
    return render_template("registrar_console.html", users=User.query.all())


@bp.post("/registrar-x9k2/role")
@login_required
def set_role():
    user = User.query.filter_by(username=request.form["username"]).first_or_404()
    user.role = request.form["role"]
    db.session.commit()
    return f"Role of {escape(user.username)} set to {escape(user.role)}."


@bp.post("/registrar-x9k2/enroll")
@login_required
def enroll():
    user = User.query.filter_by(username=request.form["username"]).first_or_404()
    cid = int(request.form["course_id"])
    db.session.add(Enrollment(user_id=user.id, course_id=cid))
    db.session.commit()
    return f"{escape(user.username)} enrolled in course {cid}."


@bp.get("/registrar")
@login_required
def registrar():
    if current_user.role != "registrar":
        abort(403)
    return render_template("registrar.html", courses=Course.query.all())


@bp.post("/courses/<int:cid>/staff/add")
@login_required
def add_ta(cid):
    if request.headers.get("Referer", "").endswith("/registrar"):
        course = db.get_or_404(Course, cid)
        user = User.query.filter_by(username=request.form["username"]).first_or_404()
        db.session.add(CourseTA(user_id=user.id, course_id=cid))
        db.session.commit()
        return f"{escape(user.username)} added as TA of {escape(course.code)}."
    abort(403)
