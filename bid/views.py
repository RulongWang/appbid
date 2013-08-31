__author__ = 'Jarvis'
from django.http import Http404
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from appbid import models
from bid import forms
from query.views import initBidInfo


@csrf_protect
@login_required(login_url='/account/home/')
def createBid(request, *args, **kwargs):
    if kwargs['pk']:
        initParam = {}
        app = get_object_or_404(models.App, pk=kwargs['pk'])
        initParam['app_id'] = app.id
        if request.method == "POST":
            biddingForm = forms.BiddingForm(request.POST)
            if biddingForm.is_valid():
                if request.POST.get('comment'):#From bid_create.html
                    bid = biddingForm.save(commit=False)
                    bid.app = app
                    bid.status = 1
                    if app.is_verified:#Need be verified by app publisher.
                        bid.status = 3
                    bid.save()
                    bid.buyer.add(request.user)
                    return HttpResponseRedirect(reverse('query:app_detail', kwargs={'pk': app.id}))
                else:#From list_detail.html
                    initParam['biddingForm'] = biddingForm
        initBidInfo(app=app, initParam=initParam)
        return render_to_response('bid/bid_create.html', initParam, context_instance=RequestContext(request))
    raise Http404


def getBids(request, *args, **kwargs):
    print 'bid list'