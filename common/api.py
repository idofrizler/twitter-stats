import os, requests
from ..common import urls
from time import sleep


def auth():
    return os.environ['TwitterToken']


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params=None, next_token=None, method="GET", data=None):
    if params:
        params['next_token'] = next_token   # params object received from create_url function
    response = requests.request(method, url, headers=headers, params=params, data=data)

    while response.status_code == 429:  # Rate limiting
        print('Rate limit reached; sleeping for 5 minutes')
        sleep(300)  # Sleep for 5 minutes and try again
        response = requests.request(method, url, headers=headers, params=params)

    if response.status_code != 200:
         raise Exception(response.status_code, response.text)

    return response.json()

# Tweets endpoints


def get_user_tweets(user_id, pagination_token=None):
    url, params = urls.create_url_user_tweets(user_id, pagination_token)
    tweets = connect_to_endpoint(url, headers, params)
    return tweets


def get_liking_user_for_tweet(tweet_id):
    url, params = urls.create_url_liking_users(tweet_id)
    liking_users = connect_to_endpoint(url, headers, params)
    return liking_users


def get_user_public_metrics(user_id):
    url, params = urls.create_url_user_public_metrics(user_id)
    public_metrics = connect_to_endpoint(url, headers, params)
    return public_metrics


def get_tweet_info(tweet_id):
    url, params = urls.create_url_tweet_public_metrics(tweet_id)
    public_metrics = connect_to_endpoint(url, headers, params)
    return public_metrics

# Followers endpoints

def get_user_followers(user_id, pagination_token=None):
    url, params = urls.create_url_user_followers(user_id, pagination_token)
    followers = connect_to_endpoint(url, headers, params)
    return followers



# Comment endpoints

def get_recent_comments_from_twitter(tweet_id, since_id, pagination_token=None):
    url, params = urls.create_url_recent_tweets_on_conversation(tweet_id, since_id, pagination_token)
    recent_comments = connect_to_endpoint(url, headers, params)
    return recent_comments


# Post comment

def post_comment(comment_id, text):
    url, data = urls.create_url_post_in_reply_to_tweet(comment_id, text)
    post_headers = headers.copy()
    post_headers['Content-type'] = 'application/json'
    connect_to_endpoint(url, method="POST", headers=post_headers, data=data)

# Init auth information

bearer_token = auth()
headers = create_headers(bearer_token)

