#!/home/sparlor/bin/python
from reddit_connect import r
from spongelog import SpongeLog
from spongeconfig import YEET_BOT, NPC
from playerclass import Player

log = SpongeLog("yeeted.log")

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
                username = line.split('/')[1]
                player =  Player(username)
                log.info(f"Player removed: \{'name': {player.name}, 'suds': {player.suds}, 'inventory': {player.inventory_string()}\}")
                player.flush()
                del(player)
            except Exception as e:
                log.error("Failed to remove user. Entry line: " + str(e))

# NPCs are removed, as well.
for n in NPC:
    try:
        non_player = Player(n)
        player.flush()
        log.info("Removed NPC: " + n)
    except:
        pass
