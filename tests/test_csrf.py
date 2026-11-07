"""The CSRF attacks from Part 3 and the design from the CSRF deck (slides 19 to 23).

The token lives in the session as session["csrf_token"]. A page sends it back
in a form field named csrf_token, a script in an X-CSRF-Token header.
"""
from conftest import login
from portal.models import Submission, db

FORGED = {"grade": "A+"}   # what lina's attack page asks dr_haddad's browser to send


def grade_of_submission_2():
    db.session.expire_all()
    return db.session.get(Submission, 2).grade


def test_c1_post_without_token_is_refused(client):
    login(client, "dr_haddad")
    before = grade_of_submission_2()
    r = client.post("/submissions/2/grade", data=FORGED, csrf=False)
    assert r.status_code == 403
    assert grade_of_submission_2() == before


def test_c2_wrong_token_is_refused(client):
    login(client, "dr_haddad")
    before = grade_of_submission_2()
    r = client.post("/submissions/2/grade", data=dict(FORGED, csrf_token="guessed"),
                    csrf=False)
    assert r.status_code == 403
    assert grade_of_submission_2() == before


def test_c3_token_of_another_session_is_refused(app):
    lina = login(app.test_client(), "lina")
    lina_token = lina.csrf_token() or "none"
    haddad = login(app.test_client(), "dr_haddad")
    before = grade_of_submission_2()
    r = haddad.post("/submissions/2/grade", data=FORGED, csrf=False,
                    headers={"X-CSRF-Token": lina_token})
    assert r.status_code == 403
    assert grade_of_submission_2() == before


def test_c4_login_creates_a_new_long_random_token(app):
    first = login(app.test_client(), "dr_haddad").csrf_token()
    second = login(app.test_client(), "dr_haddad").csrf_token()
    assert first and second, "no token in session['csrf_token'] after login"
    assert len(first) >= 22, "a token needs at least 128 bits of randomness"
    assert first != second


def test_c5_token_in_the_header_is_accepted(client):
    login(client, "dr_haddad")
    r = client.post("/submissions/2/grade", data={"grade": "B+"})
    assert r.status_code == 200
    assert grade_of_submission_2() == "B+"


def test_c6_token_in_the_form_field_is_accepted(client):
    login(client, "dr_haddad")
    token = client.csrf_token()
    data = {"grade": "A-"} if token is None else {"grade": "A-", "csrf_token": token}
    r = client.post("/submissions/2/grade", data=data, csrf=False)
    assert r.status_code == 200
    assert grade_of_submission_2() == "A-"


def test_c7_session_cookie_is_httponly_and_samesite_lax(client):
    r = client.post("/login", data={"username": "dr_haddad", "password": "Portal1234!"})
    cookies = [h for h in r.headers.getlist("Set-Cookie") if h.startswith("session=")]
    assert cookies, "login set no session cookie"
    attrs = cookies[-1].lower()
    assert "httponly" in attrs
    assert "samesite=lax" in attrs


def test_c8_a_link_cannot_release_grades(client):
    login(client, "dr_haddad")
    r = client.get("/staff/release/1")
    assert r.status_code in (403, 404, 405)
    db.session.expire_all()
    assert db.session.get(Submission, 2).released is False
