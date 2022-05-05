from functools import total_ordering
import logging
import azure.functions as func
from ..common import api


def get_tweets_stats(user_id):
    logging.info('Collecting tweet statistics')
    max_like_count = 0
    total_like_count = 0
    total_reply_count = 0
    total_retweet_count = 0
    total_quote_count = 0
    num_of_tweets = 0
    max_tweet = None

    pagination_token = 'FIRST_RUN'
    tweets = api.get_user_tweets(user_id)

    while pagination_token:
        num_of_tweets += len(tweets['data'])
        for tweet in tweets['data']:
            current_like_count = tweet['public_metrics']['like_count']
            
            total_reply_count += tweet['public_metrics']['reply_count']
            
            if not tweet['text'].startswith('RT @'):
                total_retweet_count += tweet['public_metrics']['retweet_count']
            
            total_quote_count += tweet['public_metrics']['quote_count']
            total_like_count += current_like_count
            
            if  current_like_count > max_like_count:
                max_tweet = tweet
                max_like_count = tweet['public_metrics']['like_count']

        pagination_token = tweets['meta'].get('next_token', None)
        if pagination_token:
            tweets = api.get_user_tweets(user_id, pagination_token)

    return max_tweet, total_like_count, total_reply_count, total_retweet_count, total_quote_count, num_of_tweets

def get_url_from_tweet_data(tweet):
    return 'https://twitter.com/qwer/status/{}'.format(tweet['id'])

def serialize_stats_to_msg(tweet_stats):
    max_tweet, total_like_count, total_reply_count, total_retweet_count, total_quote_count, num_of_tweets = tweet_stats
    ratio = round(total_like_count*1.0/num_of_tweets, 2)
    max_tweet_url = get_url_from_tweet_data(max_tweet)

    msg_str = 'You tweeted {} times so far, and received {} likes, {} replies, {} retweets and {} quotes, in total.\n' \
    'Your like/tweet ratio is {}, and your most popular tweet was:\n{}' \
    .format(num_of_tweets, total_like_count, total_reply_count, total_retweet_count, total_quote_count, ratio, max_tweet_url)

    logging.info('Message length: {}'.format(len(msg_str)))
    logging.info(msg_str)

    return msg_str

def run_tweet_stats(user_id):
    tweet_stats = get_tweets_stats(user_id)
    msg_str = serialize_stats_to_msg(tweet_stats)


def main(msg: func.QueueMessage) -> None:
    msg_content = msg.get_body().decode('utf-8')
    logging.info('Python queue trigger function processed a queue item: %s', msg_content)
    run_tweet_stats(msg_content)

