import datetime, logging, typing
import azure.functions as func
from ..common import table
from ..common import api


def lookup_new_comments(users_table, tweet_id, tweet_author_id, since_id):
    new_comments = set()
    preexisting_user_ids = users_table.get_preexisting_commenting_users(tweet_id)

    pagination_token = 'FIRST_RUN'
    recent_comments = api.get_recent_comments_from_twitter(tweet_id, since_id)
    
    newest_id = recent_comments['meta'].get('newest_id', since_id)

    while pagination_token and 'data' in recent_comments:
        for comment in recent_comments['data']:
            author_id = comment['author_id']
            comment_id = comment['id']
            if author_id not in preexisting_user_ids and comment['in_reply_to_user_id'] == tweet_author_id:
                new_comments.add((author_id, comment_id))
                preexisting_user_ids.add(author_id)

        pagination_token = recent_comments['meta'].get('next_token', None)
        if pagination_token:
            recent_comments = api.get_recent_comments_from_twitter(tweet_id, since_id, pagination_token)

    return new_comments, newest_id


def write_state_to_table(users_table, tweet_id, comments):
    for comment in comments:
        users_table.update_new_comment_for_processing(tweet_id, comment[0], comment[1])


def add_new_comments_to_queue(msg, users_table, tweet_id, comments):
    write_state_to_table(users_table, tweet_id, comments)
    comments = ['{}|{}|{}'.format(tweet_id, comment[0], comment[1]) for comment in comments]

    logging.info('Pushing {} to queue'.format(comments))
    msg.set(comments)


def track_tweets(msg):
    tweets_table = table.TrackedTweetsTable()
    users_table = table.UsersTable()
    tracked_tweets = tweets_table.read_tracked_tweets_from_table()

    for tweet in tracked_tweets:
        tweet_id, author_id, since_id = tweet
        logging.info('Found tweet {}'.format(tweet))

        new_comments, newest_id = lookup_new_comments(users_table, tweet_id, author_id, since_id)
        logging.info('Found {} new comments; resetting since_id to {}'.format(len(new_comments), newest_id))
        add_new_comments_to_queue(msg, users_table, tweet_id, new_comments)
        tweets_table.update_newest_id(tweet_id, author_id, newest_id)


def main(mytimer: func.TimerRequest, msg: func.Out[typing.List[str]]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    track_tweets(msg)



