__author__ = 'Jarvis'

import string
import datetime
import logging

from django.db.models import Max, Q

from appbid import models as appModels
from notification import models as notificationModels
from transaction import models as txnModels
from bid import models as bidModels
from utilities import common, email
from credit import views as creditViews
from transaction import views as txnViews


log = logging.getLogger('appbid')

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
                subject = templates[0].subject.replace('{param1}', app.app_name)
                message = templates[0].template.replace('{param1}', app.publisher.username).replace('{param2}', app.app_name)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
                ownerShipScan.delete()
                #Update app is_verified value
                app.is_verified = True
                app.save()
        else:
            ownerShipScan.times += 1
            ownerShipScan.save()
            templates = notificationModels.NotificationTemplate.objects.filter(name='verified_app_failed_inform_seller')
            if ownerShipScan.times == 3 and templates:
                subject = templates[0].subject.replace('{param1}', app.app_name)
                message = templates[0].template.replace('{param1}', app.publisher.username).replace('{param2}', app.app_name)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
    massEmailThread.start()

    return None


def checkServiceDateForApps(*args, **kwargs):
    """
        The task will be done every hour.
        Do something, when the app service date is ending.
        1. App status will be changed from published to closed.
        2. Send email of expiry date to seller.(The email: 1.Service end; 2.Seller can trade now.)
    """
    # current_date = datetime.datetime.combine(datetime.date.today(), datetime.time())
    # next_date = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time())
    # apps = appModels.App.objects.filter(status=2, end_date__gte=current_date, end_date__lt=next_date)
    apps = appModels.App.objects.filter(status=2, end_date__lte=datetime.datetime.now())
    massEmailThread = email.MassEmailThread()
    for app in apps:
        app.status = 3
        app.save()
        max_price = app.bidding_set.filter(status=1).aggregate(Max('price'))
        current_price = max_price.get('price__max', 0)
        #If bidding price is more than max price, seller has 7 days to trade or else seller can not trade it.
        if app.reserve_price and app.reserve_price <= current_price:
            bids = bidModels.Bidding.objects.filter(app_id=app.id, price=current_price, status=1)
            transactions = app.transaction_set.filter(is_active=True)
            if transactions:
                transaction = transactions[0]
            else:
                transaction = txnModels.Transaction()
                transaction.status = 1
                transaction.app = app
                transaction.is_active = True
            paid_expiry_date = string.atoi(common.getSystemParam(key='sell_expiry_date', default=7))
            transaction.end_time = app.end_date + datetime.timedelta(days=paid_expiry_date)
            transaction.save()

            transactionsLog = txnModels.TransactionLog()
            transactionsLog.transaction = transaction
            transactionsLog.app = app
            transactionsLog.status = 1
            transactionsLog.save()
            templates = notificationModels.NotificationTemplate.objects.filter(name='service_end_inform_seller')
            if templates:
                subject = templates[0].subject.replace('{param1}', bids[0].buyer.username)
                message = templates[0].template.replace('{param1}', app.publisher.username).replace('{param2}', app.app_name)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
        else:
            templates = notificationModels.NotificationTemplate.objects.filter(name='service_end_inform_seller_lt_reserve_price')
            if templates:
                subject = templates[0].subject.replace('{param1}', app.app_name)
                message = templates[0].template.replace('{param1}', app.publisher.username)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
    massEmailThread.start()
    return None


def checkIfSellApp(*args, **kwargs):
    """
        The task will be done every hour.
        When service stop, if bidding price is more than max price, seller has 7 days to trade now. Then seller did not
        trade app in 7 days, seller's credit points will be decreased.
    """
    transactions = txnModels.Transaction.objects.filter(status=1, end_time__isnull=False, end_time__lte=datetime.datetime.now())
    massEmailThread = email.MassEmailThread()
    points = common.getSystemParam(key='cp_buyer_unpaid', default=50)
    log.info("----")
    for transaction in transactions:
        log.info(transaction.id)
        #Decrease seller's credit points
        creditViews.decreaseCreditPoint(user=transaction.seller, point=string.atoi(points), type=1, ref_id=transaction.id)
        templates = notificationModels.NotificationTemplate.objects.filter(name='unsold_end_inform_seller')
        if templates:
            subject = templates[0].subject
            message = templates[0].template.replace('{param1}', transaction.seller.username).replace('{param2}', points)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[transaction.seller.email])
    massEmailThread.start()
    return None


