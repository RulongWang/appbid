__author__ = 'Jarvis'

import jobdetail
import logging

log = logging.getLogger('appbid')

def jobByFourHour(*args, **kwargs):
    """The task will be done every four hours."""
    log.info('Run jobByFourHour - verificationAppForSeller.')
    jobdetail.verificationAppForSeller()


def jobByMidnight(*args, **kwargs):
    """Server invoke the method to do schedule task every night at midnight."""
    log.info('Run jobByMidnight - sendMailForRemind.')
    jobdetail.sendMailForRemind()


def jobByEveryHour(*args, **kwargs):
    """Server invoke the method to do schedule task at schedule time, such as: every hour."""
    log.info('Run jobByEveryHour - checkServiceDateForApps.')
    jobdetail.checkServiceDateForApps()
    log.info('Run jobByEveryHour - taskForBuyUnpaid.')
    jobdetail.taskForBuyUnpaid()
    log.info('Run jobByEveryHour - checkIfSellApp.')
    jobdetail.checkIfSellApp()


def jobByFiveMin(*args, **kwargs):
    """Server invoke the method to do schedule task at schedule time, such as: every five min."""
    log.info('Run jobByFiveMin - jobPayStatus.')
    jobdetail.jobPayStatus()
