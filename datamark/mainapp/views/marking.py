# -*- coding: utf-8 -*-
 
#from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from mainapp.models import Dataset, Sample
from .login import getuser, authbar, redirectLogin
from utils.common import parse_datetime, RegionType
from utils.imgproc import prepare_sample, review_sample, complete_sample as imgproc_complete_sample, PreparedSample, Rect
import os, shutil, time
from django.conf import settings
from utils.configs import MarkConfig
from utils.mainparams import marksize
from urllib.parse import unquote as unescape

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

def make_userdir(user):
    userpath = "static/runtime/" + user.username + "/"
    dirpath = os.path.join(settings.BASE_DIR, userpath)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
    return userpath

def remove_userdir(user):
    userpath = "static/runtime/" + user.username + "/"
    dirpath = os.path.join(settings.BASE_DIR, userpath)
    if os.path.isdir(dirpath):
        filelist = os.listdir(dirpath)
        for filename in filelist:
            os.remove(os.path.join(dirpath, filename))

def clear_pendings(request):
    user = getuser(request)
    if user is None: return HttpResponse(403)
    setname = request.GET["setname"]
    dataset = Dataset.objects.get(setname=setname)
    samples = Sample.objects.filter(dataset=dataset, marker=user, status=Sample.STATUS_PENDING)
    samples.update(status=Sample.STATUS_UNMARKED)
    remove_userdir(user)
    return JsonResponse({ "success": True })

def sample_list(request):
    user = getuser(request)
    if user is None: return HttpResponse(403)
    dataset = Dataset.objects.get(setname=request.GET["setname"])
    samples = [item["id"] for item in Sample.objects.filter(dataset=dataset).order_by("plate", "seq").values("id")]
    return JsonResponse({
            "success": True,
            "data": samples
        })

def fetch_sample(request):
    user = getuser(request)
    if user is None: return HttpResponse(403)
    rank = request.GET["rank"] if "rank" in request.GET else "descending"
    sampleid = int(request.GET["sampleid"]) if "sampleid" in request.GET else None
    # Fetch a sample record in the database
    if not sampleid is None:
        sample = Sample.objects.get(id=sampleid)
    elif rank == "ascending":
        dataset = Dataset.objects.get(setname=request.GET["setname"])
        sample = Sample.objects.filter(dataset=dataset, status=Sample.STATUS_UNMARKED).order_by("seq", "plate").first()
    elif rank == "descending":
        dataset = Dataset.objects.get(setname=request.GET["setname"])
        sample = Sample.objects.filter(dataset=dataset, status=Sample.STATUS_UNMARKED).order_by("-seq", "plate").first()
    elif rank == "random":
        import random
        dataset = Dataset.objects.get(setname=request.GET["setname"])
        queryset = Sample.objects.filter(dataset=dataset, status=Sample.STATUS_UNMARKED)
        total = queryset.count()
        sample = queryset[int(random.random()*total)] if total > 0 else None
    else:
        raise ValueError("rank must be 'ascending', 'descending' or 'random'")
    if sample is None:
        return JsonResponse({
                "success": False,
                "reason": "all samples in this dataset has been marked"
            })
    userpath = make_userdir(user)
    if sample.status == Sample.STATUS_MARKED:
        markconfig = MarkConfig()
        outdir = os.path.join(markconfig.outdir, sample.dataset.setname, sample.plate)
        outname = sample.plate + "__" + sample.subdir
        storedname = os.path.join(outdir, outname)
        extractname = os.path.join(settings.BASE_DIR, userpath, outname)
        timing0 = time.time()
        props = review_sample(storedname, extractname)
        timing1 = time.time()
        timing = timing1 - timing0
    else:
        sample.status = Sample.STATUS_PENDING
        sample.marker = user
        sample.save()
        # prepare the sample
        filepath = os.path.join(sample.rootdir, sample.subdir, sample.filename)
        outname = sample.plate + "__" + sample.subdir
        outfullname = os.path.join(settings.BASE_DIR, userpath, outname)
        timing0 = time.time()
        props = prepare_sample(filepath, outfullname)
        timing1 = time.time()
        timing = timing1 - timing0
    # make the return data
    retdata = {}
    retdata["sampleid"] = sample.id
    retdata["imgsrc"] = "/" + userpath + outname + ".jpg"
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
    sample = Sample.objects.get(id=sampledata["sampleid"])
    regions = [Rect(item["x"], item["y"], item["width"], item["height"]) for item in sampledata["marks"]]
    regiontypes = [RegionType.get(name=item["type"]) for item in sampledata["marks"]]
    markedsample = PreparedSample(regions=regions, regiontypes=regiontypes)
    markconfig = MarkConfig()
    userpath = make_userdir(user)
    outdir = markconfig.outdir
    outdir = os.path.join(outdir, sample.dataset.setname)
    if not os.path.exists(outdir): os.mkdir(outdir)
    outdir = os.path.join(outdir, sample.plate)
    if not os.path.exists(outdir): os.mkdir(outdir)
    inname = outname = sample.plate + "__" + sample.subdir
    infullname = os.path.join(settings.BASE_DIR, userpath, outname)
    outfullname = os.path.join(outdir, outname)
    imgproc_complete_sample(markedsample, infullname, outfullname)
    sample.status = Sample.STATUS_MARKED
    sample.marker = user
    sample.datapath = outfullname + ".mat"
    sample.save()
    return JsonResponse({ "success": True })

def search_sample(request):
    user = getuser(request)
    if user is None: return HttpResponse(403)
    import re
    limit = int(request.GET["n"]) if "n" in request.GET else 5
    keywords = unescape(request.GET["q"]) if "q" in request.GET else ""
    keywords = list(filter(lambda x: x, re.split(r"[^0-9a-zA-Z]", keywords)))
    kwplate = None
    kwdate = ""
    kwdateconcaters = ["", "-", "-", "__", "-", "-"]
    kwdatecnt = 0
    for kw in keywords:
        if re.match(r"[a-zA-Z]\d*", kw) is None:
            kwdate += kwdateconcaters[kwdatecnt] + kw
            kwdatecnt += 1
        else:
            kwplate = kw
    queryset = Sample.objects.all()
    if kwplate: queryset = queryset.filter(plate=kwplate)
    if kwdate: queryset = queryset.filter(subdir__startswith=kwdate)
    queryset = queryset[:limit]
    def sample_tojson(sampleitem):
        retdata = {}
        retdata["sampleid"] = sampleitem.id
        retdata["plate"] = sampleitem.plate
        retdata["subdir"] = sampleitem.subdir
        return retdata
    retdata = list(map(sample_tojson, queryset))
    return JsonResponse({
            "success": True,
            "data": retdata
        })


apis = [
    ("statistics", statistics),
    ("clear_pendings", clear_pendings),
    ("sample_list", sample_list),
    ("fetch_sample", fetch_sample),
    ("complete_sample", complete_sample),
    ("search_sample", search_sample)
]