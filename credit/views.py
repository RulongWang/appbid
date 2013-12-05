__author__ = 'Jarvis'

import logging

from django.utils.translation import ugettext as _

from credit import models
from credit import forms
from utilities import common

log = logging.getLogger('appbid')


def initCreditPoint(*args, **kwargs):
    user = kwargs.get('user')
    if user:
        creditPoint = models.CreditPoint()
        creditPoint.user = user
        creditPoint.points = common.getSystemParam(key='cp_init_number', default=100)
        creditPoint.save()
        #Log Credit Point Change
        creditLog = models.CreditLog()
        creditLog.user = user
        creditLog.credit_point = creditPoint
        creditLog.points = creditPoint.points
        creditLog.change_reason = _('Init credit point.')
        creditLog.save()
    else:
        #Log error message
        print 'Init credit point.'
    return None


def increaseCreditPoint(*args, **kwargs):
    user = kwargs.get('user')
    point = kwargs.get('point')
    type = kwargs.get('type')
    ref_id = kwargs.get('ref_id')
    if user and point:
        creditPoints = models.CreditPoint.objects.filter(user_id=user.id)
        if creditPoints:
            creditPoints[0].points += point
            creditPoints[0].save()
            #Log Credit Point Change
            creditLog = models.CreditLog()
            creditLog.user = user
            creditLog.credit_point = creditPoints[0]
            creditLog.points = point
            creditLog.type = type
            creditLog.ref_id = ref_id
            creditLog.change_reason = _('Increase credit point.')
            creditLog.save()
        else:
            #Log error message
            print 'Credit point data does not exist.'
    else:
        #Log error message
        print 'Increase credit point.'
    return None


def decreaseCreditPoint(*args, **kwargs):
    user = kwargs.get('user')
    point = kwargs.get('point')
    type = kwargs.get('type')
    ref_id = kwargs.get('ref_id')
    if user and point:
        if point > 0:
            point = -point
        creditPoints = models.CreditPoint.objects.filter(user_id=user.id)
        if creditPoints:
            creditPoints[0].points += point
            creditPoints[0].save()
            #Log Credit Point Change
            creditLog = models.CreditLog()
            creditLog.user = user
            creditLog.credit_point = creditPoints[0]
            creditLog.points = point
            creditLog.type = type
            creditLog.ref_id = ref_id
            creditLog.change_reason = _('Decrease credit point.')
            creditLog.save()
        else:
            #Log error message
            print 'Credit point data does not exist.'
    else:
        #Log error message
        print 'Decrease credit point.'
    return None


def getUserCreditPoint(*args, **kwargs):
    user = kwargs.get('user')
    if user:
        creditPoints = models.CreditPoint.objects.filter(user_id=user.id)
        if creditPoints:
            return creditPoints[0].points
    return -1


def createAppraisement(request, *args, **kwargs):
    initParam = kwargs.get('initParam')
    form = forms.AppraisementForm()
    if request.method == 'POST':
        appraisementForm = forms.AppraisementForm(request.POST)
        if appraisementForm.is_valid():
            appraisement = appraisementForm.save(commit=False)
            appraisement.user_id = request.user.id
            appraisement.transaction_id = initParam.get('transaction').id
            appraisement.save()
            return appraisement
        else:
            initParam['error_msg'] = _("Appraisement failed. Please try again.")
            log.error(_("Appraisement failed. Please try again."))
    initParam['form'] = form
    return None


def getAppraisement(*args, **kwargs):
    user_id = kwargs.get('user_id')
    txn_id = kwargs.get('txn_id')
    if user_id and txn_id:
        appraisements = models.Appraisement.objects.filter(user_id=user_id, transaction_id=txn_id)
        if appraisements:
            return appraisements[0]
    return None