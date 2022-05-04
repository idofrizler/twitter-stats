import datetime, logging, typing
import azure.functions as func
from ..common import table
from ..common import api


def lookup_new_comments(tweet_id, tweet_author_id, since_id):
    new_user_ids = set()
    preexisting_user_ids = table.get_preexisting_commenting_users_from_table()

    pagination_token = 'FIRST_RUN'
    recent_comments = api.get_recent_comments_from_twitter(tweet_id, since_id)
    
    newest_id = recent_comments['meta'].get('newest_id', since_id)

    while pagination_token and 'data' in recent_comments:
        recent_user_ids = [
            comment['author_id'] for comment in recent_comments['data'] 
            if comment['author_id'] not in preexisting_user_ids 
            and comment['in_reply_to_user_id'] == tweet_author_id
        ]
        new_user_ids.update(recent_user_ids)

        pagination_token = recent_comments['meta'].get('next_token', None)
        if pagination_token:
            recent_comments = api.get_recent_comments_from_twitter(tweet_id, since_id, pagination_token)

    return new_user_ids, newest_id


def write_state_to_table(commenting_user_ids):
    for user_id in commenting_user_ids:
        table.update_new_comment_for_processing(user_id)


def add_new_comments_to_queue(msg, commenting_user_ids):
    write_state_to_table(commenting_user_ids)
    user_id_list = list(commenting_user_ids)
    logging.info('Pushing {} to queue'.format(user_id_list))
    msg.set(user_id_list)


def track_tweets(msg):
    tracked_tweets = table.read_tracked_tweets_from_table()
    for tweet in tracked_tweets:
        tweet_id, author_id, since_id = tweet
        logging.info('Found tweet {}'.format(tweet_id))

        new_user_ids, newest_id = lookup_new_comments(tweet_id, author_id, since_id)
        logging.info('Found {} new comments; resetting since_id to {}'.format(len(new_user_ids), newest_id))
        add_new_comments_to_queue(msg, new_user_ids)
        table.update_newest_id(tweet_id, author_id, newest_id)


def main(mytimer: func.TimerRequest, msg: func.Out[typing.List[str]]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    track_tweets(msg)



