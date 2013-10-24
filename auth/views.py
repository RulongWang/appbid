__author__ = 'Jarvis'


import urllib
from django.shortcuts import render_to_response, render, RequestContext, get_object_or_404, HttpResponse, Http404, redirect
from django.views.decorators.csrf import csrf_protect

from appbid import settings

@csrf_protect
def authComplete(request, *args, **kwargs):
    access_token = '2.00k2kaSB5zPLLDe61c5e4ed1DVX24B'
    status = 'Yes, the apps walk.'
    params = urllib.urlencode({'source': settings.WEIBO_CLIENT_KEY, 'access_token': access_token, 'status': status})
    try:
        data = urllib.urlopen('https://api.weibo.com/2/statuses/update.json?', params).read()
    except (ValueError, KeyError, IOError), e:
        print e

    return render_to_response('usersetting/register_active_confirm.html', context_instance=RequestContext(request))


@csrf_protect
def authError(request, *args, **kwargs):
    return None

