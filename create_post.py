#!/home/sparlor/bin/python
import sys
from reddit_connect import r
from spongedb import SpongeDB
from spongelog import SpongeLog
from spongeconfig import R_SUBREDDIT, YEET_BOT, NPC

############################
# Creates the weekly post.
############################


# Title of post supplied via command line argument.
submission_title = str(sys.argv[1])

log = SpongeLog("posts.log")
db = SpongeDB()

parlor = r.subreddit(R_SUBREDDIT)

# Remove NPCs before creating the post, just in case they got added during the last calculation.
for n in NPC:
    db.remove_player(n)
    log.info("Removed NPC: " + n)

body = """# Welcome to the Spiral Tower Number Extravaganza!

New? Don't know what STONE is? [Click here!](https://spiral.bibbleskit.com/about)

## Your Stats
---------------

You can check your stats on the STONE website!

* [Leaderboard](https://spiral.bibbleskit.com/leaderboard)
* Your inventory: either click your name on the leaderboard, or go to https://spiral.bibbleskit.com/u/USERNAME 

---------------

## Top Ten by Score


Player|Score
:--|--:
"""

body += db.show_all('score_7d',10)

body += """

## Top Ten by Pebbles


Player|Pebbles
:--|--:
"""

body += db.show_all('suds',10)


submission = parlor.submit(title=submission_title, selftext=body)
log.info("'{}' submitted. ID: {}".format(submission_title, str(submission)))
