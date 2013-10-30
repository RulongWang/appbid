__author__ = 'Jarvis'

import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

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
else:
    EC_RETURNURL = "https://www.appswalk.com/payment/paypal_return"
    EC_CANCELURL = "https://www.appswalk.com/payment/paypal_cancel"
    AP_RETURNURL = "https://www.appswalk.com/payment/paypal_ap_return"
    AP_CANCELURL = "https://www.appswalk.com/payment/paypal_cancel"
    AP_REDIRECTURL = "https://www.paypal.com/webscr?cmd=_ap-payment&paykey="


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
    if amount and currency:
        p = driver.PayPal()
        result = p.SetExpressCheckout(amount, currency, EC_RETURNURL, EC_CANCELURL, initParam=initParam)
        if result:
            #The needed operation for verification later when payment return token..
            if executeMethod:
                initParam['token'] = p.token
                if executeMethod(request, initParam=initParam):
                    redirect_url = p.paypal_url()
                    return HttpResponseRedirect(redirect_url)
                else:
                    log.error(_('ServiceDetail with id %(param1)s. Execute method %(param2)s failed.')
                              % {'param1': id, 'param2': executeMethod.__name__})
            else:
                log.error(_('ServiceDetail with id %(param1)s. ExecuteMethod does not exist.') % {'param1': id})
        else:
            log.error(_('ServiceDetail with id %(param1)s. %(param2)s') % {'param1': id, 'param2': str(p.apierror)})
    else:
        log.error(_('ServiceDetail with id %(param1)s. Amount or Currency no exists.') % {'param1': id})

    back_page = request.session.get('back_page', None)
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
    initParam['gateway'] = 'paypal'
    if token and payerID:
        p = driver.PayPal()
        res_dict = p.GetExpressCheckoutDetailsInfo(EC_RETURNURL, EC_CANCELURL, token)
        state = p._get_value_from_qs(res_dict, 'ACK')
        if state in ["Success", "SuccessWithWarning"]:
            #Show the list of service detail to user.
            executeMethod = kwargs.pop('executeMethod', None)
            if executeMethod:
                serviceDetail, serviceItems, discount_rate = executeMethod(request, token=token, initParam=initParam)
                if serviceDetail and serviceItems:
                    initParam['serviceDetail'] = serviceDetail
                    initParam['serviceItems'] = serviceItems
                    initParam['discount_rate'] = discount_rate
                    return render_to_response('payment/paypal_return.html', initParam, context_instance=RequestContext(request))
                else:
                    log.error(_('Token %(param1)s, PayerID: %(param2)s, Execute method %(param3)s failed.')
                              % {'param1': token, 'param2': payerID, 'param3': executeMethod.__name__})
            else:
                log.error(_('Token %(param1)s, PayerID: %(param2)s, ExecuteMethod does not exist.')
                          % {'param1': token, 'param2': payerID})
        else:
            error = p._get_value_from_qs(res_dict, 'L_SHORTMESSAGE0')
            log.error(_('Token %(param1)s, PayerID: %(param2)s, %(param3)s.')
                      % {'param1': token, 'param2': payerID, 'param3': error})
    else:
        log.error(_('Token or PayerID no exists.'))

    back_page = request.session.get('back_page', None)
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
    token = request.GET.get("token")
    payerID = request.GET.get("PayerID")
    initParam['token'] = token
    initParam['payerid'] = payerID
    initParam['gateway'] = 'paypal'
    if token and payerID:
        result, response = utils.process_payment_request('40', 'USD', token, payerID)
        if result:
            #Do something after payment success.
            executeMethod = kwargs.pop('executeMethod', None)
            if executeMethod:
                if executeMethod(request, initParam=initParam):
                    back_page = request.session.get('back_page', None)
                    if back_page:
                        del request.session['back_page']
                        initParam['back_page'] = back_page
                        initParam['msg'] = _('The payment success. Please check your paypal account.')
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
        log.error(_('Token or PayerID no exists.'))

    back_page = request.session.get('back_page', None)
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
def paymentCancel(request, *args, **kwargs):
    """User cancel Payment operation."""
    initParam = {}
    error_msg = _("You cancel the payment to finish performing PayPal payment process. We don't charge your money.")
    initParam['error_msg'] = error_msg
    back_page = request.session.get('back_page', None)
    if back_page:
        initParam['back_page'] = back_page
        del request.session['back_page']
    return render_to_response("payment/paypal_cancel.html", initParam, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def start_paypal_ap(request, *args, **kwargs):
    """Payment operation."""
    p = driver.PayPal()
    result = p.setAPCall(AP_RETURNURL, AP_CANCELURL, 'pay')

    paykey = request.GET.get('Paykey')

    if paykey is None:
        error = "paykey is missing"
    else:
        p = driver.PayPal()
        return render_to_response("payment/paypal_return.html", {"token":paykey}, context_instance=RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paypal_ap_return(request, *args, **kwargs):
    """Payment operation."""
    # paykey = request.GET.get('Paykey')
    #
    # if paykey is None:
    #     error = "paykey is missing"
    # else:
    p = driver.PayPal()
    result = p.check_ap_payment_status('AP-6WN52515K6610334Y')# need to search the paykey from transaction table
    if result['status'][0] == 'COMPLETED':
       print('success')
    #

    #Do something after user payed.
    executeMethod = kwargs.pop('executeMethod', None)
    if executeMethod:
        result = executeMethod(request, kwargs=kwargs)
        if result:
            print result
        else:
            #transaction is not correct. or return error page.
            print 'the pay is not correct. Please check your operation or contact customer service.'

    return render_to_response("payment/paypal_ap_return.html", {"token":'test'}, context_instance=RequestContext(request))
