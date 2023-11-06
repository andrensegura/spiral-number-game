#!/home/sparlor/bin/python
from reddit_connect import r
from spongeconfig import SHOPS
from spongelog import SpongeLog
from spongedb import *
from playerclass import Player
from itemclass import Item
import importlib
import sys
sys.path.append('shops')

log = SpongeLog("purchases.log")

# Returns an item name if someone uses /buy
def get_item_from_buy_command(body: str, shop) -> Item:
    if body.startswith('/buy '):
        requested_item_name = body.partition('\n')[0][5:]
        i = Item(requested_item_name)
        for shop_item in shop.inventory:
            if i.name == shop_item.name:
                return shop_item

def add_comment(comment_id):
    db = SpongeDB()
    db.add_comment(comment_id)
    db.save()
    db.close()
    del(db)

def is_comment_added(comment_id):
    db = SpongeDB()
    answer = db.is_comment_added(comment_id)
    db.close()
    del(db)
    return answer

for shop_name in SHOPS:
    shop_module = importlib.import_module(f"{shop_name}")
    shop = shop_module.shop

    shop_post = r.submission(id=shop._submission_id)

    # Creates a queue of items and processes them after.
    purchase_requests = []
    shop_post.comments.replace_more(limit=None)
    for comment in shop_post.comments.list():
        try:
            if is_comment_added(comment.id):
                continue
            item = get_item_from_buy_command(comment.body, shop)
            # None returned means the comment doesn't start with /buy
            # or item isn't in the shop
            if not item:
                continue
            purchase_requests.append({'item': item,
                                 'buyer_name': comment.author.name,
                                 'comment_id': comment.id
                                 }
                            )
        except ItemNonexistantError:
            continue

    # Processes the queue created earlier
    for purchase in purchase_requests:
        item = purchase['item']
        buyer_name = purchase['buyer_name']
        comment_id = purchase['comment_id']
    
        buyer = ''
        try:
            buyer = Player(buyer_name)
        except NoSuchPlayerError:
            buyer = NewPlayer(buyer_name)

        try:
            buyer = Player(buyer_name)
    
            if item.is_limited and shop.is_banned(buyer.name):
                add_comment(comment_id)
                r.comment(comment_id).reply("> You've already purchased a limited item.") 
                log.info(f"User already made limited purchase: {buyer_name}")
                continue

            buyer.buy(item)
            buyer.save()
            item.save()

            r.comment(comment_id).reply(f"> Purchase of '{item.name}' Successful!")
            log.info(f"Item purchased successfully: {buyer.name}, {item.name}")
    
            if item.is_limited:
                shop.ban(buyer.name)
    
        except (OutOfStockError, ItemNonexistantError, NotEnoughSudsError, NotForSaleError) as error:
            r.comment(comment_id).reply(f"> {error}")

        add_comment(comment_id)

    shop.update_post()
