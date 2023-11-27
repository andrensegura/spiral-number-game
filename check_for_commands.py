#!/home/sparlor/bin/python
import shlex
from random import randint, choice
from reddit_connect import r
from spongedb import *
from spongelog import SpongeLog
from spongeconfig import R_SUBREDDIT

from playerclass import Player, NewPlayer
from itemclass import Item

log = SpongeLog("commands.log")

def logwrap(command_func):
    def wrapper(*args):
        if len(args) > 1:
            log.info(f"{command_func.__name__} initiated -- {args[0].name}: {args[1:]}")
        else:
            log.info(f"{command_func.__name__} initiated -- {args[0].name}")

        output = command_func(*args) 

        log.info(f"{command_func.__name__} completed -- {args[0].name}: {output}")
        return output
    return wrapper

# New commands to be processed can be added here.

@logwrap
def command_safe_off(user: Player) -> str:
    if user.safemode is False:
        return "> `safe mode` is already off."
    
    user.safemode = False
    user.update_safemode_timer()
    return "> You are now out of `safe mode`."

@logwrap
def command_safe_on(user: Player) -> str:
    if user.safemode is True:
        return "> `safe mode` is already on."

    # convert from float to int for nicer display
    hours = int(user.hours_since_safe_toggle())
    if user.hours_since_safe_toggle() >= 24:
        user.safemode = True
        return "> You are now in `safe mode`."
    else:
        return f"> You cannot enter `safe mode` for {hours} more hours."

def command_steal(perp, victim):
    victim = victim.split('/')[-1]
    msg = ''
    try:
        # If victim doesn't exist:
        if not db.get_player(victim):
            msg = "> \"{}\" is not a valid player.".format(victim)
            return 

        # If the perp is in safe mode, they can't steal.
        if db.is_in_safemode(perp):
            msg = "> You are in `safe mode`, so you cannot steal from other players."
            return msg

        # user must have item "Bag o' Tricks" in their inventory
        if perp not in db.get_player_with_item("Bag o' Tricks"):
            msg = "> You need a \"Bag o' Tricks\" to steal. You can get them from the shop."
            return msg

        # If the victim is in safe mode, they can't be targeted.
        if db.is_in_safemode(victim):
            msg = "> [{}](https://spiral.bibbleskit.com/{}) is in `safe mode`. They cannot be targeted.".format(victim, victim)
            return msg

        # If victim has a protection charm, they use one to defend.
        if victim in db.get_player_with_item("Protection Charm"):
            db.remove_item("Protection Charm", victim)
            db.remove_item("Bag o' Tricks", perp)

            msg = "> Dang! Their Protection Charm guarded them!"
            msg += "\n\n> You lost one bag, and they lost one charm."
            return msg

        # steals an item
        n = randint(0, 99)
        if n >= 85:
            inventory = db.get_player(victim, "inventory")
            if inventory:
                inventory = [int(x) for x in inventory[0].split(',')]
                prize = choice(inventory)

                # transfer item
                db.give_item(prize, perp)
                db.remove_item(prize, victim)

                # gotta remove a bag from the perp
                db.remove_item("Bag o' Tricks", perp)

                msg = "> Wow, lucky you! You pulled just the right tool to get an item!"
                msg += "\n\n> Item obtained: {}".format(db.get_item(prize)[1])

                db.save()
            else:
                msg = "> {} doesn't have any items to steal.".format(victim)
        # fails
        else:
            db.remove_item("Bag o' Tricks", perp)
            msg = "> The bag didn't have anything useful in it. Unfortunately, you couldn't steal anything!"
            db.save()

        return msg
    except Exception as e:
        log.error(e)
        return "> Something went wrong. Contact /u/bibbleskit"

@logwrap
def command_give_item(from_user: Player, item_str: str, to_user_str: str) -> str:
    try:
        item = Item(item_str)
        to_user = Player(to_user_str)

        from_user.give(item, to_user)

        from_user.save()
        to_user.save()
        return f"> '{item.name}' given to /u/{to_user.name}."
    except (ItemNonexistantError, NoSuchPlayerError, ItemNotOwnedError) as error:
        return f"> {error}"

@logwrap
def command_pay(from_user: Player, amount: int, to_user: str) -> str:
    # remove decimals and negatives
    amount = abs(int(amount))

    try:
        payee = Player(to_user)
        from_user.pay(amount, payee)

        from_user.save()
        payee.save()
        return f"> {from_user.name} sent {amount}o to /u/{payee.name}."
    except (NoSuchPlayerError, NotEnoughSudsError) as error:
        return f"> {error}"

# Go through the latest 200 comments for commands.
# 200 may be overkill, since this checks every minute.
# It could be smaller, but already processed comments
# are skipped.
db = SpongeDB()
for comment in r.subreddit(R_SUBREDDIT).comments(limit=200):
    if not db.is_comment_added(comment.id):
        if comment.body.startswith('/'):
            # shlex is used to split strings up as if they were command line inputs.
            # /give "Item Name" username becomes:
            # ('/give', 'Item Name', 'username')
            cargs = shlex.split(comment.body)
            
            commander = ''
            try:
                commander = Player(comment.author.name)
            except NoSuchPlayerError:
                commander = NewPlayer(comment.author.name)

            # Record a success or error reply if necessary.
            cmd_msg = ""
            if cargs[0] == '/give':
                cmd_msg = command_give_item(commander, cargs[1], cargs[2])
            elif cargs[0] == '/pay':
                cmd_msg = command_pay(commander, int(cargs[1]), cargs[2])
            elif cargs[0] == '/steal':
                cmd_msg = command_steal(comment.author.name, cargs[1])
                log.info("/steal initiated -- {}: {}".format(comment.author.name, cmd_msg))
            elif cargs[0] == '/safe':
                cmd_msg = command_safe_on(commander)
            elif cargs[0] == '/unsafe':
                cmd_msg = command_safe_off(commander)

            # properly processed command will get replied to.
            # we also save the comment id in the db so that it doesn't get processed
            # again. this also effectively disqualifies it for points.
            if cmd_msg:
                comment.reply(cmd_msg)
                db.add_comment(comment.id)
                log.info("comment {} added".format(comment.id))

            db.save()
