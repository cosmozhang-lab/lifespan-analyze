# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from mainapp.models import Sample
 
def index(request):
    context = {}
    return render(request, 'index.html', context)

def statistics(request):
    result = {}
    result["marked"] = Sample.objects.filter(status=Sample.STATUS_MARKED).count()
    result["total"] = Sample.objects.count()
    return JsonResponse(result)

apis = [
    ("statistics", statistics)
]