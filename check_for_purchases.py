#!/home/sparlor/python36/python
from reddit_connect import r
from spongelog import SpongeLog
from spongedb import *

log = SpongeLog("purchases.log")

# Returns an item name if someone uses /buy
def check_for_purchase(body):
    if body.startswith('/buy '):
        item = body.partition('\n')[0][5:]
        return item

# Shows the item is no longer for sale in the post.
def update_sold(post, item):
    new_body = post.selftext.replace(item, "~~" + item + "~~")
    post.edit(body=new_body)

def is_on_banlist(username):
    with open('banlist.txt', 'r') as banlist:
        if str(username) in [str(x.strip()) for x in banlist.readlines()]:
            return True
        else:
            return False

# banlist just keeps track of who has made a purchase this week.
# It keeps users from buying multiple items. Perhaps this could
# be kept in the database, instead of a flat file.
def add_to_banlist(username):
    with open('banlist.txt', 'a') as banlist:
       banlist.write(username + '\n') 

# This could also probably be a database value.
post = ''
with open('store_id.txt', 'r') as file:
    sub_id = file.readline()
    post = r.submission(id=sub_id)

# Creates a queue of items and processes them after.
purchases = []
post.comments.replace_more(limit=None)
for comment in post.comments.list():
    item = check_for_purchase(comment.body)
    if item:
        purchases.append((item, comment.author.name, comment.id))

# Processes the queue created earlier
# Need to include logging for this. Would be easy to add.
db = SpongeDB()
for p in purchases:
    try:
        if db.is_comment_added(p[2]):
            continue
        if is_on_banlist(p[1]):
            db.add_comment(p[2])
            db.save()
            r.comment(p[2]).reply("You've already purchased an item.".format(p[0])) 
            log.info("User already made purchase: {}".format(p[1]))
            continue
        db.add_comment(p[2])
        db.purchase_item(p[0], p[1])
        r.comment(p[2]).reply('Purchase of "{}" Successful!'.format(p[0]))
        log.info("Item purchased successfully: {}, {}".format(p[1], p[0]))
        update_sold(post, p[0])
        add_to_banlist(p[1])
    except OutOfStockError:
        r.comment(p[2]).reply('Sorry, "{}" is out of stock.'.format(p[0]))
    except ItemNonexistantError:
        r.comment(p[2]).reply('"{}" isn\'t an item.'.format(p[0]))
    except NotEnoughSudsError:
        r.comment(p[2]).reply('Sorry, [you don\'t have enough suds]({}).'.format("https://spiral.bibbleskit.com/u/" + p[1]))
    except NotForSaleError:
        r.comment(p[2]).reply('Sorry, that item is not for sale.')
    db.save()
