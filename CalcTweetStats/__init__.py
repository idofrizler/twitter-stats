from collections import defaultdict
from functools import total_ordering
import logging
from typing import OrderedDict
import azure.functions as func
from ..common import api, table


def get_twitter_stats(user_id):
    logging.info('Collecting tweet statistics')
    max_like_count = 0
    total_like_count = 0
    total_reply_count = 0
    total_retweet_count = 0
    total_quote_count = 0
    num_of_tweets = 0
    max_tweet_id = None

    replied_to_dict = defaultdict(int)

    pagination_token = 'FIRST_RUN'
    tweets = api.get_user_tweets(user_id)

    while pagination_token:
        num_of_tweets += len(tweets['data'])
        for tweet in tweets['data']:
            current_like_count = tweet['public_metrics']['like_count']
            total_like_count += current_like_count

            total_reply_count += tweet['public_metrics']['reply_count']
            
            if not tweet['text'].startswith('RT @'):
                total_retweet_count += tweet['public_metrics']['retweet_count']
            
            total_quote_count += tweet['public_metrics']['quote_count']

            if  current_like_count > max_like_count:
                max_tweet_id = tweet['id']
                max_like_count = tweet['public_metrics']['like_count']

            replied_to = tweet.get('in_reply_to_user_id', None)
            if replied_to:
                replied_to_dict[replied_to] += 1

        pagination_token = tweets['meta'].get('next_token', None)
        if pagination_token:
            tweets = api.get_user_tweets(user_id, pagination_token)

    # Removing self replies from total count
    self_replies = replied_to_dict.get(user_id, 0)
    total_reply_count -= self_replies

    # We want most replied to, except if it's the user itself
    most_replied_to = None
    replied_to_dict.pop(user_id)

    if len(replied_to_dict.items()) > 0:
        most_replied_to_tuple = sorted(replied_to_dict.items(), key=lambda k_v: k_v[1], reverse=True)[0]
        logging.info(most_replied_to_tuple)
        if most_replied_to_tuple[1] >= 10: # only save metric, if this is significant enough
            most_replied_to = most_replied_to_tuple
    
    return max_tweet_id, total_like_count, total_reply_count, total_retweet_count, total_quote_count, num_of_tweets, most_replied_to


def write_results_to_table(tweet_id, user_id, comment_id, tweet_stats):
    users_table = table.UsersTable()
    users_table.update_twitter_stats_for_user(tweet_id, user_id, comment_id, tweet_stats)


def post_message_to_queue(tweet_id, user_id, comment_id, out_queue):
    msg_str = '{}|{}|{}'.format(tweet_id, user_id, comment_id)

    logging.info('Pushing {} to queue'.format(msg_str))
    out_queue.set(msg_str)


def run_twitter_stats(tweet_id, user_id, comment_id, out_queue):
    tweet_stats = get_twitter_stats(user_id)
    write_results_to_table(tweet_id, user_id, comment_id, tweet_stats)
    post_message_to_queue(tweet_id, user_id, comment_id, out_queue)


def main(msgin: func.QueueMessage, msgout: func.Out[str]) -> None:
    msg_content = msgin.get_body().decode('utf-8')
    logging.info('Python queue trigger function processed a queue item: %s', msg_content)
    
    tweet_id, user_id, comment_id = msg_content.split('|')
    run_twitter_stats(tweet_id, user_id, comment_id, msgout)

