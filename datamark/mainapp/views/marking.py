# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from mainapp.models import Dataset, Sample
from .login import getuser, authbar, redirectLogin
 
def index(request):
    user = getuser(request)
    if user is None:
        return redirectLogin(request)
    context = {}
    authbar(request, context)
    return render(request, 'marking.html', context)

def statistics(request):
    setname = request.GET["setname"]
    dataset = Dataset.objects.get(setname=setname)
    result = {}
    result["marked"] = Sample.objects.filter(dataset=dataset, status=Sample.STATUS_MARKED).count()
    result["total"] = Sample.objects.filter(dataset=dataset).count()
    return JsonResponse({
        "success": True,
        "data": result
    })

apis = [
    ("statistics", statistics)
]