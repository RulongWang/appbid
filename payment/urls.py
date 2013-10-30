__author__ = 'Jarvis'

from django.conf.urls import patterns, url

from payment import views
#Actual business views
from order import views as orderViews
from transaction import views as txnViews

urlpatterns = patterns('',
    # url(r'^payment/(?P<app_id>\d+)/(?P<service_id>\d+)/(?P<service_sn>\d+)$', views.payment,
    #     #The needed operation in payment.
    #     {'executeMethod': orderViews.updateServiceDetail,
    #     },name='payment'),
    url(r'^paypal_return/$', views.payPalReturn,
        #Show the list of service detail to user.
        {'executeMethod': orderViews.getServiceDetail,
        }, name='paypal_return'),
    url(r'^paypal_checkout/$', views.payPalDoCheckOut,
        #After payment, do something for actual business.
        {'executeMethod': orderViews.executeCheckOut,
        }, name='paypal_checkout'),
    url(r'^paypal_cancel/$', views.paymentCancel, name='paypal_cancel'),

    url(r'^buynow/$', views.start_paypal_ap, name='buynow'),
    url(r'^paypal_ap_return/$', views.paypal_ap_return,
        #After buyer payed or one price buy, do something for actual business.
        {'executeMethod': txnViews.executePay,
        }, name='paypal_ap_return'),
)