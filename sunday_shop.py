#!/home/sparlor/python36/python
from reddit_connect import r
from spongedb import SpongeDB
from spongeconfig import R_SUBREDDIT

db = SpongeDB()

# RESET CUSTOM FLAIR
owner = db.get_player_with_item("Custom Flair")
if owner:
    db.remove_item("Custom Flair", owner)
db.set_stock("Custom Flair")

# SELECT STOCK
db.select_store_stock()

# CREATE REDDIT POST
title = "STONE: Sunday Shop Open!"
body = """
# Welcome! What are ya buyin'?
-----------------------

Welcome to the Sunday Shop. Use your accumulated suds to buy from a small selection of items each Sunday!

[What is SPONGE? How do I get points? Click here.](https://www.reddit.com/r/TheSpiralParlor/comments/wmpjyi/sponge_version_update_and_hotfix/)

[Check out the leaderboard and your own stats on the website!](https://spiral.bibbleskit.com)


### How it works:
--------------------------

* **Simply leave a top level comment like so:** `/buy The North Star`

* **NOTE**: It must be the exact name. For example, if the item is `Evil's Bane`, then none of these will work: `evils bane`, `Evils Bane`.

* **First come first serve**.

* Limit one purchase per user. You can't just buy the whole shop.

* (\*) **You can sell your items to others**. You can set the price, it's yours now. When the sale is finalized, please ping me in the discussion so I can perform the item/suds transfer.

* The shop will appear at a random time on Sunday each week, so that the same people don't always get there first.

* The things in this list starting with **(\*)** will eventually become automated through the website (once I have the time).

# The Goods
------------------------

Item|Description|Cost|Stock
:--|:--|--:|--:
"""

stock = db.get_forsale()
for i in stock:
    body += "{}|{}|{} o|{}\n".format(i[1], i[3], i[2],i[4]) 

parlor = r.subreddit(R_SUBREDDIT)
submission = parlor.submit(title=title, selftext=body)

# This should probably be moved to a value in the database.
# That would mean also updating check_for_purchases.py
with open("store_id.txt", 'w') as file:
    file.write(str(submission))


db.save()
db.close()
