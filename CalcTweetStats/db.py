import datetime
from abc import ABC
import pymongo


class StatsDatabase(ABC):
    def __init__(self) -> None:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client['twitter_stats']
        self.tweets = db['tweets']
        self.users = db['users']

    def get_cache_lifetime(self):
        return datetime.datetime.now() - datetime.timedelta(hours=24)

    def insert_tweet_stats(self, tweet):
        tweet_id = tweet['id']
        author_id = tweet['author_id']
        text = tweet['text']
        public_metrics = tweet['public_metrics']
        created_at = tweet['created_at']

        filter_doc = {
            '_id': tweet_id,
        }
        update_doc = {
            '$set': {
                'author_id': author_id,
                'text': text,
                'metrics': public_metrics,
                'created_at': created_at,
                'modified_date': datetime.datetime.now(),
            }
        }
        self.tweets.update_one(filter_doc, update_doc, upsert=True)

    def get_tweet_stats(self, tweet_id):
        return self.tweets.find_one({'_id': tweet_id, 'modified_date': {'$gt': self.get_cache_lifetime()}})

    def insert_user_metrics(self, user_id, alias, pretty_name, metrics):
        filter_doc = {
            '_id': user_id
        }
        update_doc = {
            '$set': {
                'alias': alias,
                'pretty_name': pretty_name,
                'metrics': metrics,
                'modified_date': datetime.datetime.now(),
            }
        }
        self.users.update_one(filter_doc, update_doc, upsert=True)

    def get_user_metrics(self, user_id):
        return self.users.find_one({'_id': user_id, 'modified_date': {'$gt': self.get_cache_lifetime()}})

    def add_to_following_set(self, following_user_id, followed_user_id):
        doc = {
            '$addToSet': {
                'following': followed_user_id
            }
        }
        self.users.update_one({'_id': following_user_id}, doc)

    def get_celeb_follower(self, user_id):
        doc = {
            'following': user_id
        }
        return self.users.find(doc, sort=[('metrics.followers_count', -1)]).limit(5)

    def get_pulitzer_tweet(self, user_id):
        doc = {
            'author_id': str(user_id)
        }
        return self.tweets.find_one(doc, sort=[('metrics.like_count', -1)])
