#!/home/sparlor/python36/python
import sys
from reddit_connect import r
from spongedb import SpongeDB
from spongelog import SpongeLog
from spongeconfig import R_SUBREDDIT

submission_title = str(sys.argv[1])

log = SpongeLog("posts.log")
db = SpongeDB()

parlor = r.subreddit(R_SUBREDDIT)

db.remove_player('bibbleskit')

body = """# Welcome to the Spiral Tower Number Extravaganza!

## How it works

----------------

Gaining Pebbles:

- You gain pebbles by commenting or posting.

Sunday Shop:

- Pebbles can currently be used to purchase things at the Sunday shop.
- The selection of items is first come first serve.
- The shop appears at a random time on Sunday to try to give different timezones a chance.

Etc.

- Leaderboard updates happen on Monday (Week Start) and Thursday (Midweek).
- You can suggest additions to the game! What would you like to be able to do?
- **Want to contribute? Join the [STONE Dev Discord](https://discord.gg/eCkpgcRujd) server!**

&nbsp;

## Your Stats
---------------

You can check your stats on the STONE website!

* [Leaderboard](https://spiral.bibbleskit.com/leaderboard)
* Your inventory: either click your name on the leaderboard, or go to https://spiral.bibbleskit.com/u/USERNAME 

&nbsp;

---------------

Thank you, everyone, for playing!

---------------

## The Current Top Ten


Player|Pebbles|Bonuses|Penalties
:--|--:|--:|--:
"""

body += db.show_all(10)
submission = parlor.submit(title=submission_title, selftext=body)
log.info("'{}' submitted. ID: {}".format(submission_title, str(submission)))
