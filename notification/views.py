__author__ = 'Jarvis'

import logging

from django.utils.translation import ugettext as _
from notification import models
from dashboard import models as dashboardModels
from utilities import email
from utilities import common

log = logging.getLogger('email')


def sendRegisterActiveEmail(request, *args, **kwargs):
    """After user register, send the account active link to his email."""
    user = kwargs.get('user')
    if user:
        temp_name = 'register_active'
        link_header = common.getHttpHeader(request)
        token = common.getToken(key='token_length', default=30)
        active_link = '/'.join([link_header, 'usersetting', user.username, 'emails', str(user.id),
                                'register-confirm-verification', token])
        temp_params = [user.username, active_link]
        recipient_list = [user.email]
        sendCommonEmail(temp_name=temp_name, temp_params=temp_params, recipient_list=recipient_list)
    return None


def sendSecurityVerificationEmail(request, *args, **kwargs):
    """After user update email in security setting, send the email verification link to the new email."""
    user = kwargs.get('user')
    if user:
        temp_name = 'email_security_verification'
        link_header = common.getHttpHeader(request)
        token = common.getToken(key='token_length', default=30)
        active_link = '/'.join([link_header, 'usersetting', user.username, 'emails', str(user.id),
                                'email-security-verification', token])
        temp_params = [user.username, active_link]
        recipient_list = [user.email]
        sendCommonEmail(temp_name=temp_name, temp_params=temp_params, recipient_list=recipient_list)
    return None


def sendCommonEmail(*args, **kwargs):
    """Send common email by param setting."""
    temp_name = kwargs.get('temp_name')
    sub_params = kwargs.get('sub_params')
    temp_params = kwargs.get('temp_params')
    from_email = kwargs.get('from_email')
    recipient_list = kwargs.get('recipient_list')
    templates = models.NotificationTemplate.objects.filter(name=temp_name)
    if templates and recipient_list:
        subject = templates[0].subject
        template = templates[0].template
        if sub_params:
            for i in range(len(sub_params)):
                param = ''.join(['{param', str(i+1), '}'])
                subject = subject.replace(param, str(sub_params[i]))
        if temp_params:
            for i in range(len(temp_params)):
                param = ''.join(['{param', str(i+1), '}'])
                template = template.replace(param, str(temp_params[i]))
        email.EmailThread(from_email=from_email, subject=subject, message=template, recipient_list=recipient_list).start()
    else:
        log.error(_('%(param)s does not exist.') % {'param': temp_name})


def tradeNowInformBuyerPayEmail(request, *args, **kwargs):
    """After seller click button 'Trade Now', send email to buyer inform that he won the bidding, and can pay now."""
    app = kwargs.get('app')
    user = kwargs.get('user')
    if app and user:
        temp_name = 'buyer_trade_now'
        link_header = common.getHttpHeader(request)
        app_detail_url = '/'.join([link_header, 'query/app-detail', str(app.id)])
        pay_url = '/'.join([link_header, 'dashboard/my-bidding'])
        temp_params = [user.username, app_detail_url, app.app_name, pay_url]
        recipient_list = [user.email]
        sendCommonEmail(temp_name=temp_name, temp_params=temp_params, recipient_list=recipient_list)
    return None


def closedTradeInform(*args, **kwargs):
    """After buyer close trade, send email to seller that trade is closed."""
    transaction = kwargs.get('transaction')
    if transaction:
        massEmailThread = email.MassEmailThread()
        templates_seller = models.NotificationTemplate.objects.filter(name='closed_trade_inform_seller')
        if templates_seller:
            subject = templates_seller[0].subject
            message = templates_seller[0].template.replace('{param1}', transaction.seller.username)
            recipient_list = [transaction.seller.email]
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=recipient_list)
        templates_buyer = models.NotificationTemplate.objects.filter(name='closed_trade_inform_buyer')
        if templates_buyer:
            subject = templates_buyer[0].subject
            message = templates_buyer[0].template.replace('{param1}', transaction.buyer.username)
            recipient_list = [transaction.seller.email]
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=recipient_list)
        #Notify user when new auctions appear for user's watched categories
        categories = transaction.app.category.all()
        watchCategories = dashboardModels.WatchCategory.objects.filter(category__in=categories)
        templates_watch = models.NotificationTemplate.objects.filter(name='closed_trade_inform_buyer_watched_category')
        for watchCategory in watchCategories:
            if templates_watch:
                subject = templates_watch[0].subject
                message = templates_watch[0].template.replace('{param1}', transaction.buyer.username).replace('{param2}', transaction.app.app_name)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[watchCategory.buyer.email])
        massEmailThread.start()
    return None


def onePriceBuyInformSellerEmail(*args, **kwargs):
    """After seller click button 'Buy It Now with 10 USD', send email to seller inform that he can trade now."""
    transaction = kwargs.get('transaction')
    if transaction:
        temp_name = 'buyer_one_price_inform_seller'
        sub_params = [transaction.buyer.username, transaction.app.app_name]
        temp_params = [transaction.seller.username, transaction.buyer.username, transaction.app.app_name]
        recipient_list = [transaction.app.publisher.username]
        sendCommonEmail(temp_name=temp_name, sub_params=sub_params, temp_params=temp_params, recipient_list=recipient_list)
    return None


