#!/home/sparlor/python36/python
from reddit_connect import r
from spongelog import SpongeLog
from spongedb import SpongeDB
from spongeconfig import YEET_BOT, NPC

log = SpongeLog("yeeted.log")
db = SpongeDB()

yeeter = r.redditor(YEET_BOT)
subs   = yeeter.submissions.new(limit=5)
for sub in subs:
    for line in sub.selftext.split('\n'):
        if '*' in line:
            log.info("Removed " + line[4:])
            db.remove_player(line[4:])

for n in NPC:
    db.remove_player(n)
    log.info("Removed NPC: " + n)

db.save()
db.close()
