__author__ = 'Jarvis'

import time
import datetime
import string

from django.http import Http404
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import ugettext as _
from django.db.models import Q, Count
from django.core.urlresolvers import reverse

from appbid import models as appModels
from usersetting import models as userSettingModels
from transaction import models as txnModels
from bid import forms
from query.views import initBidInfo
from message.views import sendMessage
from credit import views as creditViews
from utilities import common


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
        #Do something, when the time is app end date.
        if app.status == 2 and initParam['begin_bid']:
            initParam['is_callback'] = True
        if request.method == "POST":
            biddingForm = forms.BiddingForm(request.POST)
            #Buyer credit point judge for bidding.
            min_cp = common.getSystemParam(key='min_cp_for_bid', default=50)
            cp = creditViews.getUserCreditPoint(user=request.user)
            if cp == -1 or cp < string.atoi(min_cp):
                initParam['biddingForm'] = biddingForm
                initParam['bid_error'] = _('You can not bid, because your credit point is too low. You can pay credit point, after our verification.')
            else:
                if biddingForm.is_valid():
                    #From bid_create.html
                    if 'yes' == request.POST.get('bid_create'):
                        bid = biddingForm.save(commit=False)
                        if datetime.datetime.now() > app.end_date:
                            initParam['biddingForm'] = biddingForm
                            initParam['bid_error'] = _('The bidding is closed, you can not bid.')
                        elif bid.price >= initParam.get('bid_price'):
                            bid.app = app
                            bid.buyer = request.user
                            bid.status = 1
                            # userPrivateItem = userSettingModels.UserPrivateItem.objects.filter(key='is_bid_approved')
                            # if userPrivateItem:
                            #     is_bid_approved = userSettingModels.UserPrivateSetting.objects.filter(user_id=app.publisher.id, user_private_item_id=userPrivateItem[0])
                            #     #Need be verified by app publisher.
                            #     if is_bid_approved and is_bid_approved[0].value == 'True':
                            #         bid.status = 3
                            bid.save()

                            #Send the message to app publisher
                            send_message = request.POST.get('send_message')
                            if send_message and send_message == 'yes':
                                if sendMessage(request, initParam=initParam):
                                    return redirect(reverse('bid:bid_list', kwargs={'pk': app.id}))
                                else:
                                    initParam['biddingForm'] = biddingForm
                                    initParam['bid_error'] = initParam['message_error']
                            else:
                                return redirect(reverse('bid:bid_list', kwargs={'pk': app.id}))
                        else:
                            initParam['biddingForm'] = biddingForm
                            initParam['bid_error'] = _('The new bid has been submitted.')
                    #From list_detail.html
                    else:
                        initParam['biddingForm'] = biddingForm
        initParam['sender'] = request.user
        initParam['receiver'] = app.publisher
        transactions = txnModels.Transaction.objects.filter(app_id=app.id).exclude(status=1)
        if transactions:
            initParam['transaction'] = transactions[0]

        sendMessage(request, initParam=initParam)
        return render_to_response('bid/bid_create.html', initParam, context_instance=RequestContext(request))
    raise Http404


@csrf_protect
@login_required(login_url='/usersetting/home/')
def bidList(request, *args, **kwargs):
    if kwargs.get('pk'):
        initParam = {}
        app = get_object_or_404(appModels.App, pk=kwargs.get('pk'))
        initParam['app'] = app
        initParam['appInfo'] = app.appinfo
        initBidInfo(request, app=app, initParam=initParam)
        #Do something, when the time is app end date.
        if app.status == 2 and initParam['begin_bid']:
            initParam['is_callback'] = True

        bids = app.bidding_set.filter(Q(status=1) | Q(buyer=request.user)).order_by('-price', '-bid_time')
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
        #Show app transaction status to buyer or seller
        transactions = txnModels.Transaction.objects.filter(app_id=app.id).exclude(status=1)
        if transactions:
            initParam['transaction'] = transactions[0]

        return render_to_response('bid/bid_list.html', initParam, context_instance=RequestContext(request))
    raise Http404