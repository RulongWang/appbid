

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('verified_app_success_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('verified_app_failed_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('service_end_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);

insert into notification_notificationtemplate(`name`,`language`,`type`,`subject`,`template`,`description`,`version`,`create_time`,`last_modify`,`modifier_id`)
values('unsold_end_inform_seller',1,1,'{param1} has bought your app {param2} from AppsWalk','Hi {param1},\n\r User {param2} has bought your app {param3}. You can begin to delivery your content to buyer now.','Tell seller after buyer paid..','1.0',now(),now(),1);


#New template name
#name = 'buyer_unpaid_inform_buyer'
#name = 'buyer_unpaid_inform_seller'
#name = 'buyer_unpaid_inform_second_buyer'
#name = 'buyer_unpaid_inform_seller_no_bidding'
#name = 'service_end_inform_seller_lt_reserve_price'
#name = 'new_bid_inform_seller'
#name = 'new_bid_inform_buyer' -> 'Notify me when a bid is placed above one of my bids'