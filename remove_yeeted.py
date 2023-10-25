#!/home/sparlor/bin/python
from reddit_connect import r
from spongelog import SpongeLog
from spongedb import SpongeDB
from spongeconfig import YEET_BOT, NPC

log = SpongeLog("yeeted.log")
db = SpongeDB()

##########################################################
# Removes all users in the latest flush post from the
# database. Eventually, should just lock the user instead.
##########################################################

yeeter = r.redditor(YEET_BOT)
subs   = yeeter.submissions.new(limit=5)
for sub in subs:
    for line in sub.selftext.split('\n'):
        if '*' in line:
            try:
                user = line.split('/')[1]
                log.info("Removed " + user)
                db.remove_player(user)
            except Exception as e:
                log.error("Failed to remove user. Entry line: " + str(e))

# NPCs are removed, as well.
for n in NPC:
    db.remove_player(n)
    log.info("Removed NPC: " + n)

# test comment
db.save()
db.close()
