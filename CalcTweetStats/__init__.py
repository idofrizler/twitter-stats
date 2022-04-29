import logging
import azure.functions as func
from .api import *

bearer_token = auth()
headers = create_headers(bearer_token)


def get_pulitzer_tweet(user_id):
    logging.info('Running Pulitzer metric')
    max_likes_count = 0
    max_tweet = None

    pagination_token = 'FIRST_RUN'
    tweets = get_user_tweets(headers, user_id)
    while pagination_token:
        for tweet in tweets['data']:
            current_likes_count = tweet['public_metrics']['like_count']
            if  current_likes_count > max_likes_count:
                max_tweet = tweet
                max_likes_count = tweet['public_metrics']['like_count']

        pagination_token = tweets['meta'].get('next_token', None)
        if pagination_token:
            tweets = get_user_tweets(headers, user_id, pagination_token)

    return max_tweet


def main(msg: func.QueueMessage) -> None:
    msg_content = msg.get_body().decode('utf-8')
    logging.info('Python queue trigger function processed a queue item: %s', msg_content)
    logging.info(get_pulitzer_tweet(msg_content))


