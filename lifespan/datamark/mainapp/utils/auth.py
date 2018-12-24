from mainapp.models import User
    
def getuser(request):
    # if "HTTP_AUTHORIZATION" in request.META:
    if "username" in request.session:
        user = User.objects.filter(username=request.session["username"]).first()
        return user
    else:
        return None
