__author__ = 'Jarvis'

from job import jobdetail

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

# test()

# from django_cron import CronJobBase, Schedule
# class MyCronJobJarvis(CronJobBase):
#     RUN_EVERY_MINS = 1 #every 1 min
#     #RUN_AT_TIMES = ['6:30']
#     MIN_NUM_FAILURES = 3
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'appbid.cron_job' # a unique code
#
#     def do(self):
#         print 'Hello Job test.'