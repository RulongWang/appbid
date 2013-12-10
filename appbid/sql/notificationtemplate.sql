insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('register_active',1,1,'The active account email for register from AppsWalk','Hi {param1},\n\r Please click the blow link to active your account \n\r {param2}','active account email','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('email_security_verification',1,1,'The security verification email for new email from AppsWalk','Hi {param1},\n\r Please click the blow link to verify your new email \n\r {param2}','The security verification email for new email.','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('buyer_trade_now',1,1,'The paid email of {param1} you won from AppsWalk','Hi {param1},\n\r Congratulation for your won bidding of <a href="{param2}">{param3}</a>.\n\r Now you can pay by the link:\n\r {param4}','Buyer pay email.','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('buyer_paid_inform_seller',1,1,'Your app {param1} from AppsWalk','Hi {param1},\n\r User {param2} won bidding has been paid. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('buyer_one_price_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('closed_trade_inform_buyer',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('closed_trade_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('verified_app_success_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('verified_app_failed_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('service_end_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('unsold_end_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('reset_password_email',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

#New template name
#name = 'buyer_unpaid_inform_buyer'
#name = 'buyer_unpaid_inform_seller'
#name = 'buyer_unpaid_inform_second_buyer'
#name = 'buyer_unpaid_inform_seller_no_bidding'
#name = 'service_end_inform_seller_lt_reserve_price'
#name = 'new_bid_inform_seller'
#name = 'new_bid_inform_buyer' -> 'Notify me when a bid is placed above one of my bids'
#name = 'new_app_inform_buyer'
#name = 'new_comment_inform_seller'
#name = 'new_comment_inform_buyer'
#name ='closed_trade_inform_buyer_watched_category'