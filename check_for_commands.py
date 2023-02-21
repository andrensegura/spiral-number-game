#!/home/sparlor/python36/python
import shlex
import traceback
from random import randint, choice
from reddit_connect import r
from spongedb import SpongeDB
from spongelog import SpongeLog
from spongeconfig import R_SUBREDDIT

log = SpongeLog("commands.log")

# New commands to be processed can be added here.

def command_steal(perp, victim):
    msg = ''
    try:
        # user must have item "Bag o' Tricks" in their inventory
        if perp not in db.get_player_with_item("Bag o' Tricks"):
            msg = "> You need a \"Bag o' Tricks\" to steal. You can get them from the shop."
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
        if n >= 95:
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
            msg = "> The bag didn't have anything useful in it. Unfortunately, you couldn't steal anything!"
            db.save()

        return msg
    except Exception as e:
        log.error(e)
        return "> Something went wrong. Contact /u/bibbleskit"

def command_give_item(from_user, item, to_user):
    try:
        db.remove_item(item, from_user)
        db.give_item(item, to_user)

        db.save()
        return("> \"{}\" successfully given to /u/{}.".format(item, to_user))
    except:
        return("> Couldn't give \"{}\" to /u/{}. Check the spelling.".format(item, to_user))

def command_pay(from_user, amount, to_user):
    amount = abs(amount)
    try:
        from_user_suds = db.get_player(from_user, 'suds')[0]
        if from_user_suds > amount:
            db.add_suds(from_user, amount * -1)
            db.add_suds(to_user, amount)
            db.save()
            return("> {}o successfully sent to /u/{}.".format(amount, to_user))
        else:
            return("> You don't have enough suds.")
    except Exception as e:
        return("> Couldn't send {}o to /u/{}. Please contact me.".format(amount, to_user))

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
            # Record a success or error reply if necessary.
            cmd_msg = ""
            if cargs[0] == '/give':
                cmd_msg = command_give_item(comment.author.name, cargs[1], cargs[2])
                log.info("/give initiated -- {}: {}".format(comment.author.name, cmd_msg))
            elif cargs[0] == '/pay':
                cmd_msg = command_pay(comment.author.name, int(cargs[1]), cargs[2])
                log.info("/pay initiated -- {}: {}".format(comment.author.name, cmd_msg))
            elif cargs[0] == '/steal':
                cmd_msg = command_steal(comment.author.name, cargs[1])
                log.info("/steal initiated -- {}: {}".format(comment.author.name, cmd_msg))

            # properly processed command will get replied to.
            # we also save the comment id in the db so that it doesn't get processed
            # again. this also effectively disqualifies it for points.
            if cmd_msg:
                comment.reply(cmd_msg)
                db.add_comment(comment.id)
                log.info("comment {} added".format(comment.id))

            db.save()
