# /workspaces/python/rent_tracker/rentals/middleware.py
import threading

_thread_locals = threading.local()

def get_current_user():
    """
    Retrieves the currently logged-in user from thread-local storage.
    Returns None if no user is set (e.g., during background tasks or if middleware hasn't run).
    """
    return getattr(_thread_locals, 'user', None)

class CurrentUserMiddleware:
    """
    Middleware that stores the request's user in thread-local storage.
    This allows signal handlers (and other parts of the code without direct
    request access) to know who the current user is.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store the user in thread-local storage before processing the view
        _thread_locals.user = getattr(request, 'user', None)

        response = self.get_response(request)

        # Clean up after the response is generated to avoid data leakage
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user

        return response
