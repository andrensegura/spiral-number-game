#!/home/sparlor/bin/python
from reddit_connect import r
from spongelog import SpongeLog
from spongedb import *
from playerclass import Player
from itemclass import Item

log = SpongeLog("purchases.log")

# Returns an item name if someone uses /buy
def get_item_from_buy_command(body: str) -> Item:
    if body.startswith('/buy '):
        requested_item_name = body.partition('\n')[0][5:]
        i = Item(requested_item_name)
        return Item(requested_item_name)

# Shows the item is no longer for sale in the post.
def update_sold(post):
    # Gets everything before the inventory section
    body_pretext = post.selftext.split("The Goods",1)[0]
    body_shop_text = """ The Goods
------------------------

## Unlimited Items

Item|Description|Cost|Stock
:--|:--|--:|--:
"""

    stock = db.get_forsale_unlimited()
    for i in stock:
        body_shop_text += f"{i['name']}|{i['description']}|{i['price']} o|{i['stock']}\n"

    body_shop_text += """

## Limited Items

Item|Description|Cost|Stock
:--|:--|--:|--:
""" 

    # Update the entire store with the current stock.
    # Cross out the item name if it's not available.
    stock = db.get_forsale()
    # sort stock by price
    stock.sort(key = lambda i: i['price'], reverse = True)
    # put out of stock items at bottom of list
    instock = [x for x in stock if x['stock'] > 0]
    nonstock = [x for x in stock if x['stock'] == 0]
    stock = instock + nonstock

    # create md format and cross out out of stock items.
    for i in stock:
        # need a copy of the name
        item_name = i['name']
        if i['stock'] == 0:
            item_name = f"~~{i['name']}~~"
        body_shop_text += f"{item_name}|{i['description']}|{i['price']} o|{i['stock']}\n"

    body_full = body_pretext + body_shop_text
    post.edit(body=body_full)

def is_on_banlist(username):
    with open('banlist.txt', 'r') as banlist:
        if str(username) in [str(x.strip()) for x in banlist.readlines()]:
            return True
        else:
            return False

# banlist just keeps track of who has made a purchase this week.
# It keeps users from buying multiple items. Perhaps this could
# be kept in the database, instead of a flat file.
def add_to_banlist(username):
    with open('banlist.txt', 'a') as banlist:
       banlist.write(username + '\n') 

# This could also probably be a database value.
post = ''
with open('store_id.txt', 'r') as file:
    sub_id = file.readline()
    post = r.submission(id=sub_id)

# Creates a queue of items and processes them after.
purchase_requests = []
post.comments.replace_more(limit=None)
for comment in post.comments.list():
    try:
        item = get_item_from_buy_command(comment.body)
        # None returned the comment doesn't start with /buy
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
# Need to include logging for this. Would be easy to add.
db = SpongeDB()
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

        if db.is_comment_added(comment_id):
            continue
        if item.is_limited and is_on_banlist(buyer.name):
            db.add_comment(comment_id)
            db.save()
            r.comment(comment_id).reply("> You've already purchased a limited item.") 
            log.info(f"User already made limited purchase: {buyer_name}")
            continue


        buyer.buy(item)
        buyer.save()
        item.save()

        r.comment(comment_id).reply(f"> Purchase of '{item.name}' Successful!")
        log.info(f"Item purchased successfully: {buyer.name}, {item.name}")

        db.add_comment(comment_id)

        if item.is_limited:
            add_to_banlist(buyer.name)
    
    except (OutOfStockError, ItemNonexistantError, NotEnoughSudsError, NotForSaleError) as error:
        r.comment(comment_id).reply(f"> {error}")

    db.add_comment(comment_id)
    db.save()

update_sold(post)
