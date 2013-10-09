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