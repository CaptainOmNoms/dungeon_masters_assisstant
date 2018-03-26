import base64
from apistar import Component, http, Route, annotate
from apistar.exceptions import Forbidden
from apistar.authentication import Authenticated
from apistar.interfaces import Auth


class BasicAuth():
    @staticmethod
    def authenticate(authorization: http.Header):
        """
        Determine the user associated with a request, using HTTP Basic Authentication.
        """
        if authorization is None:
            return None

        scheme, token = authorization.split()
        if scheme.lower() != 'basic':
            return None

        username, password = base64.b64decode(token).decode('utf-8').split(':')
        return Authenticated(username)


@annotate(authentication=[BasicAuth()])
def say_hello(user: Auth):
    if user.is_authenticated():
        return {'hello': user.username}
    raise Forbidden('Invalid credentials')


test_routes = [
    Route('/hello', 'POST', say_hello)
]
