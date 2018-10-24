# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from utils.detect import detect
from django.http import JsonResponse
from utils.files import FileFinder, FileItem
from mainapp.models import Sample

def index(request):
    context = {}
    return render(request, 'install.html', context)

def setup_info(request):
    directory = request.jsondata["directory"] or None
    if directory is None:
        raise ValueError("directory must be set")
    plates = request.jsondata["plates"] or None
    if plates is None:
        raise ValueError("plates must be set")
    import re
    plates = re.sub(r'\s', '', plates).split(",")
    ifile0 = request.jsondata["from"] or None
    ifile0 = None if ifile0 is None else int(ifile0)
    nfiles = request.jsondata["to"] or None
    nfiles = None if nfiles is None else int(nfiles)
    filelists = FileFinder(directory).get_file_lists(plates, ifile0, nfiles)
    for plate in filelists:
        filelists[plate] = [item.to_json() for item in filelists[plate]]
    return JsonResponse(filelists)

def setup_confirm(request):
    Sample.objects.all().delete()
    data = request.jsondata
    for plate in data:
        for i in range(len(data[plate])):
            item = FileItem.from_json(data[plate][i])
            o = Sample(seq=i+1, plate=plate, rootdir=item.rootdir, subdir=item.subdir, filename=item.filename)
            o.save()
    return JsonResponse({"success": True})

apis = [
    ("setup_info", setup_info),
    ("setup_confirm", setup_confirm)
]