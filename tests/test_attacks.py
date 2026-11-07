"""The 7 attacks from Part 2. Each must FAIL after your fix."""
from conftest import login
from portal.models import CourseTA, Submission, User, db


def test_1_hidden_console_is_refused(client):
    login(client, "lina")
    r = client.post("/registrar-x9k2/role", data={"username": "lina", "role": "instructor"})
    assert r.status_code in (403, 404)
    assert db.session.get(User, 6).role == "student"


def test_2_role_cookie_is_ignored(client):
    login(client, "lina")
    client.set_cookie("role", "ta")
    assert client.get("/gradebook/1").status_code in (403, 404)


def test_3_get_does_not_release_grades(client):
    login(client, "lina")
    r = client.get("/staff/release/1")
    assert r.status_code in (403, 404, 405)
    assert db.session.get(Submission, 2).released is False


def test_4_other_students_submission_is_hidden(client):
    login(client, "lina")
    r = client.get("/submissions/3")
    assert r.status_code == 404
    assert "honours track" not in r.get_data(as_text=True)


def test_5_cannot_change_another_users_email(client):
    login(client, "lina")
    r = client.put("/api/users/2/email", json={"email": "lina@portal.lab"})
    assert r.status_code in (403, 404, 405)
    assert db.session.get(User, 2).email == "haddad@portal.lab"


def test_6_step_two_checks_for_itself(client):
    login(client, "lina")
    r = client.post("/submissions/1/change/confirm", data={"grade": "A+", "confirmed": "true"})
    assert r.status_code in (403, 404)
    assert db.session.get(Submission, 1).grade == "B"


def test_7_referer_is_not_authorization(client):
    login(client, "lina")
    r = client.post("/courses/1/staff/add", data={"username": "lina"},
                    headers={"Referer": "http://127.0.0.1:5002/registrar"})
    assert r.status_code in (403, 404)
    assert CourseTA.query.filter_by(user_id=6, course_id=1).count() == 0


def test_8_a_route_with_no_rule_is_denied(app, client):
    @app.route("/forgotten-debug")
    def forgotten_debug():
        return "open"
    login(client, "lina")
    assert client.get("/forgotten-debug").status_code == 403


def test_9_public_pages_still_work(client):
    assert client.get("/login").status_code == 200
    assert client.get("/robots.txt").status_code == 200
    assert client.post("/forgot", data={"username": "lina"}).status_code == 200
