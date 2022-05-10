from table import *
from urls import *
import os, requests
from time import sleep


def add_tweet_to_tracked_list(tweet_id, author_id):
    TrackedTweetsTable().update_newest_id(tweet_id, author_id, tweet_id)


def create_url_tweet_public_metrics(tweet_id):
    search_url = '{}tweets/{}'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {'tweet.fields': 'public_metrics,author_id'}
    return search_url, query_params


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


def auth():
    return os.environ['TwitterToken']


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


bearer_token = auth()
headers = create_headers(bearer_token)


def get_tweet_info(tweet_id):
    url, params = create_url_tweet_public_metrics(tweet_id)
    public_metrics = connect_to_endpoint(url, headers, params)
    return public_metrics


if __name__ == '__main__':
    tweet_id = 1523706291784282114
    tweet_info = get_tweet_info(tweet_id)
    add_tweet_to_tracked_list(tweet_id, tweet_info['data']['author_id'])