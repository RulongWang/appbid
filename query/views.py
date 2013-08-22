# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,render
from django.shortcuts import render_to_response,HttpResponse,  RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
import urllib
import json
# from PIL import Image

#register app entry
def register_app(request):
    return render(request, "seller/register_content.html",{"test":"test"})


def hello(request):
    return HttpResponse(" This is the home page")


def getIcon(request):
    pass




def getDetail(request):
    """

    :param request:
    :return:
    """
    search_url = 'http://itunes.apple.com/lookup?id=639384326'
    raw = urllib.urlopen(search_url)
    js = raw.read()
    js_object = json.loads(js)
    results = js_object["results"][0]
    icon = results['artworkUrl60']
    return render_to_response('query/listing_detail.html',
                              {"json_objects": js_object["resultCount"],
                               "icon": icon},
                              context_instance=RequestContext(request))
