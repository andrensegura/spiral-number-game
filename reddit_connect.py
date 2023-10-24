import praw
from spongeconfig import *

r = praw.Reddit(
    client_id=R_CLIENT_ID,
    client_secret=R_CLIENT_SECRET,
    password=R_PASSWORD,
    user_agent=R_USER_AGENT,
    username=R_USERNAME,
)

r.validate_on_submit = True
