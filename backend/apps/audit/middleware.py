import threading

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


def get_current_ip():
    return getattr(_thread_locals, 'ip', None)


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cache active caller authentication status
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            
        _thread_locals.user = user

        # Retrieve IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        _thread_locals.ip = ip

        response = self.get_response(request)

        # Clear active context
        _thread_locals.user = None
        _thread_locals.ip = None

        return response
