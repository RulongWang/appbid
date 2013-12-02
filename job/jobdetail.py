__author__ = 'Jarvis'

import string
import datetime

from django.db.models import Max

from appbid import models as appModels
from notification import models as notificationModels
from transaction import models as txnModels
from utilities import common, email
from credit import views as creditViews
from transaction import views as txnViews


def verificationAppForSeller(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every four hours.
        After Seller creating app clicks verified, verified app owner ship on schedule plan
    """
    times = string.atoi(common.getSystemParam(key='verify_app_times', default=3))
    ownerShipScans = appModels.OwnerShip_Scan.objects.filter(times__lte=times)
    massEmailThread = email.MassEmailThread()
    for ownerShipScan in ownerShipScans:
        app = ownerShipScan.app
        result = common.getITunes(app.apple_id)
        if result is None:
            continue
        description = result.get('description', None)
        if app.verify_token in description:
            templates = notificationModels.NotificationTemplate.objects.filter(name='verified_app_success_inform_seller')
            if templates:
                subject = ''
                message = ''
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
                ownerShipScan.delete()
                #Update app is_verified value
                app.is_verified = True
                app.save()
        else:
            templates = notificationModels.NotificationTemplate.objects.filter(name='verified_app_failed_inform_seller')
            if templates:
                subject = ''
                message = ''
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
                ownerShipScan.times += 1
                ownerShipScan.save()
    massEmailThread.start()

    return None


def checkServiceDateForApps(*args, **kwargs):
    """
        The task will be done every night at midnight.
        Do something, when the app service date is ending.
        1. App status will be changed from published to closed.
        2. Send email of expiry date to seller.(The email: 1.Service end; 2.Seller can trade now.)
    """
    current_date = datetime.datetime.combine(datetime.date.today(), datetime.time())
    next_date = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time())
    apps = appModels.App.objects.filter(status=2, end_date__gte=current_date, end_date__lt=next_date)
    massEmailThread = email.MassEmailThread()
    for app in apps:
        app.status = 3
        app.save()
        transaction = app.transaction
        max_price = app.bidding_set.filter(status=1).aggregate(Max('price'))
        current_price = max_price.get('price__max', 0)
        #If bidding price is more than max price, seller has 7 days to trade or else seller can not trade it.
        if transaction and transaction.status == 1 and app.reserve_price <= current_price:
            if transaction.end_time is None:
                paid_expiry_date = string.atoi(common.getSystemParam(key='sell_expiry_date', default=7))
                transaction.end_time = app.end_date + datetime.timedelta(days=paid_expiry_date)
                transaction.save()
            #Log transaction
            transactionsLog = txnModels.TransactionLog()
            transactionsLog.app = app
            transactionsLog.status = 1
            transactionsLog.save()
        templates = notificationModels.NotificationTemplate.objects.filter(name='service_end_inform_seller')
        if templates:
            subject = ''
            message = ''
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
    massEmailThread.start()
    return None


def checkIfSellApp(*args, **kwargs):
    """
        The task will be done every night at midnight.
        When service stop, if bidding price is more than max price, seller has 7 days to trade now. Then seller did not
        trade app in 7 days, seller's credit points will be decreased.
    """
    transactions = txnModels.Transaction.objects.filter(status=1, end_time__isnull=False)
    massEmailThread = email.MassEmailThread()
    for transaction in transactions:
        #Decrease seller's credit points
        creditViews.decreaseCreditPoint(user=transaction.seller)
        templates = notificationModels.NotificationTemplate.objects.filter(name='unsold_end_inform_seller')
        if templates:
            subject = ''
            message = ''
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[transaction.seller.email])
    massEmailThread.start()
    return None


def sendMailForRemind(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every hour.
        1. The paid_expiry_date set in system-param table is 7 days.
           If buyer does not pay, will send email to buyer in remain 4, 2, 1 days.
        2. The txn_expiry_date set in system-param table is 15 days.
           If buyer does not finish trade, will send email to buyer in remain 7, 4, 2, 1 days.
    """
    return None


def taskForBuyUnpaid(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every hour.
        Do something, if buy still unpaid after 7 days of paid_expiry_date set in system-param table.
        1. Buyer will be subtracted 50 credit point, and put into blacklist.
        2. Buyer's all bidding status is changed from approved to rejected.(Note: All bidding for this buyer.)
        3. For transaction data, status be changed from Unpaid to Unsold, and set buyer, price, end_time to None.
          (Invoke initTransaction method.)
        4. Send email to buyer.(The email: 1.Subtract his 50 credit point; 2.Put him into blacklist.)
        5. Send email to seller.(The email: 1.Seller may choice the buyer bidding with second max price to trade again;
                                            2.The unpaid buyer has been put into blacklist.)
        6. Send email to new buyer bidding with second max price. (The email: 1. He is the max bidding one now;
                                            2. Seller will trade with you later.)
    """
    return None


def taskForTradeFinished(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every hour.
        Do something, if buyer still click finish trade button on time after 15 days of txn_expiry_date set in system-param table.
        1.
    """
    return None


def jobPayStatus(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every 5 min..
        Check whether buyer pay is complete in case that buyer close the page after pay by paypal.
        In the case, payReturn (url 'paypal_ap_return') is not executed.
    """
    txnViews.jobCheckPayComplete()
