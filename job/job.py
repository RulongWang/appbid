__author__ = 'Jarvis'

import jobdetail


def jobByFourHour(*args, **kwargs):
    """The task will be done every four hours."""
    jobdetail.verificationAppForSeller()


def jobByMidnight(*args, **kwargs):
    """Server invoke the method to do schedule task every night at midnight."""
    print 'jobForMidnight'


def jobByEveryHour(*args, **kwargs):
    """Server invoke the method to do schedule task at schedule time, such as: every hour."""
    jobdetail.checkServiceDateForApps()
    jobdetail.taskForBuyUnpaid()
    jobdetail.checkIfSellApp()


def jobByFiveMin(*args, **kwargs):
    """Server invoke the method to do schedule task at schedule time, such as: every five min."""
    jobdetail.jobPayStatus()
