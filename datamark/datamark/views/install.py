# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from utils.detect import detect
from django.http import JsonResponse
import json

def index(request):
    context = {}
    return render(request, 'install.html', context)

def setup_info(request):
    result = json.loads(request.body)
    return JsonResponse(result)

apis = [
    ("setup_info", setup_info)
]