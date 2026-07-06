class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        print(f"Request Method: {request.method}, Request Path: {request.path}")
    
        response = self.get_response(request)
        return response
