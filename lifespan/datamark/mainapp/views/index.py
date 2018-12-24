# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from mainapp.models import Dataset, Sample
from .login import authbar, getuser, redirectLogin
 
def index(request):
    user = getuser(request)
    if user is None:
        return redirectLogin(request)
    context = {}
    authbar(request, context)
    return render(request, 'index.html', context)

def datasets(request):
    dss = Dataset.objects.all()
    datasets = []
    for ds in dss:
        dataset = {}
        dataset["setname"] = ds.setname
        dataset["marked"] = Sample.objects.filter(dataset=ds, status=Sample.STATUS_MARKED).count()
        dataset["total"] = Sample.objects.filter(dataset=ds).count()
        datasets.append(dataset)
    return JsonResponse({
        "success": True,
        "data": datasets
    })


apis = [
    ("datasets", datasets)
]