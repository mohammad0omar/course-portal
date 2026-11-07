import pytest
from flask.testing import FlaskClient

from portal import create_app
from portal.models import Assignment, Course, Submission, User, db
from portal.seed import seed

UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}


class PortalClient(FlaskClient):
    """A test browser that behaves like the portal's own pages.

    Every POST, PUT, PATCH and DELETE carries the CSRF token stored in the
    session (session["csrf_token"]) in the X-CSRF-Token header, the way a page of
    the portal would send it. Pass csrf=False to send a request the way another
    site's page would: with the cookie, but without the token.
    """

    def csrf_token(self):
        with self.session_transaction() as sess:
            return sess.get("csrf_token")

    def open(self, *args, csrf=True, **kwargs):
        method = str(kwargs.get("method", "GET")).upper()
        if csrf and method in UNSAFE:
            token = self.csrf_token()
            if token:
                headers = dict(kwargs.get("headers") or {})
                headers.setdefault("X-CSRF-Token", token)
                kwargs["headers"] = headers
        return super().open(*args, **kwargs)


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True,
                      "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
                      "SECRET_KEY": "test"})
    app.test_client_class = PortalClient
    with app.app_context():
        seed()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username, password="Portal1234!"):
    r = client.post("/login", data={"username": username, "password": password})
    assert r.status_code == 302, f"login failed for {username}"
    return client


@pytest.fixture
def world(app):
    u = {x.username: x for x in User.query.all()}
    c = {x.code: x for x in Course.query.all()}
    a = {x.title.split()[0]: x for x in Assignment.query.all()}
    s = {x.id: x for x in Submission.query.all()}
    return {
        "lina": u["lina"], "sami": u["sami"], "omar_ta": u["omar"], "rana_ta": u["rana"],
        "dr_haddad": u["dr_haddad"], "dr_khoury": u["dr_khoury"],
        "registrar": u["registrar"], "chair": u["chair"],
        "cmps215": c["CMPS 215"], "cmps202": c["CMPS 202"],
        "a2_open": a["A2"], "a3_late": a["A3"],
        "sub_released": s[1], "sub_open_215": s[2], "sub_sami": s[3], "sub_open_202": s[4],
        "sub_rel_215": s[1],
    }
