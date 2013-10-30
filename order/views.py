__author__ = 'Jarvis'

import datetime
import string
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, Http404, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.db import transaction
from django.contrib.auth.models import User

from appbid import models as appModels
from order import models, forms
from payment import views as paymentViews
from transaction import views as transactionViews
from utilities import common

log = logging.getLogger('appbid')


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def checkout(request, *args, **kwargs):
    """checkout for service detail payment."""
    initParam = {'begin_date': None}
    app_id = kwargs.get('app_id')
    service_id = kwargs.get('service_id')
    service_sn = kwargs.get('service_sn')
    user = get_object_or_404(User, pk=request.user.id, username=request.user.username)
    app = get_object_or_404(appModels.App, pk=app_id, publisher_id=user.id)
    serviceDetail = get_object_or_404(models.ServiceDetail, pk=service_id, app_id=app_id, sn=service_sn)
    acceptGateways = user.acceptgateway_set.filter(is_active=True, is_default=True)
    serviceDetails = models.ServiceDetail.objects.filter(app_id=app_id, is_payed=True,
                            end_date__gte=datetime.datetime.now().strftime('%Y-%m-%d')).order_by('-pk')
    #Init data
    if serviceDetails:
        initParam['begin_date'] = serviceDetails[0].end_date
        serviceDetail.start_date = serviceDetails[0].end_date
    else:
        serviceDetail.start_date = datetime.datetime.now()
    initParam['service_expiry_date'] = common.getSystemParam(key='service_expiry_date', default=1)
    initParam['currency'] = app.currency.currency
    if acceptGateways:
        initParam['acceptGateway'] = acceptGateways[0]

    if request.method == "POST":
        form = forms.ServiceDetailForm(request.POST)
        if form.is_valid():
            days = (form.cleaned_data['end_date'] - form.cleaned_data['start_date']).days
            service_expiry_date = string.atoi(common.getSystemParam(key='service_expiry_date', default=31))
            if serviceDetail.is_payed:
                initParam['order_error'] = _('The payment is paid.')
            elif len(acceptGateways) == 0:
                initParam['order_error'] = _('The gateway is required.Please choice gateway.')
            elif (initParam['begin_date'] and form.cleaned_data['start_date'] < initParam['begin_date']) or days != service_expiry_date:
                initParam['order_error'] = _('Service date is not correct.')
            else:
                form.save(commit=False)
                serviceDetail.start_date = form.cleaned_data['start_date']
                serviceDetail.end_date = form.cleaned_data['end_date']
                serviceDetail.acceptgateway = acceptGateways[0]
                serviceDetail.save()

                if serviceDetail.actual_amount <= 0:
                    if executeCheckOut(request, business_id=serviceDetail.id):
                        initParam['payment_msg'] = _('The payment is successful.')
                        #TODO:Need show the message.
                        return redirect('/'.join(['/seller/payment', str(app.id), serviceDetail.sn]))
                    else:
                        initParam['order_error'] = _('The payment is failed. Please payment again.')
                else:
                    #Invoke payment method - payment for service detail
                    initParam['serviceDetail_id'] = serviceDetail.id
                    initParam['amount'] = serviceDetail.actual_amount
                    initParam['DESC'] = 'Service fee on AppsWalk.'
                    initParam['PAYMENTREQUEST_0_DESC'] = 'Service fee for App %(param1)s of user %(param2)s on AppsWalk.' % {'param1':app.app_name, 'param2':user.username}
                    initParam['ITEMAMT'] = serviceDetail.actual_amount
                    initParam['L_NAME0'] = 'Service fee on AppsWalk'
                    initParam['L_DESC0'] = 'Service fee for App %(param)s' % {'param':app.app_name}
                    initParam['L_AMT0'] = serviceDetail.actual_amount
                    initParam['L_QTY0'] = 1
                    #The needed operation method in payment.
                    initParam['executeMethod'] = kwargs.get('executeMethod')
                    #The back page, when payment has error.
                    initParam['back_page'] = '/'.join([common.getHttpHeader(request), 'seller/payment', str(app.id)])
                    return paymentViews.payment(request, initParam=initParam)
    #Init data
    initParam['form'] = forms.ServiceDetailForm(instance=serviceDetail)

    return render_to_response("order/checkout.html", initParam, context_instance=RequestContext(request))


def updateServiceDetail(request, *args, **kwargs):
    """Insert token into serviceDetail table for verification later, when payment return token."""
    initParam = kwargs.get('initParam')
    serviceDetail_id = initParam.get('serviceDetail_id')
    token = initParam.get('token')
    if serviceDetail_id and token:
        serviceDetails = models.ServiceDetail.objects.filter(pk=1)
        if serviceDetails:
            serviceDetails[0].pay_token = token
            serviceDetails[0].save()
            return True
    return False


def executeCheckOut(request, *args, **kwargs):
    """The operation after user payment successfully."""
    business_id = kwargs.get('business_id')
    if business_id:
        serviceDetails = models.ServiceDetail.objects.filter(pk=business_id, is_payed=False)
        if serviceDetails:
            serviceDetail = serviceDetails[0]
            app = serviceDetail.app
            if app.publisher == request.user:
                service_expiry_date = string.atoi(common.getSystemParam(key='service_expiry_date', default=31))
                if serviceDetail.start_date < datetime.datetime.now():
                    serviceDetail.start_date = datetime.datetime.now()
                    serviceDetail.end_date = datetime.datetime.now() + datetime.timedelta(days=service_expiry_date)
                serviceDetail.is_payed = True
                serviceDetail.save()
                # If app is draft or has been closed, change app to published after payment,.
                if app.status == 1 or app.status == 3:
                    app.status = 2
                    app.publish_date = serviceDetail.start_date
                    app.begin_date = serviceDetail.start_date
                    app.end_date = serviceDetail.end_date
                else:
                    app.end_date = serviceDetail.end_date
                app.save()

                #Init transaction model data
                transactionViews.initTransaction(request, app=app)

                log.info(_('The ServiceDetail with id %(param1)s is payed by %(param2)s.')
                          % {'param1': business_id, 'param2': request.user.username})
                return serviceDetail
            else:
                log.error(_('The ServiceDetail with id %(param1)s do not belong the user %(param2)s.')
                          % {'param1': business_id, 'param2': request.user.username})
        else:
            log.error(_('The ServiceDetail with id %(param)s does not exist.') % {'param': business_id})
    else:
        log.error('The business_id is None.')
    return None