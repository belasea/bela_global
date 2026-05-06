from .models import UserSession
from .utils import get_client_ip


class UserSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Ensure session exists
        if not request.session.session_key:
            request.session.save()

        if request.user.is_authenticated:
            session_key = request.session.session_key

            exists = UserSession.objects.filter(
                session_key=session_key
            ).exists()

            if not exists:
                UserSession.objects.create(
                    user=request.user,
                    ip_address=get_client_ip(request),
                    session_key=session_key,
                    active=True
                )

        response = self.get_response(request)
        return response