def sendMailForRemind(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every hour.
        1. The paid_expiry_date set in system-param table is 7 days.
           If buyer does not pay, will send email to buyer in remain 4, 2, 1 days.
        2. The txn_expiry_date set in system-param table is 15 days.
           If buyer does not finish trade, will send email to buyer in remain 7, 4 days.
    """
    massEmailThread = email.MassEmailThread()
    seven_next_date = datetime.datetime.now() + datetime.timedelta(days=7)
    four_next_date = datetime.datetime.now() + datetime.timedelta(days=4)
    two_next_date = datetime.datetime.now() + datetime.timedelta(days=2)
    one_next_date = datetime.datetime.now() + datetime.timedelta(days=1)

    remind_template = notificationModels.NotificationTemplate.objects.filter(name='pay_remind_buyer')
    if remind_template:
        fourTxn = txnModels.Transaction.objects.filter(status=2, is_active=True, end_time__year=four_next_date.year, end_time__month=four_next_date.month, end_time__day=four_next_date.day)
        for txn in fourTxn:
            subject = remind_template[0].subject.replace('{param1}', txn.app.app_name)
            message = remind_template[0].template.replace('{param1}', txn.buyer.username).replace('{param2}', 4)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[txn.buyer.email])
        twoTxn = txnModels.Transaction.objects.filter(status=2, is_active=True, end_time__year=two_next_date.year, end_time__month=two_next_date.month, end_time__day=two_next_date.day)
        for txn in twoTxn:
            subject = remind_template[0].subject.replace('{param1}', txn.app.app_name)
            message = remind_template[0].template.template.replace('{param1}', txn.buyer.username).replace('{param2}', 2)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[txn.buyer.email])
        oneTxn = txnModels.Transaction.objects.filter(status=2, is_active=True, end_time__year=one_next_date.year, end_time__month=one_next_date.month, end_time__day=one_next_date.day)
        for txn in oneTxn:
            subject = remind_template[0].subject.replace('{param1}', txn.app.app_name)
            message = remind_template[0].template.template.replace('{param1}', txn.buyer.username).replace('{param2}', 1)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[txn.buyer.email])

    remind_template = notificationModels.NotificationTemplate.objects.filter(name='txn_remind_seller')
    if remind_template:
        sevenTxn = txnModels.Transaction.objects.filter(status=3, is_active=True, end_time__year=seven_next_date.year, end_time__month=seven_next_date.month, end_time__day=seven_next_date.day)
        for txn in sevenTxn:
            subject = remind_template[0].subject.replace('{param1}', txn.app.app_name)
            message = remind_template[0].template.template.replace('{param1}', txn.seller.username).replace('{param2}', 7).replace('{param3}', txn.app.app_name)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[txn.buyer.email])
        fourTxn = txnModels.Transaction.objects.filter(status=3, is_active=True, end_time__year=four_next_date.year, end_time__month=four_next_date.month, end_time__day=four_next_date.day)
        for txn in fourTxn:
            subject = remind_template[0].subject.replace('{param1}', txn.app.app_name)
            message = remind_template[0].template.template.replace('{param1}', txn.seller.username).replace('{param2}', 4).replace('{param3}', txn.app.app_name)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[txn.buyer.email])
    massEmailThread.start()
    return None


def taskForBuyUnpaid(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every hour.
        Do something, if buy still unpaid after 7 days of paid_expiry_date set in system-param table.
        1. Change transaction is_active from True to False.
        2. Buyer will be subtracted 50 credit point, and put into blacklist.
        3. Buyer's all bidding status is changed from approved to rejected.(Note: All bidding for this buyer.)
        4. Send email to buyer.(The email: 1.Subtract his 50 credit point; 2.Put him into blacklist.)
        5. Send email to seller.(The email: 1.Seller may choice the buyer bidding with second max price to trade again;
                                            2.The unpaid buyer has been put into blacklist.)
        6. Send email to new buyer bidding with second max price. (The email: 1. He is the max bidding one now;
                                            2. Seller will trade with you later.)
    """
    points = string.atoi(common.getSystemParam(key='cp_no_closed_trade', default=50))
    templates_buyer = notificationModels.NotificationTemplate.objects.filter(name='buyer_unpaid_inform_buyer')
    templates_seller = notificationModels.NotificationTemplate.objects.filter(name='buyer_unpaid_inform_seller')
    templates_second_buyer = notificationModels.NotificationTemplate.objects.filter(name='buyer_unpaid_inform_second_buyer')
    templates_seller_no_bidding = notificationModels.NotificationTemplate.objects.filter(name='buyer_unpaid_inform_seller_no_bidding')

    transactions = txnModels.Transaction.objects.filter(is_active=True, status=2, end_time__lte=datetime.datetime.now())
    massEmailThread = email.MassEmailThread()
    for transaction in transactions:
        transaction.is_active = False
        transaction.save()
        creditViews.decreaseCreditPoint(user=transaction.buyer, point=points, type=1, ref_id=transaction.id)
        bidModels.Bidding.objects.filter(app_id=transaction.app.id, buyer_id=transaction.buyer.id).update(status=False)
        if templates_buyer:
            subject = templates_buyer[0].subject
            message = templates_buyer[0].template.replace('{param1}', transaction.buyer.username)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[transaction.buyer.email])
        bidding = bidModels.Bidding.objects.filter(app_id=transaction.app.id, status=1).order_by('-price')
        if bidding:
            if templates_seller:
                subject = templates_seller[0].subject
                message = templates_seller[0].template.replace('{param1}', transaction.seller.username).replace('{param2}', transaction.buyer.username)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[transaction.seller.email])
            if templates_second_buyer:
                subject = templates_second_buyer[0].subject
                message = templates_second_buyer[0].template.replace('{param1}', bidding[0].buyer.username).replace('{param2}', transaction.app.app_name)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[bidding[0].buyer.email])
        else:
            if templates_seller_no_bidding:
                subject = templates_seller_no_bidding[0].subject
                message = templates_seller_no_bidding[0].template.replace('{param1}', transaction.seller.username)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[transaction.seller.email])
    massEmailThread.start()

    return None


def jobPayStatus(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every 5 min..
        Check whether buyer pay is complete in case that buyer close the page after pay by paypal.
        In the case, payReturn (url 'paypal_ap_return') is not executed.
    """
    txnViews.jobCheckPayComplete()
