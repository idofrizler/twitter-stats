from table import *


def add_tweet_to_tracked_list(tweet_id, author_id):
    update_newest_id(tweet_id, author_id, tweet_id)


if __name__ == '__main__':
    add_tweet_to_tracked_list(1521900288327753734, 2847890797)