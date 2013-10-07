__author__ = 'Jarvis'


def checkServiceDateForApps(*args, **kwargs):
    """
        The task will be done every night at midnight.
        Do something, when the app service date is ending.
        1. App status will be changed from published to closed.
        2. Send email of expiry date to seller.(The email: 1.Service end; 2.Seller can trade now.)
    """
    return None


def taskForBuyUnpaid(*args, **kwargs):
    """
        The task will be done in at schedule time, such as: every hour.
        Do something, if buy unpaid on time after 7 days of paid_expiry_date set in system-param table.
        1. Buyer will be subtracted 50 credit point, and put into blacklist.
        2. Buyer's all bidding status is changed from approved to rejected.(Note: All bidding for this buyer.)
        3. For transaction data, status be changed from Unpaid to Unsold, and set buyer, price, end_time to None.
          (Invoke initTransaction method.)
        4. Send email to buyer.(The email: 1.Subtract his 50 credit point; 2.Put him into blacklist.)
        5. Send email to seller.(The email: 1.Seller may choice the buyer bidding with second max price to trade again;
                                            2.The unpaid buyer has been put into blacklist.)
        6. Send email to new buyer bidding with second max price. (The email: 1. He is the max bidding one now;
                                            2. Seller will trade with you later.)
    """
    return None
