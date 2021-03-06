import os, requests
from venv import create
from ..common import urls
from time import sleep


def auth():
    return os.environ['TwitterToken']


def create_headers(bearer_token, is_json=False):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    if is_json:
        headers['Content-type'] = 'application/json'
    return headers


def connect_to_endpoint(url, headers, params=None, next_token=None, method="GET", data=None, auth=None):
    if params:
        params['next_token'] = next_token   # params object received from create_url function
    response = requests.request(method, url, headers=headers, params=params, data=data, auth=auth)

    while response.status_code == 429:  # Rate limiting
        print('Rate limit reached; sleeping for 5 minutes')
        sleep(300)  # Sleep for 5 minutes and try again
        response = requests.request(method, url, headers=headers, params=params)

    if response.status_code not in (200, 201):
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

def post_comment(comment_id, text, oauth_token):
    url, data = urls.create_url_post_in_reply_to_tweet(comment_id, text)
    # oauth_token = os.environ['OauthToken']
    post_headers = create_headers(oauth_token, True)
    connect_to_endpoint(url, method="POST", headers=post_headers, data=data)


# Oauth token refresh

def get_new_oauth_token(current_access_token, current_refresh_token):
    url, auth, data = urls.create_url_post_refresh_oauth_token(current_access_token, current_refresh_token)
    headers = {
        'Content-Type': 'application/json'
    }
    resp = connect_to_endpoint(url, method="POST", headers=headers, data=data, auth=auth)
    return resp['access_token'], resp['refresh_token']

# Init auth information

bearer_token = auth()
headers = create_headers(bearer_token)

