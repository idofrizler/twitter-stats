import os, requests
from .urls import *
from time import sleep


def auth():
    return os.getenv('TOKEN')


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params, next_token=None):
    params['next_token'] = next_token   # params object received from create_url function
    response = requests.request("GET", url, headers=headers, params=params)

    while response.status_code == 429:  # Rate limiting
        print('Rate limit reached; sleeping for 5 minutes')
        sleep(300)  # Sleep for 5 minutes and try again
        response = requests.request("GET", url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()

# Tweets endpoints


def get_user_tweets(headers, user_id, pagination_token=None):
    url, params = create_url_user_tweets(user_id, pagination_token)
    tweets = connect_to_endpoint(url, headers, params)
    return tweets


def get_liking_user_for_tweet(headers, tweet_id):
    url, params = create_url_liking_users(tweet_id)
    liking_users = connect_to_endpoint(url, headers, params)
    return liking_users


def get_user_public_metrics(headers, user_id):
    url, params = create_url_user_public_metrics(user_id)
    public_metrics = connect_to_endpoint(url, headers, params)
    return public_metrics


def get_tweet_info(headers, tweet_id):
    url, params = create_url_tweet_public_metrics(tweet_id)
    public_metrics = connect_to_endpoint(url, headers, params)
    return public_metrics

# Followers endpoints

def get_user_followers(headers, user_id, pagination_token=None):
    url, params = create_url_user_followers(user_id, pagination_token)
    followers = connect_to_endpoint(url, headers, params)
    return followers
