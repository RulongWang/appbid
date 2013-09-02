__author__ = 'Jarvis'
from django.http import Http404
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
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
                if 'yes' == request.POST.get('bid_create'):#From bid_create.html
                    bid = biddingForm.save(commit=False)
                    bid.app = app
                    bid.buyer = request.user
                    bid.status = 1
                    if app.is_verified:#Need be verified by app publisher.
                        bid.status = 3
                    bid.save()
                    return HttpResponseRedirect(reverse('query:app_detail', kwargs={'pk': app.id}))
                else:#From list_detail.html
                    initParam['biddingForm'] = biddingForm
        initBidInfo(app=app, initParam=initParam)
        return render_to_response('bid/bid_create.html', initParam, context_instance=RequestContext(request))
    raise Http404


def getBids(request, *args, **kwargs):
    if kwargs['pk']:
        initParam = {}
        app = get_object_or_404(models.App, pk=kwargs['pk'])
        initParam['app'] = app
        initParam['appInfo'] = app.appinfo
        initBidInfo(app=app, initParam=initParam)
        bids = app.bidding_set.filter(Q(status=1) | Q(buyer=request.user)).order_by('-price', '-bid_time')
        buyer_map = {}
        bid_info_list = []
        for bid in bids:
            buyer = bid.buyer
            if buyer_map.get(buyer.id, None) is None:
                info_list = []
                info_list.append(bid)
                info_list.append(len(buyer_map) + 1)
                info_list.append(len(buyer.bidding_set.all()))
                info_list.append(len(buyer.bidding_set.values('app').annotate(Count('app'))))
                buyer_map[buyer.id] = info_list
            bid_info_list.append(buyer_map.get(buyer.id))
        initParam['bid_info_list'] = bid_info_list
        return render_to_response('bid/bid_list.html', initParam, context_instance=RequestContext(request))
    raise Http404