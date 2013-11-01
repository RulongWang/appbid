__author__ = 'Jarvis'

from django.conf.urls import patterns, url
from transaction import views


urlpatterns = patterns('',
    url(r'^trade-now/(?P<app_id>\d+)/(?P<buyer_id>\d+)/(?P<bid_id>\d+)', views.tradeNow, name='trade_now'),
    url(r'^trade-action/(?P<action>\w+)/(?P<app_id>\d+)/(?P<user_id>\d+)', views.tradeAction, name='trade_action'),
    url(r'^closed-trade/(?P<txn_id>\d+)/(?P<buyer_id>\d+)', views.closedTrade, name='closed_trade'),

    url(r'^one-price-buy/(?P<app_id>\d+)/(?P<publisher_id>\d+)$', views.onePriceBuy,
        #The needed operation method in pay.
        {'executeMethod': views.updateTransaction,
        }, name='one_price_buy'),
    url(r'^buyer-pay/(?P<app_id>\d+)/(?P<txn_id>\d+)/(?P<token>\w{30})$', views.buyerPay,
        #The needed operation method in pay.
        {'executeMethod': views.updateTransaction,
        }, name='buyer_pay'),
)
