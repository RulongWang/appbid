__author__ = 'Jarvis'

from django.http import Http404
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import ugettext as _
from django.db.models import Q, Count
from django.core.urlresolvers import reverse
from appbid import models as appModels
from usersetting import models as userSettingModels
from bid import forms
from query.views import initBidInfo
from message.views import sendMessage


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def createBid(request, *args, **kwargs):
    if kwargs.get('pk'):
        initParam = {}
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'))
        initParam['app'] = app
        initParam['appInfo'] = app.appinfo
        initBidInfo(request, app=app, initParam=initParam)#For below code using the value
        if request.method == "POST":
            biddingForm = forms.BiddingForm(request.POST)
            if biddingForm.is_valid():
                #From bid_create.html
                if 'yes' == request.POST.get('bid_create'):
                    bid = biddingForm.save(commit=False)
                    if bid.price >= initParam.get('bid_price'):
                        bid.app = app
                        bid.buyer = request.user
                        bid.status = 1
                        userPrivateItem = userSettingModels.UserPrivateItem.objects.filter(key='is_bid_approved')
                        if userPrivateItem:
                            is_bid_approved = userSettingModels.UserPrivateSetting.objects.filter(user_id=app.publisher.id, user_private_item_id=userPrivateItem[0])
                            #Need be verified by app publisher.
                            if is_bid_approved and is_bid_approved[0].value == 'True':
                                bid.status = 3
                        bid.save()

                        #Send the message to app publisher
                        send_message = request.POST.get('send_message')
                        if send_message and send_message == 'yes':
                            if sendMessage(request, initParam=initParam):
                                return HttpResponseRedirect(reverse('bid:bid_list', kwargs={'pk': app.id}))
                            else:
                                initParam['biddingForm'] = biddingForm
                                initParam['bid_error'] = initParam['message_error']
                        else:
                            return HttpResponseRedirect(reverse('bid:bid_list', kwargs={'pk': app.id}))
                    else:
                        initParam['biddingForm'] = biddingForm
                        initParam['bid_error'] = _('The new bid has been submitted.')
                #From list_detail.html
                else:
                    initParam['biddingForm'] = biddingForm
        initParam['sender'] = request.user
        initParam['receiver'] = app.publisher
        sendMessage(request, initParam=initParam)
        return render_to_response('bid/bid_create.html', initParam, context_instance=RequestContext(request))
    raise Http404


@csrf_protect
def getBids(request, *args, **kwargs):
    if kwargs.get('pk'):
        initParam = {}
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'))
        initParam['app'] = app
        initParam['appInfo'] = app.appinfo
        initBidInfo(request, app=app, initParam=initParam)
        if request.user.id and request.user.username:
            bids = app.bidding_set.filter(Q(status=1) | Q(buyer=request.user)).order_by('-price', '-bid_time')
        else:
            bids = app.bidding_set.filter(status=1).order_by('-price', '-bid_time')
        buyer_map = {}
        bid_info_list = []
        for bid in bids:
            info_list = [bid]#The bid info
            buyer = bid.buyer
            if buyer_map.get(buyer.id, None) is None:
                temp_info_list = []
                temp_info_list.append(len(buyer_map) + 1)#The index of buyer in all bid buyers
                temp_info_list.append(len(buyer.bidding_set.all()))#The bid amount of the buyer
                temp_info_list.append(len(buyer.bidding_set.values('app').annotate(Count('app'))))#The app amount of the buyer
                buyer_map[buyer.id] = temp_info_list
            info_list.extend(buyer_map.get(buyer.id))
            bid_info_list.append(info_list)
        initParam['bid_info_list'] = bid_info_list
        return render_to_response('bid/bid_list.html', initParam, context_instance=RequestContext(request))
    raise Http404