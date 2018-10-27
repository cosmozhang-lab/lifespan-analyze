# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from mainapp.models import Dataset, Sample
from .login import getuser, authbar, redirectLogin
from utils.common import parse_datetime, RegionType
from utils.imgproc import prepare_sample, complete_sample as imgproc_complete_sample, PreparedSample, Rect
import os, time
from django.conf import settings
from utils.configs import MarkConfig
from utils.mainparams import marksize

def index(request):
    user = getuser(request)
    if user is None: return redirectLogin(request)
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

def clear_pendings(request):
    user = getuser(request)
    if user is None: return HttpResponse(403)
    setname = request.GET["setname"]
    dataset = Dataset.objects.get(setname=setname)
    Sample.objects.filter(dataset=dataset, marker=user, status=Sample.STATUS_PENDING).update(status=Sample.STATUS_UNMARKED)
    return JsonResponse({ "success": True })

def fetch_sample(request):
    user = getuser(request)
    if user is None: return HttpResponse(403)
    setname = request.GET["setname"]
    dataset = Dataset.objects.get(setname=setname)
    # Fetch a sample record in the database
    sample = Sample.objects.filter(dataset=dataset, status=Sample.STATUS_UNMARKED).order_by("seq", "plate").first()
    if sample is None:
        return JsonResponse({
                "success": False,
                "reason": "all samples in this dataset has been marked"
            })
    sample.status = Sample.STATUS_PENDING
    sample.marker = user
    sample.save()
    # prepare the sample
    filepath = os.path.join(sample.rootdir, sample.subdir, sample.filename)
    outname = sample.plate + "__" + sample.subdir
    outfullname = os.path.join(settings.BASE_DIR, "static", "runtime", outname)
    timing0 = time.time()
    props = prepare_sample(filepath, outfullname)
    timing1 = time.time()
    timing = timing1 - timing0
    # make the return data
    retdata = {}
    retdata["sampleid"] = sample.id
    retdata["imgsrc"] = "/static/runtime/" + outname + ".jpg"
    retdata["plate"] = sample.plate
    retdata["subdir"] = sample.subdir
    retdata["datetime"] = parse_datetime(sample.subdir).strftime("%Y-%m-%dT%H:%M:%S")
    retdata["proctime"] = timing
    retdata["marks"] = [{
            "type": props.regiontypes[i].name,
            "x": props.regions[i].x,
            "y": props.regions[i].y,
            "width": props.regions[i].width,
            "height": props.regions[i].height
        } for i in range(len(props.regiontypes))]
    retdata["marksize"] = { "width": marksize[1], "height": marksize[0] }
    return JsonResponse({
            "success": True,
            "data": retdata
        })

def complete_sample(request):
    user = getuser(request)
    if user is None: return HttpResponse(403)
    sampledata = request.jsondata
    sample = Sample.objects.get(sampledata["sampleid"])
    regions = [Rect(item["x"], item["y"], item["width"], item["height"]) for item in sampledata["marks"]]
    regiontypes = [RegionType.get(name=item["type"]) for item in sampledata["marks"]]
    markedsample = PreparedSample(regions=regions, regiontypes=regiontypes)
    markconfig = MarkConfig()
    outdir = markconfig.outdir
    outdir = os.path.join(outdir, sample.dataset.setname)
    if not os.path.exists(outdir): os.mkdir(outdir)
    outdir = os.path.join(outdir, sample.plate)
    if not os.path.exists(outdir): os.mkdir(outdir)
    inname = outname = sample.plate + "__" + sample.subdir
    infullname = os.path.join(settings.BASE_DIR, "static", "runtime", outname)
    outfullname = os.path.join(outdir, outname)
    imgproc_complete_sample(markedsample, infullname, outfullname)
    sample.status = Sample.STATUS_MARKED
    sample.marker = user
    sample.datapath = outfullname + ".mata"
    sample.save()
    return JsonResponse({ "success": True })

apis = [
    ("statistics", statistics),
    ("clear_pendings", clear_pendings),
    ("fetch_sample", fetch_sample),
    ("complete_sample", complete_sample)
]