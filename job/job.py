__author__ = 'Jarvis'

import datetime
import jobdetail


def jobForMidnight(*args, **kwargs):
    """Server invoke the method to do schedule task every night at midnight."""
    print 'jobForMidnight', datetime.datetime.now()
    # jobdetail.checkServiceDateForApps()
    # jobdetail.checkIfSellApp()
    return None


def jobForScheduleTime(*args, **kwargs):
    """Server invoke the method to do schedule task at schedule time, such as: every hour."""
    jobdetail.taskForBuyUnpaid()
    return None
