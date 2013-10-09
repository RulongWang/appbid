__author__ = 'Jarvis'

from django.utils.translation import ugettext as _

from credit import models
from utilities import common


def initCreditPoint(*args, **kwargs):
    user = kwargs.get('user')
    if user:
        creditPoint = models.CreditPoint()
        creditPoint.user = user
        creditPoint.points = common.getSystemParam()(key='cp_init_number', default=100)
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