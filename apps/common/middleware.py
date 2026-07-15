import time

from .logger import app_logger


class RequestLoggingMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        start = time.time()

        response = self.get_response(request)

        duration = round(time.time() - start, 3)

        username = "Anonymous"

        if request.user.is_authenticated:

            username = request.user.username

        app_logger.info(
            "%s %s User=%s Status=%s Time=%ss", request.method, request.path, username, response.status_code, duration
        )

        return response
