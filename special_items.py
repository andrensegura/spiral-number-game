#!/home/sparlor/bin/python
import random
from spongelog import SpongeLog
from itemclass import Item
from playerclass import Player

log = SpongeLog("calculatepoints.log")

###############################################################
# This file contains the inner workings for special items.
# If a new special pebble-accumulating item needs to be added,
# a new function for it will need to be created, and then it
# will need to be implemented within process_item_bonuses()
###############################################################

def item_letter(username, letter, text):
    points = round((text.lower().count(letter) * 0.01))
    points = points if points else 1

    player = Player(username)
    player + points
    player.save()

    log.info("Letter: {}\tPoints: {}\nText: {}".format(letter, points,text.encode('utf-8').lower()))

def couch_goblin(username):
    if random.randint(0, 99) > 79:
        points = random.randrange(5, 25, 5)

        player = Player(username)
        player + points
        player.save()

        log.info("couch goblin found {} suds!".format(points))

def process_item_bonuses(comment):
    print("process: item bonus")
    # Special Letters
    for letter in 'spiral':
        list_of_owners = Item(f"the letter {letter}").ownedby()
        if not list_of_owners:
            continue
        for owner in Item(f"the letter {letter}").ownedby():
            item_letter(owner, letter, comment.body)

    # Couch Goblin Grog
    if comment.author.name in Item('couch goblin').ownedby():
        couch_goblin(comment.author.name)
