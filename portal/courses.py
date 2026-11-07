from markupsafe import escape
from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required

from .models import Assignment, Course, Submission, db, utcnow

bp = Blueprint("courses", __name__)


@bp.get("/")
@login_required
def dashboard():
    ids = current_user.enrolled_in | current_user.staff_of
    courses = Course.query.filter(Course.id.in_(ids)).all() if ids else []
    return render_template("dashboard.html", courses=courses)


@bp.get("/courses/<int:cid>/materials")
@login_required
def materials(cid):
    if cid not in current_user.enrolled_in and cid not in current_user.staff_of:
        abort(403)
    return render_template("materials.html", course=db.get_or_404(Course, cid))


@bp.post("/assignments/<int:aid>/submit")
@login_required
def submit(aid):
    assignment = db.get_or_404(Assignment, aid)
    if assignment.course_id not in current_user.enrolled_in:
        abort(403)
    if utcnow() >= assignment.deadline:
        abort(403)
    sub = Submission.query.filter_by(assignment_id=aid, student_id=current_user.id).first()
    if sub is None:
        sub = Submission(assignment_id=aid, student_id=current_user.id)
        db.session.add(sub)
    sub.body = request.form.get("body", "")
    db.session.commit()
    return render_template("submission.html", sub=sub)


@bp.get("/submissions/<int:sid>")
@login_required
def view_submission(sid):
    sub = Submission.query.get_or_404(sid)
    return render_template("submission.html", sub=sub)


@bp.post("/submissions/<int:sid>/grade")
@login_required
def grade(sid):
    sub = db.get_or_404(Submission, sid)
    if current_user.role not in ("ta", "instructor"):
        abort(403)
    if sub.course_id not in current_user.staff_of:
        abort(403)
    if sub.released:
        abort(403)
    sub.grade = request.form.get("grade")
    db.session.commit()
    return f"Grade for submission {sub.id} set to {escape(sub.grade)}."


@bp.post("/submissions/<int:sid>/change")
@login_required
def change(sid):
    sub = db.get_or_404(Submission, sid)
    if current_user.role != "instructor":
        abort(403)
    if sub.course_id not in current_user.teaches:
        abort(403)
    if not sub.released:
        abort(403)
    return render_template("change_confirm.html", sub=sub,
                           grade=request.form.get("grade"))


@bp.post("/submissions/<int:sid>/change/confirm")
@login_required
def change_confirm(sid):
    sub = db.get_or_404(Submission, sid)
    if request.form.get("confirmed") == "true":
        sub.grade = request.form.get("grade")
        db.session.commit()
        return f"Grade for submission {sub.id} changed to {escape(sub.grade)}."
    return "Change cancelled."


@bp.get("/gradebook/<int:cid>")
def gradebook(cid):
    role = request.cookies.get("role", "student")
    if role not in ("ta", "instructor"):
        abort(403)
    course = db.get_or_404(Course, cid)
    subs = (Submission.query.join(Assignment)
            .filter(Assignment.course_id == cid).all())
    return render_template("gradebook.html", course=course, subs=subs)
