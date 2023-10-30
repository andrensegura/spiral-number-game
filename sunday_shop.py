#!/home/sparlor/bin/python
from reddit_connect import r
from spongedb import SpongeDB
from spongeconfig import R_SUBREDDIT
from playerclass import Player
from itemclass import Item

db = SpongeDB()

# RESET CUSTOM FLAIR
custom_flair = Item('custom flair')
if custom_flair.ownedby():
    owner = Player(custom_flair.ownedby()[0])
    owner - custom_flair
    owner.save()
#owner = db.get_player_with_item("Custom Flair")[0]
#if owner:
#    db.remove_item("Custom Flair", owner)
custom_flair.stock = 1
custom_flair.save()

# SELECT STOCK
db = SpongeDB()
store_item_ids = db.get_items_with_tag('general')
db.close()

# CREATE REDDIT POST
title = "STONE: Sunday Shop Open!"
body = """
# Welcome! What are ya buyin'?
-----------------------

Welcome to the Sunday Shop. Use your accumulated pebbles to buy from a small selection of items each Sunday!

* [What is STONE? How do I gain points/pebbles?](https://spiral.bibbleskit.com/about)

* [Check out the leaderboard and your own stats on the website!](https://spiral.bibbleskit.com/leaderboard)

* [Commands list.](https://spiral.bibbleskit.com/commands)

### How it works:
--------------------------

* **Simply leave a top level comment like so:** `/buy The North Star`. Item names are not case sensitive, but you have to use the proper quotation marks if it's in the name: `'` or `"`

* Unlimited Section: You can buy as many things as you want from here.

* Limited Section: You can buy only ONE item from this section each week.

* The shop remains active all week, until the next shop opens.

# The Goods
------------------------

## Unlimited Items

Item|Description|Cost|Stock
:--|:--|--:|--:
"""

unlimited_items = [Item(x) for x in store_item_ids if Item(x).is_unlimited]
for item in unlimited_items:
    body += f"{item.name}|{item.description}|{item.price} o|{item.stock}\n"

body += """

## Limited Items

Item|Description|Cost|Stock
:--|:--|--:|--:
"""

limited_items   = [Item(x) for x in store_item_ids if Item(x).is_limited]
for item in limited_items:
    if item.is_for_sale:
        body += f"{item.name}|{item.description}|{item.price} o|{item.stock}\n"


parlor = r.subreddit(R_SUBREDDIT)
submission = parlor.submit(title=title, selftext=body)

# This should probably be moved to a value in the database.
# That would mean also updating check_for_purchases.py
with open("store_id.txt", 'w') as file:
    file.write(str(submission))
