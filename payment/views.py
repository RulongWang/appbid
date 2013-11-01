__author__ = 'Jarvis'

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _
from django.db import transaction
from paypal import driver, utils
from django.conf import settings

log = logging.getLogger('appbid')

if getattr(settings, "PAYPAL_DEBUG", False):
    EC_RETURNURL = "https://beta.appswalk.com/payment/paypal_return"
    EC_CANCELURL = "https://beta.appswalk.com/payment/paypal_cancel"
    AP_RETURNURL = "https://beta.appswalk.com/payment/paypal_ap_return"
    AP_CANCELURL = "https://beta.appswalk.com/payment/paypal_cancel"
    AP_REDIRECTURL = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey="
    # EC_RETURNURL = "http://127.0.0.1:8000/payment/paypal_return"
    # EC_CANCELURL = "http://127.0.0.1:8000/payment/paypal_cancel"
    # AP_RETURNURL = "http://127.0.0.1:8000/payment/paypal_ap_return"
    # AP_CANCELURL = "http://127.0.0.1:8000/payment/paypal_cancel"
else:
    EC_RETURNURL = "https://www.appswalk.com/payment/paypal_return"
    EC_CANCELURL = "https://www.appswalk.com/payment/paypal_cancel"
    AP_RETURNURL = "https://www.appswalk.com/payment/paypal_ap_return"
    AP_CANCELURL = "https://www.appswalk.com/payment/paypal_cancel"
    # AP_REDIRECTURL = "https://www.paypal.com/webscr?cmd=_ap-payment&paykey="


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payment(request, *args, **kwargs):
    """Begin payment operation."""
    initParam = kwargs.get('initParam')
    executeMethod = initParam.pop('executeMethod', None)
    amount = initParam.pop('amount')
    currency = initParam.pop('currency')
    id = initParam.get('serviceDetail_id')
    if amount and currency and id:
        p = driver.PayPal()
        result = p.SetExpressCheckout(amount, currency, EC_RETURNURL, EC_CANCELURL, initParam=initParam)
        if result:
            #The needed operation for verification later when payment return token..
            if executeMethod:
                initParam['token'] = p.token
                if executeMethod(request, initParam=initParam):
                    if request.session.get('gateway', None):
                        del request.session['gateway']
                    request.session['gateway'] = initParam.get('gateway')
                    redirect_url = p.paypal_url()
                    return redirect(redirect_url)
                else:
                    log.error(_('ServiceDetail with id %(param1)s. Execute method %(param2)s failed.')
                              % {'param1': id, 'param2': executeMethod.__name__})
            else:
                log.error(_('ServiceDetail with id %(param1)s. ExecuteMethod does not exist.') % {'param1': id})
        else:
            log.error(_('ServiceDetail with id %(param1)s. %(param2)s') % {'param1': id, 'param2': str(p.apierror)})
    else:
        log.error(_('payment. Amount or Currency or ServiceDetail ID no exists.'))

    success_page = request.session.get('success_page', None)
    back_page = request.session.get('back_page', None)
    if success_page:
        del request.session['success_page']
    if back_page:
        del request.session['back_page']
        error_msg = driver.GENERIC_PAYPAL_ERROR
        return render_to_response('payment/paypal_cancel.html',
                                  {'error_msg': error_msg, 'back_page': back_page}, context_instance=RequestContext(request))
    else:
        error_msg = _('%(param1)s Please payment again.') % {'param1': driver.GENERIC_PAYPAL_ERROR}
        return render_to_response('payment/paypal_error.html',
                                  {"error_msg": error_msg}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payPalReturn(request, *args, **kwargs):
    """The PayPal method for payment verification."""
    initParam = {}
    token = request.GET.get('token')
    payerID = request.GET.get('PayerID')
    initParam['token'] = token
    initParam['payerid'] = payerID
    if token and payerID:
        p = driver.PayPal()
        res_dict = p.GetExpressCheckoutDetailsInfo(EC_RETURNURL, EC_CANCELURL, token)
        state = p._get_value_from_qs(res_dict, 'ACK')
        if state in ["Success", "SuccessWithWarning"]:
            #Show the list of service detail to user.
            executeMethod = kwargs.pop('executeMethod', None)
            if executeMethod:
                gateway = request.session.get('gateway', None)
                if gateway:
                    initParam['gateway'] = gateway
                    serviceDetail, serviceItems, discount_rate = executeMethod(request, initParam=initParam)
                    if serviceDetail and serviceItems:
                        initParam['serviceDetail'] = serviceDetail
                        initParam['serviceItems'] = serviceItems
                        initParam['discount_rate'] = discount_rate
                        return render_to_response('payment/paypal_return.html', initParam, context_instance=RequestContext(request))
                    else:
                        log.error(_('Token %(param1)s, PayerID: %(param2)s, Execute method %(param3)s failed.')
                                  % {'param1': token, 'param2': payerID, 'param3': executeMethod.__name__})
                else:
                    log.error(_('Token %(param1)s, PayerID: %(param2)s. Gateway no exists in request.session.')
                          % {'param1': token, 'param2': payerID})
            else:
                log.error(_('Token %(param1)s, PayerID: %(param2)s, ExecuteMethod does not exist.')
                          % {'param1': token, 'param2': payerID})
        else:
            error = p._get_value_from_qs(res_dict, 'L_SHORTMESSAGE0')
            log.error(_('Token %(param1)s, PayerID: %(param2)s, %(param3)s.')
                      % {'param1': token, 'param2': payerID, 'param3': error})
    else:
        log.error(_('Token or PayerID no exists.'))

    if request.session.get('gateway', None):
        del request.session['gateway']
    success_page = request.session.get('success_page', None)
    back_page = request.session.get('back_page', None)
    if success_page:
        del request.session['success_page']
    if back_page:
        del request.session['back_page']
        error_msg = driver.GENERIC_PAYPAL_ERROR
        return render_to_response('payment/paypal_cancel.html',
                                  {'error_msg': error_msg, 'back_page': back_page}, context_instance=RequestContext(request))
    else:
        error_msg = _('%(param1)s Please payment again.') % {'param1': driver.GENERIC_PAYPAL_ERROR}
        return render_to_response('payment/paypal_error.html',
                                  {"error_msg": error_msg}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payPalDoCheckOut(request, *args, **kwargs):
    """The PayPal method to charge the money, after all verification passed."""
    initParam = {}
    id = request.GET.get("id")
    token = request.GET.get("token")
    payerID = request.GET.get("PayerID")
    initParam['id'] = id
    initParam['token'] = token
    if token and payerID and id:
        #Check and get Service detail information
        checkMethod = kwargs.pop('checkMethod', None)
        if checkMethod:
            gateway = request.session.get('gateway', None)
            if gateway:
                del request.session['gateway']
                initParam['gateway'] = gateway
                serviceDetail = checkMethod(request, initParam=initParam)
                if serviceDetail:
                    amount = serviceDetail.actual_amount
                    currency = serviceDetail.app.currency.currency
                    result, response = utils.process_payment_request(amount, currency, token, payerID)
                    if result:
                        #Do something after payment success.
                        executeMethod = kwargs.pop('executeMethod', None)
                        if executeMethod:
                            initParam['serviceDetail_id'] = serviceDetail.id
                            if executeMethod(request, initParam=initParam):
                                success_page = request.session.get('success_page', None)
                                back_page = request.session.get('back_page', None)
                                if back_page:
                                    del request.session['back_page']
                                if success_page:
                                    del request.session['success_page']
                                    initParam['success_page'] = success_page
                                initParam['msg'] = _('The payment success. Please check your paypal account.')
                                log.info(_('Seller %(param1)s has paid service fee with service detail id %(param2)s.')
                                          % {'param1': request.user.username, 'param2': serviceDetail.id})
                                return render_to_response("payment/paypal_success.html", initParam, context_instance=RequestContext(request))
                            else:
                                log.error(_('Token %(param1)s, PayerID: %(param2)s, Execute method %(param3)s failed.')
                                          % {'param1': token, 'param2': payerID, 'param3': executeMethod.__name__})
                        else:
                            log.error(_('Token %(param1)s, PayerID: %(param2)s, ExecuteMethod does not exist.')
                                      % {'param1': token, 'param2': payerID})
                    else:
                        log.error(_('Token %(param1)s, PayerID: %(param2)s, %(param3)s : %(param4)s.')
                                  % {'param1': token, 'param2': payerID, 'param3': response.error, 'param4': response.error_msg})
                else:
                    log.error(_('Token %(param1)s, PayerID: %(param2)s, User: %(param3)s, Execute method %(param4)s failed.')
                              % {'param1': token, 'param2': payerID, 'param3': request.user.username, 'param4': checkMethod.__name__})
            else:
                log.error(_('Token %(param1)s, PayerID: %(param2)s, Gateway no exists in request.session.')
                          % {'param1': token, 'param2': payerID})
        else:
            log.error(_('Token %(param1)s, PayerID: %(param2)s, CheckMethod does not exist.')
                      % {'param1': token, 'param2': payerID})
    else:
        log.error(_('Token or PayerID no exists.'))

    if request.session.get('gateway', None):
        del request.session['gateway']
    success_page = request.session.get('success_page', None)
    back_page = request.session.get('back_page', None)
    if success_page:
        del request.session['success_page']
    if back_page:
        del request.session['back_page']
        error_msg = driver.GENERIC_PAYPAL_ERROR
        return render_to_response('payment/paypal_cancel.html',
                                  {'error_msg': error_msg, 'back_page': back_page}, context_instance=RequestContext(request))
    else:
        error_msg = _('%(param1)s Please payment again.') % {'param1': driver.GENERIC_PAYPAL_ERROR}
        return render_to_response('payment/paypal_error.html',
                                  {"error_msg": error_msg}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payPalCancel(request, *args, **kwargs):
    """User cancel payment or pay operation."""
    initParam = {}
    error_msg = _("You cancel the payment to finish performing PayPal payment process. We don't charge your money.")
    initParam['error_msg'] = error_msg

    if request.session.get('gateway', None):
        del request.session['gateway']

    success_page = request.session.get('success_page', None)
    back_page = request.session.get('back_page', None)
    if success_page:
        del request.session['success_page']
    if back_page:
        initParam['back_page'] = back_page
        del request.session['back_page']
    log.info(_('User %(param1)s cancel the payment.') % {'param1': request.user.username})
    return render_to_response("payment/paypal_cancel.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def pay(request, *args, **kwargs):
    initParam = kwargs.get('initParam')
    executeMethod = initParam.pop('executeMethod', None)
    currency = initParam.get('currency')
    id = initParam.get('txn_id')
    if currency and id:
        p = driver.PayPal()
        result = p.setAPCall(currency, AP_RETURNURL, AP_CANCELURL, 'PAY', initParam=initParam)
        if result['responseEnvelope.ack'][0] == 'Success':
            pay_key = result['payKey'][0]
            #The needed operation for verification later when pay return pay_key.
            if executeMethod:
                initParam['pay_key'] = pay_key
                if executeMethod(request, initParam=initParam):
                    #payReturn will do operation by two session values.
                    if request.session.get('pay_key', None):
                        del request.session['pay_key']
                    request.session['pay_key'] = pay_key
                    if request.session.get('gateway', None):
                        del request.session['gateway']
                    request.session['gateway'] = 'paypal'
                    #redirect PayPal pay website.
                    redirect_url = p.AP_REDIRECTURL + pay_key
                    return redirect(redirect_url)
                else:
                    log.error(_('Transaction with id %(param1)s. Execute method %(param2)s failed.')
                              % {'param1': id, 'param2': executeMethod.__name__})
            else:
                log.error(_('Transaction with id %(param1)s. ExecuteMethod does not exist.') % {'param1': id})
        else:
            log.error(_('Transaction with id %(param1)s. %(param2)s') % {'param1': id, 'param2': str(result['error(0).message'][0])})
    else:
        log.error(_('Pay. Currency or Transaction ID no exists.'))

    success_page = request.session.get('success_page', None)
    back_page = request.session.get('back_page', None)
    if success_page:
        del request.session['success_page']
    if back_page:
        del request.session['back_page']
        error_msg = driver.GENERIC_PAYPAL_ERROR
        return render_to_response('payment/paypal_cancel.html',
                                  {'error_msg': error_msg, 'back_page': back_page}, context_instance=RequestContext(request))
    else:
        error_msg = _('%(param1)s Please transaction again.') % {'param1': driver.GENERIC_PAYPAL_ERROR}
        return render_to_response('payment/paypal_error.html',
                                  {"error_msg": error_msg}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def payReturn(request, *args, **kwargs):
    """The operation after user pay successfully."""
    initParam = {}
    pay_key = request.session.get('pay_key', None)
    gateway = request.session.get('gateway', None)
    if pay_key and gateway:
        del request.session['pay_key']
        del request.session['gateway']
        #Check and get Transaction information
        checkMethod = kwargs.pop('checkMethod', None)
        if checkMethod:
            initParam['pay_key'] = pay_key
            initParam['gateway'] = gateway
            transaction = checkMethod(request, initParam=initParam)
            if transaction:
                p = driver.PayPal()
                #Check whether use has paid successfully.
                result = p.check_ap_payment_status(transaction.pay_key)
                if result['status'][0] == 'COMPLETED':
                    #Do something after user payed successfully.
                    executeMethod = kwargs.pop('executeMethod', None)
                    if executeMethod:
                        initParam['transaction_id'] = transaction.id
                        initParam['buyer_account'] = result['senderEmail'][0]
                        if executeMethod(request, initParam=initParam):
                            success_page = request.session.get('success_page', None)
                            back_page = request.session.get('back_page', None)
                            if back_page:
                                del request.session['back_page']
                            if success_page:
                                del request.session['success_page']
                                initParam['success_page'] = success_page
                            initParam['msg'] = _('Your pay success. Please check your paypal account. We have email to seller. You also can send message to seller.')
                            log.info(_('User %(param1)s has paid with transaction id %(param2)s.')
                                      % {'param1': request.user.username, 'param2': transaction.id})
                            return render_to_response("payment/paypal_success.html", initParam, context_instance=RequestContext(request))
                        else:
                            log.error(_('User %(param1)s has paid with transaction id %(param2)s, but execute method %(param3)s failed.')
                                      % {'param1': request.user.username, 'param2': transaction.id, 'param3': executeMethod.__name__})
                    else:
                        log.error(_('User %(param1)s has paid with transaction id %(param2)s, but ExecuteMethod does not exist.')
                                  % {'param1': request.user.username, 'param2': transaction.id})
                else:
                    log.error(_('User %(param1)s has no paid with transaction id %(param2)s.')
                              % {'param1': request.user.username, 'param2': transaction.id})
            else:
                log.error(_('PayKey %(param1)s, Gateway: %(param2)s, User: %(param3)s, Execute method %(param4)s failed.')
                          % {'param1': pay_key, 'param2': gateway, 'param3': request.user.username, 'param4': checkMethod.__name__})
        else:
            log.error(_('PayKey %(param1)s, Gateway: %(param2)s, CheckMethod does not exist.')
                      % {'param1': pay_key, 'param2': gateway})
    else:
        log.error(_('Pay. PayKey or Gateway no exists.'))

    success_page = request.session.get('success_page', None)
    back_page = request.session.get('back_page', None)
    if success_page:
        del request.session['success_page']
    if back_page:
        del request.session['back_page']
        error_msg = driver.GENERIC_PAYPAL_ERROR
        return render_to_response('payment/paypal_cancel.html',
                                  {'error_msg': error_msg, 'back_page': back_page}, context_instance=RequestContext(request))
    else:
        error_msg = _('%(param1)s Please transaction again.') % {'param1': driver.GENERIC_PAYPAL_ERROR}
        return render_to_response('payment/paypal_error.html',
                                  {"error_msg": error_msg}, context_instance=RequestContext(request))
