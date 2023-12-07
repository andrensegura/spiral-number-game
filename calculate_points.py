#!/home/sparlor/bin/python

import special_items
from spongedb import SpongeDB, NoSuchPlayerError
from spongelog import SpongeLog
from spongeconfig import R_SUBREDDIT
from reddit_connect import r
from playerclass import Player, NewPlayer

# The algorithms for score/pebbles are kept in
# untracked modules and imported for use here.
from update_scores import update_all_scores
import points_algorithm

log = SpongeLog("calculatepoints.log")

parlor = r.subreddit(R_SUBREDDIT)

def grant_points_to_player(username: str, points: int):
    player = ''
    try:
        player = Player(username)
    except NoSuchPlayerError:
        player = NewPlayer(username)

    player + points
    player.dailysuds += points
    player.save()

def is_submission_added(submission_id: str) -> bool:
    db = SpongeDB()
    is_added = db.is_submission_added(submission_id)
    db.close()
    return is_added

def add_submission(submission_id: str):
    db = SpongeDB()
    db.add_submission(submission_id)
    db.save()
    db.close()

def is_comment_added(comment_id: str) -> bool:
    db = SpongeDB()
    is_added = db.is_comment_added(comment_id)
    db.close()
    return is_added

def add_comment(comment_id: str):
    db = SpongeDB()
    db.add_comment(comment_id)
    db.save()
    db.close()

def iterate_points():
    for submission in parlor.new(limit=50):
        # Add points per comment.
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if is_comment_added(comment.id):
                continue
            if not comment.author:
                log.info(f"New Comment ID {comment.id}: <deleted user?>")
                continue

            points = points_algorithm.comment_point_value(comment)
            grant_points_to_player(submission.author.name, points)

            special_items.process_owned_items(comment)
            special_items.process_global_items(comment)

            add_comment(comment.id)
            log.info(f"New Comment ID {comment.id} - {comment.author.name}: +{points} pebbles")

        # Add points for submission title, text, upvotes...
        if is_submission_added(submission.id):
            continue
        if not submission.author:
            log.info(f"New Submission ID {submission.id}: <deleted user?>")
            continue

        points = points_algorithm.submission_point_value(submission)
        grant_points_to_player(submission.author.name, points)
        log.info(f"New Submission ID {submission.id} - {submission.author.name}: +{points} pebbles")

        add_submission(submission.id)

iterate_points()
special_items.process_daily_items()

# Update scores for all players
update_all_scores()

bibs = Player('bibbleskit')
bibs._suds = 0
bibs.save()

log.info("Calculations complete.")
