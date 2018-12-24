from mainapp.models import User
    
def AuthMiddleware(get_response):
    login_path = "/login"
    def middleware(request):
        request.user = None
        if request.path == login_path:
            return get_response(request)
        if "HTTP_AUTHORIZATION" in request.META:
            username, password = tuple([item.strip() for item in request.META["HTTP_AUTHORIZATION"].split(":")])
            user = User.objects.filter(username=username, password=password).first()
            if user:
                request.user = user
                return get_response(request)
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("/login")
    return middleware
