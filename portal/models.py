from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Enrollment(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), primary_key=True)


class CourseTA(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), primary_key=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, ta, instructor, registrar, chair
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(40), nullable=False, default="CS")
    enrollments = db.relationship("Enrollment", backref="user", cascade="all, delete-orphan")
    ta_links = db.relationship("CourseTA", backref="user", cascade="all, delete-orphan")
    courses_taught = db.relationship("Course", backref="instructor")

    def set_password(self, pw, method=None):
        if method:
            self.password_hash = generate_password_hash(pw, method=method)
        else:
            self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    @property
    def enrolled_in(self):        # courses I study
        return {e.course_id for e in self.enrollments}

    @property
    def teaches(self):            # courses I teach
        return {c.id for c in self.courses_taught}

    @property
    def assists(self):            # courses I am a TA on
        return {t.course_id for t in self.ta_links}

    @property
    def staff_of(self):           # courses I teach OR assist
        return self.teaches | self.assists


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(40), nullable=False, default="CS")
    instructor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    grade_deadline = db.Column(db.DateTime, nullable=False)   # term grade deadline
    materials = db.Column(db.Text, nullable=False, default="")


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    course = db.relationship("Course")


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    body = db.Column(db.Text, nullable=False, default="")
    grade = db.Column(db.String(5))
    feedback = db.Column(db.Text, default="")
    released = db.Column(db.Boolean, nullable=False, default=False)
    assignment = db.relationship("Assignment")
    student = db.relationship("User")

    @property
    def course_id(self):
        return self.assignment.course_id

    @property
    def course(self):
        return self.assignment.course


class Mail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to_address = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False, default=utcnow)


class ResetToken(db.Model):
    token = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship("User")
