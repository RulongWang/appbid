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
from payment import models as paymentModels
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
    initParam['discount_rate'] = 1 - string.atof(common.getSystemParam(key='discount_rate', default=1))

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
                    if checkOutSuccess(request, serviceDetail=serviceDetail):
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
                    initParam['L_DESC0'] = 'Service fee for App %(param1)s' % {'param1':app.app_name}
                    initParam['L_AMT0'] = serviceDetail.actual_amount
                    initParam['L_QTY0'] = 1
                    #The needed operation method in payment.
                    initParam['executeMethod'] = kwargs.get('executeMethod')
                    #The back page, when payment has error.
                    back_page = request.session.get('back_page', None)
                    if not back_page:
                        request.session['back_page'] = '/'.join([common.getHttpHeader(request), 'seller/payment', str(app.id)])
                    #The success return page, when payment finish.
                    success_page = request.session.get('success_page', None)
                    if not success_page:
                        request.session['success_page'] = '/'.join([common.getHttpHeader(request), 'query/app-detail', str(app.id)])
                    return paymentViews.payment(request, initParam=initParam)
    #Init data
    initParam['form'] = forms.ServiceDetailForm(instance=serviceDetail)

    return render_to_response('order/checkout.html', initParam, context_instance=RequestContext(request))


def updateServiceDetail(request, *args, **kwargs):
    """Insert token into serviceDetail table for verification later, when payment return token."""
    initParam = kwargs.get('initParam')
    serviceDetail_id = initParam.get('serviceDetail_id')
    token = initParam.get('token')
    if serviceDetail_id and token:
        serviceDetails = models.ServiceDetail.objects.filter(pk=serviceDetail_id)
        if serviceDetails:
            serviceDetails[0].pay_token = token
            serviceDetails[0].save()
            log.info(_('ServiceDetail with id %(param1)s set pay_token to %(param2)s.')
                     % {'param1': serviceDetail_id, 'param2': token})
            return serviceDetails[0]
        else:
            log.error(_('Token: %(param1)s, ServiceDetail with id %(param2)s no exists.')
                      % {'param1': token, 'param2': serviceDetail_id})
    else:
        log.error(_('ServiceDetail_id or Token no exists.'))
    return None


def getServiceInfo(request, *args, **kwargs):
    """#Show service information to user."""
    initParam = kwargs.get('initParam')
    token = initParam.get('token')
    gateway = initParam.get('gateway')
    if token and gateway:
        discount_rate = 1 - string.atof(common.getSystemParam(key='discount_rate', default=1))
        gateways = paymentModels.Gateway.objects.filter(name__iexact=gateway)
        if gateways:
            acceptGateways = paymentModels.AcceptGateway.objects.filter(user_id=request.user.id,
                                                                        type_id=gateways[0].id, is_active=True)
            if acceptGateways:
                serviceDetails = models.ServiceDetail.objects.filter(pay_token=token, is_payed=False,
                                                                     acceptgateway_id=acceptGateways[0].id)
                if serviceDetails:
                    serviceItems = serviceDetails[0].serviceitem.all()
                    return serviceDetails[0], serviceItems, discount_rate
                else:
                    log.error(_('User:%(param1)s, ServiceDetail with pay_token %(param2)s no exists.')
                              % {'param1': request.user.username, 'param2': token})
            else:
                log.error(_('User:%(param1)s, Token: %(param2)s, acceptGateway no exists.')
                          % {'param1': request.user.username, 'param2': token})
        else:
            log.error(_('Gateway %(param1)s no exists.') % {'param1': gateway})
    else:
        log.error(_('Token or Gateway no exists.'))
    return None


def checkServiceDetail(request, *args, **kwargs):
    """Check and get service detail information."""
    initParam = kwargs.get('initParam')
    id = initParam.get('id')
    token = initParam.get('token')
    if id and token:
        serviceDetails = models.ServiceDetail.objects.filter(pk=id, pay_token=token, is_payed=False)
        if serviceDetails:
            return serviceDetails[0]
        else:
            log.error(_('User:%(param1)s, ServiceDetail with pay_token %(param2)s no exists.')
                      % {'param1': request.user.username, 'param2': token})
    else:
        log.error(_('Token or ServiceDetail ID no exists.'))
    return None


def executeCheckOut(request, *args, **kwargs):
    """The operation after user payment successfully."""
    initParam = kwargs.get('initParam')
    token = initParam.get('token')
    gateway = initParam.get('gateway')
    if token and gateway:
        gateways = paymentModels.Gateway.objects.filter(name__iexact=gateway)
        if gateways:
            acceptGateways = paymentModels.AcceptGateway.objects.filter(user_id=request.user.id,
                                                                        type_id=gateways[0].id, is_active=True)
            if acceptGateways:
                serviceDetails = models.ServiceDetail.objects.filter(pay_token=token, is_payed=False,
                                                                     acceptgateway_id=acceptGateways[0].id)
                if serviceDetails:
                    serviceDetail = checkOutSuccess(request, serviceDetail=serviceDetails[0])
                    log.info(_('User:%(param1)s, ServiceDetail with id %(param2)s, pay_token %(param3)s is payed.')
                             % {'param1': request.user.username, 'param2': serviceDetail.id, 'param3': token})
                    return serviceDetail
                else:
                    log.error(_('User:%(param1)s, ServiceDetail with pay_token %(param2)s no exists.')
                              % {'param1': request.user.username, 'param2': token})
            else:
                log.error(_('User:%(param1)s, Token: %(param2)s, acceptGateway no exists.')
                          % {'param1': request.user.username, 'param2': token})
        else:
            log.error(_('Gateway %(param1)s no exists.') % {'param1': gateway})
    else:
        log.error(_('Token or Gateway no exists.'))
    return None


def checkOutSuccess(request, *args, **kwargs):
    """The operation after user payment successfully."""
    serviceDetail = kwargs.get('serviceDetail')
    if serviceDetail:
        app = serviceDetail.app
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
        return serviceDetail
    return None