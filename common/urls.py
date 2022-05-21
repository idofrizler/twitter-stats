import json


TWITTER_URL_PREFIX = 'https://api.twitter.com/2/'


def create_url_user_tweets(user_id, pagination_token=None):
    search_url = '{}users/{}/tweets'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {
        'tweet.fields': 'id,author_id,public_metrics,created_at,in_reply_to_user_id',
        'exclude': 'retweets',
        'max_results': 100,
        'pagination_token': pagination_token}
    return search_url, query_params


def create_url_liking_users(tweet_id):
    search_url = '{}tweets/{}/liking_users'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {'user.fields': 'id'}
    return search_url, query_params


def create_url_user_public_metrics(user_id):
    search_url = '{}users/{}'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {'user.fields': 'username,public_metrics'}
    return search_url, query_params


def create_url_tweet_public_metrics(tweet_id):
    search_url = '{}tweets/{}'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {'tweet.fields': 'public_metrics,author_id'}
    return search_url, query_params


def create_url_user_followers(user_id, pagination_token=None):
    search_url = '{}users/{}/followers'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {
        'pagination_token': pagination_token
    }
    return search_url, query_params

def create_url_recent_tweets_on_conversation(tweet_id, since_id, pagination_token=None):
    search_url = '{}tweets/search/recent?query=conversation_id%3A{}'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {
        'since_id': since_id,
        'max_results': 100,
        'tweet.fields': 'id,created_at,text,author_id,in_reply_to_user_id,entities,public_metrics,conversation_id',
        'user.fields': 'id,name,username,public_metrics',
        'pagination_token': pagination_token
    }
    return search_url, query_params

def create_url_post_in_reply_to_tweet(comment_id, text):
    url = '{}tweets'.format(TWITTER_URL_PREFIX)
    data = json.dumps({
        "reply": {
            "in_reply_to_tweet_id": str(comment_id)
        },
        "text": text
    })
    return url, data