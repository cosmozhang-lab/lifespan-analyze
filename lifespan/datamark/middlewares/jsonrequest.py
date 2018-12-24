import json
from django.conf import settings
    
def JsonRequestMiddleware(get_response):
    def middleware(request):
        if request.content_type.lower() == "application/json":
            encoding = request.encoding or settings.DEFAULT_CHARSET
            request.jsondata = json.loads(request.body.decode(encoding))
        return get_response(request)
    return middleware
