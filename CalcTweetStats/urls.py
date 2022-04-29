TWITTER_URL_PREFIX = 'https://api.twitter.com/2/'


def create_url_user_tweets(user_id, pagination_token=None):
    search_url = '{}users/{}/tweets'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {
        'tweet.fields': 'id,author_id,public_metrics,created_at',
        'max_results': 100,
        'pagination_token': pagination_token}
    return search_url, query_params


def create_url_liking_users(tweet_id):
    search_url = '{}tweets/{}/liking_users'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {'user.fields': 'id'}
    return search_url, query_params


def create_url_user_public_metrics(user_id):
    search_url = '{}users/{}?user.fields=public_metrics'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {}
    return search_url, query_params


def create_url_tweet_public_metrics(tweet_id):
    search_url = '{}tweets/{}?tweet.fields=public_metrics'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {}
    return search_url, query_params


def create_url_user_followers(user_id, pagination_token=None):
    search_url = '{}users/{}/followers'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {
        'pagination_token': pagination_token
    }
    return search_url, query_params
