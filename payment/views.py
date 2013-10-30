__author__ = 'Jarvis'

import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.shortcuts import render_to_response, HttpResponse, RequestContext, get_object_or_404, Http404, redirect
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from payment import models
from paypal import driver
from paypal.models import PayPalResponse
from paypal.utils import process_payment_request, process_refund_request
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
    """Payment operation."""
    #For saving the redirect url of the success or failed page, after payment done.
    initParam = kwargs.get('initParam')
    back_page = initParam.pop('back_page')
    executeMethod = initParam.pop('executeMethod', None)
    amount = initParam.pop('amount')
    currency = initParam.pop('currency')
    id = initParam.get('serviceDetail_id')
    if amount and currency:
        p = driver.PayPal()
        #Parameters needed:  1, amount  2, currency  ,3 EC_RETURNRUL 4, EC_CANCELURL 5,
        result = p.SetExpressCheckout(amount, currency, EC_RETURNURL, EC_CANCELURL, initParam=initParam)
        if result:
            #The needed operation for verification later when payment return token..
            if executeMethod:
                initParam['token'] = p.token
                if executeMethod(request, initParam=initParam):
                    redirect_url = p.paypal_url()
                    print('success_excute_setExpressCheckout')
                    print(redirect_url)
                    return HttpResponseRedirect(redirect_url)
                else:
                    log.error(' '.join(['ServiceDetail ID:', str(id), '- Execute method', executeMethod.__name__, 'failed.']))
            else:
                log.error(' '.join(['ServiceDetail ID:', str(id), '- ExecuteMethod does not exist.']))
        else:
            log.error(' '.join(['ServiceDetail ID:', str(id), '-', str(p.apierror)]))
    else:
        log.error(' '.join(['ServiceDetail ID:', str(id), '- Amount or currency is not correct.']))

    error_msg = driver.GENERIC_PAYPAL_ERROR

    return render_to_response('payment/paypal_failed.html',
            {'error_msg': error_msg, 'back_page': back_page}, context_instance=RequestContext(request))

    # return HttpResponseRedirect('/payment/paypal_cancel')

    # initParam['success_url'] = 'payment/payment.html'
    # return 'success'
    # initParam['failed_url'] = 'payment/payment.html'
    # return 'failed'



        #error message from paypal
        # ACK=notSuccess&TIMESTAMP=date/timeOfResponse&
        # CORRELATIONID=debuggingToken&VERSION=VersionNo&
        # BUILD=buildNumber&L_ERRORCODE0=errorCode&
        # L_SHORTMESSAGE0=shortMessage&
        # L_LONGMESSAGE0=longMessage&
        # L_SEVERITYCODE0=severityCode

@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paypalreturn(request, *args, **kwargs):
    """The paypal method for payment verification."""
    initParam = {}
    token = request.GET.get('token')
    payerid = request.GET.get('PayerID')
    initParam['token'] = token
    initParam['payerid'] = payerid
    initParam['gateway'] = 'paypal'
    if token and payerid:
        p = driver.PayPal()
        res_dict = p.GetExpressCheckoutDetailsInfo(EC_RETURNURL, EC_CANCELURL, token)
        state = p._get_value_from_qs(res_dict, 'ACK')

        if state in ["Success", "SuccessWithWarning"]:
            #Show the list of service detail to user.
            executeMethod = kwargs.pop('executeMethod', None)
            if executeMethod:
                serviceDetail, serviceItems = executeMethod(request, token=token, initParam=initParam)
                if serviceDetail and serviceItems:
                    initParam['serviceDetail'] = serviceDetail
                    initParam['serviceItems'] = serviceItems
                    return render_to_response('payment/paypal_return.html', initParam, context_instance=RequestContext(request))
                else:
                    log.error(' '.join(['Token:', token, 'PayerID:', payerid, '- Execute method', executeMethod.__name__, 'failed.']))
            else:
                log.error(' '.join(['Token:', token, 'PayerID:', payerid, '- ExecuteMethod does not exist.']))
        else:
            error = p._get_value_from_qs(res_dict, 'L_SHORTMESSAGE0')
            log.error(' '.join(['Token:', token, 'PayerID:', payerid, '-', error]))
    else:
        log.error(' '.join(['Token or PayerID is missing.']))

    error_msg = ' '.join([driver.GENERIC_PAYPAL_ERROR, 'Please payment again.'])

    return render_to_response('payment/paypal_error.html',
                              {"error_msg": error_msg}, context_instance=RequestContext(request))


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




@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paypal_docheckout(request, *args, **kwargs):
    """The paypal method to charge the money, after all verification passed."""
    token = request.GET.get("token")
    payerid = request.GET.get("PayerID")

    # charge from PayPal

    # get the order id by token

    result, response = process_payment_request('40', 'USD', token, payerid)
    # process the result
    if not result:
        # show the error message (comes from PayPal API) and redirect user to the error page
        #if request.user.is_authenticated():
            #request.user.message_set.create(message = _("Amount %s has not been charged, server error is '%s'" % (amount, response.error)))
        #return HttpResponseRedirect(error_url)

    # Now we are gone, redirect user to success page
    #if request.user.is_authenticated():
        #request.user.message_set.create(message = _("Amount %s has been successfully charged, your transaction id is '%s'" % (amount, response.trans_id)))


        return render_to_response("payment/paypal_failed.html", context_instance = RequestContext(request))
    else:
        #Do something after payment.
        executeMethod = kwargs.pop('executeMethod', None)
        if executeMethod:
            result = executeMethod(request, kwargs=kwargs)
            if result:
                print result
            else:
                #business id is not correct. or return error page.
                print 'the payment is not correct. Please check your operation or contact customer service.'
        return render_to_response("payment/paypal_success.html", context_instance = RequestContext(request))


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def paymentcancel(request, *args, **kwargs):
    """Payment operation."""
    initParam = {'payment': None}
    return render_to_response("payment/paypal_cancel.html", initParam, context_instance=RequestContext(request))