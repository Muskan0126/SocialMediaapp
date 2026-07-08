from user_agents import parse


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        print(f"Request Method: {request.method}, Request Path: {request.path}")
    
        response = self.get_response(request)
        return response
 
class SystemInfoMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        ip = request.META.get("REMOTE_ADDR")

        ua = parse(user_agent)

        print("\n========== USER SYSTEM INFO ==========")
        print(f"IP Address      : {ip}")
        print(f"Browser         : {ua.browser.family} {ua.browser.version_string}")
        print(f"Operating System: {ua.os.family} {ua.os.version_string}")
        print(f"Device          : {ua.device.family}")
        print(f"Is Mobile       : {ua.is_mobile}")
        print(f"Is Tablet       : {ua.is_tablet}")
        print(f"Is PC           : {ua.is_pc}")
        print(f"Request Method  : {request.method}")
        print(f"Request Path    : {request.path}")
        print("======================================\n")

        response = self.get_response(request)
        return response