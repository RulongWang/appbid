appbid
======
Private project

Prerequisites
Python 2.7
Django 1.5
MySQL 5.0
MySQL-python, yum install MySQL-python
PIL (1.1.7), download URL:http://www.pythonware.com/products/pil/
django-social-auth (0.7.28), download URL:https://pypi.python.org/pypi/django-social-auth

//sanbox paypal testing account
username: me_api1.rulong.org
API Password: 1380869543
Signature:A2vypYAyoKWCr5HKJHXEzqAil0rBANhDLrGYeKZ-H8Wjmb.OShNvkwhY

sudo easy_install pip


nohup uwsgi --ini appbid.ini&

Kill -INT PID

$ mysqladmin -u root -p'oldpassword' password newpass


Adaptive payment application ID:

Sandbox ID:APP-80W284485P519543T
Live App ID:APP-5RW64647DB339963H
/*************************************
development api
https://developer.paypal.com/webapps/developer/docs/classic/adaptive-payments/gs_AdaptivePayments/

Adaptive Payments
JSON, NVP, SOAP, XML
AppID	https://svcs.paypal.com/AdaptivePayments/{API_operation}
https://svcs.sandbox.paypal.com/AdaptivePayments/{API_operation}

redirect to confirm page:
https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=AP-2US53783SG376864S

configure https:
http://blog.creke.net/762.html


#installed     'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
need run command: python manage.py migrate
