class CharsetMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if '/admin' not in request.path:
            response = self.get_response(request)
            response["Content-Type"] = "application/json; charset=utf-8"
            return response
        else:
            response = self.get_response(request)
            response["Content-Type"] = "text/html; charset=utf-8"
            return response

