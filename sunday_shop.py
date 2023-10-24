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
#owner = db.get_player_with_item("Custom Flair")[0]
#if owner:
#    db.remove_item("Custom Flair", owner)
db.set_stock("Custom Flair")

# SET UNLIMITED ITEM STOCK
db.set_stock("Bag o' Tricks", 25)
db.set_stock("Floor Floosher 4000", 5)
db.set_stock("Towering Tool Belt", 5)
db.set_stock("Hunky DTI Poster", 10)
db.set_stock("Sexy Sinjury Poster", 10)
db.set_stock("How To Spiral 101", 10)
db.set_stock("Tower Rations", 10)


# SELECT STOCK
db.select_store_stock()

# CREATE REDDIT POST
title = "STONE: Sunday Shop Open!"
body = """
# Welcome! What are ya buyin'?
-----------------------

Welcome to the Sunday Shop. Use your accumulated suds to buy from a small selection of items each Sunday!

* [What is STONE? How do I gain points/pebbles?](https://spiral.bibbleskit.com/about)

* [Check out the leaderboard and your own stats on the website!](https://spiral.bibbleskit.com/leaderboard)

* [Commands list.](https://spiral.bibbleskit.com/commands)

### How it works:
--------------------------

* **Simply leave a top level comment like so:** `/buy The North Star`

* **NOTE**: It must be the exact name. For example, if the item is `Evil's Bane`, then none of these will work: `evils bane`, `Evils Bane`.

* **First come first serve**.

* Unlimited Section: You can buy as many things as you want from here.

* Limited Section: You can buy only ONE item from this section each week.

* The shop will appear at a random time on Sunday each week, so that the same people don't always get there first.

* The shop remains active all week, until the next shop opens.


### Commands:
--------------------------

**/buy**

    /buy <Item Name>
    
    e.g.: /buy Sword of Regret

**/pay**

    /pay <amount> <username>
    
    e.g.: /pay 200 bibbleskit

**/give**

    /give "<Item Name>" <username>
    
    e.g.: /give "Sword of Regret" bibbleskit

# The Goods
------------------------

## Unlimited Items

Item|Description|Cost|Stock
:--|:--|--:|--:
"""

stock = db.get_forsale_unlimited()
for i in stock:
    body += "{}|{}|{} o|{}\n".format(i[1], i[3], i[2],i[4]) 

body += """

## Limited Items

Item|Description|Cost|Stock
:--|:--|--:|--:
"""
stock = db.get_forsale_limited()
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
