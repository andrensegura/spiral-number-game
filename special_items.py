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

def item_letter(letter, text):
    if not Item(f"the letter {letter}").ownedby():
        return
    for ownername in Item(f"the letter {letter}").ownedby():
        points = round((text.lower().count(letter) * 0.1))
        points = points if points else 1

        player = Player(ownername)
        player + points
        player.save()

        logtext = text.encode('utf-8').lower()
        log.info(f"Letter: {letter}\tPoints: {points}\nText: {logtext}")

def couch_goblin(username):
    if username not in Item('couch goblin').ownedby():
        return

    if random.randint(0, 99) > 79:
        points = random.randrange(5, 25, 5)

        player = Player(username)
        player + points
        player.save()

        log.info("couch goblin found {} suds!".format(points))

# These are items that are procced for every new comment
def process_global_items(comment):
    # Special Letters
    for letter in 'spiral':
        item_letter(letter, comment.body)

# These are items that are procced when the owner comments
def process_owned_items(comment):
    couch_goblin(comment.author.name)

