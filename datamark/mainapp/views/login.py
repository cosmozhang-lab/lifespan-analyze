# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from mainapp.models import User
from mainapp.utils.auth import getuser
from urllib.parse import quote as escape
 
def login(request):
    context = {}
    return render(request, 'login.html', context)

def register(request):
    context = {}
    return render(request, 'register.html', context)

def authbar(request, context):
    user = getuser(request)
    context["user"] = user

def doRegister(request):
    username = request.jsondata["username"]
    password = request.jsondata["password"]
    if User.objects.filter(username=username).count() > 0:
        return JsonResponse({"success": False, "reason": "User already exists"})
    user = User(username=username, password=password)
    user.save()
    request.session["username"] = username
    return JsonResponse({"success": True})

def doLogin(request):
    username = request.jsondata["username"]
    password = request.jsondata["password"]
    user = User.objects.filter(username=username).first()
    if user is None:
        return JsonResponse({"success": False, "reason": "User doesn't exist"})
    if user.password != password:
        return JsonResponse({"success": False, "reason": "Incorrect password"})
    request.session["username"] = username
    return JsonResponse({"success": True})

def doLogout(request):
    request.session.pop("username")
    return JsonResponse({"success": True})

def redirectLogin(request):
    return HttpResponseRedirect("/login?return=" + escape(request.get_full_path()))

apis = [
    ("login", doLogin),
    ("logout", doLogout),
    ("register", doRegister)
]