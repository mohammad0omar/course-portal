# AGENTS.md

Course Portal: a small Flask course site. Students submit assignments, TAs and
instructors grade them, and a registrar manages roles and enrolment.

Start it with `python run.py` (after `pip install -r requirements.txt` in a
virtual environment) and open http://127.0.0.1:5002. `python run.py --reset`
rebuilds the seed data.

Layout:

- `portal/` - the application: `__init__.py` (app setup), `auth.py` (sign in,
  password reset, inbox), `courses.py`, `staff.py`, `api.py`, `models.py`,
  `policy.py`, `seed.py`, `templates/`, `static/`
- `tests/` - the tests the student's fix must make pass
- `run.py` - starts the server on 127.0.0.1:5002

There is no build step. Restart `python run.py` after an edit to the code.

If you are an AI assistant working in this repository, read the rules first:

@.course/rules.md
