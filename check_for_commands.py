#!/home/sparlor/python36/python
import shlex
from reddit_connect import r
from spongedb import SpongeDB
from spongeconfig import R_SUBREDDIT

def command_give_item(from_user, item, to_user):
#    db = SpongeDB()

    try:
        db.remove_item(item, from_user)
        db.give_item(item, to_user)

        db.save()
        return("> \"{}\" successfully given to /u/{}.".format(item, to_user))
    except:
        return("> Couldn't give \"{}\" to /u/{}. Check the spelling.".format(item, to_user))

def command_pay(from_user, amount, to_user):
#    db = SpongeDB()
    amount = abs(amount)
    try:
        from_user_suds = db.get_player(from_user, 'suds')[0]
        print(from_user_suds)
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

db = SpongeDB()
for comment in r.subreddit(R_SUBREDDIT).comments(limit=200):
    if not db.is_comment_added(comment.id):
        if comment.body.startswith('/'):
            if comment.body.startswith('/give'):
               cargs = shlex.split(comment.body) 
               reply = command_give_item(comment.author.name, cargs[1], cargs[2])
               comment.reply(reply)
               print("{}: {}".format(comment.author.name, reply))
               db.add_comment(comment.id)
               print("comment added")
               db.save()
            if comment.body.startswith('/pay'):
               cargs = shlex.split(comment.body)
               reply = command_pay(comment.author.name, int(cargs[1]), cargs[2])
               comment.reply(reply)
               print("{}: {}".format(comment.author.name, reply))
               db.add_comment(comment.id)
               print("comment added")
               db.save()
