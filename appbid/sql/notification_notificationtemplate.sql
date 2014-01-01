INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('seller_remind_buyer_pay', 1, 1, 'Payment reminder for auction of {param1}', 'Dear {param1},
This is the reminder email from seller, since you are the winner of {param2}, you need to pay seller according to the deal agreement.Thank you very much for your cooperation.

Thanks
Appswalk Ltd. ', 'seller_remind_buyer_pay', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:35:42', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('register_active', 1, 1, 'Please activate your Appswalk account', 'Dear {param1},

Please copy the blow link to your browser and active your account

{param2}

Thanks
Appswalk Ltd. ', 'active account email', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:35:42', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('email_security_verification', 1, 1, 'Appswalk email verification', 'Dear {param1},

Please copy the blow link to your browser and verify your new email

{param2}

Thanks
Appswalk Ltd. ', 'The security verification email for new email.', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:34:20', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('seller_trade_now', 1, 1, 'Congratulations for your bidding at Appswalk', 'Dear {param1},

Congratulations! You are the winner of the auction {param2}.

Now you can pay the money to the seller by the following link:

{param3}

Thanks
Appswalk Ltd. ', 'Buyer pay email after seller click trade now', '1.0', '2013-12-08 20:11:12', '2013-12-11 22:55:23', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('buyer_paid_inform_seller', 1, 1, 'Please start to transfer your app to { param1 }', 'Dear {param1},

{param2} already paid you for app {param3} with Paypal. You should start to deliver everything to the buyer {param2} as you claimed on Appswalk.
This transaction is guaranteed  by Paypal.
Thanks
Appswalk Ltd. ', 'Tell seller after buyer paid..', '1.0', '2013-12-08 20:11:12', '2013-12-11 22:57:16', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('buyer_one_price_inform_seller', 1, 1, '{param1} decised to buy your app {param2} from AppsWalk', 'Dear  {param1},

User {param2} has bought your app {param3} via ''Buy it now''. You should start to deliver everything to {param2} as you claimed on Appswalk.
This transaction is guaranteed by Paypal.
Thanks
Appswalk Ltd. ', 'Tell seller after buyer paid..', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:33:39', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('closed_trade_inform_buyer', 1, 1, 'The app transaction is completed', 'Dear {param1},

Your app transaction is completed, for more details please logon to  www.appswalk.com.

Thanks
Appswalk Ltd. ', 'Tell seller after buyer paid..', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:41:03', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('closed_trade_inform_seller', 1, 1, 'The app transaction is completed', 'Dear {param1},

Your app transaction is completed, for more details please logon to  www.appswalk.com.

Thanks
Appswalk Ltd. ', 'Tell seller after buyer paid..', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:56:26', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('verified_app_success_inform_seller', 1, 1, 'Congratulations! Your ownership of app {param1} has been verified.', 'Dear {param1},

We are happy to inform you that your app {param2} has been verified at Appswalk.
Please kindly logon to appswalk.com , and check your account details.
The last step is to finish your payment for your listing, and then your app could be listed on Appswalk.
Thank you very much.
Appswalk Ltd', 'Tell seller after buyer paid..', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:47:38', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('verified_app_failed_inform_seller', 1, 1, 'Failed to validate your ownership of app {param1} ', 'Dear {param1},

We are not able to verify your ownership of app {param2} . Please ensure if have copied and pasted the verification code at your app description on AppleStore.
If you meet any difficulty , please kindly send a message to us via support@appswalk.com
Thank you very much.
Appswalk Ltd
', 'Tell seller after buyer paid..', '1.0', '2013-12-08 20:11:12', '2013-12-08 22:44:26', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('service_end_inform_seller', 1, 1, 'You need to start the transaction with your auction winner {param1}', 'Dear {param1},

Your listing of app {param2} has already ended, you need to start the transaction with your auction winner within 7 days, otherwise your credit points will be deducted. Please logon on www.appswalk.com and check details.
Thank you very much.
Appswalk Ltd', 'The bidding price exceed  the reservce price, and listing finished and after 7 days , The seller didn''t start the transaction with the buyer. ', '1.0', '2013-12-08 20:11:12', '2013-12-11 23:12:03', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('unsold_end_inform_seller', 1, 1, 'Need your action immediately ', 'Dear {param1},

7days has passed, however you didn''t start any transaction with you buyer yet. As an agreement {param2} points will be deducted from your account. And you can also start your transaction right now.
Regards,
Appswalk Ltd', '7days passed, but the seller didn''t start the transaction , credit points deducted', '1.0', '2013-12-08 20:11:12', '2013-12-11 23:21:25', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('reset_password_email', 1, 1, 'Your Appswalk Password has been reset', 'Dear  {param1},

please go to {param2} to reset your password immediately. Then review and update your security settings at www.appswalk.com
Thanks,
Apple Customer Support
', 'reset notification email', '1.0', '2013-12-08 20:11:12', '2013-12-11 23:22:38', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('buyer_unpaid_inform_second_buyer', 1, 1, 'The seller decided to make deal with you', 'Dear ｛param1},
Glad to tell you, you are the winner of the {param2} auction. Now you can pay the seller, after the payment.
The seller should start to deliver everything he/she claimed on Appswalk.
Regards,
Appswalk Ltd', 'buyer_unpaid_inform_second_buyer,
Seller choose the second bidder for the transaction', '1.0', '2013-12-09 21:38:18', '2013-12-11 23:24:17', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('buyer_unpaid_inform_seller_no_bidding', 1, 1, 'Failed to sell your app ', 'Dear {param1},
We are so sorry, you really meet a fraud buyer, he/she didn''t pay the money, we have already put him/her as a fraud. He/she will never be allowed to make deal on Appswalk.
Unfortunately, the bidder is the only one for your auction, so we are not able to help you select a second bidder.
Now you can re-list your app and start a new auction on Appswalk.
Best regards,
Appswalk Ltd', 'This auction only has one bidder , and this bidder didn\'t pay the money.', '1.0', '2013-12-09 21:50:44', '2013-12-11 23:25:05', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('buyer_unpaid_inform_buyer', 1, 1, 'Your attention please', 'Dear {param1},
You didn''t comply our transaction guide, you credit points has been deducted to Zero. Which means you are not allowed to do any other deal on Appswalk.
Any confusing please send email to support@appswalk.com
Regards,
Appswalk Ltd', '', '1.0', '2013-12-10 22:14:49', '2013-12-11 23:26:26', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('buyer_unpaid_inform_seller', 1, 1, 'Information from Appswalk', 'Dear {param1},
The buyer {param2} didn''t pay you the auction money. We have already take that account as fraud.
Now you can start your new transaction with your second buyer.
Please logon to www.appswalk.com and start your new transaction.
Regards,
Appswalk Ltd', '', '1.0', '2013-12-10 22:18:03', '2013-12-11 23:26:52', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('service_end_inform_seller_lt_reserve_price', 1, 1, 'Need your action on your listing of app {param1}', 'Dear {param1},
The bidding price doesn''t reach your reserved price.  However you can start your transaction with your buyer who placed the highest price.
Please logon to www.appswalk.com for more details.
Regards,
Appswalk Ltd', 'Service end, and reserve price not reach, seller can start the transaction', '1.0', '2013-12-10 22:18:29', '2013-12-11 23:14:56', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('new_bid_inform_seller', 1, 1, 'Your auction  just got a new bidding', 'Dear {param1},
 Your auction of app {param2} just got a new bidding. Please logon to www.appswalk.com for more details.
 Regards,
 Appswalk Ltd', '', '1.0', '2013-12-10 22:18:56', '2013-12-11 23:27:43', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('new_bid_inform_buyer', 1, 1, 'Your bidding price has been exceeded', 'Dear {param1},
Other bidder just placed a new price for the app {param2}. You can place a higher price there.
Regards,
Appswalk Ltd', 'Notify me when a bid is placed above one of my bids', '1.0', '2013-12-10 22:20:29', '2013-12-11 23:32:29', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('new_comment_inform_seller', 1, 1, 'You got a new comment ', 'Dear {param1},
You just got a new comment regarding your auction {param2}.
Please login www.appswalk.com ,and check comment details.
Best regards,
Appswalk Ltd', 'Inform seller there is new comment from buyer', '1.0', '2013-12-13 14:59:29', '2013-12-13 14:59:29', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('new_comment_inform_buyer', 1, 1, 'There is a new comment on APP {param1}', 'Dear {param1},
There is a new comment on APP {param1} at Appswalk, please login and check details.
Best regards,
Appswalk Ltd', 'Seller replied buyer, inform buyer', '1.0', '2013-12-13 15:01:47', '2013-12-13 15:01:47', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('closed_trade_inform_buyer_watched_category', 1, 1, 'There is new auction in your watching category', 'Dear {param1},
There is new auction {param2} in your watching category, please login and check details.
Best regards,
Appswalk Ltd', 'Newlisting at watching category, inform buyer', '1.0', '2013-12-13 15:06:19', '2013-12-13 15:06:19', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('new_app_inform_buyer', 1, 1, 'Your watching seller just list a new APP', 'Dear {param1},
Your watching seller just list a new APP {param2} on Appswalk
Best regards,
Appswalk Ltd', 'Your watching seller just list a new APP', '1.0', '2013-12-13 15:10:16', '2013-12-13 15:10:16', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('new_message_inform_user', 1, 1, 'There is a new message in your Appswalk Inbox', 'Dear {param1},
There is a new message in your Appswalk Inbox , please login and check details.
Best regards,
Appswalk Ltd', 'Your get the private message', '1.0', '2013-12-13 15:10:16', '2013-12-13 15:10:16', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('txn_remind_seller', 1, 1, 'Reminder for your app {param1} delivery', 'Dear {param1},
{param2} days passed. Kindly reminder you that you should deliver/transfer your app {param3} to your buyer. Otherwise the buyer could revoke his/her payment from Paypal. And at the meanwhile your account would be put into the blacklist forever.
Best regards,
Appswalk Ltd.', '', '1.0', '2013-12-31 20:17:51', '2013-12-31 20:17:51', 1);
INSERT INTO appbid.notification_notificationtemplate (name, language, type, subject, template, description, version, create_time, last_modify, modifier_id) VALUES ('pay_remind_buyer', 1, 1, 'Kind reminder for the payment of app {param1} ', 'Dear {param1},
{param2} days passed, but you didn''t pay any money to the app seller. Please be notice that you already agree the transaction terms before you place the bid.  
Please be careful about your credit points in Appswalk which is very important for you. Without enough credit points, you can not do any business with your partner or the other developers.
Best regards,
Appswalk Ltd', '', '1.0', '2013-12-31 21:20:32', '2013-12-31 21:20:32', 1);