#!/home/sparlor/bin/python
import sys
sys.path.append('..')
from playerclass import Player
from itemclass import Item
from shopclass import Shop

# RESET CUSTOM FLAIR
custom_flair = Item('custom flair')
custom_flair.stock = 1
custom_flair.save()
if custom_flair.ownedby():
    for username in custom_flair.ownedby():
        owner = Player(username)
        owner - custom_flair
        owner.save()

# GENERAL SHOP
# Shop class without any arguments is the default shop.
Shop().submit_post()
