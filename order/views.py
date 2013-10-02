__author__ = 'Jarvis'

import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, Http404, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.db import transaction
from django.contrib.auth.models import User

from appbid import models as appModels
from order import models, forms
from payment import views as paymentViews
from utilities import common


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def checkout(request, *args, **kwargs):
    """checkout for service detail payment."""
    initParam = {}
    initParam['begin_date'] = None
    app_id = kwargs.get('app_id')
    service_id = kwargs.get('service_id')
    service_sn = kwargs.get('service_sn')
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    app = get_object_or_404(appModels.App, pk=app_id, publisher_id=user.id)
    serviceDetail = get_object_or_404(models.ServiceDetail, pk=service_id, app_id=app_id, sn=service_sn)
    acceptGateways = user.acceptgateway_set.filter(is_active=True, is_default=True)
    serviceDetails = models.ServiceDetail.objects.filter(app_id=app_id, is_payed=True, end_date__gt=datetime.datetime.now()).order_by('-pk')
    #Init data
    if serviceDetails:
        initParam['begin_date'] = serviceDetails[0].end_date
        serviceDetail.start_date = serviceDetails[0].end_date
    else:
        serviceDetail.start_date = datetime.datetime.now()

    if request.method == "POST":
        form = forms.ServiceDetailForm(request.POST)
        if form.is_valid():
            days = (form.cleaned_data['end_date'] - form.cleaned_data['start_date']).days
            if serviceDetail.is_payed:
                initParam['order_error'] = _('The payment is paid.')
            elif (initParam['begin_date'] and form.cleaned_data['start_date'] < initParam['begin_date']) or days > 31 or days < 28:
                initParam['order_error'] = _('Service date is not correct.')
            else:
                #Invoke payment method - payment for service detail
                payment = paymentViews.payment(request, initParam=initParam)
                if payment == 'success':
                    form.save(commit=False)
                    serviceDetail.start_date = form.cleaned_data['start_date']
                    serviceDetail.end_date = form.cleaned_data['end_date']
                    serviceDetail.is_payed = True
                    serviceDetail.save()
                    # If app is draft or has been closed, change app to published after payment,.
                    if app.status == 1 or app.status == 3:
                        app.publish_date = form.cleaned_data['start_date']
                        app.status = 2
                        app.save()
                    return render_to_response(initParam['success_url'], initParam, context_instance=RequestContext(request))
                else:
                    initParam['order_error'] = _('Payment failed.')
                    return render_to_response(initParam['failed_url'], initParam, context_instance=RequestContext(request))

    #Init data
    initParam['form'] = forms.ServiceDetailForm(instance=serviceDetail)
    initParam['service_expiry_date'] = common.getSystemParam(key='service_expiry_date', default=1)
    initParam['currency'] = app.currency.currency
    if acceptGateways:
        initParam['acceptGateway'] = acceptGateways[0]

    return render_to_response("order/checkout.html", initParam, context_instance=RequestContext(request))