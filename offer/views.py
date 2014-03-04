__author__ = 'jia.qianpeng'

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404


@csrf_protect
@login_required(login_url='/usersetting/home/')
def registerOffer(request, *args, **kwargs):
    """The function for create, update offer information."""
    initParam = {}
    print 'register offer....'
    return render_to_response("offer/register_offer.html", initParam, context_instance=RequestContext(request))