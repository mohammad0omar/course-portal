"""Access control policy for the Course Portal.

Part 4 of Level 4 asks you to write this file.

  ROLE_PERMISSIONS   RBAC: which permissions each role could ever use
  CONDITIONS         ABAC: one function per permission, (user, obj, ctx) -> bool
  can()              step 1 RBAC, step 2 ABAC; anything unknown is denied
  requires()         declare the permission a route needs, next to the route
  install(app)       one before_request hook that checks every request

Until you write it, can() denies everything, and nothing calls it yet.
"""

ROLE_PERMISSIONS = {}

CONDITIONS = {}


def can(user, perm, obj=None, ctx=None):
    return False


def requires(perm, load=None):
    def deco(f):
        return f
    return deco


def install(app):
    pass