def buyerPayInformSellerEmail(*args, **kwargs):
    """After buyer pay, send email to seller inform that buyer has paid, and he can trade now."""
    transaction = kwargs.get('transaction')
    if transaction:
        temp_name = 'buyer_paid_inform_seller'
        sub_params = [transaction.app.app_name]
        temp_params = [transaction.seller.username, transaction.buyer.username, transaction.app.app_name]
        recipient_list = [transaction.app.publisher.username]
        sendCommonEmail(temp_name=temp_name, sub_params=sub_params, temp_params=temp_params, recipient_list=recipient_list)
    return None


def sendResetPasswordEmail(request, *args, **kwargs):
    """Send the email of reset password."""
    user = kwargs.get('user')
    type = kwargs.get('type')
    if user and type:
        header = common.getHttpHeader(request)
        token = common.getToken(key='token_length', default=30)
        url = '/'.join([header, 'usersetting/reset-password', str(type), str(user.id), user.username, token])
        temp_name = 'reset_password_email'
        temp_params = [user.username, url]
        recipient_list = [user.email]
        sendCommonEmail(temp_name=temp_name, temp_params=temp_params, recipient_list=recipient_list)
    return None


def sendNewBidEmail(request, *args, **kwargs):
    """Send email when new bidding."""
    app = kwargs.get('app')
    bid = kwargs.get('bid')
    massEmailThread = email.MassEmailThread()
    templates_seller = models.NotificationTemplate.objects.filter(name='new_bid_inform_seller')
    templates_buyer = models.NotificationTemplate.objects.filter(name='new_bid_inform_buyer')
    item_seller = app.publisher.subscriptionitem_set.filter(key='new_bid')
    if item_seller and templates_seller:
        subject = templates_seller[0].subject
        message = templates_seller[0].template.replace('{param1}', app.publisher.username).replace('{param2}', app.app_name)
        massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
    user_ids = [bid.buyer.id]
    bids = app.bidding_set.exclude(buyer_id=bid.buyer.id)
    for bidding in bids:
        if bidding.buyer.id not in user_ids:
            user_ids.append(bidding.buyer.id)
            item_buyer = bidding.buyer.subscriptionitem_set.filter(key='new_bid_above_mine')
            if item_buyer and templates_buyer:
                subject = templates_seller[0].subject
                message = templates_seller[0].template.replace('{param1}', bidding.buyer.username).replace('{param2}', app.app_name)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[bidding.buyer.email])
    massEmailThread.start()


def sendNewAppEmail(request, *args, **kwargs):
    """Send email to user, when the new app whose publisher watched by user is created."""
    app = kwargs.get('app')
    watchSellers = dashboardModels.WatchSeller.objects.filter(seller_id=app.publisher.id)
    if app and watchSellers:
        massEmailThread = email.MassEmailThread()
        templates = models.NotificationTemplate.objects.filter(name='new_app_inform_buyer')
        for watchSeller in watchSellers:
            if templates:
                subject = templates[0].subject
                message = templates[0].template.replace('{param1}', watchSeller.buyer.username).replace('{param2}', app.app_name)
                massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[watchSeller.buyer.email])
        massEmailThread.start()


def sendNewCommentEmail(request, *args, **kwargs):
    """Send email to seller and buyer, when user add comment."""
    app = kwargs.get('app')
    comment = kwargs.get('comment')
    common_msg = comment.comment
    massEmailThread = email.MassEmailThread()
    if request.user.id != app.publisher.id:
        templates_seller = models.NotificationTemplate.objects.filter(name='new_comment_inform_seller')
        templates_buyer = models.NotificationTemplate.objects.filter(name='new_comment_inform_buyer')
        item_seller = app.publisher.subscriptionitem_set.filter(key='new_comment')
        if item_seller and templates_seller:
            subject = templates_seller[0].subject
            message = templates_seller[0].template.replace('{param1}', app.publisher.username).replace('{param2}', app.app_name)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[app.publisher.email])
    watchApps = dashboardModels.WatchApp.objects.filter(app_id=app.id)
    for watchApp in watchApps:
        if templates_buyer:
            subject = templates_buyer[0].subject.replace('{param1}', app.app_name)
            message = templates_buyer[0].template.replace('{param1}', watchApp.buyer.username).replace('{param2}', app.app_name)
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=[watchApp.buyer.email])
    massEmailThread.start()


def sendNewMessageEmail(request, *args, **kwargs):
    """Send email to seller or buyer, when user send message to seller or buyer."""
    message = kwargs.get('message')
    item_user = message.receiver.subscriptionitem_set.filter(key='private_msg')
    if item_user:
        temp_name = 'new_message_inform_user'
        temp_params = [message.receiver.username]
        recipient_list = [message.receiver.email]
        sendCommonEmail(temp_name=temp_name, temp_params=temp_params, recipient_list=recipient_list)