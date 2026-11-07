"""Policy tests. Red when you get the portal; green when Part 3 is done."""
import pytest

from portal.policy import can

CASES = [
    # user,        action,              object,          expected   rule
    ("lina",      "view_grade",        "sub_released",  True),   # R3
    ("lina",      "submit",            "a3_late",       False),  # R2
    ("lina",      "submit",            "a2_open",       True),   # R2
    ("lina",      "view_material",     "cmps202",       False),  # R1
    ("lina",      "view_material",     "cmps215",       True),   # R1
    ("lina",      "view_grade",        "sub_sami",      False),  # R3, IDOR
    ("omar_ta",   "grade",             "sub_open_215",  True),   # R5
    ("omar_ta",   "grade",             "sub_open_202",  False),  # R5
    ("omar_ta",   "change_grade",      "sub_rel_215",   False),  # R5
    ("dr_haddad", "change_grade",      "sub_rel_215",   True),   # R5
    ("dr_haddad", "create_assignment", "cmps202",       False),  # R4
    ("dr_haddad", "create_assignment", "cmps215",       True),   # R4
    ("registrar", "view_grade",        "sub_released",  False),  # R6
    ("registrar", "enroll",            "cmps215",       True),   # R6
    ("lina",      "view_gradebook",    "cmps215",       False),  # attack 2
    ("omar_ta",   "view_gradebook",    "cmps215",       True),
    ("lina",      "release_grades",    "cmps215",       False),  # attack 3
    ("dr_khoury", "release_grades",    "cmps215",       False),  # not his course
    ("dr_haddad", "release_grades",    "cmps215",       True),
    ("lina",      "manage_roles",      None,            False),  # attack 1
    ("registrar", "manage_roles",      None,            True),
    ("lina",      "assign_staff",      "cmps215",       False),  # attack 7
    ("registrar", "assign_staff",      "cmps215",       True),
    ("lina",      "no_such_permission", None,           False),  # deny by default
]


# The request context the hook builds on the server for every request.
# These rows are all made from the campus network.
CAMPUS = {"network": "campus"}


@pytest.mark.parametrize("user,action,obj,expected", CASES)
def test_policy(user, action, obj, expected, world):
    target = world[obj] if obj else None
    assert can(world[user], action, target, CAMPUS) is expected
