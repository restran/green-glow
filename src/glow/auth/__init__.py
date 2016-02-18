# -*- encoding: utf-8 -*-
import datetime
from warnings import warn
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from grnglow.glow.auth.backends import EmailAuthBackend
from grnglow.glow.auth.models import AnonymousUser

SESSION_KEY = 'auth_user_id'
BACKEND_SESSION_KEY = 'auth_user_backend'
REDIRECT_FIELD_NAME = 'next'


def load_backend(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing authentication backend %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured(
            'Error importing authentication backends. Is AUTHENTICATION_BACKENDS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" authentication backend' % (module, attr))
    try:
        getattr(cls, 'supports_object_permissions')
    except AttributeError:
        warn(
            "Authentication backends without a `supports_object_permissions` attribute are deprecated. Please define it in %s." % cls,
            PendingDeprecationWarning)
        cls.supports_object_permissions = False
    try:
        getattr(cls, 'supports_anonymous_user')
    except AttributeError:
        warn(
            "Authentication backends without a `supports_anonymous_user` attribute are deprecated. Please define it in %s." % cls,
            PendingDeprecationWarning)
        cls.supports_anonymous_user = False
    return cls()


def authenticate(**credentials):
    """
    If the given credentials are valid, return a User object.
    """
    backend = EmailAuthBackend()

    try:
        user = backend.authenticate(**credentials)
    except TypeError:
        # This backend doesn't accept these credentials as arguments.
        pass
    if user is not None:
        # Annotate the user object with the path of the backend.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user


def login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    user.last_login = datetime.datetime.now()  # 更新上次登陆时间
    user.save()  # 将数据写入数据库

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = user.id
    request.session[BACKEND_SESSION_KEY] = user.backend
    if hasattr(request, 'user'):
        request.user = user


def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    request.session.flush()
    if hasattr(request, 'user'):
        request.user = AnonymousUser()


def get_user(request):
    try:
        user_id = request.session[SESSION_KEY]
        backend_path = request.session[BACKEND_SESSION_KEY]
        backend = load_backend(backend_path)
        user = backend.get_user(user_id) or AnonymousUser()
    except KeyError:
        user = AnonymousUser()
    return user
