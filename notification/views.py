__author__ = 'Jarvis'


from notification import models
from utilities import email
from utilities import common


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
        sendCommonEmail(request, temp_name=temp_name, temp_params=temp_params, recipient_list=recipient_list)
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
        sendCommonEmail(request, temp_name=temp_name, temp_params=temp_params, recipient_list=recipient_list)
    return None


def sendCommonEmail(request, *args, **kwargs):
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
                subject = subject.replace(param, sub_params[i])
        if temp_params:
            for i in range(len(temp_params)):
                param = ''.join(['{param', str(i+1), '}'])
                template = template.replace(param, temp_params[i])
        email.EmailThread(from_email=from_email, subject=subject, message=template, recipient_list=recipient_list).start()
    else:
        #TODO: Log error
        print 'No template'


def tradeNowInformBuyerPayEmail(request, *args, **kwargs):
    """After seller click button 'Trade Now', send email to buyer inform that he won the bidding, and can pay now."""
    app = kwargs.get('app')
    user = kwargs.get('user')
    if app and user:
        temp_name = 'buyer_trade_now'
        sub_params = [app.app_name]
        link_header = common.getHttpHeader(request)
        app_detail_url = '/'.join([link_header, 'query/app-detail', str(app.id)])
        pay_url = '/'.join([link_header, 'dashboard/my-bidding'])
        temp_params = [user.username, app_detail_url, app.app_name, pay_url]
        recipient_list = [user.email]
        sendCommonEmail(request, temp_name=temp_name, sub_params=sub_params, temp_params=temp_params, recipient_list=recipient_list)
    return None


def closedTradeInform(request, *args, **kwargs):
    """After buyer close trade, send email to seller that trade is closed."""
    transaction = kwargs.get('transaction')
    if transaction:
        massEmailThread = email.MassEmailThread()
        templates = models.NotificationTemplate.objects.filter(name='')
        if templates:
            subject = ''
            message = ''
            recipient_list = [transaction.seller.email]
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=recipient_list)
        templates = models.NotificationTemplate.objects.filter(name='')
        if templates:
            subject = ''
            message = ''
            recipient_list = [transaction.seller.email]
            massEmailThread.addEmailData(subject=subject, message=message, recipient_list=recipient_list)
        massEmailThread.start()
    return None


def onePriceBuyInformSellerEmail(request, *args, **kwargs):
    """After seller click button 'Buy It Now with 10 USD', send email to seller inform that he can trade now."""
    transaction = kwargs.get('transaction')
    if transaction:
        temp_name = 'buyer_one_price_inform_seller'
        sub_params = [transaction.buyer.username, transaction.app.app_name]
        temp_params = [request.user.username, transaction.buyer.username, transaction.app.app_name]
        recipient_list = [transaction.app.publisher.username]
        sendCommonEmail(request, temp_name=temp_name, sub_params=sub_params, emp_params=temp_params, recipient_list=recipient_list)
    return None


def buyerPayInformSellerEmail(request, *args, **kwargs):
    """After buyer pay, send email to seller inform that buyer has paid, and he can trade now."""
    transaction = kwargs.get('transaction')
    if transaction:
        temp_name = 'buyer_paid_inform_seller'
        sub_params = [transaction.app.app_name]
        temp_params = [transaction.app.app_name, transaction.buyer.username]
        recipient_list = [transaction.app.publisher.username]
        sendCommonEmail(request, temp_name=temp_name, sub_params=sub_params, temp_params=temp_params, recipient_list=recipient_list)
    return None