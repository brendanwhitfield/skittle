from django.shortcuts import render_to_response,render
from django.conf import settings 
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, QueryDict
from django.views.decorators.cache import cache_control
from SkittleCore.GraphRequestHandler import handleRequest
from SkittleCore.models import StatePacket
from SkittleCore.Graphs.models import *
import json

def index(request, genome="",chromosome=""):
    width = request.GET.get('width',100)
    scale = request.GET.get('scale',1)
    start = request.GET.get('start',1)
    zoom = request.GET.get('zoom',1)
    graphs = request.GET.get('graphs',"n")
    fileLength = 721000
    context = {'genome':genome,'width':width, "scale":scale,"start":start,"zoom":zoom,"graphs":graphs,"fileLength":fileLength}
    return render(request, 'index.html',context)

@cache_control(must_revalidate=False, max_age=3600)
def graph(request, genome="hg19",chromosome="chrY-sample"):
    state = StatePacket()
    state.chromosome = chromosome
    if state.chromosome == "chrY-sample":
        state.genome = "Animalia/Mammalia/Homo/Sapiens/" + genome
    else:
        state.genome = "Plantae/Angiosperms/Zea/Mays/" + genome

    state.start = int(request.GET.get('start',1))
    state.width = int(request.GET.get('width',100))
    state.scale = int(request.GET.get('scale',1))
    state.requestedGraph = request.GET.get('graph','n')
    # if state.requestedGraph == 'm':
    # 	repeatMapState = RepeatMapState()
    # 	repeatMapState.F_width = int(request.GET.get('F_width',40))
    # 	repeatMapState.F_start = int(request.GET.get('F_start',1))
    	# allGraphSettings = state.getActiveGraphSettings()
    	# allGraphSettings.filter()

    image_data = handleRequest(state)
    # image_data = open("/Users/marshallds/Sites/Skittle/master/SkittleCore/UI/assets/n-display.png", "rb").read()
    return HttpResponse(image_data, content_type="image/png")

def state(request):
	json = '''graphStatus = {
        "a":{name:"Annotations",visible:false,fn:"drawAnnotations",isRasterable:true},
        "n":{name:"Nucleotide Display",visible:true,fn:"drawNucDisplay",isRasterable:true},
        "b":{name:"Nucleotide Bias",visible:false,fn:"drawNucBias",isRasterable:false},
        "m":{name:"Repeat Map",visible:false,fn:"drawRMap",isRasterable:false}
    }'''
	return HttpResponse(json,content_type="application/json")