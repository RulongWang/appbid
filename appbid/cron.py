__author__ = 'Jarvis'

from job import jobdetail

def test():
    print 'job.cron'
    jobdetail.verificationAppForSeller()


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