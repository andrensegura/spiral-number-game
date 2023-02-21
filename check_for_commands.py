#!/home/sparlor/python36/python
import shlex
from reddit_connect import r
from spongedb import SpongeDB
from spongelog import SpongeLog
from spongeconfig import R_SUBREDDIT

log = SpongeLog("commands.log")

# New commands to be processed can be added here.

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
        print(e)
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
                log.info("/give initiated -- {}: {}".format(comment.author.name, reply))
            if cargs[0] == '/pay':
                cmd_msg = command_pay(comment.author.name, int(cargs[1]), cargs[2])
                log.info("/pay initiated -- {}: {}".format(comment.author.name, reply))

            # properly processed command will get replied to.
            # we also save the comment id in the db so that it doesn't get processed
            # again. this also effectively disqualifies it for points.
            if cmd_msg:
                comment.reply(cmd_msg)
                db.add_comment(comment.id)
                log.info("comment {} added".format(comment.id))

            db.save()
