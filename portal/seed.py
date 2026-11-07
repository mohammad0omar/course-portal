from datetime import timedelta

from flask import current_app

from .models import (Assignment, Course, CourseTA, Enrollment, Submission, User,
                     db, utcnow)

PASSWORD = "Portal1234!"

USERS = [  # ids 1..8 in this order
    ("registrar", "registrar"), ("dr_haddad", "instructor"), ("dr_khoury", "instructor"),
    ("omar", "ta"), ("rana", "ta"), ("lina", "student"), ("sami", "student"),
    ("chair", "chair"),
]
EMAILS = {"dr_haddad": "haddad@portal.lab", "dr_khoury": "khoury@portal.lab"}


def seed():
    """Drop and rebuild every table, then insert the lab data with stable ids."""
    db.drop_all()
    db.create_all()
    now = utcnow()
    # Tests use a cheap (still salted) hash so the suite stays fast.
    method = "pbkdf2:sha256:1000" if current_app.config.get("TESTING") else None

    for name, role in USERS:
        u = User(username=name, role=role, department="CS",
                 email=EMAILS.get(name, f"{name}@portal.lab"))
        u.set_password(PASSWORD, method=method)
        db.session.add(u)
    db.session.flush()

    db.session.add_all([
        Course(code="CMPS 215", title="Software Security", instructor_id=2,
               grade_deadline=now + timedelta(days=30),
               materials="Week 1: threat modelling. Week 2: access control."),
        Course(code="CMPS 202", title="Data Structures", instructor_id=3,
               grade_deadline=now + timedelta(days=30),
               materials="Week 1: linked lists. Week 2: trees."),
    ])
    db.session.flush()

    db.session.add_all([
        Enrollment(user_id=6, course_id=1), Enrollment(user_id=7, course_id=2),
        Enrollment(user_id=5, course_id=2),
        CourseTA(user_id=4, course_id=1), CourseTA(user_id=5, course_id=2),
    ])

    db.session.add_all([
        Assignment(course_id=1, title="A1 Threat model", deadline=now - timedelta(days=10)),
        Assignment(course_id=1, title="A2 Access control", deadline=now + timedelta(days=7)),
        Assignment(course_id=1, title="A3 Late lab", deadline=now - timedelta(hours=1)),
        Assignment(course_id=2, title="B1 Linked lists", deadline=now - timedelta(days=10)),
        Assignment(course_id=2, title="B2 Trees", deadline=now + timedelta(days=7)),
    ])
    db.session.flush()

    db.session.add_all([
        Submission(assignment_id=1, student_id=6, body="Our threat model.", grade="B",
                   feedback="Good model, missing trust boundaries.", released=True),
        Submission(assignment_id=2, student_id=6, body="Draft access control.",
                   grade=None, released=False),
        Submission(assignment_id=4, student_id=7, body="Linked list code.", grade="A-",
                   feedback="Private: consider the honours track.", released=True),
        Submission(assignment_id=4, student_id=5, body="Linked list code.", grade="B+",
                   released=False),
    ])
    db.session.commit()
