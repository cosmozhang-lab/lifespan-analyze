# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from utils.detect import detect
 
def index(request):
    context = {}
    return render(request, 'index.html', context)

def install(request):
    context = {}
    return render(request, 'install.html', context)
